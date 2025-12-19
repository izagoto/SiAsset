from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text as sa_text
from alembic import context

from app.db.base import Base
from app.core.config import settings
from app.models import * 

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        {
            "sqlalchemy.url": settings.DATABASE_URL
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
            try:
                from urllib.parse import urlparse
                parsed = urlparse(settings.DATABASE_URL)
                db_user = parsed.username or "digifor"
                
                connection.execute(
                    sa_text(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {db_user}")
                )
                connection.execute(
                    sa_text(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {db_user}")
                )
                connection.execute(
                    sa_text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {db_user}")
                )
                connection.execute(
                    sa_text(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {db_user}")
                )
                connection.commit()
            except Exception as e:
                print(f"Warning: Could not grant permissions automatically: {e}")
                print("Please run scripts/grant_permissions.sql manually as a superuser")

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
