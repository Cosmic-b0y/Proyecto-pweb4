"""
Adaptador de Repositorio de Usuario en Memoria

Implementación del puerto UserRepositoryPort que almacena
los datos en memoria. Útil para desarrollo y pruebas.

En Arquitectura Hexagonal:
- Los Adaptadores implementan los Puertos (interfaces)
- Pertenecen a la capa de Infraestructura
- Pueden ser fácilmente intercambiados por otras implementaciones
"""

from typing import Optional, List, Dict
from src.application.ports.user_repository import UserRepositoryPort
from src.domain.entities.user import User


class MemoryUserRepository(UserRepositoryPort):
    """
    Implementación en memoria del repositorio de usuarios.
    
    Almacena los usuarios en un diccionario en memoria.
    Ideal para desarrollo, pruebas y prototipos.
    """
    
    def __init__(self):
        """Inicializa el almacén en memoria."""
        self._users: Dict[str, User] = {}
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            User si existe, None si no se encuentra
        """
        return self._users.get(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Correo electrónico del usuario
            
        Returns:
            User si existe, None si no se encuentra
        """
        email_lower = email.lower()
        for user in self._users.values():
            if user.email.lower() == email_lower:
                return user
        return None
    
    async def get_all(self) -> List[User]:
        """
        Obtiene todos los usuarios.
        
        Returns:
            Lista de todos los usuarios
        """
        return list(self._users.values())
    
    async def save(self, user: User) -> User:
        """
        Guarda un usuario (crear o actualizar).
        
        Args:
            user: Entidad de usuario a guardar
            
        Returns:
            Usuario guardado
        """
        self._users[user.id] = user
        return user
    
    async def delete(self, user_id: str) -> bool:
        """
        Elimina un usuario por su ID.
        
        Args:
            user_id: Identificador único del usuario
            
        Returns:
            True si se eliminó, False si no existía
        """
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    
    def clear(self) -> None:
        """Limpia todos los usuarios (útil para tests)."""
        self._users.clear()
    
    @property
    def count(self) -> int:
        """Retorna el número de usuarios almacenados."""
        return len(self._users)
