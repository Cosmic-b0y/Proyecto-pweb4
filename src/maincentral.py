"""
Main Central - Orquestador de Microservicios

Punto de entrada central que podría orquestar múltiples servicios
o actuar como API Gateway para el ecosistema de microservicios.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.core.config import get_settings
from src.core.exceptions import DomainException
from src.infrastructure.api.v1 import router as v1_router
from src.infrastructure.api.v2 import router as v2_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Microservicios Central Gateway",
    version="1.0.0",
    description="""
    ## Central Gateway
    
    Punto de entrada central para el ecosistema de microservicios.
    Proporciona:
    - Enrutamiento a diferentes versiones de API
    - Manejo centralizado de errores
    - Logging centralizado
    - Middleware común
    """
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log todas las peticiones entrantes."""
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# Manejador de excepciones de dominio
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    """Maneja las excepciones del dominio."""
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.code,
            "message": exc.message
        }
    )


# Rutas
app.include_router(v1_router, prefix="/api/v1", tags=["v1"])
app.include_router(v2_router, prefix="/api/v2", tags=["v2"])


@app.get("/")
async def root():
    """Gateway info."""
    return {
        "gateway": "Microservicios Central",
        "services": {
            "users_v1": "/api/v1/users",
            "users_v2": "/api/v2/users"
        }
    }


@app.get("/health")
async def health():
    """Health check del gateway."""
    return {
        "gateway": "healthy",
        "services": {
            "users": "healthy"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "maincentral:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
