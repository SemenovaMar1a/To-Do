from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

# Явный импорт всех моделей
from models.users import User
from models.tasks import Task

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Убедитесь, что метаданные берутся из SQLModel
target_metadata = SQLModel.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            # Добавьте эту настройку:
            include_schemas=True,
            process_revision_directives=lambda x, y, z: None,
            compare_type=True,
            compare_server_default=True,
            # Добавляем импорт sqlmodel в миграции
            user_module_prefix="sqlmodel.",
        )
        with context.begin_transaction():
            context.run_migrations()
    import os
    print("Current working directory:", os.getcwd())
    print("Database URL:", config.get_main_option("sqlalchemy.url"))

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()