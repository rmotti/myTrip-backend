from pathlib import Path
import sys
from logging.config import fileConfig
from alembic import context

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.db import engine, Base        # ou from app.database ...
import app.models                      # garante que as tabelas estão no Base.metadata

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    raise RuntimeError("Use o modo online")

def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            # connection.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS citext;")
            context.run_migrations()

run_migrations_online()
