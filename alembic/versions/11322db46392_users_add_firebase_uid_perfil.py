"""users: add firebase_uid + perfil

Revision ID: 11322db46392
Revises: cede9066a5da
Create Date: 2025-10-21 13:37:10.549600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11322db46392'
down_revision: Union[str, Sequence[str], None] = 'cede9066a5da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")

    op.add_column("users", sa.Column("firebase_uid", sa.String(), nullable=True))
    op.add_column("users", sa.Column("photo_url", sa.String(), nullable=True))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_users_firebase_uid", "users", ["firebase_uid"], unique=True)


def downgrade():
    op.drop_index("ix_users_firebase_uid", table_name="users")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "is_active")
    op.drop_column("users", "photo_url")
    op.drop_column("users", "firebase_uid")
