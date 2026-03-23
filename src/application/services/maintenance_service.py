"""
Servicio de Mantenimientos - Casos de Uso

Implementa los casos de uso relacionados con la gestión de mantenimientos.
Valida machine_id (PostgreSQL) y component_id (MySQL) a nivel de servicio.
"""

from typing import Optional, List
from datetime import date
from src.application.ports.maintenance_repository import MaintenanceRepositoryPort
from src.application.ports.machine_repository import MachineRepositoryPort
from src.application.ports.component_repository import ComponentRepositoryPort
from src.domain.entities.maintenance import Maintenance, MaintenanceType


class MaintenanceService:
    """Servicio de aplicación para operaciones de mantenimientos."""

    def __init__(
        self,
        maintenance_repository: MaintenanceRepositoryPort,
        machine_repository: MachineRepositoryPort,
        component_repository: ComponentRepositoryPort,
    ):
        self._maintenance_repository = maintenance_repository
        self._machine_repository = machine_repository
        self._component_repository = component_repository

    async def create_maintenance(
        self,
        machine_id: str,
        type: str,
        description: str,
        scheduled_date: date,
        cost: float = 0.0,
        component_id: Optional[str] = None,
    ) -> Maintenance:
        """Caso de uso: Crear un nuevo mantenimiento."""
        # Validar FK: la máquina debe existir en PostgreSQL
        machine = await self._machine_repository.get_by_id(machine_id)
        if not machine:
            raise ValueError(f"Máquina con id '{machine_id}' no encontrada")

        # Validar FK lógica: el componente debe existir en MySQL (si se proporciona)
        if component_id:
            component = await self._component_repository.get_by_id(component_id)
            if not component:
                raise ValueError(f"Componente con id '{component_id}' no encontrado (MySQL)")

        maintenance = Maintenance.create(
            machine_id=machine_id,
            type=MaintenanceType(type),
            description=description,
            scheduled_date=scheduled_date,
            cost=cost,
            component_id=component_id,
        )
        return await self._maintenance_repository.save(maintenance)

    async def get_maintenance_by_id(self, maintenance_id: str) -> Optional[Maintenance]:
        """Caso de uso: Obtener mantenimiento por ID."""
        return await self._maintenance_repository.get_by_id(maintenance_id)

    async def get_all_maintenances(self) -> List[Maintenance]:
        """Caso de uso: Listar todos los mantenimientos."""
        return await self._maintenance_repository.get_all()

    async def get_maintenances_by_machine(self, machine_id: str) -> List[Maintenance]:
        """Caso de uso: Listar mantenimientos de una máquina."""
        return await self._maintenance_repository.get_by_machine_id(machine_id)

    async def complete_maintenance(
        self, maintenance_id: str, cost: Optional[float] = None
    ) -> Optional[Maintenance]:
        """Caso de uso: Completar un mantenimiento."""
        maintenance = await self._maintenance_repository.get_by_id(maintenance_id)
        if not maintenance:
            return None
        maintenance.complete(cost=cost)
        return await self._maintenance_repository.save(maintenance)

    async def cancel_maintenance(self, maintenance_id: str) -> Optional[Maintenance]:
        """Caso de uso: Cancelar un mantenimiento."""
        maintenance = await self._maintenance_repository.get_by_id(maintenance_id)
        if not maintenance:
            return None
        maintenance.cancel()
        return await self._maintenance_repository.save(maintenance)

    async def delete_maintenance(self, maintenance_id: str) -> bool:
        """Caso de uso: Eliminar mantenimiento."""
        return await self._maintenance_repository.delete(maintenance_id)
