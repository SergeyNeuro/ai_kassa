import urllib
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys

# Проброс пути, чтобы работали импорты моделей приложения.
sys.path.append(os.path.join(sys.path[0], 'src'))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

from storage.database.db.postgres_alchemy.alchemy_core import Base

# Импортируем все модели, чтобы Alembic их видел и мог сделать миграцию
from storage.database.db.postgres_alchemy.customers import CustomersTable
from storage.database.db.postgres_alchemy.auth import AuthTokenTable
from storage.database.db.postgres_alchemy.menu import MenuTable
from storage.database.db.postgres_alchemy.changing_dish import ChangingDishTable
from storage.database.db.postgres_alchemy.dish import DishTable
from storage.database.db.postgres_alchemy.food_point import FoodPointTable
from storage.database.db.postgres_alchemy.week_day_dish import WeekDayDishTable
from storage.database.db.postgres_alchemy.r_keeper_credentials import RKeeperCredentialsTable
from storage.database.db.postgres_alchemy.r_keeper_dish import RKeeperDishTable
from storage.database.db.postgres_alchemy.discount_account import DiscountAccountTable
from storage.database.db.postgres_alchemy.kassa import KassaTable
from storage.database.db.postgres_alchemy.history import HistoryTable
from storage.database.db.postgres_alchemy.discount_transaction import DiscountTransactionTable

# импортируем глобальные переменные
from config import DB_HOST, DB_NAME, DB_PORT, DB_PASS, DB_USER

# escape password so it fits into connection string
DB_PASS = urllib.parse.quote_plus(DB_PASS).replace("%", "%%")

section = config.config_ini_section
config.set_section_option(section, "DB_HOST", DB_HOST)
config.set_section_option(section, "DB_NAME", DB_NAME)
config.set_section_option(section, "DB_PORT", DB_PORT)
config.set_section_option(section, "DB_PASS", DB_PASS)
config.set_section_option(section, "DB_USER", DB_USER)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
