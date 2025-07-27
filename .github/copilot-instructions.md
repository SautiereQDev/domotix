# Domotix AI Coding Instructions

## Architecture Overview

Domotix is a **home automation system** built with **clean architecture patterns**. The system manages smart devices (lights, shutters, sensors) with persistent SQLite storage.

### Core Patterns (Critical Understanding)

1. **Repository + Factory Pattern**: ALL data access flows through repositories via factories
   ```python
   # ALWAYS use factories, never instantiate directly
   controller = ControllerFactory.create_light_controller(session)
   # Controllers use repositories, repositories use SQLAlchemy sessions
   ```

2. **UUID-based IDs**: Device IDs are strings (UUID4), not integers
   ```python
   # CORRECT: device_id: str
   # WRONG: device_id: int
   ```

3. **Thread-safe Singleton**: `StateManager` uses custom `SingletonMeta` metaclass
   ```python
   # Always reset in tests
   StateManager.reset_instance()
   ```

## Critical Development Patterns

### Database Session Management
```python
# MANDATORY pattern for all CLI commands
session = create_session()
try:
    controller = ControllerFactory.create_xxx_controller(session)
    # operations...
finally:
    session.close()  # NEVER forget this
```

### Type Safety Requirements
- **MyPy compliance is mandatory** (100% coverage enforced)
- Use `if obj is not None:` for Optional types (MyPy strict)
- Device IDs are always `str`, never `int`
- Controllers return `Optional[Device]` - always check for None

### Testing Conventions
- Use `StateManager.reset_instance()` at start of singleton tests
- Repository tests use in-memory SQLite (`create_tables()`)
- 157 tests, 80% coverage minimum
- Test files mirror source structure: `tests/test_<module>/`

## Key Files & Responsibilities

- `domotix/models/`: Business entities (Device, Light, Shutter, Sensor)
- `domotix/repositories/`: Data access with SQLAlchemy ORM
- `domotix/controllers/`: Business logic, use repositories via DI
- `domotix/factories.py`: **Entry point** for all object creation
- `domotix/core/database.py`: Session management (`create_session()`)
- `domotix/cli/device_cmds.py`: CLI commands with session handling

## Build & Quality Commands

```bash
# Essential workflow commands
poetry run pytest                           # Run 157 tests
poetry run mypy domotix/ --config-file pyproject.toml  # Type checking
poetry run isort domotix/                   # Import sorting
poetry run black domotix/                   # Code formatting
poetry run pre-commit run --all-files      # All quality checks
```

## Domain-Specific Rules

1. **Device Creation**: Always through controllers, never direct model instantiation
2. **CLI Error Handling**: Check if objects are None before accessing attributes
3. **Database Migrations**: No migration system - recreate tables for schema changes
4. **Enum Usage**: Import from `domotix.globals.enums` (DeviceType, DeviceState)

When adding new device types: extend Device abstract class, create specialized repository, add to factories, update CLI commands.
