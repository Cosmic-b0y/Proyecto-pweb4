"""
Puerto de Repositorio de Componentes (Interface)

Define el contrato que deben implementar los adaptadores
de persistencia de componentes.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.component import Component


class ComponentRepositoryPort(ABC):
    """Puerto (Interface) para el repositorio de componentes."""

    @abstractmethod
    async def get_by_id(self, component_id: str) -> Optional[Component]:
        """Obtiene un componente por su ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Component]:
        """Obtiene todos los componentes."""
        pass

    @abstractmethod
    async def get_by_machine_id(self, machine_id: str) -> List[Component]:
        """Obtiene los componentes de una máquina."""
        pass

    @abstractmethod
    async def save(self, component: Component) -> Component:
        """Guarda un componente."""
        pass

    @abstractmethod
    async def delete(self, component_id: str) -> bool:
        """Elimina un componente."""
        pass
