# alembic/env.py
from __future__ import annotations
from pathlib import Path
import sys
from logging.config import fileConfig

from alembic import context

# --- garante que o pacote "app" é importável ---
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# --- importe do seu app: Base e FACTORY do engine ---
from app.db import Base, get_engine  # <--- trocamos engine por get_engine
import app.models  # garante que todos os modelos registrem no Base.metadata

# --- config padrão do Alembic ---
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Modo offline (sem conexão). Usaremos a URL do engine do app."""
    url = str(get_engine().url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online (com conexão aberta) usando o engine lazy do app."""
    engine = get_engine()
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,  # seguro p/ alterações em alguns providers
        )
        with context.begin_transaction():
            # Exemplo opcional:
            # connection.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS citext;")
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
