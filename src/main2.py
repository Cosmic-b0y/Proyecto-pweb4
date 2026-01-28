"""
Main2 - Versión alternativa de entrada

Versión simplificada de la aplicación que solo incluye la API v1.
Útil para pruebas o despliegues específicos.
"""

from fastapi import FastAPI
from src.infrastructure.api.v1 import router as v1_router

app = FastAPI(
    title="Microservicios API v1 Only",
    version="1.0.0",
    description="API simplificada solo con v1"
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "API v1 Only", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main2:app", host="0.0.0.0", port=8001, reload=True)
