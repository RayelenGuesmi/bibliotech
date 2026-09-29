"""ajout due_date sur loans

Revision ID: 1df1bbd58a7f
Revises: a9aae99c0094
Create Date: 2026-09-29 14:34:19.347579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1df1bbd58a7f'
down_revision: Union[str, Sequence[str], None] = 'a9aae99c0094'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ajoute la colonne d'abord en nullable pour ne pas bloquer sur les lignes existantes
    op.add_column('loans', sa.Column('due_date', sa.DateTime(), nullable=True))
    # Donne une valeur de secours aux emprunts déjà existants (14 jours après leur loan_date)
    op.execute("UPDATE loans SET due_date = loan_date + INTERVAL '14' DAY WHERE due_date IS NULL")
    # Rend la colonne obligatoire maintenant que toutes les lignes ont une valeur
    op.alter_column('loans', 'due_date', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('loans', 'due_date')