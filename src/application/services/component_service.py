"""
Servicio de Componentes - Casos de Uso

Implementa los casos de uso relacionados con la gestión de componentes.
Valida la existencia de la máquina (PostgreSQL) a nivel de servicio.
"""

from typing import Optional, List
from src.application.ports.component_repository import ComponentRepositoryPort
from src.application.ports.machine_repository import MachineRepositoryPort
from src.domain.entities.component import Component


class ComponentService:
    """Servicio de aplicación para operaciones de componentes."""

    def __init__(
        self,
        component_repository: ComponentRepositoryPort,
        machine_repository: MachineRepositoryPort,
    ):
        self._component_repository = component_repository
        self._machine_repository = machine_repository

    async def create_component(
        self,
        name: str,
        part_number: str,
        machine_id: str,
        category: str,
        stock: int,
        unit_cost: float,
        supplier: str,
    ) -> Component:
        """Caso de uso: Crear un nuevo componente."""
        # Validar FK lógica: la máquina debe existir en PostgreSQL
        machine = await self._machine_repository.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Máquina con id '{machine_id}' no encontrada (PostgreSQL)")

        component = Component.create(
            name=name,
            part_number=part_number,
            machine_id=machine_id,
            category=category,
            stock=stock,
            unit_cost=unit_cost,
            supplier=supplier,
        )
        return await self._component_repository.save(component)

    async def get_component_by_id(self, component_id: str) -> Optional[Component]:
        """Caso de uso: Obtener componente por ID."""
        return await self._component_repository.get_by_id(component_id)

    async def get_all_components(self) -> List[Component]:
        """Caso de uso: Listar todos los componentes."""
        return await self._component_repository.get_all()

    async def get_components_by_machine(self, machine_id: str) -> List[Component]:
        """Caso de uso: Listar componentes de una máquina."""
        return await self._component_repository.get_by_machine_id(machine_id)

    async def update_component(
        self,
        component_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        stock: Optional[int] = None,
        unit_cost: Optional[float] = None,
        supplier: Optional[str] = None,
    ) -> Optional[Component]:
        """Caso de uso: Actualizar componente."""
        component = await self._component_repository.get_by_id(component_id)
        if not component:
            return None
        updates = {k: v for k, v in {
            "name": name, "category": category,
            "stock": stock, "unit_cost": unit_cost, "supplier": supplier
        }.items() if v is not None}
        if updates:
            component.update(**updates)
        return await self._component_repository.save(component)

    async def delete_component(self, component_id: str) -> bool:
        """Caso de uso: Eliminar componente."""
        return await self._component_repository.delete(component_id)
