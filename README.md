# Feature Flag Service

A lightweight REST API for managing feature flags, built with Python, FastAPI, and SQLite.

## 1. Problem Statement

Applications often need to enable or disable features without changing their source code. This service provides an API to create feature flags, update their status, retrieve flags, and evaluate whether a feature is enabled.

Unknown feature flags evaluate to `false` by default.

## 2. Technologies Used

- **Python** — application logic
- **FastAPI** — REST API framework
- **SQLite** — persistent database storage
- **Pydantic** — request validation
- **Pytest** — automated testing

## 3. Features

- Create feature flags with optional initial states
- List all feature flags
- Enable or disable existing flags
- Evaluate individual flags
- Reject duplicate flag names
- Validate flag names
- Return appropriate HTTP error codes
- Persist flag data across application restarts
- Automated tests for core behaviour

## 4. Project Setup

### Prerequisites

- Python 3.10 or newer
- pip

### Install dependencies

Activate your virtual environment, then run:

```bash
python -m pip install -r requirements.txt
```

### Start the application

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## 5. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/flags` | Create a feature flag |
| GET | `/flags` | List all flags |
| PATCH | `/flags/{name}` | Enable or disable a flag |
| GET | `/flags/{name}/evaluate` | Evaluate a flag |

## 6. Example Requests

### Create a flag

```json
{
  "name": "dark_mode",
  "enabled": false
}
```

Send this JSON using `POST /flags`.

### Enable a flag

Send this JSON using `PATCH /flags/dark_mode`:

```json
{
  "enabled": true
}
```

### Evaluate a flag

Send a `GET` request to `/flags/dark_mode/evaluate`.

Example response:

```json
{
  "name": "dark_mode",
  "enabled": true
}
```

An unknown flag returns `enabled: false`.

## 7. Error Handling

- `409 Conflict` — a flag already exists
- `404 Not Found` — attempting to update a missing flag
- `422 Unprocessable Entity` — invalid request data

## 8. Run Automated Tests

```bash
python -m pytest tests -v
```

The test suite covers creation, duplicate handling, validation, updates, evaluation, missing flags, and persistence across application restarts.

## 9. Database

SQLite stores feature flags in `feature_flags.db`. The database is created automatically when the application starts.

## 10. Future Improvements

- Add authentication and role-based access
- Add bulk flag operations
- Add structured logging
- Add API integration tests and continuous integration
