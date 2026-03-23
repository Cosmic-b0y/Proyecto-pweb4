"""
API de Autenticación.

Endpoints para registro, login (pasa por RabbitMQ) y perfil.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr

from src.application.services.auth_service import AuthService
from src.infrastructure.api.dependencies import get_auth_service, get_current_user
from src.domain.entities.user import User


# ============== Schemas ==============

class RegisterRequest(BaseModel):
    """Schema para registro de usuario."""
    email: EmailStr
    name: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "name": "Juan Pérez",
                "password": "mipassword123"
            }
        }


class LoginRequest(BaseModel):
    """Schema para login."""
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "password": "mipassword123"
            }
        }


class TokenResponse(BaseModel):
    """Schema de respuesta con JWT token."""
    access_token: str
    token_type: str
    user: dict


class UserProfileResponse(BaseModel):
    """Schema de respuesta del perfil del usuario autenticado."""
    id: str
    email: str
    name: str
    is_active: bool
    created_at: str


# ============== Router ==============

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Registra un nuevo usuario.

    Crea el usuario en MySQL y publica un evento de registro en RabbitMQ.

    Returns:
        JWT token + datos del usuario
    """
    try:
        user = await auth_service.register(
            email=request.email,
            name=request.name,
            password=request.password,
        )
        # Generar token para el nuevo usuario
        token = auth_service.create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user.to_dict(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Inicia sesión.

    Flujo:
    1. Publica intento de login en RabbitMQ
    2. Valida credenciales contra MySQL
    3. Publica resultado en RabbitMQ
    4. Retorna JWT token

    Returns:
        JWT token + datos del usuario
    """
    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password,
        )
        return TokenResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene el perfil del usuario autenticado.

    Requiere token JWT en el header:
    `Authorization: Bearer <token>`

    Returns:
        Datos del perfil del usuario
    """
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
    )
