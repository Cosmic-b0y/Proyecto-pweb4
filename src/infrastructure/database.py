"""
Módulo de conexión a la base de datos MySQL.

Configura SQLAlchemy async para conectarse a MySQL usando aiomysql.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.core.config import get_settings

settings = get_settings()

# Motor async de SQLAlchemy para MySQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base para los modelos SQLAlchemy."""
    pass


async def init_db():
    """Crea todas las tablas en la base de datos."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """
    Generador de sesiones para inyección de dependencias.

    Yields:
        AsyncSession conectada a MySQL
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
