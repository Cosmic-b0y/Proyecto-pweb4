"""
Microservicio de Usuarios - Punto de entrada principal.

Configura FastAPI con:
- Conexión a MySQL (SQLAlchemy async)
- Conexión a RabbitMQ (aio-pika)
- Autenticación JWT
- CRUD de usuarios
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.infrastructure.database import init_db
from src.infrastructure.messaging.rabbitmq import RabbitMQConnection
from src.infrastructure.api.auth import router as auth_router
from src.infrastructure.api.v1 import router as users_router

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

    Startup: Inicializa MySQL y RabbitMQ.
    Shutdown: Cierra conexiones.
    """
    # === STARTUP ===
    logger.info("🚀 Iniciando Microservicio de Usuarios...")

    # Inicializar base de datos MySQL
    try:
        await init_db()
        logger.info("✅ Base de datos MySQL inicializada")
    except Exception as e:
        logger.error(f"❌ Error inicializando MySQL: {e}")
        logger.warning("⚠️ La app continuará pero la BD no está disponible")

    # Conectar a RabbitMQ
    try:
        await RabbitMQConnection.connect()
        logger.info("✅ RabbitMQ conectado")
    except Exception as e:
        logger.error(f"❌ Error conectando a RabbitMQ: {e}")
        logger.warning("⚠️ La app continuará pero RabbitMQ no está disponible")

    yield

    # === SHUTDOWN ===
    logger.info("🛑 Cerrando Microservicio de Usuarios...")
    await RabbitMQConnection.disconnect()
    logger.info("👋 Microservicio cerrado")


# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio de Usuarios",
    version="2.0.0",
    description="""
    ## Microservicio de Usuarios - Puerto 8001
    
    CRUD de usuarios + Autenticación con:
    - **MySQL** como base de datos
    - **RabbitMQ** para eventos de login
    - **JWT** para autenticación
    - **Arquitectura Hexagonal** (Ports & Adapters)
    
    ### Auth Endpoints:
    - `POST /api/v1/auth/register` - Registrar usuario
    - `POST /api/v1/auth/login` - Iniciar sesión (pasa por RabbitMQ)
    - `GET /api/v1/auth/me` - Perfil del usuario autenticado
    
    ### User CRUD:
    - `GET /api/v1/users` - Listar usuarios
    - `GET /api/v1/users/{id}` - Obtener usuario
    - `POST /api/v1/users` - Crear usuario
    - `PUT /api/v1/users/{id}` - Actualizar usuario
    - `DELETE /api/v1/users/{id}` - Eliminar usuario
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

# Registrar routers
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(users_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Endpoint raíz con información del microservicio."""
    return {
        "service": "Microservicio de Usuarios",
        "version": "2.0.0",
        "port": 8001,
        "database": "MySQL",
        "messaging": "RabbitMQ",
        "docs": "/docs",
        "endpoints": {
            "auth_register": f"{settings.api_v1_prefix}/auth/register",
            "auth_login": f"{settings.api_v1_prefix}/auth/login",
            "auth_me": f"{settings.api_v1_prefix}/auth/me",
            "users": f"{settings.api_v1_prefix}/users",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "users", "database": "mysql", "messaging": "rabbitmq"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
