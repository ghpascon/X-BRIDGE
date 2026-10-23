# SMARTX X-BRIDGE

## Overview

SMARTX X-BRIDGE is a high-performance RFID device management platform built with FastAPI. It acts as middleware between physical RFID readers and business systems, providing real-time tag processing, multi-device management, flexible integrations, and a built-in web interface.

---

## Features

- **Multi-device RFID management** — Connect and manage multiple readers simultaneously via TCP/IP, Serial, or USB
- **Real-time tag processing** — Duplicate filtering, EPC/TID validation, RSSI monitoring, antenna and power control
- **Tag prefix filtering** — Accept only tags matching configured prefixes
- **Integrations** — Webhook with retry, MQTT (IoT), XTRACK, and relational database persistence (SQLite, MySQL, PostgreSQL)
- **Device-aware events** — Every event carries a device descriptor (`name` and `serial_number`) plus `event_type` and `event_data`
- **Web interface** — Responsive dashboard with live updates, log viewer, and device settings
- **API** — Full RESTful API with interactive Swagger documentation
- **Simulation** — Simulate tags and events without physical hardware, including GTIN-14 generation
- **License management** — Built-in license validation
- **System tray** — Native tray icon integration
- **Prometheus metrics** — Built-in observability endpoint

---

## Project Structure

```
app/
├── async_func/       Background tasks (RFID polling, etc.)
├── core/             App factory, config, middlewares, exception handlers
├── db/               Database session and initialization
├── models/           SQLAlchemy models (Tag, Event)
├── routers/
│   ├── api/v1/       REST API endpoints
│   └── pages/        Web interface routes (dashboard, logs, settings)
├── schemas/          Pydantic schemas for validation
├── services/
│   ├── rfid/         RFID controller, event handling, integrations
│   ├── settings_service/  Dynamic config management
│   ├── license/      License validation
│   └── tray/         System tray integration
├── static/           Frontend assets (CSS, JS, images, sounds)
└── templates/        Jinja2 templates

config/
├── config.json       Main application configuration
└── devices/          Per-device RFID reader configuration files

alembic/              Database migration scripts
scripts/              Utility scripts (build, format, migrate, startup)
tests/                Unit and integration tests
docs/                 API documentation assets
```

---

## Configuration

### `config/config.json`

