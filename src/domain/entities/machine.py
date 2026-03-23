"""
Entidad de Máquina (Machine)

Define la entidad de dominio Machine con sus reglas de negocio.
Una máquina es el equipo principal del sistema mecánico.
Almacenada en PostgreSQL.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from enum import Enum
import uuid


class MachineStatus(Enum):
    """Estados posibles de una máquina."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


@dataclass
class Machine:
    """
    Entidad de dominio: Máquina

    Representa una máquina/equipo del sistema mecánico.
    """

    id: str
    name: str
    model: str
    serial_number: str
    location: str
    status: MachineStatus
    purchase_date: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        name: str,
        model: str,
        serial_number: str,
        location: str,
        purchase_date: Optional[date] = None,
    ) -> "Machine":
        """Factory method para crear una nueva máquina."""
        return cls(
            id=str(uuid.uuid4()),
            name=name.strip(),
            model=model.strip(),
            serial_number=serial_number.strip(),
            location=location.strip(),
            status=MachineStatus.ACTIVE,
            purchase_date=purchase_date,
            created_at=datetime.utcnow(),
        )

    def update(self, **kwargs) -> None:
        """Actualiza atributos de la máquina."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ("id", "created_at"):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def set_maintenance(self) -> None:
        """Marca la máquina como en mantenimiento."""
        self.status = MachineStatus.MAINTENANCE
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activa la máquina."""
        self.status = MachineStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def decommission(self) -> None:
        """Da de baja la máquina."""
        self.status = MachineStatus.DECOMMISSIONED
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "serial_number": self.serial_number,
            "location": self.location,
            "status": self.status.value,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
