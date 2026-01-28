"""
Main Entry Point - Aplicación Principal

Punto de entrada principal de la aplicación FastAPI.
Configura la aplicación, middleware y rutas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.infrastructure.api.v1 import router as v1_router
from src.infrastructure.api.v2 import router as v2_router
from src.infrastructure.api.orders import router as orders_router

# Obtener configuración
settings = get_settings()

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Microservicios API - Usuarios y Pedidos
    
    Sistema de gestión de usuarios y pedidos con:
    - **Arquitectura Hexagonal** (Ports & Adapters)
    - **Clean Architecture**
    - **Domain-Driven Design (DDD)**
    
    ### Módulos:
    - **Usuarios**: Gestión completa de usuarios (v1 y v2)
    - **Pedidos**: Creación y gestión de pedidos con estados
    
    ### Versiones de API:
    - **v1/users**: API básica de usuarios
    - **v2/users**: API mejorada con paginación
    - **v1/orders**: API de pedidos
    """,
    docs_url="/docs",
    redoc_url="/redoc"
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
app.include_router(v1_router, prefix=settings.api_v1_prefix)
app.include_router(v2_router, prefix=settings.api_v2_prefix)
app.include_router(orders_router, prefix=f"{settings.api_v1_prefix}")


@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "api": {
            "users_v1": f"{settings.api_v1_prefix}/users",
            "users_v2": f"{settings.api_v2_prefix}/users",
            "orders": f"{settings.api_v1_prefix}/orders"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
