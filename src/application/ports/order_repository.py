"""
Puerto de Repositorio de Pedidos (Interface)

Define el contrato que deben implementar los adaptadores
de persistencia de pedidos.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.order import Order, OrderStatus


class OrderRepositoryPort(ABC):
    """
    Puerto (Interface) para el repositorio de pedidos.
    """
    
    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Obtiene un pedido por su ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Order]:
        """Obtiene todos los pedidos de un usuario."""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Obtiene pedidos por estado."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Order]:
        """Obtiene todos los pedidos."""
        pass
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        """Guarda un pedido."""
        pass
    
    @abstractmethod
    async def delete(self, order_id: str) -> bool:
        """Elimina un pedido."""
        pass
