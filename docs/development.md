# Development Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.9 or higher
- pip (Python package manager)
- Redis (for caching)
- Git

## Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/friday.git
cd friday
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
# Application
APP_NAME=Friday
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///app.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Database Setup

1. Initialize the database:
```bash
alembic upgrade head
```

2. (Optional) Load sample data:
```bash
python scripts/seed_data.py
```

## Running the Development Server

1. Start Redis (if not already running):
```bash
# On macOS with Homebrew
brew services start redis

# On Linux
sudo service redis-server start

# On Windows
# Start Redis server based on your installation
```

2. Start the development server:
```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

## Development Tools

### Code Formatting

We use `black` for code formatting:
```bash
# Format all Python files
black .

# Check formatting without making changes
black . --check
```

### Linting

We use `flake8` for linting:
```bash
flake8 .
```

### Type Checking

We use `mypy` for type checking:
```bash
mypy src tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# Run specific test file
pytest tests/path/to/test_file.py

# Run tests with verbose output
pytest -v
```

### Debugging

1. VS Code Configuration:
   - Use the provided `.vscode/launch.json` for debugging
   - Set breakpoints in your code
   - Press F5 to start debugging

2. Debug Toolbar:
   - Available at `http://localhost:8000/debug` in development mode
   - Shows request/response information
   - Displays SQL queries
   - Provides Redis cache statistics

## Git Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "feat: your feature description"
```

3. Push your changes:
```bash
git push origin feature/your-feature-name
```

4. Create a pull request on GitHub

## Code Style Guide

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public modules, functions, classes, and methods
- Keep functions focused and small
- Use meaningful variable and function names
- Add comments only when necessary to explain complex logic

## Troubleshooting

### Common Issues

1. Database connection errors:
   - Verify DATABASE_URL in .env
   - Check if migrations are up to date
   - Ensure database file permissions are correct

2. Redis connection errors:
   - Verify Redis is running
   - Check REDIS_URL in .env
   - Ensure Redis port is not blocked

3. Import errors:
   - Verify virtual environment is activated
   - Check if all dependencies are installed
   - Ensure PYTHONPATH includes project root

For more issues, check the [GitHub Issues](https://github.com/yourusername/friday/issues) page. 