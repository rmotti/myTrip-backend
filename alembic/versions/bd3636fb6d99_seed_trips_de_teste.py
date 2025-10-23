"""seed trips de teste

Revision ID: 20251023_seed_trips
Revises: 1cba98eb2be9
Create Date: 2025-10-23 00:00:00.000000
"""
from alembic import op
from sqlalchemy.sql import text

# revisões
revision = "20251023_seed_trips"
down_revision = "1cba98eb2be9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    user_row = conn.execute(text("SELECT id FROM users ORDER BY id LIMIT 1")).first()
    if not user_row:
        print("⚠️ Nenhum usuário encontrado, seed de trips ignorado.")
        return

    user_id = user_row[0]

    conn.execute(
        text("""
            INSERT INTO trips (user_id, name, start_date, end_date, currency_code, total_budget)
            VALUES 
              (:uid, :n1, :s1, :e1, :c1, :b1),
              (:uid, :n2, :s2, :e2, :c2, :b2),
              (:uid, :n3, :s3, :e3, :c3, :b3)
        """),
        dict(
            uid=user_id,
            n1="Viagem a Paris",
            s1="2025-03-10",
            e1="2025-03-17",
            c1="BRL",
            b1=5000.00,
            n2="Nordeste — Rota das Praias",
            s2="2025-07-05",
            e2="2025-07-15",
            c2="BRL",
            b2=8000.00,
            n3="Buenos Aires Gastronômica",
            s3="2025-11-01",
            e3="2025-11-06",
            c3="ARS",
            b3=3500.00,
        ),
    )

    # 🔥 COMMIT EXPLÍCITO
    conn.commit()



def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("""
            DELETE FROM trips
             WHERE name IN (
               'Viagem a Paris',
               'Nordeste — Rota das Praias',
               'Buenos Aires Gastronômica'
             )
        """)
    )
