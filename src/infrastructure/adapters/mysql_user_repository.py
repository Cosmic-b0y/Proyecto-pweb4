"""
Adaptador de Repositorio de Usuario en MySQL.

Implementación del puerto UserRepositoryPort que almacena
los datos en MySQL usando SQLAlchemy async.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.user_repository import UserRepositoryPort
from src.domain.entities.user import User
from src.infrastructure.models import UserModel


class MySQLUserRepository(UserRepositoryPort):
    """
    Implementación MySQL del repositorio de usuarios.

    Usa SQLAlchemy async sessions para comunicarse con MySQL.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            password_hash=model.password_hash,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convierte una entidad de dominio a modelo SQLAlchemy."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            name=entity.name,
            password_hash=entity.password_hash,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por su ID desde MySQL."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email desde MySQL."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[User]:
        """Obtiene todos los usuarios desde MySQL."""
        result = await self._session.execute(select(UserModel))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, user: User) -> User:
        """Guarda un usuario en MySQL (crear o actualizar)."""
        # Verificar si ya existe
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Actualizar
            existing.email = user.email
            existing.name = user.name
            existing.password_hash = user.password_hash
            existing.is_active = user.is_active
            existing.updated_at = user.updated_at
        else:
            # Crear nuevo
            model = self._to_model(user)
            self._session.add(model)

        await self._session.flush()
        return user

    async def delete(self, user_id: str) -> bool:
        """Elimina un usuario de MySQL por su ID."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
