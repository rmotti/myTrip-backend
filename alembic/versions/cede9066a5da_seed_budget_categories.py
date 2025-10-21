"""seed budget categories

Revision ID: cede9066a5da
Revises: eddecdb10d91
Create Date: 2025-10-20 22:32:11.975515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cede9066a5da'
down_revision: Union[str, Sequence[str], None] = 'eddecdb10d91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        INSERT INTO budget_categories (id, key, label) VALUES
        (1,'flight','Voos'),
        (2,'lodging','Hospedagem'),
        (3,'food','Alimentação'),
        (4,'transport','Transporte'),
        (5,'tour','Passeios'),
        (6,'insurance','Seguro'),
        (7,'other','Outros')
        ON CONFLICT (id) DO NOTHING;
    """)
def downgrade():
    op.execute("DELETE FROM budget_categories WHERE id IN (1,2,3,4,5,6,7);")