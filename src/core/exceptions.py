"""
Excepciones del Dominio

Define las excepciones personalizadas para el manejo de errores
en las diferentes capas de la aplicación.
"""


class DomainException(Exception):
    """Excepción base para errores del dominio."""
    
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationException(DomainException):
    """Excepción para errores de validación."""
    
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, code="VALIDATION_ERROR")


class NotFoundException(DomainException):
    """Excepción cuando un recurso no se encuentra."""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} con id '{identifier}' no encontrado"
        self.resource = resource
        self.identifier = identifier
        super().__init__(message, code="NOT_FOUND")


class ConflictException(DomainException):
    """Excepción para conflictos (ej: duplicados)."""
    
    def __init__(self, message: str):
        super().__init__(message, code="CONFLICT")


class UnauthorizedException(DomainException):
    """Excepción para accesos no autorizados."""
    
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, code="UNAUTHORIZED")
