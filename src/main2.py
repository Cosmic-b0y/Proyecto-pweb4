from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.infrastructure.api.orders import router as orders_router

# Obtener configuración
settings = get_settings()

# Crear aplicación FastAPI - Microservicio de Pedidos
app = FastAPI(
    title="Microservicio de Pedidos",
    version="1.0.0",
    description="""
    ## Microservicio de Pedidos - Puerto 8002
    
    CRUD completo para la gestión de pedidos con:
    - **Arquitectura Hexagonal** (Ports & Adapters)
    - **Clean Architecture**
    
    ### Endpoints CRUD:
    - `GET /api/v1/orders` - Listar pedidos
    - `GET /api/v1/orders/{id}` - Obtener pedido
    - `POST /api/v1/orders` - Crear pedido
    - `PUT /api/v1/orders/{id}` - Actualizar pedido
    - `DELETE /api/v1/orders/{id}` - Eliminar pedido
    
    ### Transiciones de estado:
    - `POST /api/v1/orders/{id}/confirm` - Confirmar
    - `POST /api/v1/orders/{id}/process` - Procesar
    - `POST /api/v1/orders/{id}/ship` - Enviar
    - `POST /api/v1/orders/{id}/deliver` - Entregar
    - `POST /api/v1/orders/{id}/cancel` - Cancelar
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

# Registrar router de pedidos
app.include_router(orders_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Endpoint raíz con información del microservicio."""
    return {
        "service": "Microservicio de Pedidos",
        "version": "1.0.0",
        "port": 8002,
        "docs": "/docs",
        "endpoints": {
            "orders": f"{settings.api_v1_prefix}/orders"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "orders"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main2:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
