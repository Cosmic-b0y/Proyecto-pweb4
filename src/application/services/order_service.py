"""
Servicio de Pedidos - Casos de Uso

Implementa los casos de uso relacionados con la gestión de pedidos.
"""

from typing import Optional, List
from src.application.ports.order_repository import OrderRepositoryPort
from src.application.ports.user_repository import UserRepositoryPort
from src.domain.entities.order import Order, OrderItem, OrderStatus


class OrderService:
    """Servicio de aplicación para operaciones de pedidos."""
    
    def __init__(
        self, 
        order_repository: OrderRepositoryPort,
        user_repository: UserRepositoryPort
    ):
        self._order_repository = order_repository
        self._user_repository = user_repository
    
    async def create_order(
        self,
        user_id: str,
        items: List[dict],
        shipping_address: str,
        notes: Optional[str] = None
    ) -> Order:
        """
        Caso de uso: Crear un nuevo pedido.
        
        Args:
            user_id: ID del usuario
            items: Lista de items [{product_id, product_name, quantity, unit_price}]
            shipping_address: Dirección de envío
            notes: Notas opcionales
        """
        # Verificar que el usuario existe
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con id '{user_id}' no encontrado")
        
        # Crear items del pedido
        order_items = [
            OrderItem(
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )
            for item in items
        ]
        
        # Crear pedido
        order = Order.create(
            user_id=user_id,
            items=order_items,
            shipping_address=shipping_address,
            notes=notes
        )
        
        return await self._order_repository.save(order)
    
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Caso de uso: Obtener pedido por ID."""
        return await self._order_repository.get_by_id(order_id)
    
    async def get_user_orders(self, user_id: str) -> List[Order]:
        """Caso de uso: Obtener pedidos de un usuario."""
        return await self._order_repository.get_by_user_id(user_id)
    
    async def get_all_orders(self) -> List[Order]:
        """Caso de uso: Listar todos los pedidos."""
        return await self._order_repository.get_all()
    
    async def get_orders_by_status(self, status: str) -> List[Order]:
        """Caso de uso: Obtener pedidos por estado."""
        order_status = OrderStatus(status)
        return await self._order_repository.get_by_status(order_status)
    
    async def confirm_order(self, order_id: str) -> Optional[Order]:
        """Caso de uso: Confirmar pedido."""
        order = await self._order_repository.get_by_id(order_id)
        if not order:
            return None
        order.confirm()
        return await self._order_repository.save(order)
    
    async def process_order(self, order_id: str) -> Optional[Order]:
        """Caso de uso: Procesar pedido."""
        order = await self._order_repository.get_by_id(order_id)
        if not order:
            return None
        order.process()
        return await self._order_repository.save(order)
    
    async def ship_order(self, order_id: str) -> Optional[Order]:
        """Caso de uso: Enviar pedido."""
        order = await self._order_repository.get_by_id(order_id)
        if not order:
            return None
        order.ship()
        return await self._order_repository.save(order)
    
    async def deliver_order(self, order_id: str) -> Optional[Order]:
        """Caso de uso: Marcar pedido como entregado."""
        order = await self._order_repository.get_by_id(order_id)
        if not order:
            return None
        order.deliver()
        return await self._order_repository.save(order)
    
    async def cancel_order(self, order_id: str) -> Optional[Order]:
        """Caso de uso: Cancelar pedido."""
        order = await self._order_repository.get_by_id(order_id)
        if not order:
            return None
        order.cancel()
        return await self._order_repository.save(order)
    
    async def update_order(
        self,
        order_id: str,
        shipping_address: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Order]:
        """Caso de uso: Actualizar pedido."""
        order = await self._order_repository.get_by_id(order_id)
        if not order:
            return None
        order.update(shipping_address=shipping_address, notes=notes)
        return await self._order_repository.save(order)
    
    async def delete_order(self, order_id: str) -> bool:
        """Caso de uso: Eliminar pedido."""
        return await self._order_repository.delete(order_id)
