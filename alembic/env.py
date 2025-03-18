import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.database import sync_engine 
from app.models import Base  

config = context.config


DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgresql+asyncpg"):
    SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
else:
    SYNC_DATABASE_URL = DATABASE_URL

config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_online():
    """Run migrations in 'online' mode."""
    with sync_engine.connect() as connection:  
        context.configure(
            connection=connection,
            target_metadata=Base.metadata
        )

        with context.begin_transaction():
            context.run_migrations()

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
