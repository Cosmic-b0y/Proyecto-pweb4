"""
API v1 - Controladores de la versión 1

Expone los endpoints REST de la API versión 1.
En Arquitectura Hexagonal, los controladores son adaptadores
que traducen las peticiones HTTP a llamadas de casos de uso.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from src.application.services.user_service import UserService
from src.infrastructure.api.dependencies import get_user_service


# ============== Schemas (DTOs) ==============

class UserCreateRequest(BaseModel):
    """Schema para crear un usuario."""
    email: EmailStr
    name: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "name": "Juan Pérez",
                "password": "contraseña123"
            }
        }


class UserUpdateRequest(BaseModel):
    """Schema para actualizar un usuario."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """Schema de respuesta de usuario."""
    id: str
    email: str
    name: str
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============== Router ==============

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Usuario no encontrado"}}
)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    service: UserService = Depends(get_user_service)
):
    """
    Lista todos los usuarios.
    
    Returns:
        Lista de usuarios registrados
    """
    users = await service.get_all_users()
    return [UserResponse(**user.to_dict()) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Obtiene un usuario por su ID.
    
    Args:
        user_id: Identificador único del usuario
        
    Returns:
        Datos del usuario
        
    Raises:
        HTTPException: Si el usuario no existe
    """
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id '{user_id}' no encontrado"
        )
    return UserResponse(**user.to_dict())


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    service: UserService = Depends(get_user_service)
):
    """
    Crea un nuevo usuario.
    
    Args:
        request: Datos del usuario a crear
        
    Returns:
        Usuario creado
        
    Raises:
        HTTPException: Si el email ya está registrado
    """
    try:
        user = await service.create_user(
            email=request.email,
            name=request.name,
            password=request.password
        )
        return UserResponse(**user.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    service: UserService = Depends(get_user_service)
):
    """
    Actualiza un usuario existente.
    
    Args:
        user_id: Identificador del usuario
        request: Datos a actualizar
        
    Returns:
        Usuario actualizado
        
    Raises:
        HTTPException: Si el usuario no existe
    """
    user = await service.update_user(
        user_id=user_id,
        name=request.name,
        email=request.email
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id '{user_id}' no encontrado"
        )
    return UserResponse(**user.to_dict())


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """
    Elimina un usuario.
    
    Args:
        user_id: Identificador del usuario a eliminar
        
    Raises:
        HTTPException: Si el usuario no existe
    """
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id '{user_id}' no encontrado"
        )
