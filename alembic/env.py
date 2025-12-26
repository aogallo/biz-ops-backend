"""Alembic environment configuration for database migrations.

This module configures Alembic to work with our FastAPI application and SQLModel.
"""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import all models so Alembic can detect schema changes
# IMPORTANT: Import all entities here so SQLModel.metadata includes them
from app.internal.account.entity import Account  # noqa: F401
from app.internal.account_payable.entity import AccountPayable  # noqa: F401
from app.internal.account_receivable.entity import (  # noqa: F401
    AccountReceivable,
)
from app.internal.business_partner.entity import BusinessPartner  # noqa: F401
from app.internal.category.entity import Category  # noqa: F401
from app.internal.company.entity import Company  # noqa: F401
from app.internal.invoice.entity import Invoice, InvoiceDetail  # noqa: F401
from app.internal.journal.entity import JournalEntry  # noqa: F401
from app.internal.organization.entity import Organization  # noqa: F401
from app.internal.product.entity import Product  # noqa: F401
from app.internal.user.entity import User, UserCompanyAccess  # noqa: F401
from sqlmodel import SQLModel

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel metadata for autogenerate support
target_metadata = SQLModel.metadata

# Override sqlalchemy.url with environment variable
database_uri = os.getenv("DATABASE_URI")
if database_uri:
    config.set_main_option("sqlalchemy.url", database_uri)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    # Get configuration from alembic.ini
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}

    # Override with environment variable
    if database_uri:
        configuration["sqlalchemy.url"] = database_uri

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Detect column type changes
            compare_server_default=True,  # Detect default value changes
            # Don't automatically drop indexes when renaming tables
            render_as_batch=True,  # For SQLite support
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
