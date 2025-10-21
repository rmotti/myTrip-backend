"""make password_hash nullable for firebase users

Revision ID: 7c3c1b9e2f6a
Revises: 11322db46392
Create Date: 2025-10-21 19:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c3c1b9e2f6a'
down_revision: Union[str, Sequence[str], None] = '11322db46392'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        'users',
        'password_hash',
        existing_type=sa.String(),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        'users',
        'password_hash',
        existing_type=sa.String(),
        nullable=False,
    )

