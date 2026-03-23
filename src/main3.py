"""
Microservicio de Sistema Mecánico - Punto de entrada principal.

Configura FastAPI con:
- Conexión a MySQL (componentes, órdenes de trabajo)
- Conexión a PostgreSQL (máquinas, mantenimientos)
- CRUD completo del sistema mecánico
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.infrastructure.database import init_db
from src.infrastructure.database_pg import init_db_pg
from src.infrastructure.api.mechanical import router as mechanical_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Obtener configuración
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.

    Startup: Inicializa MySQL y PostgreSQL.
    Shutdown: Cierra conexiones.
    """
    # === STARTUP ===
    logger.info("🚀 Iniciando Microservicio de Sistema Mecánico...")

    # Inicializar MySQL (componentes, órdenes de trabajo)
    try:
        await init_db()
        logger.info("✅ Base de datos MySQL inicializada (componentes, work_orders)")
    except Exception as e:
        logger.error(f"❌ Error inicializando MySQL: {e}")
        logger.warning("⚠️ La app continuará pero MySQL no está disponible")

    # Inicializar PostgreSQL (máquinas, mantenimientos)
    try:
        await init_db_pg()
        logger.info("✅ Base de datos PostgreSQL inicializada (machines, maintenances)")
    except Exception as e:
        logger.error(f"❌ Error inicializando PostgreSQL: {e}")
        logger.warning("⚠️ La app continuará pero PostgreSQL no está disponible")

    yield

    # === SHUTDOWN ===
    logger.info("🛑 Cerrando Microservicio de Sistema Mecánico...")
    logger.info("👋 Microservicio cerrado")


# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio de Sistema Mecánico",
    version="1.0.0",
    description="""
    ## Microservicio de Sistema Mecánico - Puerto 8003
    
    CRUD completo para la gestión de un sistema mecánico con:
    - **PostgreSQL** para máquinas y mantenimientos
    - **MySQL** para componentes y órdenes de trabajo
    - **Llaves foráneas lógicas** entre ambas bases de datos
    - **Arquitectura Hexagonal** (Ports & Adapters)
    
    ### Máquinas (PostgreSQL) 🔧:
    - `GET /api/v1/mechanical/machines` - Listar máquinas
    - `GET /api/v1/mechanical/machines/{id}` - Obtener máquina
    - `POST /api/v1/mechanical/machines` - Crear máquina
    - `PUT /api/v1/mechanical/machines/{id}` - Actualizar máquina
    - `DELETE /api/v1/mechanical/machines/{id}` - Eliminar máquina
    
    ### Componentes (MySQL) 🔩:
    - `GET /api/v1/mechanical/components` - Listar componentes
    - `GET /api/v1/mechanical/components/{id}` - Obtener componente
    - `POST /api/v1/mechanical/components` - Crear componente
    - `PUT /api/v1/mechanical/components/{id}` - Actualizar componente
    - `DELETE /api/v1/mechanical/components/{id}` - Eliminar componente
    
    ### Mantenimientos (PostgreSQL) 🛠️:
    - `GET /api/v1/mechanical/maintenances` - Listar mantenimientos
    - `POST /api/v1/mechanical/maintenances` - Crear mantenimiento
    - `POST /api/v1/mechanical/maintenances/{id}/complete` - Completar
    - `POST /api/v1/mechanical/maintenances/{id}/cancel` - Cancelar
    - `DELETE /api/v1/mechanical/maintenances/{id}` - Eliminar
    
    ### Órdenes de Trabajo (MySQL) 📋:
    - `GET /api/v1/mechanical/work-orders` - Listar órdenes
    - `POST /api/v1/mechanical/work-orders` - Crear orden
    - `POST /api/v1/mechanical/work-orders/{id}/assign` - Asignar
    - `POST /api/v1/mechanical/work-orders/{id}/complete` - Completar
    - `POST /api/v1/mechanical/work-orders/{id}/cancel` - Cancelar
    - `DELETE /api/v1/mechanical/work-orders/{id}` - Eliminar
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar router del sistema mecánico
app.include_router(mechanical_router, prefix=settings.api_v1_prefix + "/mechanical")


@app.get("/")
async def root():
    """Endpoint raíz con información del microservicio."""
    return {
        "service": "Microservicio de Sistema Mecánico",
        "version": "1.0.0",
        "port": 8003,
        "databases": {
            "postgresql": "machines, maintenances",
            "mysql": "components, work_orders",
        },
        "docs": "/docs",
        "endpoints": {
            "machines": f"{settings.api_v1_prefix}/mechanical/machines",
            "components": f"{settings.api_v1_prefix}/mechanical/components",
            "maintenances": f"{settings.api_v1_prefix}/mechanical/maintenances",
            "work_orders": f"{settings.api_v1_prefix}/mechanical/work-orders",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mechanical-system",
        "databases": {"mysql": "components,work_orders", "postgresql": "machines,maintenances"},
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main3:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
    )
