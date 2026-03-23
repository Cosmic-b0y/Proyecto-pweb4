"""
Servicio de Órdenes de Trabajo - Casos de Uso

Implementa los casos de uso relacionados con la gestión de órdenes de trabajo.
Valida machine_id (PostgreSQL) y component_id (MySQL) a nivel de servicio.
"""

from typing import Optional, List
from src.application.ports.work_order_repository import WorkOrderRepositoryPort
from src.application.ports.machine_repository import MachineRepositoryPort
from src.application.ports.component_repository import ComponentRepositoryPort
from src.domain.entities.work_order import WorkOrder, Priority


class WorkOrderService:
    """Servicio de aplicación para operaciones de órdenes de trabajo."""

    def __init__(
        self,
        work_order_repository: WorkOrderRepositoryPort,
        machine_repository: MachineRepositoryPort,
        component_repository: ComponentRepositoryPort,
    ):
        self._work_order_repository = work_order_repository
        self._machine_repository = machine_repository
        self._component_repository = component_repository

    async def create_work_order(
        self,
        machine_id: str,
        description: str,
        priority: str,
        component_id: Optional[str] = None,
    ) -> WorkOrder:
        """Caso de uso: Crear una nueva orden de trabajo."""
        # Validar FK lógica: la máquina debe existir en PostgreSQL
        machine = await self._machine_repository.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Máquina con id '{machine_id}' no encontrada (PostgreSQL)")

        # Validar FK: el componente debe existir en MySQL (si se proporciona)
        if component_id:
            component = await self._component_repository.get_by_id(component_id)
            if not component:
                raise ValueError(f"Componente con id '{component_id}' no encontrado (MySQL)")

        work_order = WorkOrder.create(
            machine_id=machine_id,
            description=description,
            priority=Priority(priority),
            component_id=component_id,
        )
        return await self._work_order_repository.save(work_order)

    async def get_work_order_by_id(self, work_order_id: str) -> Optional[WorkOrder]:
        """Caso de uso: Obtener orden de trabajo por ID."""
        return await self._work_order_repository.get_by_id(work_order_id)

    async def get_all_work_orders(self) -> List[WorkOrder]:
        """Caso de uso: Listar todas las órdenes de trabajo."""
        return await self._work_order_repository.get_all()

    async def get_work_orders_by_machine(self, machine_id: str) -> List[WorkOrder]:
        """Caso de uso: Listar órdenes de trabajo de una máquina."""
        return await self._work_order_repository.get_by_machine_id(machine_id)

    async def assign_work_order(
        self, work_order_id: str, assigned_to: str
    ) -> Optional[WorkOrder]:
        """Caso de uso: Asignar orden a técnico."""
        work_order = await self._work_order_repository.get_by_id(work_order_id)
        if not work_order:
            return None
        work_order.assign(assigned_to)
        return await self._work_order_repository.save(work_order)

    async def complete_work_order(self, work_order_id: str) -> Optional[WorkOrder]:
        """Caso de uso: Completar orden de trabajo."""
        work_order = await self._work_order_repository.get_by_id(work_order_id)
        if not work_order:
            return None
        work_order.complete()
        return await self._work_order_repository.save(work_order)

    async def cancel_work_order(self, work_order_id: str) -> Optional[WorkOrder]:
        """Caso de uso: Cancelar orden de trabajo."""
        work_order = await self._work_order_repository.get_by_id(work_order_id)
        if not work_order:
            return None
        work_order.cancel()
        return await self._work_order_repository.save(work_order)

    async def delete_work_order(self, work_order_id: str) -> bool:
        """Caso de uso: Eliminar orden de trabajo."""
        return await self._work_order_repository.delete(work_order_id)
