# SMARTX CONNECTOR v1.2.0

## Summary
SMARTX CONNECTOR is a modern RFID reader management solution built with FastAPI, offering high performance, scalability, and flexibility in system integration. It provides comprehensive functionality for configuring RFID readers, managing device connections, processing tag events, database integration with SQLAlchemy models, real-time monitoring through a web interface, and extensive API endpoints for system integration.

## Project Structure
- **app/**: Main application code
  - **async_func/**: Asynchronous background tasks for RFID operations
  - **core/**: Core application functionality
    - `build_app.py`: FastAPI application factory
    - `config.py`: Configuration management and settings
    - `middleware.py`: CORS, GZIP, and custom middlewares
    - `build_templates.py`: Jinja2 template configuration
    - `exeption_handlers.py`: Error handling setup
  - **db/**: Database connection and session management
    - `__init__.py`: Database initialization and model registration
  - **models/**: SQLAlchemy data models
    - `mixin.py`: Base model classes with utilities
    - `rfid.py`: Tag and Event models for RFID data
    - `__init__.py`: Model discovery and registration
  - **routers/**: API route definitions
    - **api/v1/**: REST API endpoints
      - `devices.py`: Device management endpoints
      - `rfid.py`: RFID tag operations
      - `simulator.py`: Tag simulation for testing
      - `receive.py`: External data reception
    - **pages/**: Web interface routes
      - `index.py`: Home page and documentation
      - `logs.py`: Log viewing interface
  - **schemas/**: Pydantic data validation schemas
    - `simulator.py`: Validation for simulation endpoints
  - **services/**: Business logic and integrations
    - **rfid/**: RFID service management
      - `_main.py`: Main RFID manager
      - `devices.py`: Device connection handling
      - `events.py`: Event processing
      - `integration.py`: Database and webhook integration
  - **static/**: Frontend assets
    - **css/**: Tailwind CSS styling
    - **js/**: Alpine.js for reactive components
    - **docs/**: Swagger UI assets
    - **images/**: Application images and logos
    - **sounds/**: Audio notification files
  - **templates/**: Jinja2 HTML templates
    - `base.html`: Base template with navigation
    - **pages/**: Page-specific templates
      - **index/**: Dashboard components
      - **logs/**: Log viewing interface
    - **includes/**: Reusable template components
- **config/**: Configuration files
  - `config.json`: Main application configuration
  - **devices/**: RFID device-specific configurations
  - **examples/**: Example device configurations
- **alembic/**: Database migration management
  - **versions/**: Migration scripts
- **Logs/**: Application log files

## Language & Runtime
**Language**: Python
**Version**: 3.11 (exact)
**Build System**: Poetry
**Package Manager**: Poetry

## Dependencies
**Main Dependencies**:
- FastAPI (0.110.0) - Modern web framework for building APIs
- Uvicorn (0.29.0) - ASGI server implementation
- SQLAlchemy (2.0+) - Modern Python SQL toolkit and ORM
- Alembic (1.17.2+) - Database migration tool
- Jinja2 (3.1.3) - Template engine for web interface
- Python-Multipart (0.0.9) - Form data parsing
- SMARTX-RFID (1.5.0) - Core RFID management library
- HTTPx (0.28.1) - HTTP client for webhook integrations
- PyGame (2.6.1) - Audio notification support
- GMQTT (0.7.0) - MQTT client for IoT integration
- Prometheus FastAPI Instrumentator (7.1.0+) - Metrics and monitoring
- Cryptography (44.0.3) - Security and encryption support
- Passlib[bcrypt] (1.7.4) - Password hashing utilities

**Development Dependencies**:
- Tomli (2.2.1+) - TOML file parsing
- Ruff (0.8.0+) - Fast Python linter and formatter
- PyInstaller (6.10.0+) - Executable builder
- Pytest (7.4.0+) - Testing framework

## Build & Installation
```bash
# Install dependencies
poetry install

# Run the application
poetry run python main.py

# Build executable
poetry run python build_exe.py
```

## Key Features
**RFID Management**:
- Multi-protocol device support (TCP/IP, Serial, USB)
- Real-time tag reading and event processing
- Configurable antenna control and power settings
- RSSI monitoring and proximity analysis
- Automatic duplicate tag filtering
- EPC/TID validation and processing

**Web Interface**:
- Modern responsive dashboard with real-time updates
- Device status monitoring and configuration
- Live log viewing with filtering and search
- Tag simulation for testing and development
- Interactive API documentation (Swagger UI)

**Integration & API**:
- RESTful API with comprehensive endpoints
- Database integration with SQLAlchemy models
- Webhook support for external system integration
- MQTT connectivity for IoT platforms
- Prometheus metrics for monitoring
- Configurable data persistence

**Application Structure**:
**Entry Point**: main.py
**Web Framework**: FastAPI with async/await support
**Template Engine**: Jinja2 with Alpine.js reactivity
**Database ORM**: SQLAlchemy 2.0+ with Alembic migrations
**Frontend**: Tailwind CSS + Alpine.js
**Async Support**: Full async implementation with asyncio
**Monitoring**: Prometheus metrics and structured logging

## Configuration
**Main Configuration**: `config/config.json`
- Application title and port settings
- Database connection URL (SQLite/MySQL/PostgreSQL)
- Webhook integration URLs
- Logging configuration
- Device-specific settings
- MQTT broker configuration
- Storage and cleanup policies

**Device Definitions**: `config/devices/*.json`
- Individual RFID reader configurations
- Protocol-specific connection parameters
- Antenna and power settings
- Event processing rules

**Settings Management**: `app/core/config.py`
- Dynamic configuration loading
- Environment variable support
- Runtime configuration updates
- Validation and defaults

## API Endpoints
**Device Management** (`/api/v1/devices`):
- `GET /get_devices` - List all registered devices
- `GET /get_device_config/{name}` - Get device configuration
- `GET /get_device_types_list` - List supported device types
- `GET /get_device_config_example/{name}` - Get configuration examples

**RFID Operations** (`/api/v1/rfid`):
- `GET /get_tags` - Retrieve all detected tags
- `GET /get_tag_count` - Get total tag count
- `POST /clear_tags` - Clear all detected tags
- `GET /get_epcs` - Get all EPC values
- `GET /get_gtin_count` - Get GTIN statistics

**Simulation & Testing** (`/api/v1/simulator`):
- `POST /tag` - Simulate single tag event
- `POST /event` - Simulate device event
- `POST /tag_list` - Simulate multiple tags

**Web Interface**:
- `/` - Main dashboard with device status
- `/logs` - Real-time log viewing interface
- `/docs` - Interactive API documentation

## Database Models
**Tag Model** (`app/models/rfid.py`):
- Device identification
- EPC/TID data storage
- Antenna and RSSI information
- Timestamp tracking
- Unique constraints and indexing

**Event Model** (`app/models/rfid.py`):
- Device event logging
- Event type classification
- JSON data storage
- Automatic timestamping

**Base Models** (`app/models/mixin.py`):
- Common model functionality
- Serialization utilities
- Timestamp mixins
- Database session handling

## Development & Packaging
**Package Manager**: Poetry for dependency management
**Code Quality**: Ruff for linting and formatting
**Testing**: Pytest framework with async support
**Migrations**: Alembic for database schema management
**Executable Builder**: PyInstaller via `build_exe.py`
**Build Configuration**: One-file executable with embedded resources
**Included Resources**: All app directories, static files, and dependencies
