"""
Run - Script de ejecución principal

Script para iniciar la aplicación principal con configuración estándar.
"""

import uvicorn
from src.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    print(f"🚀 Iniciando {settings.app_name}...")
    print(f"📚 Documentación disponible en: http://localhost:8000/docs")
    print(f"📖 ReDoc disponible en: http://localhost:8000/redoc")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
