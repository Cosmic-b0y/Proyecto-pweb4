"""
Adaptador de Repositorio de Mantenimientos en PostgreSQL.

Implementación del puerto MaintenanceRepositoryPort que almacena
los datos en PostgreSQL usando SQLAlchemy async.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.maintenance_repository import MaintenanceRepositoryPort
from src.domain.entities.maintenance import Maintenance, MaintenanceType, MaintenanceStatus
from src.infrastructure.models_pg import MaintenanceModel


class PgMaintenanceRepository(MaintenanceRepositoryPort):
    """Implementación PostgreSQL del repositorio de mantenimientos."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: MaintenanceModel) -> Maintenance:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return Maintenance(
            id=model.id,
            machine_id=model.machine_id,
            component_id=model.component_id,
            type=MaintenanceType(model.type),
            description=model.description,
            scheduled_date=model.scheduled_date,
            completed_date=model.completed_date,
            cost=model.cost,
            status=MaintenanceStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, maintenance_id: str) -> Optional[Maintenance]:
        """Obtiene un mantenimiento por su ID desde PostgreSQL."""
        result = await self._session.execute(
            select(MaintenanceModel).where(MaintenanceModel.id == maintenance_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[Maintenance]:
        """Obtiene todos los mantenimientos."""
        result = await self._session.execute(select(MaintenanceModel))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_machine_id(self, machine_id: str) -> List[Maintenance]:
        """Obtiene los mantenimientos de una máquina."""
        result = await self._session.execute(
            select(MaintenanceModel).where(MaintenanceModel.machine_id == machine_id)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, maintenance: Maintenance) -> Maintenance:
        """Guarda un mantenimiento en PostgreSQL."""
        result = await self._session.execute(
            select(MaintenanceModel).where(MaintenanceModel.id == maintenance.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.machine_id = maintenance.machine_id
            existing.component_id = maintenance.component_id
            existing.type = maintenance.type.value
            existing.description = maintenance.description
            existing.scheduled_date = maintenance.scheduled_date
            existing.completed_date = maintenance.completed_date
            existing.cost = maintenance.cost
            existing.status = maintenance.status.value
            existing.updated_at = maintenance.updated_at
        else:
            model = MaintenanceModel(
                id=maintenance.id,
                machine_id=maintenance.machine_id,
                component_id=maintenance.component_id,
                type=maintenance.type.value,
                description=maintenance.description,
                scheduled_date=maintenance.scheduled_date,
                completed_date=maintenance.completed_date,
                cost=maintenance.cost,
                status=maintenance.status.value,
                created_at=maintenance.created_at,
                updated_at=maintenance.updated_at,
            )
            self._session.add(model)

        await self._session.flush()
        return maintenance

    async def delete(self, maintenance_id: str) -> bool:
        """Elimina un mantenimiento de PostgreSQL."""
        result = await self._session.execute(
            select(MaintenanceModel).where(MaintenanceModel.id == maintenance_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
