# Friday - Clean Architecture API Service

A FastAPI-based API service implementing Clean Architecture principles.

## Project Structure

The project follows the Clean Architecture pattern with the following layers:

- **Core** (`src/core/`): Domain entities, repository interfaces, and DTOs.
- **Application** (`src/application/`): Use cases and business logic.
- **Infrastructure** (`src/infrastructure/`): Repository and service implementations.
- **API** (`src/api/`): FastAPI routes, dependencies, and middleware.

## Documentation

- [API Documentation](docs/api.md) - Complete API endpoint documentation
- [Database Schema](docs/database.md) - Database structure and relationships
- [Development Guide](docs/development.md) - Setup and development guidelines

## Features

- User authentication with JWT tokens
- CRUD operations for users and notes
- Redis caching
- SQLAlchemy ORM for database operations

## Getting Started

### Prerequisites

- Python 3.9+
- Redis (optional, for caching)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/friday.git
   cd friday
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Create a `.env` file (see `.env.example` for reference)

For detailed setup instructions, see the [Development Guide](docs/development.md).

## License

This project is licensed under the Apache License, Version 2.0.