| Field                     | Type        | Default (code) / Example file   | Description                                                                                                                                                                      |
| ------------------------- | ----------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TITLE`                   | string      | `SMARTX` / `SMARTX`             | Application title                                                                                                                                                                |
| `PORT`                    | int         | `5000` / `5000`                 | HTTP server port                                                                                                                                                                 |
| `LOG_PATH`                | string      | `Logs` / (example path)         | Directory for log files                                                                                                                                                          |
| `DATABASE_URL`            | string      | `null` / `null`                 | SQLAlchemy DB URL (SQLite/MySQL/PostgreSQL)                                                                                                                                      |
| `WEBHOOK_URL`             | string      | `null` / `null`                 | Webhook endpoint for tag events                                                                                                                                                  |
| `XTRACK_URL`              | string      | `null` / `null`                 | XTRACK integration URL                                                                                                                                                           |
| `TAG_PREFIX`              | string/list | `null` / `null`                 | Accept only tags with this prefix (single or list)                                                                                                                               |
| `STORAGE_DAYS`            | int         | `7` / `7`                       | Days to retain tag/event records                                                                                                                                                 |
| `CLEAR_OLD_TAGS_INTERVAL` | int         | `3600 (code) / null (example)`  | Seconds between automatic tag memory clears; if set to `null` or an invalid value the application defaults to `3600` seconds (1 hour).                                           |
| `ALWAYS_SEND`             | bool        | `false` / `false`               | Forward all tags to integrations, even duplicates                                                                                                                                |
| `BEEP`                    | bool        | `false` / `false`               | Play beep sound on new tag read                                                                                                                                                  |
| `OPEN_BROWSER`            | bool        | `true (code) / false (example)` | Auto-open browser on startup. Note: the repository `config/config.json` example sets `OPEN_BROWSER` to `false`; when no config file is present the code-level default is `true`. |

### `config/devices/*.json`

Each file defines one RFID reader (protocol, antennas, read power, events, etc). See `examples/devices/` for templates covering TCP, Serial, X714, R700, XPAD, ACUPAD, and SATO readers.

## Note: The values shown under "Default (code)" are applied when no configuration file is present. The application always loads values from `config/config.json` at runtime, so edit that file to change behavior in your deployment.

## Quickstart

1. Install dependencies and start the application locally:

```bash
poetry install
poetry run python main.py
```

2. Open your browser at `http://localhost:5000` (unless `OPEN_BROWSER` is disabled in `config/config.json`).

## Installation & Running

Install dependencies and common commands:

```bash
# Install dependencies
poetry install

# Run the application (recommended)
poetry run python main.py

# Alternative (development) using uvicorn with autoreload
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Build standalone executable (requires PyInstaller)
poetry run python scripts/build_exe.py

# Run database migrations (interactive helper)
poetry run python scripts/migrate.py

# Run tests
poetry run pytest
```

### Docker

Build and run using the included `Dockerfile`:

```bash
# Build image (from repo root)
docker build -t x-bridge .

# Run container and map port 5000
docker run -it --rm -p 5000:5000 x-bridge
```

## When running in Docker you may want to mount a persistent `config/` and `Logs/` folder via `-v` mounts.

## API Groups

| Group           | Prefix                | Description                                                                                              |
| --------------- | --------------------- | -------------------------------------------------------------------------------------------------------- |
| **RFID**        | `/api/v1/rfid`        | Read tags, EPCs, TIDs, GTIN stats, clear tag memory, write EPC                                           |
| **Devices**     | `/api/v1/devices`     | List devices, get/set config, device status and info                                                     |
| **Application** | `/api/v1/application` | App settings CRUD, device config CRUD, restart/shutdown                                                  |
| **Simulator**   | `/api/v1/simulator`   | Simulate tags, events, tag lists, GTIN-14 tag generation                                                 |
| **Receive**     | `/api/v1/receive`     | Ingest tag/event data from external readers (X714, R700, XSCAN); accepts optional `device_serial_number` |
| **License**     | `/api/v1/license`     | Get license info, upload license                                                                         |
| **Controller**  | `/api/v1/controller`  | RFID controller runtime info                                                                             |
| **Dispatchers** | `/api/v1/dispatchers` | Manage dispatchers: list examples, get example content, create/update and delete dispatch configurations |

Full interactive documentation available at `/docs`.

---

## Dispatchers

Dispatchers are configurable event forwarders. They listen to RFID/runtime events and dispatch payloads to external systems using HTTP POST, SQL inserts, MQTT publishing, or MongoDB inserts.

API endpoints available at `/api/v1/dispatchers` allow listing example dispatches, retrieving example content, creating/updating, and deleting dispatch configurations at runtime.

### Locations

- **Active dispatchers**: `config/dispatchers/`
- **Ready-to-use examples**: `examples/dispatchers/`

### Supported dispatch types

| Type      | Purpose                                  |
| --------- | ---------------------------------------- |
| `post`    | Send events to external HTTP endpoints   |
| `sql`     | Persist events directly in SQL databases |
| `mqtt`    | Publish events to MQTT topics            |
| `mongodb` | Insert events into MongoDB collections   |

### Event model

Every event emitted by a device (or injected through the API) carries three parts:

| Part         | Type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| `device`     | dict   | Device descriptor: `{"name": str, "serial_number": str \| null}` |
| `event_type` | string | Event type (`tag`, `reading`, `connection`, ...)                 |
| `event_data` | any    | Event payload (dict, bool, string, number, list)                 |

The `serial_number` is `null` until the reader reports it. For events received through `/api/v1/receive/*` or `/api/v1/simulator/*`, it is taken from the request (`device_serial_number`) or, when omitted, resolved from the connected device with the same name.

Tags stored in memory also expose `device` (name) and `device_serial_number`.

The built-in webhook (`WEBHOOK_URL`) posts the same structure:

```json
{
  "device": { "name": "reader-01", "serial_number": "37100000001" },
  "event_type": "tag",
  "event_data": { "epc": "...", "tid": "...", "ant": 1, "rssi": -50 }
}
```

> **Note:** `device` is an object (previously a plain device name string). Update external consumers of the webhook accordingly.

### Common event triggers (`on_event`)

- `tag` — tag read events (dict payload with EPC/TID/ANT/RSSI/timestamp)
- `reading` — reader reading state changes (boolean payload)
- `connection` — reader connectivity state changes
- `serial_number` — serial-number oriented events
- `add_to_write_list`, `remove_from_write_list`, `write_list_empty`, `write_list_cleared` — write list events (emitted with the `write_list` system device)

### Placeholders and filters

- Placeholders are resolved at runtime:
  - `{name}` — device name
  - `{serial_number}` — device serial number
  - `{device}` — full device dict
  - `{device[key]}` — a key of the device dict (e.g. `{device[serial_number]}`)
  - `{event_type}` — event type
  - `{data}` — raw event payload
  - `{data[key]}` — a payload field (e.g. `{data[epc]}`)
- For scalar payloads (like `reading`), use `{data}`
- For dict payloads (like `tag`), use keyed placeholders such as `{data[epc]}`
- Filters can restrict dispatches by payload/device fields (`eq`, `ne`, `in`, `not_in`, `gt`, `lt`, `gte`, `lte`, `contains`)

### Example files

- `examples/dispatchers/base_post.json`, `base_sql.json`, `base_mqtt.json`, `base_mongodb.json` — annotated templates
- `examples/dispatchers/reading_post.json`, `reading_sql.json`
- `examples/dispatchers/connection_post.json`, `connection_sql.json`
- `examples/dispatchers/serial_number_post.json`, `serial_number_sql.json`
- `examples/dispatchers/write_list_empty_post.json`, `write_list_remove_post.json`

### Minimal POST example

```json
{
  "dispatch_type": "post",
  "url": "http://localhost:5001/tag",
  "on_event": "tag",
  "allow_batches": true,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "device": "{name}",
    "device_serial_number": "{device[serial_number]}",
    "event_type": "{event_type}",
    "epc": "{data[epc]}"
  }
}
```

### Minimal SQL example

```json
{
  "dispatch_type": "sql",
  "connection_string": "postgresql+asyncpg://user:password@localhost:5432/mydatabase",
  "on_event": "reading",
  "query": "INSERT INTO device_reading_events (device, device_serial_number, is_reading) VALUES (:device, :device_serial_number, :is_reading)",
  "params": {
    "device": "{name}",
    "device_serial_number": "{device[serial_number]}",
    "is_reading": "{data}"
  }
}
```

---

## Tech Stack

| Layer           | Technology                        |
| --------------- | --------------------------------- |
| Runtime         | Python >=3.11, <3.15              |
| Package manager | Poetry                            |
| Web framework   | FastAPI + Uvicorn                 |
| Database ORM    | SQLAlchemy + Alembic              |
| Templates       | Jinja2                            |
| RFID layer      | smartx-rfid (13.0.0)              |
| MQTT            | gmqtt                             |
| Metrics         | prometheus-fastapi-instrumentator |
| Auth            | passlib[bcrypt] + itsdangerous    |
| Tray            | pystray + Pillow                  |
| Audio           | pygame                            |
| Linter          | Ruff                              |
| Testing         | Pytest                            |
| Build           | PyInstaller                       |

---

## Contributing

See `CONTRIBUTING.md` for development setup, testing, and code-style guidelines.
