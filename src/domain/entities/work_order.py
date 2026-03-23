"""
Entidad de Orden de Trabajo (WorkOrder)

Define la entidad de dominio WorkOrder con sus reglas de negocio.
Una orden de trabajo se crea para una máquina y puede requerir un componente.
Almacenada en MySQL. Referencia lógica a machine_id (PostgreSQL).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class Priority(Enum):
    """Niveles de prioridad."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkOrderStatus(Enum):
    """Estados de una orden de trabajo."""
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class WorkOrder:
    """
    Entidad de dominio: Orden de Trabajo

    Representa una orden de trabajo asociada a una máquina y componente.
    """

    id: str
    machine_id: str  # FK lógica → machines (PostgreSQL)
    component_id: Optional[str]  # FK → components (MySQL)
    description: str
    priority: Priority
    status: WorkOrderStatus
    assigned_to: Optional[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        machine_id: str,
        description: str,
        priority: Priority,
        component_id: Optional[str] = None,
    ) -> "WorkOrder":
        """Factory method para crear una nueva orden de trabajo."""
        return cls(
            id=str(uuid.uuid4()),
            machine_id=machine_id,
            component_id=component_id,
            description=description.strip(),
            priority=priority,
            status=WorkOrderStatus.OPEN,
            assigned_to=None,
            created_at=datetime.utcnow(),
        )

    def assign(self, assigned_to: str) -> None:
        """Asigna la orden a un técnico."""
        if self.status in (WorkOrderStatus.COMPLETED, WorkOrderStatus.CANCELLED):
            raise ValueError("No se puede asignar una orden completada o cancelada")
        self.assigned_to = assigned_to.strip()
        self.status = WorkOrderStatus.ASSIGNED
        self.updated_at = datetime.utcnow()

    def start(self) -> None:
        """Inicia la ejecución de la orden."""
        if self.status != WorkOrderStatus.ASSIGNED:
            raise ValueError("Solo se pueden iniciar órdenes asignadas")
        self.status = WorkOrderStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Completa la orden de trabajo."""
        if self.status not in (WorkOrderStatus.ASSIGNED, WorkOrderStatus.IN_PROGRESS):
            raise ValueError("Solo se pueden completar órdenes asignadas o en progreso")
        self.status = WorkOrderStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancela la orden de trabajo."""
        if self.status == WorkOrderStatus.COMPLETED:
            raise ValueError("No se puede cancelar una orden completada")
        self.status = WorkOrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id": self.id,
            "machine_id": self.machine_id,
            "component_id": self.component_id,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
