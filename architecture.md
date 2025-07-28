# Architecture and technicals instruction about domotix

## 🏗️ Detailed Architecture

### Layer Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    🎯 CLI Layer (Typer)                     │
│                 domotix/cli/ + commands/                    │
├─────────────────────────────────────────────────────────────┤
│                 💼 Business Layer                           │
│              Controllers + Core Services                    │
├─────────────────────────────────────────────────────────────┤
│                 🏭 Factory Layer                            │
│            Dependency Injection + Object Creation           │
├─────────────────────────────────────────────────────────────┤
│                 📋 Repository Layer                         │
│               Data Access + Persistence                     │
├─────────────────────────────────────────────────────────────┤
│                 📊 Data Layer                               │
│            SQLAlchemy Models + Database                     │
└─────────────────────────────────────────────────────────────┘
```

### Implemented Design Patterns

#### 1. **Repository Pattern** 🗄️

```python
# Clear separation between business logic and data access
class LightRepository(BaseRepository[Light]):
    def find_lights_by_location(self, location: str) -> List[Light]:
        return self.session.query(Light).filter_by(location=location).all()

    def find_on_lights(self) -> List[Light]:
        return self.session.query(Light).filter_by(is_on=True).all()
```

#### 2. **Factory Pattern** 🏭

```python
# Centralized dependency injection
class ControllerFactory:
    @staticmethod
    def create_light_controller(session: Session) -> LightController:
        repository = LightRepository(session)
        return LightController(repository)
```

#### 3. **Singleton Pattern** 🔒

```python
# Thread-safe state management with custom metaclass
class StateManager(metaclass=SingletonMeta):
    def __init__(self):
        self._devices: Dict[str, Device] = {}
        self._lock = threading.Lock()
```

#### 4. **Command Pattern** ⚡

```python
# Encapsulation of device operations
class TurnOnCommand(Command):
    def __init__(self, device: Light):
        self.device = device

    def execute(self) -> None:
        self.device.turn_on()
```

### Module Structure

```text
domotix/
├── 🎯 cli/                    # Command-line interface
│   ├── main.py               # Main CLI entry point
│   ├── device_cmds.py        # Device management commands
│   ├── lumiere_cmds.py       # Light-specific commands
│   └── volet_cmds.py         # Shutter-specific commands
├── ⚡ commands/               # Command Pattern
│   ├── turn_on.py            # Turn on command
│   ├── turn_off.py           # Turn off command
│   ├── open_shutter.py       # Open shutter command
│   └── close_shutter.py      # Close shutter command
├── 💼 controllers/           # Business logic
│   ├── device_controller.py  # Generic controller
│   ├── light_controller.py   # Light controller
│   ├── sensor_controller.py  # Sensor controller
│   └── shutter_controller.py # Shutter controller
├── 🏭 core/                  # Core services
│   ├── database.py           # DB session management
│   ├── factories.py          # Modern factory patterns
│   ├── state_manager.py      # State management singleton
│   ├── singleton.py          # Thread-safe singleton metaclass
│   └── dependency_injection.py # Advanced DI system
├── 🌐 globals/               # Constants and enumerations
│   ├── enums.py              # DeviceType, DeviceState, CommandType
│   └── exceptions.py         # Custom business exceptions
├── 📊 models/                # Business entities + ORM
│   ├── device_model.py       # Abstract base model
│   ├── light.py              # Light model
│   ├── sensor.py             # Sensor model
│   └── shutter.py            # Shutter model
└── 📋 repositories/          # Data access layer
    ├── device_repository.py  # Generic repository
    ├── light_repository.py   # Light repository
    ├── sensor_repository.py  # Sensor repository
    └── shutter_repository.py # Shutter repository
```

## 🛡️ Security and Reliability Patterns

### Database Session Management

```python
# ✅ CORRECT: Recommended pattern
def safe_database_operation():
    session = create_session()
    try:
        controller = ControllerFactory.create_light_controller(session)
        # Operations...
        session.commit()  # Explicit commit if needed
    except Exception as e:
        session.rollback()  # Rollback on error
        raise
    finally:
        session.close()  # ALWAYS close

# 🎯 OPTIMAL: With context manager
def optimal_database_operation():
    with create_session() as session:
        controller = ControllerFactory.create_light_controller(session)
        # Session automatically closed
```

### Error Handling

```python
from domotix.globals.exceptions import (
    DeviceNotFoundError,
    ValidationError,
    ControllerError
)

