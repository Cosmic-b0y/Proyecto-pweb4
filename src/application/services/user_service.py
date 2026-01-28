"""
Servicio de Usuario - Casos de Uso

Este módulo contiene la lógica de negocio para las operaciones
relacionadas con usuarios. Implementa los casos de uso de la aplicación.

En Clean Architecture, los servicios de aplicación:
- Orquestan el flujo de datos
- Implementan casos de uso específicos
- Dependen de abstracciones (puertos), no de implementaciones concretas
"""

from typing import Optional, List
from src.application.ports.user_repository import UserRepositoryPort
from src.domain.entities.user import User


class UserService:
    """
    Servicio de aplicación para operaciones de usuario.
    
    Implementa los casos de uso relacionados con la gestión de usuarios.
    Depende del puerto UserRepositoryPort, no de una implementación concreta.
    """
    
    def __init__(self, user_repository: UserRepositoryPort):
        """
        Inicializa el servicio con un repositorio de usuarios.
        
        Args:
            user_repository: Implementación del puerto de repositorio
        """
        self._user_repository = user_repository
    
    async def create_user(
        self, 
        email: str, 
        name: str, 
        password: str
    ) -> User:
        """
        Caso de uso: Crear un nuevo usuario.
        
        Args:
            email: Correo electrónico del usuario
            name: Nombre completo del usuario
            password: Contraseña del usuario
            
        Returns:
            Usuario creado
            
        Raises:
            ValueError: Si el email ya está registrado
        """
        # Verificar si el email ya existe
        existing_user = await self._user_repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"El email {email} ya está registrado")
        
        # Crear entidad de usuario
        user = User.create(email=email, name=name, password=password)
        
        # Persistir y retornar
        return await self._user_repository.save(user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Caso de uso: Obtener usuario por ID.
        
        Args:
            user_id: Identificador del usuario
            
        Returns:
            Usuario si existe, None si no
        """
        return await self._user_repository.get_by_id(user_id)
    
    async def get_all_users(self) -> List[User]:
        """
        Caso de uso: Listar todos los usuarios.
        
        Returns:
            Lista de usuarios
        """
        return await self._user_repository.get_all()
    
    async def update_user(
        self, 
        user_id: str, 
        name: Optional[str] = None,
        email: Optional[str] = None
    ) -> Optional[User]:
        """
        Caso de uso: Actualizar datos de usuario.
        
        Args:
            user_id: ID del usuario a actualizar
            name: Nuevo nombre (opcional)
            email: Nuevo email (opcional)
            
        Returns:
            Usuario actualizado o None si no existe
        """
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return None
        
        if name:
            user.name = name
        if email:
            user.email = email
        
        return await self._user_repository.save(user)
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Caso de uso: Eliminar usuario.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        return await self._user_repository.delete(user_id)
