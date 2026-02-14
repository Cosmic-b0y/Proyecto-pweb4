from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.infrastructure.api.v1 import router as users_router

# Obtener configuración
settings = get_settings()

# Crear aplicación FastAPI - Microservicio de Usuarios
app = FastAPI(
    title="Microservicio de Usuarios",
    version="1.0.0",
    description="""
    ## Microservicio de Usuarios - Puerto 8001
    
    CRUD completo para la gestión de usuarios con:
    - **Arquitectura Hexagonal** (Ports & Adapters)
    - **Clean Architecture**
    
    ### Endpoints:
    - `GET /api/v1/users` - Listar usuarios
    - `GET /api/v1/users/{id}` - Obtener usuario
    - `POST /api/v1/users` - Crear usuario
    - `PUT /api/v1/users/{id}` - Actualizar usuario
    - `DELETE /api/v1/users/{id}` - Eliminar usuario
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

# Registrar router de usuarios
app.include_router(users_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Endpoint raíz con información del microservicio."""
    return {
        "service": "Microservicio de Usuarios",
        "version": "1.0.0",
        "port": 8001,
        "docs": "/docs",
        "endpoints": {
            "users": f"{settings.api_v1_prefix}/users"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "users"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
