"""
Entidad de Componente (Component)

Define la entidad de dominio Component con sus reglas de negocio.
Un componente es una pieza que pertenece a una máquina.
Almacenado en MySQL. Referencia lógica a machine_id (PostgreSQL).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Component:
    """
    Entidad de dominio: Componente/Pieza

    Representa un componente mecánico asociado a una máquina.
    """

    id: str
    name: str
    part_number: str
    machine_id: str  # FK lógica → machines (PostgreSQL)
    category: str
    stock: int
    unit_cost: float
    supplier: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        name: str,
        part_number: str,
        machine_id: str,
        category: str,
        stock: int,
        unit_cost: float,
        supplier: str,
    ) -> "Component":
        """Factory method para crear un nuevo componente."""
        return cls(
            id=str(uuid.uuid4()),
            name=name.strip(),
            part_number=part_number.strip(),
            machine_id=machine_id,
            category=category.strip(),
            stock=stock,
            unit_cost=unit_cost,
            supplier=supplier.strip(),
            created_at=datetime.utcnow(),
        )

    def update(self, **kwargs) -> None:
        """Actualiza atributos del componente."""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ("id", "created_at"):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def adjust_stock(self, quantity: int) -> None:
        """Ajusta el stock del componente."""
        new_stock = self.stock + quantity
        if new_stock < 0:
            raise ValueError("El stock no puede ser negativo")
        self.stock = new_stock
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id": self.id,
            "name": self.name,
            "part_number": self.part_number,
            "machine_id": self.machine_id,
            "category": self.category,
            "stock": self.stock,
            "unit_cost": self.unit_cost,
            "supplier": self.supplier,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
