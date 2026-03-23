"""
Adaptador de Repositorio de Máquinas en PostgreSQL.

Implementación del puerto MachineRepositoryPort que almacena
los datos en PostgreSQL usando SQLAlchemy async.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.machine_repository import MachineRepositoryPort
from src.domain.entities.machine import Machine, MachineStatus
from src.infrastructure.models_pg import MachineModel


class PgMachineRepository(MachineRepositoryPort):
    """Implementación PostgreSQL del repositorio de máquinas."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: MachineModel) -> Machine:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return Machine(
            id=model.id,
            name=model.name,
            model=model.model,
            serial_number=model.serial_number,
            location=model.location,
            status=MachineStatus(model.status),
            purchase_date=model.purchase_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, machine_id: str) -> Optional[Machine]:
        """Obtiene una máquina por su ID desde PostgreSQL."""
        result = await self._session.execute(
            select(MachineModel).where(MachineModel.id == machine_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[Machine]:
        """Obtiene todas las máquinas."""
        result = await self._session.execute(select(MachineModel))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, machine: Machine) -> Machine:
        """Guarda una máquina en PostgreSQL."""
        result = await self._session.execute(
            select(MachineModel).where(MachineModel.id == machine.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.name = machine.name
            existing.model = machine.model
            existing.serial_number = machine.serial_number
            existing.location = machine.location
            existing.status = machine.status.value
            existing.purchase_date = machine.purchase_date
            existing.updated_at = machine.updated_at
        else:
            model = MachineModel(
                id=machine.id,
                name=machine.name,
                model=machine.model,
                serial_number=machine.serial_number,
                location=machine.location,
                status=machine.status.value,
                purchase_date=machine.purchase_date,
                created_at=machine.created_at,
                updated_at=machine.updated_at,
            )
            self._session.add(model)

        await self._session.flush()
        return machine

    async def delete(self, machine_id: str) -> bool:
        """Elimina una máquina de PostgreSQL."""
        result = await self._session.execute(
            select(MachineModel).where(MachineModel.id == machine_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
