# 🏗️ Microservicios - Arquitectura Hexagonal

Proyecto de ejemplo que implementa un microservicio siguiendo el patrón de **Arquitectura Hexagonal** (también conocida como Ports & Adapters) y principios de **Clean Architecture**.

## 📁 Estructura del Proyecto

```
Microservicios/
├── src/
│   ├── application/           # Capa de Aplicación
│   │   ├── ports/             # Interfaces/Contratos
│   │   │   └── user_repository.py
│   │   └── services/          # Casos de uso
│   │       └── user_service.py
│   │
│   ├── core/                  # Configuraciones compartidas
│   │   ├── config.py
│   │   └── exceptions.py
│   │
│   ├── domain/                # Capa de Dominio
│   │   └── entities/          # Entidades de negocio
│   │       └── user.py
│   │
│   ├── infrastructure/        # Capa de Infraestructura
│   │   ├── adapters/          # Implementaciones de puertos
│   │   │   └── memory_user_repository.py
│   │   └── api/               # Controladores HTTP
│   │       ├── v1.py
│   │       └── v2.py
│   │
│   ├── main.py               # Entrada principal
│   ├── main2.py              # Entrada alternativa (solo v1)
│   ├── maincentral.py        # Gateway central
│   ├── run.py                # Script de ejecución
│   └── run2.py               # Script alternativo
│
├── requirements.txt
├── .env.example
└── README.md
```

## 🎯 Arquitectura Hexagonal

```
┌──────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                         │
│  ┌─────────────┐                          ┌────────────┐ │
│  │   API v1    │                          │  Memory    │ │
│  │   API v2    │                          │  Repository│ │
│  └──────┬──────┘                          └─────┬──────┘ │
│         │              ┌──────────┐             │        │
│         │              │          │             │        │
│         └──────────────┤  PORTS   ├─────────────┘        │
│                        │(Interfaces)                     │
│                        └────┬─────┘                      │
│  ┌──────────────────────────┴───────────────────────┐    │
│  │                    APPLICATION                    │    │
│  │               (Services/Use Cases)                │    │
│  └──────────────────────────┬───────────────────────┘    │
│                             │                             │
│  ┌──────────────────────────┴───────────────────────┐    │
│  │                      DOMAIN                       │    │
│  │                     (Entities)                    │    │
│  └───────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

## 🚀 Instalación

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Activar entorno (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecución

```bash
# Opción 1: Ejecutar con el script run
python src/run.py

# Opción 2: Ejecutar directamente
uvicorn src.main:app --reload

# Opción 3: Solo API v1
python src/run2.py
```

## 📚 API Endpoints

### API v1 (`/api/v1/users`)
- `GET /` - Listar usuarios
- `GET /{id}` - Obtener usuario
- `POST /` - Crear usuario
- `PUT /{id}` - Actualizar usuario
- `DELETE /{id}` - Eliminar usuario

### API v2 (`/api/v2/users`)
- `GET /health` - Health check
- `GET /` - Listar usuarios (con paginación)
- `GET /{id}` - Obtener usuario
- `POST /` - Crear usuario
- `DELETE /{id}` - Eliminar usuario

## 📖 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
pytest
```

## 📝 Conceptos Clave

### Puertos (Ports)
Interfaces que definen cómo la aplicación se comunica con el exterior. Ejemplo: `UserRepositoryPort`.

### Adaptadores (Adapters)
Implementaciones concretas de los puertos. Ejemplo: `MemoryUserRepository`.

### Casos de Uso (Services)
Orquestan la lógica de negocio. Ejemplo: `UserService`.

### Entidades (Entities)
Objetos del dominio con identidad y reglas de negocio. Ejemplo: `User`.
