"""
Adaptador de Repositorio de Órdenes de Trabajo en MySQL.

Implementación del puerto WorkOrderRepositoryPort que almacena
los datos en MySQL usando SQLAlchemy async.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.work_order_repository import WorkOrderRepositoryPort
from src.domain.entities.work_order import WorkOrder, Priority, WorkOrderStatus
from src.infrastructure.models import WorkOrderModel


class MySQLWorkOrderRepository(WorkOrderRepositoryPort):
    """Implementación MySQL del repositorio de órdenes de trabajo."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: WorkOrderModel) -> WorkOrder:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return WorkOrder(
            id=model.id,
            machine_id=model.machine_id,
            component_id=model.component_id,
            description=model.description,
            priority=Priority(model.priority),
            status=WorkOrderStatus(model.status),
            assigned_to=model.assigned_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
        )

    async def get_by_id(self, work_order_id: str) -> Optional[WorkOrder]:
        """Obtiene una orden de trabajo por su ID desde MySQL."""
        result = await self._session.execute(
            select(WorkOrderModel).where(WorkOrderModel.id == work_order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[WorkOrder]:
        """Obtiene todas las órdenes de trabajo."""
        result = await self._session.execute(select(WorkOrderModel))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_machine_id(self, machine_id: str) -> List[WorkOrder]:
        """Obtiene las órdenes de trabajo de una máquina."""
        result = await self._session.execute(
            select(WorkOrderModel).where(WorkOrderModel.machine_id == machine_id)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, work_order: WorkOrder) -> WorkOrder:
        """Guarda una orden de trabajo en MySQL."""
        result = await self._session.execute(
            select(WorkOrderModel).where(WorkOrderModel.id == work_order.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.machine_id = work_order.machine_id
            existing.component_id = work_order.component_id
            existing.description = work_order.description
            existing.priority = work_order.priority.value
            existing.status = work_order.status.value
            existing.assigned_to = work_order.assigned_to
            existing.updated_at = work_order.updated_at
            existing.completed_at = work_order.completed_at
        else:
            model = WorkOrderModel(
                id=work_order.id,
                machine_id=work_order.machine_id,
                component_id=work_order.component_id,
                description=work_order.description,
                priority=work_order.priority.value,
                status=work_order.status.value,
                assigned_to=work_order.assigned_to,
                created_at=work_order.created_at,
                updated_at=work_order.updated_at,
                completed_at=work_order.completed_at,
            )
            self._session.add(model)

        await self._session.flush()
        return work_order

    async def delete(self, work_order_id: str) -> bool:
        """Elimina una orden de trabajo de MySQL."""
        result = await self._session.execute(
            select(WorkOrderModel).where(WorkOrderModel.id == work_order_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
