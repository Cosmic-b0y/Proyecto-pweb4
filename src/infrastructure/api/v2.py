"""
API v2 - Controladores de la versión 2

Versión mejorada de la API con características adicionales:
- Paginación
- Filtros
- Respuestas más detalladas

Demuestra cómo versionar APIs manteniendo compatibilidad hacia atrás.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

from src.application.services.user_service import UserService
from src.application.ports.user_repository import UserRepositoryPort
from src.infrastructure.adapters.memory_user_repository import MemoryUserRepository


# ============== Schemas v2 (DTOs mejorados) ==============

class UserCreateRequestV2(BaseModel):
    """Schema v2 para crear un usuario con más campos."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "name": "Juan Pérez",
                "password": "contraseña123"
            }
        }


class UserResponseV2(BaseModel):
    """Schema v2 de respuesta con metadatos adicionales."""
    id: str
    email: str
    name: str
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Respuesta paginada genérica."""
    items: List[UserResponseV2]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthResponse(BaseModel):
    """Respuesta del health check."""
    status: str
    version: str
    timestamp: str


# ============== Dependencias ==============

_user_repository_v2: Optional[MemoryUserRepository] = None


def get_user_repository() -> UserRepositoryPort:
    """Obtiene la instancia del repositorio de usuarios."""
    global _user_repository_v2
    if _user_repository_v2 is None:
        _user_repository_v2 = MemoryUserRepository()
    return _user_repository_v2


def get_user_service(
    repository: UserRepositoryPort = Depends(get_user_repository)
) -> UserService:
    """Obtiene la instancia del servicio de usuarios."""
    return UserService(repository)


# ============== Router v2 ==============

router = APIRouter(
    prefix="/users",
    tags=["users-v2"],
    responses={
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Error de validación"}
    }
)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Verifica el estado del servicio.
    
    Returns:
        Estado del servicio
    """
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/", response_model=PaginatedResponse)
async def list_users_paginated(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Elementos por página"),
    active_only: bool = Query(False, description="Solo usuarios activos"),
    service: UserService = Depends(get_user_service)
):
    """
    Lista usuarios con paginación y filtros.
    
    Args:
        page: Número de página (desde 1)
        page_size: Cantidad de elementos por página
        active_only: Filtrar solo usuarios activos
        
    Returns:
        Lista paginada de usuarios
    """
    all_users = await service.get_all_users()
    
    # Aplicar filtro
    if active_only:
        all_users = [u for u in all_users if u.is_active]
    
    total = len(all_users)
    total_pages = (total + page_size - 1) // page_size
    
    # Aplicar paginación
    start = (page - 1) * page_size
    end = start + page_size
    paginated_users = all_users[start:end]
    
    return PaginatedResponse(
        items=[UserResponseV2(**u.to_dict()) for u in paginated_users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{user_id}", response_model=UserResponseV2)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Obtiene un usuario por su ID.
    
    Args:
        user_id: Identificador único del usuario
        
    Returns:
        Datos completos del usuario
    """
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": f"Usuario con id '{user_id}' no encontrado"
            }
        )
    return UserResponseV2(**user.to_dict())


@router.post("/", response_model=UserResponseV2, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequestV2,
    service: UserService = Depends(get_user_service)
):
    """
    Crea un nuevo usuario con validación mejorada.
    
    Args:
        request: Datos del usuario a crear
        
    Returns:
        Usuario creado con todos sus datos
    """
    try:
        user = await service.create_user(
            email=request.email,
            name=request.name,
            password=request.password
        )
        return UserResponseV2(**user.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "CONFLICT",
                "message": str(e)
            }
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Elimina un usuario (soft delete).
    
    Args:
        user_id: Identificador del usuario a eliminar
    """
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": f"Usuario con id '{user_id}' no encontrado"
            }
        )
