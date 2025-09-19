# SMART_CONNECTOR 

## Summary
SMARTX SMART_CONNECTOR is a solution developed for RFID reader management, offering high performance, scalability, and flexibility in system integration. It provides functionality for configuring and controlling readers, managing connections and reading sessions, integrating with external systems, and simulating reader behavior.

## Structure
- **app/**: Main application code
  - **async_func/**: Asynchronous functions for RFID operations
  - **core/**: Core functionality including configuration and path management
  - **db/**: Database connection and session management
  - **models/**: Data models for the application
  - **routers/**: API route definitions
  - **schemas/**: Data validation schemas
  - **static/**: Static files (JS, CSS, images)
  - **templates/**: HTML templates
- **config/**: Configuration files
  - **devices/**: RFID device configurations
  - **examples/**: Example configurations
- **Logs/**: Application logs

## Language & Runtime
**Language**: Python
**Version**: 3.11 (exact)
**Build System**: Poetry
**Package Manager**: Poetry

## Dependencies
**Main Dependencies**:
- FastAPI (0.110.0)
- Uvicorn (0.29.0)
- SQLAlchemy (2.0.29)
- Jinja2 (3.1.3)
- PySerial/PySerial-AsyncIO (3.5/0.6)
- PyEPC (0.5.0)
- Database drivers (PyMySQL, AIOMySQL, AIOSQLite, AsyncPG)

**Development Dependencies**:
- Tomli (^2.2.1)

## Build & Installation
```bash
# Install dependencies
poetry install

# Run the application
poetry run python main.py

# Build executable
poetry run python build_exe.py
```

## Application Structure
**Entry Point**: main.py
**Web Framework**: FastAPI
**Template Engine**: Jinja2
**Database ORM**: SQLAlchemy
**Async Support**: Full async implementation with asyncio

## Configuration
**Main Config**: config/config.json
**Device Definitions**: config/devices/*.json
**Actions Config**: config/actions.json
**Settings Management**: app/core/config.py

## Packaging
**Executable Builder**: PyInstaller (via build_exe.py)
**Build Configuration**: One-file executable with embedded resources
**Included Resources**: All app directories and dependencies
