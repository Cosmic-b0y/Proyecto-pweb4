

from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    
    Las variables se cargan del archivo .env o del entorno.
    """
    
    # Aplicación
    app_name: str = "Microservicios API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API
    api_prefix: str = "/api"
    api_v1_prefix: str = "/api/v1"
    api_v2_prefix: str = "/api/v2"
    
    # Base de datos MySQL
    database_url: str = "mysql+aiomysql://root:root@localhost:3306/proyecto_pweb4"
    
    # Base de datos PostgreSQL
    database_pg_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/proyecto_pweb4_mecanico"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    
    # Seguridad / JWT
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: str = "*"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia de configuración (singleton).
    
    Returns:
        Instancia de Settings cacheada
    """
    return Settings()
