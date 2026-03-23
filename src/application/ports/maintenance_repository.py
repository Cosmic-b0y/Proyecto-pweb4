"""
Puerto de Repositorio de Mantenimientos (Interface)

Define el contrato que deben implementar los adaptadores
de persistencia de mantenimientos.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.maintenance import Maintenance


class MaintenanceRepositoryPort(ABC):
    """Puerto (Interface) para el repositorio de mantenimientos."""

    @abstractmethod
    async def get_by_id(self, maintenance_id: str) -> Optional[Maintenance]:
        """Obtiene un mantenimiento por su ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Maintenance]:
        """Obtiene todos los mantenimientos."""
        pass

    @abstractmethod
    async def get_by_machine_id(self, machine_id: str) -> List[Maintenance]:
        """Obtiene los mantenimientos de una máquina."""
        pass

    @abstractmethod
    async def save(self, maintenance: Maintenance) -> Maintenance:
        """Guarda un mantenimiento."""
        pass

    @abstractmethod
    async def delete(self, maintenance_id: str) -> bool:
        """Elimina un mantenimiento."""
        pass
