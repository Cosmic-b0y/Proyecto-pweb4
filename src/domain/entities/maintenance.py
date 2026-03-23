"""
Entidad de Mantenimiento (Maintenance)

Define la entidad de dominio Maintenance con sus reglas de negocio.
Un mantenimiento se realiza sobre una máquina y puede involucrar un componente.
Almacenado en PostgreSQL. Referencia lógica a component_id (MySQL).
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from enum import Enum
import uuid


class MaintenanceType(Enum):
    """Tipos de mantenimiento."""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"


class MaintenanceStatus(Enum):
    """Estados de un mantenimiento."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Maintenance:
    """
    Entidad de dominio: Mantenimiento

    Representa un registro de mantenimiento de una máquina.
    """

    id: str
    machine_id: str  # FK → machines (PostgreSQL)
    component_id: Optional[str]  # FK lógica → components (MySQL)
    type: MaintenanceType
    description: str
    scheduled_date: date
    completed_date: Optional[date]
    cost: float
    status: MaintenanceStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        machine_id: str,
        type: MaintenanceType,
        description: str,
        scheduled_date: date,
        cost: float = 0.0,
        component_id: Optional[str] = None,
    ) -> "Maintenance":
        """Factory method para crear un nuevo mantenimiento."""
        return cls(
            id=str(uuid.uuid4()),
            machine_id=machine_id,
            component_id=component_id,
            type=type,
            description=description.strip(),
            scheduled_date=scheduled_date,
            completed_date=None,
            cost=cost,
            status=MaintenanceStatus.SCHEDULED,
            created_at=datetime.utcnow(),
        )

    def start(self) -> None:
        """Inicia el mantenimiento."""
        if self.status != MaintenanceStatus.SCHEDULED:
            raise ValueError("Solo se pueden iniciar mantenimientos programados")
        self.status = MaintenanceStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def complete(self, cost: Optional[float] = None) -> None:
        """Completa el mantenimiento."""
        if self.status not in (MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS):
            raise ValueError("Solo se pueden completar mantenimientos programados o en progreso")
        self.status = MaintenanceStatus.COMPLETED
        self.completed_date = date.today()
        if cost is not None:
            self.cost = cost
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancela el mantenimiento."""
        if self.status == MaintenanceStatus.COMPLETED:
            raise ValueError("No se puede cancelar un mantenimiento completado")
        self.status = MaintenanceStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id": self.id,
            "machine_id": self.machine_id,
            "component_id": self.component_id,
            "type": self.type.value,
            "description": self.description,
            "scheduled_date": self.scheduled_date.isoformat(),
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "cost": self.cost,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
