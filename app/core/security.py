import bcrypt


def hash_password(password: str) -> str:
    """Transforme un mot de passe en clair en empreinte bcrypt irréversible."""
    # bcrypt limite à 72 octets : on tronque proprement au besoin
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe correspond à son empreinte stockée."""
    password_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))