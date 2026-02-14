"""
Run - Microservicio de Usuarios (Puerto 8001)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from src.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    print(">>> Iniciando Microservicio de Usuarios...")
    print(">>> Documentacion: http://localhost:8001/docs")
    print(">>> ReDoc: http://localhost:8001/redoc")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level="info"
    )
