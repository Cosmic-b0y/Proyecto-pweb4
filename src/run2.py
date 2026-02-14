"""
Run2 - Microservicio de Pedidos (Puerto 8002)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from src.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    print(">>> Iniciando Microservicio de Pedidos...")
    print(">>> Documentacion: http://localhost:8002/docs")
    print(">>> ReDoc: http://localhost:8002/redoc")
    
    uvicorn.run(
        "src.main2:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.debug,
        log_level="info"
    )
