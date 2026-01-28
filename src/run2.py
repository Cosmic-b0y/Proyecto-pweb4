"""
Run2 - Script de ejecución alternativo

Script para iniciar solo la API v1 en un puerto diferente.
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando API v1 Only...")
    print("📚 Documentación: http://localhost:8001/docs")
    
    uvicorn.run(
        "src.main2:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
