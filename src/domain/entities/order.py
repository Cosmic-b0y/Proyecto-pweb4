"""
Entidad de Pedido (Order)

Define la entidad de dominio Order con sus reglas de negocio.
Un pedido pertenece a un usuario y contiene items.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum
import uuid


class OrderStatus(Enum):
    """Estados posibles de un pedido."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    """Item dentro de un pedido."""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    
    @property
    def subtotal(self) -> float:
        """Calcula el subtotal del item."""
        return self.quantity * self.unit_price


@dataclass
class Order:
    """
    Entidad de dominio: Pedido
    
    Representa un pedido del sistema con sus items y estados.
    """
    
    id: str
    user_id: str
    items: List[OrderItem]
    status: OrderStatus
    total: float
    shipping_address: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    @classmethod
    def create(
        cls, 
        user_id: str, 
        items: List[OrderItem], 
        shipping_address: str,
        notes: Optional[str] = None
    ) -> "Order":
        """
        Factory method para crear un nuevo pedido.
        
        Args:
            user_id: ID del usuario que realiza el pedido
            items: Lista de items del pedido
            shipping_address: Dirección de envío
            notes: Notas adicionales
            
        Returns:
            Nueva instancia de Order
        """
        total = sum(item.subtotal for item in items)
        
        return cls(
            id=str(uuid.uuid4()),
            user_id=user_id,
            items=items,
            status=OrderStatus.PENDING,
            total=total,
            shipping_address=shipping_address,
            notes=notes,
            created_at=datetime.utcnow()
        )
    
    def confirm(self) -> None:
        """Confirma el pedido."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Solo se pueden confirmar pedidos pendientes")
        self.status = OrderStatus.CONFIRMED
        self.updated_at = datetime.utcnow()
    
    def process(self) -> None:
        """Marca el pedido como en proceso."""
        if self.status != OrderStatus.CONFIRMED:
            raise ValueError("Solo se pueden procesar pedidos confirmados")
        self.status = OrderStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def ship(self) -> None:
        """Marca el pedido como enviado."""
        if self.status != OrderStatus.PROCESSING:
            raise ValueError("Solo se pueden enviar pedidos en proceso")
        self.status = OrderStatus.SHIPPED
        self.updated_at = datetime.utcnow()
    
    def deliver(self) -> None:
        """Marca el pedido como entregado."""
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Solo se pueden entregar pedidos enviados")
        self.status = OrderStatus.DELIVERED
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancela el pedido."""
        if self.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError("No se pueden cancelar pedidos enviados o entregados")
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def add_item(self, item: OrderItem) -> None:
        """Añade un item al pedido."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Solo se pueden modificar pedidos pendientes")
        self.items.append(item)
        self.total = sum(i.subtotal for i in self.items)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal
                }
                for item in self.items
            ],
            "status": self.status.value,
            "total": self.total,
            "shipping_address": self.shipping_address,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
