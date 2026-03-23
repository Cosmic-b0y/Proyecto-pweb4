"""
Dependencias compartidas para la API.

Provee inyección de dependencias para sesión de BD,
repositorios, y autenticación JWT.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_session
from src.infrastructure.adapters.mysql_user_repository import MySQLUserRepository
from src.infrastructure.adapters.mysql_order_repository import MySQLOrderRepository
from src.application.services.user_service import UserService
from src.application.services.order_service import OrderService
from src.application.services.auth_service import AuthService
from src.application.ports.user_repository import UserRepositoryPort
from src.application.ports.order_repository import OrderRepositoryPort
from src.domain.entities.user import User

# Esquema de seguridad Bearer
security = HTTPBearer()


async def get_db(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    """Obtiene la sesión de base de datos."""
    return session


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepositoryPort:
    """Obtiene el repositorio de usuarios (MySQL)."""
    return MySQLUserRepository(session)


def get_order_repository(
    session: AsyncSession = Depends(get_db),
) -> OrderRepositoryPort:
    """Obtiene el repositorio de pedidos (MySQL)."""
    return MySQLOrderRepository(session)


def get_user_service(
    repo: UserRepositoryPort = Depends(get_user_repository),
) -> UserService:
    """Obtiene el servicio de usuarios."""
    return UserService(repo)


def get_order_service(
    order_repo: OrderRepositoryPort = Depends(get_order_repository),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
) -> OrderService:
    """Obtiene el servicio de pedidos."""
    return OrderService(order_repo, user_repo)


def get_auth_service(
    repo: UserRepositoryPort = Depends(get_user_repository),
) -> AuthService:
    """Obtiene el servicio de autenticación."""
    return AuthService(repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepositoryPort = Depends(get_user_repository),
) -> User:
    """
    Extrae y valida el JWT del header Authorization.

    Returns:
        Usuario autenticado

    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
    """
    try:
        payload = AuthService.verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene user_id",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado",
        )

    return user