def robust_device_control(device_id: str):
    try:
        with create_session() as session:
            controller = ControllerFactory.create_light_controller(session)
            light = controller.get_light(device_id)

            if light is None:
                raise DeviceNotFoundError(device_id)

            return controller.turn_on(device_id)

    except DeviceNotFoundError as e:
        print(f"❌ Device not found: {e.device_id}")
    except ValidationError as e:
        print(f"❌ Invalid data: {e}")
    except ControllerError as e:
        print(f"❌ Controller error: {e}")
```

### Thread Safety

```python
from domotix.core.state_manager import StateManager

# 🔒 Thread-safe singleton
def thread_safe_state_management():
    StateManager.reset_instance()  # Reset for tests
    manager = StateManager()       # Thread-safe singleton

    # Thread-safe operations
    light = Light("Test", "Room")
    manager.register_device(light)
    device = manager.get_device(light.id)
```

## 🔧 Advanced Configuration

### Environment Variables

```bash
# 🗄️ Database Configuration
export DATABASE_URL="sqlite:///./domotix.db"          # SQLite (default)
export DATABASE_URL="postgresql://user:pass@localhost/domotix"  # PostgreSQL
export DATABASE_URL="mysql://user:pass@localhost/domotix"       # MySQL

# 🔧 Application Configuration
export DOMOTIX_DEBUG=true                     # Debug mode
export DOMOTIX_LOG_LEVEL=INFO                 # Log level
export DOMOTIX_CONFIG_PATH=/path/to/config    # Configuration path

# 🔒 Security Configuration
export DOMOTIX_SECRET_KEY=your-secret-key     # Secret key
export DOMOTIX_ENCRYPTION_KEY=encryption-key  # Encryption key
```

### Configuration File

```yaml
# config/domotix.yaml
database:
  url: "sqlite:///./domotix.db"
  echo: false
  pool_size: 5

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/domotix.log"

devices:
  auto_discovery: true
  timeout: 30
  retry_attempts: 3

security:
  api_key_required: false
  rate_limiting: true
  max_requests_per_minute: 100
```

## 🚀 Extensibility and Plugins

### Adding a New Device Type

```python
# 1. 📊 Create the model
from domotix.models.device_model import Device

class SmartThermostat(Device):
    def __init__(self, name: str, location: str):
        super().__init__(name, DeviceType.THERMOSTAT, location)
        self.target_temperature: float = 20.0
        self.current_temperature: float = 18.0

    def set_target_temperature(self, temp: float) -> None:
        if 5.0 <= temp <= 35.0:
            self.target_temperature = temp
        else:
            raise ValidationError("Temperature out of range")

# 2. 📋 Create the repository
class ThermostatRepository(BaseRepository[SmartThermostat]):
    def find_by_target_temp_range(self, min_temp: float, max_temp: float):
        return self.session.query(SmartThermostat).filter(
            SmartThermostat.target_temperature.between(min_temp, max_temp)
        ).all()

# 3. 💼 Create the controller
class ThermostatController:
    def __init__(self, repository: ThermostatRepository):
        self.repository = repository

    def create_thermostat(self, name: str, location: str) -> SmartThermostat:
        thermostat = SmartThermostat(name, location)
        return self.repository.save(thermostat)

    def set_temperature(self, device_id: str, temperature: float) -> bool:
        thermostat = self.repository.find_by_id(device_id)
        if thermostat:
            thermostat.set_target_temperature(temperature)
            self.repository.update(thermostat)
            return True
        return False

# 4. 🏭 Add to factory
class ControllerFactory:
    @staticmethod
    def create_thermostat_controller(session: Session) -> ThermostatController:
        repository = ThermostatRepository(session)
        return ThermostatController(repository)
```

### Plugin System

```python
# Plugin interface
from abc import ABC, abstractmethod

class DevicePlugin(ABC):
    @abstractmethod
    def get_device_type(self) -> str:
        pass

    @abstractmethod
    def create_device(self, name: str, location: str) -> Device:
        pass

    @abstractmethod
    def get_controller_class(self) -> type:
        pass

# Plugin registry
class PluginRegistry:
    _plugins: Dict[str, DevicePlugin] = {}

    @classmethod
    def register(cls, plugin: DevicePlugin):
        cls._plugins[plugin.get_device_type()] = plugin

    @classmethod
    def get_plugin(cls, device_type: str) -> DevicePlugin:
        return cls._plugins.get(device_type)

# Usage
@PluginRegistry.register
class ThermostatPlugin(DevicePlugin):
    def get_device_type(self) -> str:
        return "THERMOSTAT"

    def create_device(self, name: str, location: str) -> SmartThermostat:
        return SmartThermostat(name, location)

    def get_controller_class(self) -> type:
        return ThermostatController
```
