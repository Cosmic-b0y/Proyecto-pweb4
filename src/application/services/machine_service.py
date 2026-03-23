"""
Servicio de Máquinas - Casos de Uso

Implementa los casos de uso relacionados con la gestión de máquinas.
"""

from typing import Optional, List
from datetime import date
from src.application.ports.machine_repository import MachineRepositoryPort
from src.domain.entities.machine import Machine


class MachineService:
    """Servicio de aplicación para operaciones de máquinas."""

    def __init__(self, machine_repository: MachineRepositoryPort):
        self._machine_repository = machine_repository

    async def create_machine(
        self,
        name: str,
        model: str,
        serial_number: str,
        location: str,
        purchase_date: Optional[date] = None,
    ) -> Machine:
        """Caso de uso: Crear una nueva máquina."""
        machine = Machine.create(
            name=name,
            model=model,
            serial_number=serial_number,
            location=location,
            purchase_date=purchase_date,
        )
        return await self._machine_repository.save(machine)

    async def get_machine_by_id(self, machine_id: str) -> Optional[Machine]:
        """Caso de uso: Obtener máquina por ID."""
        return await self._machine_repository.get_by_id(machine_id)

    async def get_all_machines(self) -> List[Machine]:
        """Caso de uso: Listar todas las máquinas."""
        return await self._machine_repository.get_all()

    async def update_machine(
        self,
        machine_id: str,
        name: Optional[str] = None,
        model: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Machine]:
        """Caso de uso: Actualizar máquina."""
        machine = await self._machine_repository.get_by_id(machine_id)
        if not machine:
            return None
        updates = {k: v for k, v in {
            "name": name, "model": model, "location": location
        }.items() if v is not None}
        if status:
            from src.domain.entities.machine import MachineStatus
            updates["status"] = MachineStatus(status)
        if updates:
            machine.update(**updates)
        return await self._machine_repository.save(machine)

    async def delete_machine(self, machine_id: str) -> bool:
        """Caso de uso: Eliminar máquina."""
        return await self._machine_repository.delete(machine_id)
