"""
Entidad de Usuario

Define la entidad de dominio User con sus reglas de negocio.
Las entidades son objetos con identidad que encapsulan reglas del dominio.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid
import hashlib


@dataclass
class User:
    """
    Entidad de dominio: Usuario
    
    Representa un usuario del sistema con sus atributos y comportamientos.
    Esta entidad pertenece al núcleo del dominio y no depende de
    ninguna capa externa.
    """
    
    id: str
    email: str
    name: str
    password_hash: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, email: str, name: str, password: str) -> "User":
        """
        Factory method para crear un nuevo usuario.
        
        Args:
            email: Correo electrónico
            name: Nombre completo
            password: Contraseña en texto plano
            
        Returns:
            Nueva instancia de User
        """
        return cls(
            id=str(uuid.uuid4()),
            email=email.lower().strip(),
            name=name.strip(),
            password_hash=cls._hash_password(password),
            is_active=True,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hashea una contraseña.
        
        Nota: En producción usar bcrypt o argon2.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """
        Verifica si la contraseña es correcta.
        
        Args:
            password: Contraseña a verificar
            
        Returns:
            True si la contraseña es correcta
        """
        return self.password_hash == self._hash_password(password)
    
    def update(self, **kwargs) -> None:
        """
        Actualiza los atributos del usuario.
        
        Args:
            **kwargs: Atributos a actualizar
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ('id', 'created_at'):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Desactiva el usuario."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activa el usuario."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Convierte la entidad a diccionario.
        
        Returns:
            Diccionario con los datos del usuario (sin contraseña)
        """
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
