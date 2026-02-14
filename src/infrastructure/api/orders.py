"""
API de Pedidos (Orders)

Endpoints REST para la gestión de pedidos.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from src.application.services.order_service import OrderService
from src.application.services.user_service import UserService
from src.application.ports.order_repository import OrderRepositoryPort
from src.application.ports.user_repository import UserRepositoryPort
from src.infrastructure.adapters.memory_order_repository import MemoryOrderRepository
from src.infrastructure.adapters.memory_user_repository import MemoryUserRepository


# ============== Schemas ==============

class OrderStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderItemRequest(BaseModel):
    """Schema para un item del pedido."""
    product_id: str
    product_name: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "PROD-001",
                "product_name": "Laptop HP",
                "quantity": 1,
                "unit_price": 15000.00
            }
        }


class OrderCreateRequest(BaseModel):
    """Schema para crear un pedido."""
    user_id: str
    items: List[OrderItemRequest]
    shipping_address: str
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "uuid-del-usuario",
                "items": [
                    {
                        "product_id": "PROD-001",
                        "product_name": "Laptop HP",
                        "quantity": 1,
                        "unit_price": 15000.00
                    }
                ],
                "shipping_address": "Calle Principal #123, Ciudad",
                "notes": "Entregar en horario de oficina"
            }
        }



class OrderUpdateRequest(BaseModel):
    """Schema para actualizar un pedido."""
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "shipping_address": "Nueva Calle #456, Ciudad",
                "notes": "Actualización de dirección"
            }
        }


class OrderItemResponse(BaseModel):
    """Schema de respuesta para item."""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    """Schema de respuesta de pedido."""
    id: str
    user_id: str
    items: List[OrderItemResponse]
    status: str
    total: float
    shipping_address: str
    notes: Optional[str]
    created_at: str
    updated_at: Optional[str]


class OrderListResponse(BaseModel):
    """Respuesta de lista de pedidos."""
    orders: List[OrderResponse]
    total: int


# ============== Dependencias ==============

# Repositorios singleton
_order_repository: Optional[MemoryOrderRepository] = None
_user_repository: Optional[MemoryUserRepository] = None


def get_order_repository() -> OrderRepositoryPort:
    global _order_repository
    if _order_repository is None:
        _order_repository = MemoryOrderRepository()
    return _order_repository


def get_user_repository() -> UserRepositoryPort:
    global _user_repository
    if _user_repository is None:
        _user_repository = MemoryUserRepository()
    return _user_repository


def get_order_service(
    order_repo: OrderRepositoryPort = Depends(get_order_repository),
    user_repo: UserRepositoryPort = Depends(get_user_repository)
) -> OrderService:
    return OrderService(order_repo, user_repo)


def get_user_service(
    user_repo: UserRepositoryPort = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repo)


# ============== Router ==============

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Pedido no encontrado"}}
)


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    status: Optional[OrderStatusEnum] = Query(None, description="Filtrar por estado"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    service: OrderService = Depends(get_order_service)
):
    """Lista todos los pedidos con filtros opcionales."""
    if user_id:
        orders = await service.get_user_orders(user_id)
    elif status:
        orders = await service.get_orders_by_status(status.value)
    else:
        orders = await service.get_all_orders()
    
    return OrderListResponse(
        orders=[OrderResponse(**o.to_dict()) for o in orders],
        total=len(orders)
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Obtiene un pedido por su ID."""
    order = await service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido '{order_id}' no encontrado"
        )
    return OrderResponse(**order.to_dict())


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: OrderCreateRequest,
    service: OrderService = Depends(get_order_service)
):
    """Crea un nuevo pedido."""
    try:
        items = [item.model_dump() for item in request.items]
        order = await service.create_order(
            user_id=request.user_id,
            items=items,
            shipping_address=request.shipping_address,
            notes=request.notes
        )
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    request: OrderUpdateRequest,
    service: OrderService = Depends(get_order_service)
):
    """Actualiza un pedido existente (solo si está pendiente)."""
    try:
        order = await service.update_order(
            order_id=order_id,
            shipping_address=request.shipping_address,
            notes=request.notes
        )
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido '{order_id}' no encontrado"
            )
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Confirma un pedido pendiente."""
    try:
        order = await service.confirm_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/process", response_model=OrderResponse)
async def process_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Marca un pedido como en proceso."""
    try:
        order = await service.process_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/ship", response_model=OrderResponse)
async def ship_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Marca un pedido como enviado."""
    try:
        order = await service.ship_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/deliver", response_model=OrderResponse)
async def deliver_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Marca un pedido como entregado."""
    try:
        order = await service.deliver_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Cancela un pedido."""
    try:
        order = await service.cancel_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Elimina un pedido."""
    deleted = await service.delete_order(order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
