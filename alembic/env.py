# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys, os

# Tambah path project biar bisa import app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import Base

# Import semua models biar terdeteksi
from app.models.user import User, Session
from app.models.product import Product, ScrapeJob
from app.models.review import Review, Sentence, Report
from app.models.chat import ChatSession, ChatMessage

config = context.config

# Set URL dari .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ini yang bikin autogenerate bisa detect perubahan model
target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()