# alembic/env.py
from __future__ import annotations
from pathlib import Path
import sys, os
from logging.config import fileConfig
from alembic import context

# --- garante que o pacote "app" é importável ---
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# --- carrega variáveis do arquivo .env ---
from dotenv import load_dotenv
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Aviso: arquivo .env não encontrado em {env_path}")

# --- importa Base e engine factory do app ---
from app.db import Base, get_engine
import app.models  # garante que todos os modelos sejam registrados

# --- config padrão do Alembic ---
config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """Obtém a URL do banco de dados a partir do .env ou do alembic.ini."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        # remove aspas duplas do início/fim, se existirem
        return env_url.strip('"').strip("'")
    ini_url = config.get_main_option("sqlalchemy.url")
    if ini_url:
        return ini_url
    # fallback: pega do get_engine() do app
    return str(get_engine().url)


def run_migrations_offline() -> None:
    """Executa as migrações no modo offline."""
    url = _get_url()
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
    """Executa as migrações no modo online."""
    engine = get_engine()
    with engine.connect() as connection:  # <-- corrigido aqui!
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=False,  # útil p/ SQLite; False em Postgres
        )
        with context.begin_transaction():
            context.run_migrations()

