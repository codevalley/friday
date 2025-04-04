# Friday - Clean Architecture API Service

A FastAPI-based API service implementing Clean Architecture principles.

## Project Structure

The project follows the Clean Architecture pattern with the following layers:

- **Core** (`src/core/`): Domain entities, repository interfaces, and DTOs.
- **Application** (`src/application/`): Use cases and business logic.
- **Infrastructure** (`src/infrastructure/`): Repository and service implementations.
- **API** (`src/api/`): FastAPI routes, dependencies, and middleware.

## Features

- User authentication with JWT tokens
- CRUD operations for users and notes
- Redis caching
- SQLAlchemy ORM for database operations

## Getting Started

### Prerequisites

- Python 3.9+
- Redis (optional, for caching)

### Installation

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

### Running the API

```bash
python -m src.api.main
```

Or with Uvicorn directly:

```bash
uvicorn src.api.main:app --reload
```

## API Documentation

API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Unit Tests

Run tests with pytest:

```bash
pytest
```

### End-to-End Testing

A comprehensive end-to-end test script is provided to verify API functionality:

```bash
python test_script.py
```

This script tests:
- User creation and authentication
- Note creation, reading, updating, and deletion
- Error handling for invalid operations

You can also run it with the `--flush` flag to reset the database before testing:

```bash
python test_script.py --flush
```

### Debug Tools

Development debug scripts are located in the `debug/` directory. These were used during development to troubleshoot specific functionality.

## License

This project is licensed under the Apache License, Version 2.0.