"""
Puerto de Repositorio de Usuario (Interface)

Este módulo define el contrato/interfaz que deben implementar
los adaptadores de persistencia de usuarios.

En Arquitectura Hexagonal:
- Los Puertos son interfaces que definen cómo la aplicación
  se comunica con el mundo exterior
- Los Adaptadores implementan estos puertos
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.user import User


class UserRepositoryPort(ABC):
    """
    Puerto (Interface) para el repositorio de usuarios.
    
    Define las operaciones que cualquier implementación de
    repositorio de usuarios debe soportar.
    """
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            User si existe, None si no se encuentra
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Correo electrónico del usuario
            
        Returns:
            User si existe, None si no se encuentra
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[User]:
        """
        Obtiene todos los usuarios.
        
        Returns:
            Lista de todos los usuarios
        """
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Guarda un usuario (crear o actualizar).
        
        Args:
            user: Entidad de usuario a guardar
            
        Returns:
            Usuario guardado con ID asignado
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """
        Elimina un usuario por su ID.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            True si se eliminó, False si no existía
        """
        pass
