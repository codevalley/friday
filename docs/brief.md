
We're setting up a new API service project and adopting a Clean Architecture approach to ensure maintainability, testability, and flexibility. Please refer to the project structure diagram provided (python_clean_arch_structure_multi_entity).

Core Idea:

The structure strictly separates contracts/interfaces from concrete implementations.

src/core/: This is the heart of the application. It defines what the system does, containing:

Domain entities (domain/) - Plain data structures (e.g., User, Note).

Repository interfaces (repositories/) - Abstract Base Classes (ABCs) defining data access methods.

Service interfaces (services/) - ABCs for external services (e.g., Auth, Cache).

DTOs (use_cases/) - Pydantic models for data transfer between layers and API boundaries.

This layer should have minimal dependencies.

src/infrastructure/: Contains the concrete implementations of the interfaces defined in core/. This is where specific technologies live:

Persistence (persistence/sqlalchemy/, persistence/memory/) - Implements repository ABCs using SQLAlchemy (initially with SQLite, designed for easy switching to Postgres) or in-memory stores.

Services (services/jwt/, services/redis/) - Implements service ABCs using specific libraries (e.g., JWT, Redis).

src/application/: Holds the use case logic. It orchestrates domain entities and uses interfaces from core/ (repositories, services) to perform application-specific tasks. It depends on core but not on infrastructure or api.

src/api/: The entry point and web layer (using FastAPI).

Handles HTTP requests/responses (routes/).

Uses Pydantic DTOs for request validation and response serialization.

Calls use cases in application/.

Contains middleware (middleware/).

Performs Dependency Injection (main.py, dependencies.py) - wiring together the concrete implementations from infrastructure and injecting them where needed (primarily into the application layer).

Technology Stack:

Framework: FastAPI

Validation/DTOs: Pydantic

Database ORM: SQLAlchemy (We'll start with SQLite for simplicity/dev, but the SQLAlchemy abstraction allows us to easily switch to PostgreSQL later by just changing the connection string and driver).

Caching/Other: Redis (via interfaces defined in core/services/ and implemented in infrastructure/services/redis/).

Initial Entities:

User (userid, name, user_secret, tier)

Note (note_id, user_id, content, created)

Goal: By following this structure, we keep business logic separate from infrastructure details, making the codebase easier to test, understand, and evolve (e.g., changing the database or a third-party service implementation).

Please start by defining the core entities, DTOs, and repository/service interfaces in src/core/, then move towards implementing the use cases and infrastructure components. Let me know if you have any questions.

```
/friday-service
├── src/                      # Main source directory
│   │
│   ├── core/                 # === Contracts & Core Domain ===
│   │   ├── __init__.py
│   │   ├── domain/           # Domain Models/Entities
│   │   │   ├── __init__.py
│   │   │   ├── user.py       # Defines User entity (userid, name, user_secret, tier)
│   │   │   └── note.py       # Defines Note entity (note_id, user_id, content, created)
│   │   ├── repositories/     # Abstract Repository Interfaces (using abc.ABC)
│   │   │   ├── __init__.py
│   │   │   ├── user_repo.py  # Defines abstract class UserRepository(ABC)
│   │   │   └── note_repo.py  # Defines abstract class NoteRepository(ABC)
│   │   ├── use_cases/        # Use Case DTOs & Optional Interfaces
│   │   │   ├── __init__.py
│   │   │   ├── user_dtos.py  # Pydantic DTOs for User (UserCreateDTO, UserReadDTO, etc.)
│   │   │   └── note_dtos.py  # Pydantic DTOs for Note (NoteCreateDTO, NoteReadDTO, etc.)
│   │   └── services/         # Abstract External Service Interfaces (using abc.ABC)
│   │       ├── __init__.py
│   │       ├── auth_service.py # Defines abstract class AuthService(ABC)
│   │       └── cache_service.py # Defines abstract class CacheService(ABC)
│   │       # (Add other services like RateLimitService if needed)
│   │
│   ├── infrastructure/       # === Concrete Implementations ===
│   │   ├── __init__.py
│   │   ├── persistence/      # Data Persistence Implementations
│   │   │   ├── __init__.py
│   │   │   ├── sqlalchemy/   # SQLAlchemy Implementation (preferred over raw drivers)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py    # SQLAlchemy declarative models for User and Note tables
│   │   │   │   ├── user_repo.py # Implements core.repositories.UserRepository using SQLAlchemy
│   │   │   │   └── note_repo.py # Implements core.repositories.NoteRepository using SQLAlchemy
│   │   │   └── memory/       # In-Memory Implementation (for testing/dev)
│   │   │       ├── __init__.py
│   │       │       ├── user_repo.py # Implements core.repositories.UserRepository
│   │       │       └── note_repo.py # Implements core.repositories.NoteRepository
│   │   ├── services/         # External Service Implementations
│   │   │   ├── __init__.py
│   │   │   ├── jwt/          # JWT Implementation
│   │   │   │   ├── __init__.py
│   │   │   │   └── auth_service.py # Implements core.services.AuthService
│   │   │   └── redis/        # Redis Implementation
│   │       │   ├── __init__.py
│   │       │   └── cache_service.py # Implements core.services.CacheService
│   │       │   # (Add other service implementations like rate limiting here)
│   │
│   ├── application/          # === Application Logic (Use Case Implementations) ===
│   │   ├── __init__.py
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       ├── user_uc.py    # Implements User Use Cases (CreateUser, GetUser, etc.)
│   │       └── note_uc.py    # Implements Note Use Cases (CreateNote, GetNotesByUser, DeleteNote, etc.)
│   │
│   ├── api/                  # === Web Layer & Wiring ===
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI/Flask app instance, DI wiring, server start
│   │   ├── routes/           # API Route/Endpoint definitions
│   │   │   ├── __init__.py
│   │   │   ├── user_routes.py # Defines /users endpoints
│   │   │   └── note_routes.py # Defines /notes (or /users/{id}/notes) endpoints
│   │   ├── middleware/       # API Middleware implementations
│   │   │   ├── __init__.py
│   │   │   └── auth.py       # Authentication middleware
│   │   │   # (Add other middleware like rate limiting)
│   │   └── dependencies.py   # Optional: Centralized Dependency Injection setup/container
│   │
│   └── config.py             # Configuration loading
│
├── tests/                    # Tests directory mirroring src structure
│   ├── __init__.py
│   ├── core/
│   │   ├── domain/
│   │   ├── repositories/
│   │   └── use_cases/
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   ├── sqlalchemy/
│   │   │   └── memory/
│   │   └── services/
│   ├── application/
│   │   └── use_cases/
│   └── api/
│       ├── routes/
│       └── middleware/
├── .env                      # Environment variables file (loaded by config)
├── .gitignore
├── pyproject.toml            # Project definition, dependencies (e.g., Poetry/PDM)
└── README.md
```
