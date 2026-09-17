"""
Script d'ingestion ETL : scrape books.toscrape.com et charge les livres
dans la base via l'API FastAPI (POST /books/).

EXTRACT   : télécharge le HTML des pages du catalogue
TRANSFORM : extrait titre, prix, disponibilité de chaque livre
LOAD      : envoie chaque livre à l'API via une requête POST
"""

import time
import requests
from bs4 import BeautifulSoup

# --- Configuration ---
BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
API_URL = "http://localhost:8000/books/"
DETAIL_BASE = "https://books.toscrape.com/catalogue/"
NB_PAGES = 2  # commence petit ; le site en a 50 au total


def extract_page(page_number: int) -> BeautifulSoup:
    """EXTRACT : télécharge une page et renvoie le HTML parsé."""
    url = BASE_URL.format(page_number)
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"          # <-- AJOUTE CETTE LIGNE
    return BeautifulSoup(response.text, "html.parser")


def get_genre(detail_url: str) -> str:
    """
    Scraping en profondeur : visite la page de détail d'un livre
    et extrait son genre depuis le fil d'Ariane (breadcrumb).
    """
    try:
        response = requests.get(detail_url, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        # Le breadcrumb : Home > Books > GENRE > Titre
        # On prend les <a> ; le genre est le 3e lien (index 2)
        breadcrumb_links = soup.select("ul.breadcrumb li a")
        if len(breadcrumb_links) >= 3:
            return breadcrumb_links[2].text.strip()
    except requests.RequestException:
        pass
    return "Inconnu"  # valeur de repli si problème


def transform_book(article) -> dict:
    """TRANSFORM : extrait les données d'un livre depuis son bloc HTML."""
    title = article.h3.a["title"]

    # Le lien vers la page de détail est dans le href du h3 > a
    # Il est relatif (ex: "a-light-in-the-attic_1000/index.html")
    relative_link = article.h3.a["href"]
    detail_url = DETAIL_BASE + relative_link

    # Scraping en profondeur : on va chercher le vrai genre
    genre = get_genre(detail_url)
    time.sleep(0.3)  # pause : on reste poli avec le serveur

    return {
        "title": title,
        "author": "Auteur inconnu",
        "genre": genre,
        "published_at": None,
    }


def load_book(book: dict) -> bool:
    """LOAD : envoie un livre à l'API via POST. Renvoie True si succès."""
    try:
        response = requests.post(API_URL, json=book, timeout=10)
        if response.status_code == 201:
            print(f"   Ajouté : {book['title']}")
            return True
        else:
            print(f"    Échec ({response.status_code}) : {book['title']}")
            return False
    except requests.RequestException as e:
        print(f"   Erreur réseau : {e}")
        return False


def main():
    print("=== Début du scraping de books.toscrape.com ===\n")
    total_added = 0

    for page in range(1, NB_PAGES + 1):
        print(f" Page {page}...")
        soup = extract_page(page)

        # Chaque livre est dans un <article class="product_pod">
        articles = soup.select("article.product_pod")
        print(f"   {len(articles)} livres trouvés sur cette page")

        for article in articles:
            book = transform_book(article)
            if load_book(book):
                total_added += 1

    print(f"\n=== Terminé : {total_added} livres ajoutés à la base ===")





if __name__ == "__main__":
    main()