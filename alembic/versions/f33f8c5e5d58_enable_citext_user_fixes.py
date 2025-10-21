"""enable citext + user fixes

Revision ID: f33f8c5e5d58
Revises: 11322db46392
Create Date: 2025-10-21 14:20:45.609289
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f33f8c5e5d58'
down_revision: Union[str, Sequence[str], None] = '11322db46392'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # habilita extensão CITEXT (se ainda não estiver criada)
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")

    # torna a coluna password_hash opcional para usuários do Firebase
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(),
        nullable=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    # reverte a alteração da coluna (torna novamente obrigatória)
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(),
        nullable=False
    )
    # (normalmente não removemos a extensão citext)
    # op.execute("DROP EXTENSION IF EXISTS citext;")
