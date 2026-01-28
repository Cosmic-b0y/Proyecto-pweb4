"""
Adaptador de Repositorio de Pedidos en Memoria

Implementación del puerto OrderRepositoryPort que almacena
los datos en memoria.
"""

from typing import Optional, List, Dict
from src.application.ports.order_repository import OrderRepositoryPort
from src.domain.entities.order import Order, OrderStatus


class MemoryOrderRepository(OrderRepositoryPort):
    """Implementación en memoria del repositorio de pedidos."""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)
    
    async def get_by_user_id(self, user_id: str) -> List[Order]:
        return [
            order for order in self._orders.values() 
            if order.user_id == user_id
        ]
    
    async def get_by_status(self, status: OrderStatus) -> List[Order]:
        return [
            order for order in self._orders.values() 
            if order.status == status
        ]
    
    async def get_all(self) -> List[Order]:
        return list(self._orders.values())
    
    async def save(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order
    
    async def delete(self, order_id: str) -> bool:
        if order_id in self._orders:
            del self._orders[order_id]
            return True
        return False
    
    def clear(self) -> None:
        self._orders.clear()
    
    @property
    def count(self) -> int:
        return len(self._orders)
