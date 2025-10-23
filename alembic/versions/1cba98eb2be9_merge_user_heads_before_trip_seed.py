"""merge user heads before trip seed

Revision ID: 1cba98eb2be9
Revises: f33f8c5e5d58, 7c3c1b9e2f6a
Create Date: 2025-10-23 09:18:37.201983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1cba98eb2be9'
down_revision: Union[str, Sequence[str], None] = ('f33f8c5e5d58', '7c3c1b9e2f6a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
