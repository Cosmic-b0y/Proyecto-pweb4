"""
API del Sistema Mecánico

Endpoints REST para la gestión del sistema mecánico.
Combina datos de PostgreSQL (máquinas, mantenimientos) y MySQL (componentes, órdenes de trabajo).
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_session
from src.infrastructure.database_pg import get_pg_session

# Repositorios
from src.infrastructure.adapters.pg_machine_repository import PgMachineRepository
from src.infrastructure.adapters.mysql_component_repository import MySQLComponentRepository
from src.infrastructure.adapters.pg_maintenance_repository import PgMaintenanceRepository
from src.infrastructure.adapters.mysql_work_order_repository import MySQLWorkOrderRepository

# Puertos
from src.application.ports.machine_repository import MachineRepositoryPort
from src.application.ports.component_repository import ComponentRepositoryPort
from src.application.ports.maintenance_repository import MaintenanceRepositoryPort
from src.application.ports.work_order_repository import WorkOrderRepositoryPort

# Servicios
from src.application.services.machine_service import MachineService
from src.application.services.component_service import ComponentService
from src.application.services.maintenance_service import MaintenanceService
from src.application.services.work_order_service import WorkOrderService


# ╔══════════════════════════════════════════════════════════════════╗
# ║                          SCHEMAS                                ║
# ╚══════════════════════════════════════════════════════════════════╝

# ── Máquinas ─────────────────────────────────────────────────────

class MachineStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    maintenance = "maintenance"
    decommissioned = "decommissioned"


class MachineCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    serial_number: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    purchase_date: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Torno CNC",
                "model": "Haas ST-10",
                "serial_number": "SN-2024-001",
                "location": "Nave A - Planta 1",
                "purchase_date": "2024-01-15"
            }
        }


class MachineUpdateRequest(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    status: Optional[MachineStatusEnum] = None


class MachineResponse(BaseModel):
    id: str
    name: str
    model: str
    serial_number: str
    location: str
    status: str
    purchase_date: Optional[str]
    created_at: str
    updated_at: Optional[str]


# ── Componentes ──────────────────────────────────────────────────

class ComponentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    part_number: str = Field(..., min_length=1)
    machine_id: str = Field(..., description="ID de la máquina (PostgreSQL)")
    category: str = Field(..., min_length=1)
    stock: int = Field(..., ge=0)
    unit_cost: float = Field(..., ge=0)
    supplier: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Rodamiento SKF 6205",
                "part_number": "SKF-6205-2RS",
                "machine_id": "uuid-de-la-maquina",
                "category": "Rodamientos",
                "stock": 25,
                "unit_cost": 12.50,
                "supplier": "SKF México"
            }
        }


class ComponentUpdateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    stock: Optional[int] = None
    unit_cost: Optional[float] = None
    supplier: Optional[str] = None


class ComponentResponse(BaseModel):
    id: str
    name: str
    part_number: str
    machine_id: str
    category: str
    stock: int
    unit_cost: float
    supplier: str
    created_at: str
    updated_at: Optional[str]


# ── Mantenimientos ───────────────────────────────────────────────

class MaintenanceTypeEnum(str, Enum):
    preventive = "preventive"
    corrective = "corrective"
    predictive = "predictive"


class MaintenanceStatusEnum(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class MaintenanceCreateRequest(BaseModel):
    machine_id: str = Field(..., description="ID de la máquina (PostgreSQL)")
    component_id: Optional[str] = Field(None, description="ID del componente (MySQL)")
    type: MaintenanceTypeEnum
    description: str = Field(..., min_length=1)
    scheduled_date: date
    cost: float = Field(0.0, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "machine_id": "uuid-de-la-maquina",
                "component_id": "uuid-del-componente",
                "type": "preventive",
                "description": "Cambio de aceite del sistema hidráulico",
                "scheduled_date": "2024-06-15",
                "cost": 250.00
            }
        }


class MaintenanceCompleteRequest(BaseModel):
    cost: Optional[float] = None


class MaintenanceResponse(BaseModel):
    id: str
    machine_id: str
    component_id: Optional[str]
    type: str
    description: str
    scheduled_date: str
    completed_date: Optional[str]
    cost: float
    status: str
    created_at: str
    updated_at: Optional[str]


# ── Órdenes de Trabajo ──────────────────────────────────────────

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class WorkOrderStatusEnum(str, Enum):
    open = "open"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class WorkOrderCreateRequest(BaseModel):
    machine_id: str = Field(..., description="ID de la máquina (PostgreSQL)")
    component_id: Optional[str] = Field(None, description="ID del componente (MySQL)")
    description: str = Field(..., min_length=1)
    priority: PriorityEnum

    class Config:
        json_schema_extra = {
            "example": {
                "machine_id": "uuid-de-la-maquina",
                "component_id": "uuid-del-componente",
                "description": "Reemplazo de cojinete dañado",
                "priority": "high"
            }
        }


class WorkOrderAssignRequest(BaseModel):
    assigned_to: str = Field(..., min_length=1)


class WorkOrderResponse(BaseModel):
    id: str
    machine_id: str
    component_id: Optional[str]
    description: str
    priority: str
    status: str
    assigned_to: Optional[str]
    created_at: str
    updated_at: Optional[str]
    completed_at: Optional[str]


# ╔══════════════════════════════════════════════════════════════════╗
# ║                       DEPENDENCIAS                              ║
# ╚══════════════════════════════════════════════════════════════════╝

async def get_mysql_db(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    return session


async def get_pg_db(session: AsyncSession = Depends(get_pg_session)) -> AsyncSession:
    return session


def get_machine_repository(pg: AsyncSession = Depends(get_pg_db)) -> MachineRepositoryPort:
    return PgMachineRepository(pg)


def get_component_repository(mysql: AsyncSession = Depends(get_mysql_db)) -> ComponentRepositoryPort:
    return MySQLComponentRepository(mysql)


def get_maintenance_repository(pg: AsyncSession = Depends(get_pg_db)) -> MaintenanceRepositoryPort:
    return PgMaintenanceRepository(pg)


def get_work_order_repository(mysql: AsyncSession = Depends(get_mysql_db)) -> WorkOrderRepositoryPort:
    return MySQLWorkOrderRepository(mysql)


def get_machine_service(
    repo: MachineRepositoryPort = Depends(get_machine_repository),
) -> MachineService:
    return MachineService(repo)


def get_component_service(
    component_repo: ComponentRepositoryPort = Depends(get_component_repository),
    machine_repo: MachineRepositoryPort = Depends(get_machine_repository),
) -> ComponentService:
    return ComponentService(component_repo, machine_repo)


def get_maintenance_service(
    maintenance_repo: MaintenanceRepositoryPort = Depends(get_maintenance_repository),
    machine_repo: MachineRepositoryPort = Depends(get_machine_repository),
    component_repo: ComponentRepositoryPort = Depends(get_component_repository),
) -> MaintenanceService:
    return MaintenanceService(maintenance_repo, machine_repo, component_repo)


def get_work_order_service(
    wo_repo: WorkOrderRepositoryPort = Depends(get_work_order_repository),
    machine_repo: MachineRepositoryPort = Depends(get_machine_repository),
    component_repo: ComponentRepositoryPort = Depends(get_component_repository),
) -> WorkOrderService:
    return WorkOrderService(wo_repo, machine_repo, component_repo)


# ╔══════════════════════════════════════════════════════════════════╗
# ║                         ROUTERS                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

# ── Máquinas (PostgreSQL) ────────────────────────────────────────

machines_router = APIRouter(prefix="/machines", tags=["machines 🔧 (PostgreSQL)"])


@machines_router.get("/", response_model=List[MachineResponse])
async def list_machines(service: MachineService = Depends(get_machine_service)):
    """Lista todas las máquinas (PostgreSQL)."""
    machines = await service.get_all_machines()
    return [MachineResponse(**m.to_dict()) for m in machines]


@machines_router.get("/{machine_id}", response_model=MachineResponse)
async def get_machine(machine_id: str, service: MachineService = Depends(get_machine_service)):
    """Obtiene una máquina por ID (PostgreSQL)."""
    machine = await service.get_machine_by_id(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Máquina '{machine_id}' no encontrada")
    return MachineResponse(**machine.to_dict())


@machines_router.post("/", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(request: MachineCreateRequest, service: MachineService = Depends(get_machine_service)):
    """Crea una nueva máquina (PostgreSQL)."""
    machine = await service.create_machine(
        name=request.name, model=request.model,
        serial_number=request.serial_number, location=request.location,
        purchase_date=request.purchase_date,
    )
    return MachineResponse(**machine.to_dict())


@machines_router.put("/{machine_id}", response_model=MachineResponse)
async def update_machine(machine_id: str, request: MachineUpdateRequest, service: MachineService = Depends(get_machine_service)):
    """Actualiza una máquina (PostgreSQL)."""
    machine = await service.update_machine(
        machine_id=machine_id, name=request.name, model=request.model,
        location=request.location,
        status=request.status.value if request.status else None,
    )
    if not machine:
        raise HTTPException(status_code=404, detail=f"Máquina '{machine_id}' no encontrada")
    return MachineResponse(**machine.to_dict())


@machines_router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(machine_id: str, service: MachineService = Depends(get_machine_service)):
    """Elimina una máquina (PostgreSQL)."""
    if not await service.delete_machine(machine_id):
        raise HTTPException(status_code=404, detail=f"Máquina '{machine_id}' no encontrada")


# ── Componentes (MySQL) ─────────────────────────────────────────

components_router = APIRouter(prefix="/components", tags=["components 🔩 (MySQL)"])


@components_router.get("/", response_model=List[ComponentResponse])
async def list_components(
    machine_id: Optional[str] = Query(None, description="Filtrar por máquina"),
    service: ComponentService = Depends(get_component_service),
):
    """Lista componentes (MySQL). Filtra opcionalmente por máquina."""
    if machine_id:
        components = await service.get_components_by_machine(machine_id)
    else:
        components = await service.get_all_components()
    return [ComponentResponse(**c.to_dict()) for c in components]


@components_router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(component_id: str, service: ComponentService = Depends(get_component_service)):
    """Obtiene un componente por ID (MySQL)."""
    component = await service.get_component_by_id(component_id)
    if not component:
        raise HTTPException(status_code=404, detail=f"Componente '{component_id}' no encontrado")
    return ComponentResponse(**component.to_dict())


@components_router.post("/", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(request: ComponentCreateRequest, service: ComponentService = Depends(get_component_service)):
    """Crea un componente (MySQL). Valida machine_id en PostgreSQL."""
    try:
        component = await service.create_component(
            name=request.name, part_number=request.part_number,
            machine_id=request.machine_id, category=request.category,
            stock=request.stock, unit_cost=request.unit_cost, supplier=request.supplier,
        )
        return ComponentResponse(**component.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@components_router.put("/{component_id}", response_model=ComponentResponse)
async def update_component(component_id: str, request: ComponentUpdateRequest, service: ComponentService = Depends(get_component_service)):
    """Actualiza un componente (MySQL)."""
    component = await service.update_component(
        component_id=component_id, name=request.name, category=request.category,
        stock=request.stock, unit_cost=request.unit_cost, supplier=request.supplier,
    )
    if not component:
        raise HTTPException(status_code=404, detail=f"Componente '{component_id}' no encontrado")
    return ComponentResponse(**component.to_dict())


@components_router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component(component_id: str, service: ComponentService = Depends(get_component_service)):
    """Elimina un componente (MySQL)."""
    if not await service.delete_component(component_id):
        raise HTTPException(status_code=404, detail=f"Componente '{component_id}' no encontrado")


# ── Mantenimientos (PostgreSQL) ──────────────────────────────────

maintenances_router = APIRouter(prefix="/maintenances", tags=["maintenances 🛠️ (PostgreSQL)"])


@maintenances_router.get("/", response_model=List[MaintenanceResponse])
async def list_maintenances(
    machine_id: Optional[str] = Query(None, description="Filtrar por máquina"),
    service: MaintenanceService = Depends(get_maintenance_service),
):
    """Lista mantenimientos (PostgreSQL). Filtra opcionalmente por máquina."""
    if machine_id:
        maintenances = await service.get_maintenances_by_machine(machine_id)
    else:
        maintenances = await service.get_all_maintenances()
    return [MaintenanceResponse(**m.to_dict()) for m in maintenances]


@maintenances_router.get("/{maintenance_id}", response_model=MaintenanceResponse)
async def get_maintenance(maintenance_id: str, service: MaintenanceService = Depends(get_maintenance_service)):
    """Obtiene un mantenimiento por ID (PostgreSQL)."""
    maintenance = await service.get_maintenance_by_id(maintenance_id)
    if not maintenance:
        raise HTTPException(status_code=404, detail=f"Mantenimiento '{maintenance_id}' no encontrado")
    return MaintenanceResponse(**maintenance.to_dict())


@maintenances_router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance(request: MaintenanceCreateRequest, service: MaintenanceService = Depends(get_maintenance_service)):
    """Crea un mantenimiento (PostgreSQL). Valida machine_id (PG) y component_id (MySQL)."""
    try:
        maintenance = await service.create_maintenance(
            machine_id=request.machine_id, type=request.type.value,
            description=request.description, scheduled_date=request.scheduled_date,
            cost=request.cost, component_id=request.component_id,
        )
        return MaintenanceResponse(**maintenance.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@maintenances_router.post("/{maintenance_id}/complete", response_model=MaintenanceResponse)
async def complete_maintenance(maintenance_id: str, request: MaintenanceCompleteRequest = None, service: MaintenanceService = Depends(get_maintenance_service)):
    """Completa un mantenimiento (PostgreSQL)."""
    try:
        cost = request.cost if request else None
        maintenance = await service.complete_maintenance(maintenance_id, cost=cost)
        if not maintenance:
            raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
        return MaintenanceResponse(**maintenance.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@maintenances_router.post("/{maintenance_id}/cancel", response_model=MaintenanceResponse)
async def cancel_maintenance(maintenance_id: str, service: MaintenanceService = Depends(get_maintenance_service)):
    """Cancela un mantenimiento (PostgreSQL)."""
    try:
        maintenance = await service.cancel_maintenance(maintenance_id)
        if not maintenance:
            raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")
        return MaintenanceResponse(**maintenance.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@maintenances_router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_maintenance(maintenance_id: str, service: MaintenanceService = Depends(get_maintenance_service)):
    """Elimina un mantenimiento (PostgreSQL)."""
    if not await service.delete_maintenance(maintenance_id):
        raise HTTPException(status_code=404, detail="Mantenimiento no encontrado")


# ── Órdenes de Trabajo (MySQL) ──────────────────────────────────

work_orders_router = APIRouter(prefix="/work-orders", tags=["work-orders 📋 (MySQL)"])


@work_orders_router.get("/", response_model=List[WorkOrderResponse])
async def list_work_orders(
    machine_id: Optional[str] = Query(None, description="Filtrar por máquina"),
    service: WorkOrderService = Depends(get_work_order_service),
):
    """Lista órdenes de trabajo (MySQL). Filtra opcionalmente por máquina."""
    if machine_id:
        work_orders = await service.get_work_orders_by_machine(machine_id)
    else:
        work_orders = await service.get_all_work_orders()
    return [WorkOrderResponse(**wo.to_dict()) for wo in work_orders]


@work_orders_router.get("/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(work_order_id: str, service: WorkOrderService = Depends(get_work_order_service)):
    """Obtiene una orden de trabajo por ID (MySQL)."""
    work_order = await service.get_work_order_by_id(work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail=f"Orden de trabajo '{work_order_id}' no encontrada")
    return WorkOrderResponse(**work_order.to_dict())


@work_orders_router.post("/", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_work_order(request: WorkOrderCreateRequest, service: WorkOrderService = Depends(get_work_order_service)):
    """Crea una orden de trabajo (MySQL). Valida machine_id (PG) y component_id (MySQL)."""
    try:
        work_order = await service.create_work_order(
            machine_id=request.machine_id, description=request.description,
            priority=request.priority.value, component_id=request.component_id,
        )
        return WorkOrderResponse(**work_order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@work_orders_router.post("/{work_order_id}/assign", response_model=WorkOrderResponse)
async def assign_work_order(work_order_id: str, request: WorkOrderAssignRequest, service: WorkOrderService = Depends(get_work_order_service)):
    """Asigna una orden de trabajo a un técnico (MySQL)."""
    try:
        work_order = await service.assign_work_order(work_order_id, request.assigned_to)
        if not work_order:
            raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
        return WorkOrderResponse(**work_order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@work_orders_router.post("/{work_order_id}/complete", response_model=WorkOrderResponse)
async def complete_work_order(work_order_id: str, service: WorkOrderService = Depends(get_work_order_service)):
    """Completa una orden de trabajo (MySQL)."""
    try:
        work_order = await service.complete_work_order(work_order_id)
        if not work_order:
            raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
        return WorkOrderResponse(**work_order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@work_orders_router.post("/{work_order_id}/cancel", response_model=WorkOrderResponse)
async def cancel_work_order(work_order_id: str, service: WorkOrderService = Depends(get_work_order_service)):
    """Cancela una orden de trabajo (MySQL)."""
    try:
        work_order = await service.cancel_work_order(work_order_id)
        if not work_order:
            raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
        return WorkOrderResponse(**work_order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@work_orders_router.delete("/{work_order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_order(work_order_id: str, service: WorkOrderService = Depends(get_work_order_service)):
    """Elimina una orden de trabajo (MySQL)."""
    if not await service.delete_work_order(work_order_id):
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")


# ╔══════════════════════════════════════════════════════════════════╗
# ║                     ROUTER PRINCIPAL                            ║
# ╚══════════════════════════════════════════════════════════════════╝

router = APIRouter()
router.include_router(machines_router)
router.include_router(components_router)
router.include_router(maintenances_router)
router.include_router(work_orders_router)
