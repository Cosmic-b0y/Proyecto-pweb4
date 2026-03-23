"""
Modelos SQLAlchemy para PostgreSQL.

Mapean las entidades del sistema mecánico a tablas en PostgreSQL.
"""

from datetime import datetime, date
from sqlalchemy import String, Float, Integer, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from src.infrastructure.database_pg import BasePg


class MachineModel(BasePg):
    """Modelo de máquina → tabla 'machines' (PostgreSQL)."""

    __tablename__ = "machines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relación con mantenimientos
    maintenances: Mapped[List["MaintenanceModel"]] = relationship(
        back_populates="machine", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MachineModel(id={self.id}, name={self.name})>"


class MaintenanceModel(BasePg):
    """Modelo de mantenimiento → tabla 'maintenances' (PostgreSQL)."""

    __tablename__ = "maintenances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    machine_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("machines.id"), nullable=False, index=True
    )
    component_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # FK lógica → MySQL
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relación con máquina
    machine: Mapped["MachineModel"] = relationship(back_populates="maintenances")

    def __repr__(self) -> str:
        return f"<MaintenanceModel(id={self.id}, machine_id={self.machine_id})>"
