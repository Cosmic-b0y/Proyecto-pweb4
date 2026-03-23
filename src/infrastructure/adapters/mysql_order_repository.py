"""
Adaptador de Repositorio de Pedidos en MySQL.

Implementación del puerto OrderRepositoryPort que almacena
los datos en MySQL usando SQLAlchemy async.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.application.ports.order_repository import OrderRepositoryPort
from src.domain.entities.order import Order, OrderItem, OrderStatus
from src.infrastructure.models import OrderModel, OrderItemModel


class MySQLOrderRepository(OrderRepositoryPort):
    """
    Implementación MySQL del repositorio de pedidos.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: OrderModel) -> Order:
        """Convierte un modelo SQLAlchemy a entidad de dominio."""
        items = [
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in model.items
        ]
        return Order(
            id=model.id,
            user_id=model.user_id,
            items=items,
            status=OrderStatus(model.status),
            total=model.total,
            shipping_address=model.shipping_address,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Obtiene un pedido por su ID desde MySQL."""
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: str) -> List[Order]:
        """Obtiene todos los pedidos de un usuario."""
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Obtiene pedidos por estado."""
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.status == status.value)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_all(self) -> List[Order]:
        """Obtiene todos los pedidos."""
        result = await self._session.execute(
            select(OrderModel).options(selectinload(OrderModel.items))
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, order: Order) -> Order:
        """Guarda un pedido en MySQL."""
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.id == order.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.status = order.status.value
            existing.total = order.total
            existing.shipping_address = order.shipping_address
            existing.notes = order.notes
            existing.updated_at = order.updated_at
        else:
            model = OrderModel(
                id=order.id,
                user_id=order.user_id,
                status=order.status.value,
                total=order.total,
                shipping_address=order.shipping_address,
                notes=order.notes,
                created_at=order.created_at,
                updated_at=order.updated_at,
            )
            for item in order.items:
                model.items.append(
                    OrderItemModel(
                        product_id=item.product_id,
                        product_name=item.product_name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                    )
                )
            self._session.add(model)

        await self._session.flush()
        return order

    async def delete(self, order_id: str) -> bool:
        """Elimina un pedido de MySQL."""
        result = await self._session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False
