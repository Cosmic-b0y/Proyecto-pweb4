"""
Puerto de Repositorio de Órdenes de Trabajo (Interface)

Define el contrato que deben implementar los adaptadores
de persistencia de órdenes de trabajo.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.work_order import WorkOrder


class WorkOrderRepositoryPort(ABC):
    """Puerto (Interface) para el repositorio de órdenes de trabajo."""

    @abstractmethod
    async def get_by_id(self, work_order_id: str) -> Optional[WorkOrder]:
        """Obtiene una orden de trabajo por su ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[WorkOrder]:
        """Obtiene todas las órdenes de trabajo."""
        pass

    @abstractmethod
    async def get_by_machine_id(self, machine_id: str) -> List[WorkOrder]:
        """Obtiene las órdenes de trabajo de una máquina."""
        pass

    @abstractmethod
    async def save(self, work_order: WorkOrder) -> WorkOrder:
        """Guarda una orden de trabajo."""
        pass

    @abstractmethod
    async def delete(self, work_order_id: str) -> bool:
        """Elimina una orden de trabajo."""
        pass
