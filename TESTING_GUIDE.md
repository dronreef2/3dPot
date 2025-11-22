# Quick Testing Guide - 3dPot

## Prerequisites

- Python 3.9+ (Python 3.12 recommended for best compatibility)
- pip or pip3
- Git

**Note:** While the project may work with Python 3.8+, cadquery 2.4.0 works best with Python 3.9 or later.

## Quick Start (5 Minutes)

### 1. Install Core Dependencies

```bash
# Install only the essential packages for basic testing
pip install fastapi uvicorn sqlalchemy pydantic pytest

# Install backend-specific requirements
pip install passlib pyotp python-jose cryptography
pip install pydantic-settings email-validator python-dotenv
pip install aiosqlite prometheus-client structlog
```

### 2. Set Python Path

```bash
# From the project root
export PYTHONPATH=/path/to/3dPot:$PYTHONPATH

# Or for this session only (from project root)
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### 3. Run Quick Syntax Check

```bash
# Verify all Python files have valid syntax
python3 -m py_compile backend/main.py
python3 -m py_compile backend/services/*.py
python3 -m py_compile backend/models/*.py
```

### 4. Run Basic Import Test

```bash
# Test if modules can be imported
python3 -c "import sys; sys.path.insert(0, '.'); from backend.core import config; print('✓ Config imported')"
python3 -c "import sys; sys.path.insert(0, '.'); from backend.models import User; print('✓ Models imported')"
python3 -c "import sys; sys.path.insert(0, '.'); from backend.schemas import UserBase; print('✓ Schemas imported')"
```

### 5. Run Specific Tests

```bash
# Set PYTHONPATH and run specific test files
export PYTHONPATH=$(pwd):$PYTHONPATH

# Run a simple test module
pytest tests/unit/test_project_structure.py -v

# Run CLI tests
pytest tests/unit/cli/ -v

# Run 3D model tests
pytest tests/unit/test_3d_models.py -v
```

## Full Testing (With All Dependencies)

### 1. Install All Dependencies

```bash
# Install everything (may take 5-10 minutes)
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 2. Run Full Test Suite

```bash
# Use the test runner script
./run_tests.sh all

# Or run pytest directly
export PYTHONPATH=$(pwd):$PYTHONPATH
pytest tests/ -v --cov=backend --cov-report=html
```

### 3. Run Tests by Category

```bash
# Unit tests only (fastest)
./run_tests.sh unit

# Integration tests
./run_tests.sh integration

# Hardware tests
./run_tests.sh hardware

# 3D model tests
./run_tests.sh 3d

# Structure tests
./run_tests.sh structure
```

## Testing Without Full Dependencies

If you want to test without installing all dependencies:

### 1. Install Minimal Requirements

```bash
# Create a minimal requirements file
cat > requirements-minimal-test.txt << EOF
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
passlib==1.7.4
pyotp==2.9.0
python-jose==3.3.0
cryptography==43.0.1
email-validator==2.1.0
python-dotenv==1.0.0
aiosqlite==0.19.0
prometheus-client==0.19.0
structlog==23.2.0
EOF

pip install -r requirements-minimal-test.txt
```

### 2. Run Tests That Don't Need Heavy Dependencies

```bash
export PYTHONPATH=$(pwd):$PYTHONPATH

# Project structure tests
pytest tests/unit/test_project_structure.py -v

# CLI tests (if available)
pytest tests/unit/cli/ -v --ignore=tests/unit/cli/test_3d_generation.py

# Schema tests
pytest tests/unit/test_schemas.py -v
```

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'backend'"

**Solution:**
```bash
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### Issue: "ModuleNotFoundError: No module named 'pydantic_settings'"

**Solution:**
```bash
pip install pydantic-settings
```

### Issue: "ModuleNotFoundError: No module named 'passlib'"

**Solution:**
```bash
pip install passlib[bcrypt]
```

### Issue: "ModuleNotFoundError: No module named 'pandas'"

**Solution:**
```bash
pip install pandas openpyxl
```

### Issue: Tests hang or timeout

**Solution:**
- Some tests may try to connect to external services
- Use `pytest -x` to stop on first failure
- Use `pytest -k "not slow"` to skip slow tests

### Issue: "No module named 'core'"

**Solution:**
- This is an import path issue
- Should be fixed in commit 4db29af
- If still occurs, check that files use `from backend.core` not `from core`

## Test Coverage

To generate a coverage report:

```bash
export PYTHONPATH=$(pwd):$PYTHONPATH
pytest tests/unit/ --cov=backend --cov-report=html --cov-report=term
```

Then open `htmlcov/index.html` in your browser.

## Continuous Integration

The project uses GitHub Actions for CI/CD:

- `.github/workflows/python-tests.yml` - Python tests
- `.github/workflows/code-quality.yml` - Code quality checks
- `.github/workflows/ci.yml` - Main CI pipeline

## Performance Testing

For performance testing:

```bash
# Run benchmarks
pytest tests/ -v --benchmark-only

# Profile tests
pytest tests/ --profile

# Parallel execution
pytest tests/ -n auto
```

## Docker Testing

To test in a Docker environment:

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up --build

# Run tests in Docker
docker-compose -f docker-compose.dev.yml run backend pytest tests/

# Cleanup
docker-compose -f docker-compose.dev.yml down -v
```

## Next Steps

After basic testing works:

1. Review `run_tests.sh` for more test options
2. Check `pytest.ini` for test configuration
3. See `backend/pytest.ini` for backend-specific config
4. Read `CONTRIBUTING.md` for contribution guidelines

## Summary

**Minimal Setup:**
```bash
pip install fastapi uvicorn sqlalchemy pydantic pytest passlib pyotp
export PYTHONPATH=$(pwd):$PYTHONPATH
pytest tests/unit/test_project_structure.py -v
```

**Full Setup:**
```bash
pip install -r requirements.txt -r requirements-test.txt
export PYTHONPATH=$(pwd):$PYTHONPATH
./run_tests.sh all
```

For more details, see:
- `README.md` - Project overview
- `CONTRIBUTING.md` - Development guidelines
- `BRANCH_CONSOLIDATION_GUIDE.md` - Branch management
