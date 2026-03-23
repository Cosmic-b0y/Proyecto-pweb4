"""
Modelos SQLAlchemy para MySQL.

Mapean las entidades del dominio a tablas en la base de datos MySQL.
"""

from datetime import datetime
from sqlalchemy import String, Boolean, Float, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from src.infrastructure.database import Base


class UserModel(Base):
    """Modelo de usuario → tabla 'users'."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relación con pedidos
    orders: Mapped[List["OrderModel"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email})>"


class OrderModel(Base):
    """Modelo de pedido → tabla 'orders'."""

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relaciones
    user: Mapped["UserModel"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItemModel"]] = relationship(back_populates="order", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<OrderModel(id={self.id}, status={self.status})>"


class OrderItemModel(Base):
    """Modelo de item de pedido → tabla 'order_items'."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    # Relación
    order: Mapped["OrderModel"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return f"<OrderItemModel(order_id={self.order_id}, product={self.product_name})>"


class ComponentModel(Base):
    """Modelo de componente → tabla 'components' (MySQL)."""

    __tablename__ = "components"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    part_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    machine_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # FK lógica → PG
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    supplier: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relación con órdenes de trabajo
    work_orders: Mapped[List["WorkOrderModel"]] = relationship(
        back_populates="component", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ComponentModel(id={self.id}, name={self.name})>"


class WorkOrderModel(Base):
    """Modelo de orden de trabajo → tabla 'work_orders' (MySQL)."""

    __tablename__ = "work_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    machine_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # FK lógica → PG
    component_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("components.id"), nullable=True, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relación con componente
    component: Mapped[Optional["ComponentModel"]] = relationship(back_populates="work_orders")

    def __repr__(self) -> str:
        return f"<WorkOrderModel(id={self.id}, machine_id={self.machine_id})>"

