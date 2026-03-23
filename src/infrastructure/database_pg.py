"""
Módulo de conexión a la base de datos PostgreSQL.

Configura SQLAlchemy async para conectarse a PostgreSQL usando asyncpg.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.core.config import get_settings

settings = get_settings()

# Motor async de SQLAlchemy para PostgreSQL
pg_engine = create_async_engine(
    settings.database_pg_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session factory para PostgreSQL
pg_async_session = async_sessionmaker(
    pg_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class BasePg(DeclarativeBase):
    """Clase base para los modelos SQLAlchemy de PostgreSQL."""
    pass


async def init_db_pg():
    """Crea todas las tablas en la base de datos PostgreSQL."""
    async with pg_engine.begin() as conn:
        await conn.run_sync(BasePg.metadata.create_all)


async def get_pg_session() -> AsyncSession:
    """
    Generador de sesiones PostgreSQL para inyección de dependencias.

    Yields:
        AsyncSession conectada a PostgreSQL
    """
    async with pg_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
