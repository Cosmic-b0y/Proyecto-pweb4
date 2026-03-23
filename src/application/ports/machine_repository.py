"""
Puerto de Repositorio de Máquinas (Interface)

Define el contrato que deben implementar los adaptadores
de persistencia de máquinas.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.machine import Machine


class MachineRepositoryPort(ABC):
    """Puerto (Interface) para el repositorio de máquinas."""

    @abstractmethod
    async def get_by_id(self, machine_id: str) -> Optional[Machine]:
        """Obtiene una máquina por su ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Machine]:
        """Obtiene todas las máquinas."""
        pass

    @abstractmethod
    async def save(self, machine: Machine) -> Machine:
        """Guarda una máquina."""
        pass

    @abstractmethod
    async def delete(self, machine_id: str) -> bool:
        """Elimina una máquina."""
        pass
