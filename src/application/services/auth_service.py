"""
Servicio de Autenticación - Casos de Uso

Implementa el flujo de login/registro que pasa por RabbitMQ
y valida contra MySQL.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.application.ports.user_repository import UserRepositoryPort
from src.domain.entities.user import User
from src.core.config import get_settings
from src.infrastructure.messaging.rabbitmq import RabbitMQPublisher

logger = logging.getLogger(__name__)
settings = get_settings()

# Contexto de hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Servicio de autenticación.

    Flujo de Login:
    1. Recibe credenciales (email, password)
    2. Publica evento de intento de login en RabbitMQ
    3. Valida credenciales contra MySQL
    4. Publica evento de resultado en RabbitMQ
    5. Genera y retorna JWT token
    """

    def __init__(self, user_repository: UserRepositoryPort):
        self._user_repository = user_repository

    async def register(self, email: str, name: str, password: str) -> User:
        """
        Registra un nuevo usuario.

        Args:
            email: Correo electrónico
            name: Nombre completo
            password: Contraseña en texto plano

        Returns:
            Usuario creado

        Raises:
            ValueError: Si el email ya existe
        """
        # Verificar si el email ya existe
        existing = await self._user_repository.get_by_email(email)
        if existing:
            raise ValueError(f"El email {email} ya está registrado")

        # Hash de la contraseña con bcrypt
        password_hash = pwd_context.hash(password)

        # Crear entidad de usuario
        user = User.create(email=email, name=name, password=password)
        # Sobrescribir el hash con bcrypt
        user.password_hash = password_hash

        # Guardar en MySQL
        saved_user = await self._user_repository.save(user)

        # Publicar evento de registro en RabbitMQ
        try:
            await RabbitMQPublisher.publish_register_event(
                user_id=saved_user.id,
                email=saved_user.email,
            )
        except Exception as e:
            logger.warning(f"No se pudo publicar evento de registro en RabbitMQ: {e}")

        return saved_user

    async def login(self, email: str, password: str) -> dict:
        """
        Inicia sesión: valida credenciales via RabbitMQ + MySQL.

        Flujo:
        1. Publica intento de login en RabbitMQ
        2. Busca usuario en MySQL
        3. Verifica contraseña
        4. Publica resultado en RabbitMQ
        5. Genera JWT token

        Args:
            email: Correo electrónico
            password: Contraseña

        Returns:
            dict con access_token y token_type

        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # Publicar intento de login en RabbitMQ
        try:
            await RabbitMQPublisher.publish(
                "auth_events",
                {
                    "event_type": "login_attempt",
                    "email": email,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        except Exception as e:
            logger.warning(f"No se pudo publicar intento de login en RabbitMQ: {e}")

        # Buscar usuario en MySQL
        user = await self._user_repository.get_by_email(email)
        if not user:
            # Publicar login fallido
            try:
                await RabbitMQPublisher.publish_login_event(
                    user_id="unknown",
                    email=email,
                    success=False,
                )
            except Exception:
                pass
            raise ValueError("Credenciales inválidas")

        # Verificar contraseña con bcrypt
        if not pwd_context.verify(password, user.password_hash):
            # Publicar login fallido
            try:
                await RabbitMQPublisher.publish_login_event(
                    user_id=user.id,
                    email=email,
                    success=False,
                )
            except Exception:
                pass
            raise ValueError("Credenciales inválidas")

        if not user.is_active:
            raise ValueError("Usuario desactivado")

        # Publicar login exitoso en RabbitMQ
        try:
            await RabbitMQPublisher.publish_login_event(
                user_id=user.id,
                email=user.email,
                success=True,
            )
        except Exception as e:
            logger.warning(f"No se pudo publicar evento de login en RabbitMQ: {e}")

        # Generar JWT token
        access_token = self.create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Genera un token JWT.

        Args:
            data: Datos a incluir en el token
            expires_delta: Tiempo de expiración (opcional)

        Returns:
            Token JWT codificado
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verifica y decodifica un token JWT.

        Args:
            token: Token JWT

        Returns:
            Payload del token decodificado

        Raises:
            ValueError: Si el token es inválido o expiró
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            return payload
        except JWTError as e:
            raise ValueError(f"Token inválido: {e}")
