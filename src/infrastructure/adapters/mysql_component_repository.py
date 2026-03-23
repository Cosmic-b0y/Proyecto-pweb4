"""
Adaptador de Repositorio de Componentes en MySQL.

Implementación del puerto ComponentRepositoryPort que almacena
los datos en MySQL usando SQLAlchemy async.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.component_repository import ComponentRepositoryPort
from src.domain.entities.component import Component
from src.infrastructure.models import ComponentModel


class MySQLComponentRepository(ComponentRepositoryPort):
    """Implementación MySQL del repositorio de componentes."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: ComponentModel) -> Component:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        return Component(
            id=model.id,
            name=model.name,
            part_number=model.part_number,
            machine_id=model.machine_id,
            category=model.category,
            stock=model.stock,
            unit_cost=model.unit_cost,
            supplier=model.supplier,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, component_id: str) -> Optional[Component]:
        """Obtiene un componente por su ID desde MySQL."""
        result = await self._session.execute(
            select(ComponentModel).where(ComponentModel.id == component_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> List[Component]:
        """Obtiene todos los componentes."""
        result = await self._session.execute(select(ComponentModel))
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_machine_id(self, machine_id: str) -> List[Component]:
        """Obtiene los componentes de una máquina."""
        result = await self._session.execute(
            select(ComponentModel).where(ComponentModel.machine_id == machine_id)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, component: Component) -> Component:
        """Guarda un componente en MySQL."""
        result = await self._session.execute(
            select(ComponentModel).where(ComponentModel.id == component.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.name = component.name
            existing.part_number = component.part_number
            existing.machine_id = component.machine_id
            existing.category = component.category
            existing.stock = component.stock
            existing.unit_cost = component.unit_cost
            existing.supplier = component.supplier
            existing.updated_at = component.updated_at
        else:
            model = ComponentModel(
                id=component.id,
                name=component.name,
                part_number=component.part_number,
                machine_id=component.machine_id,
                category=component.category,
                stock=component.stock,
                unit_cost=component.unit_cost,
                supplier=component.supplier,
                created_at=component.created_at,
                updated_at=component.updated_at,
            )
            self._session.add(model)

        await self._session.flush()
        return component

    async def delete(self, component_id: str) -> bool:
        """Elimina un componente de MySQL."""
        result = await self._session.execute(
            select(ComponentModel).where(ComponentModel.id == component_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
