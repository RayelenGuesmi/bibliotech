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

    bind = op.get_bind()
    if bind.dialect.name == 'oracle':
        # Backfill + passage en NOT NULL : Oracle supporte ALTER COLUMN directement
        op.execute(
            "UPDATE loans SET due_date = loan_date + INTERVAL '14' DAY WHERE due_date IS NULL"
        )
        op.alter_column('loans', 'due_date', nullable=False)
    else:
        # SQLite (et autres moteurs limités) : backfill, puis mode batch pour la
        # contrainte NOT NULL (SQLite ne supporte pas ALTER COLUMN ... SET NOT NULL
        # directement ; le mode batch recrée la table en coulisses)
        op.execute(
            "UPDATE loans SET due_date = datetime(loan_date, '+14 days') WHERE due_date IS NULL"
        )
        with op.batch_alter_table('loans') as batch_op:
            batch_op.alter_column('due_date', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('loans', 'due_date')