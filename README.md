# Domotix

A comprehensive home automation system built with Python, providing a unified interface to control and monitor various smart home devices with persistent data storage.

## 🏠 About

Domotix is a modern home automation system that allows you to control lights, shutters, sensors, and other smart home devices through a clean command-line interface and API. The system is designed with modularity, extensibility, data persistence, and ease of use in mind.

## 🚀 Features

- **Device Management**: Control lights, shutters, and sensors with persistent state
- **Data Persistence**: SQLite database with SQLAlchemy ORM for reliable data storage
- **Command-Line Interface**: Easy-to-use CLI powered by Typer
- **Repository Pattern**: Clean separation of business logic and data access
- **Factory Pattern**: Organized dependency injection and object creation
- **Extensible Architecture**: Plugin-based system for adding new device types
- **Real-time Monitoring**: Track device states and sensor readings
- **UUID-based IDs**: Unique identification for all devices
- **Type Safety**: Full mypy type checking for reliability

## 🛠️ Technologies Used

- **Python 3.13+**: Core programming language
- **Typer**: Modern CLI framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Default database engine (configurable)
- **PyYAML**: Configuration file parsing (optional)
- **UUID**: Unique device identification
- **Poetry**: Dependency management and packaging

### Architecture Patterns

- **Repository Pattern**: Data access abstraction
- **Factory Pattern**: Object creation and dependency injection
- **Singleton Pattern**: State management
- **Command Pattern**: Device operations

### Development Tools

- **pytest**: Testing framework with 157 tests and 80% coverage
- **Black**: Code formatting
- **Flake8**: Code linting
- **isort**: Import sorting
- **mypy**: Static type checking
- **Bandit**: Security analysis
- **pre-commit**: Git hooks for code quality
- **Sphinx**: Documentation generation

## 📦 Installation

### Prerequisites

- Python 3.13 or higher
- Poetry

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/SautiereQDev/domotix.git
cd domotix

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/SautiereQDev/domotix.git
cd domotix

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## 🎯 Usage

### Command Line Interface

The Domotix CLI provides easy access to all system functions with persistent data storage:

```bash
# Show help
domotix --help

# Create devices (stored in database)
domotix device create light "Living Room Light" --location "Living Room"
domotix device create shutter "Bedroom Shutter" --location "Bedroom"
domotix device create sensor "Temperature Sensor" --location "Living Room"

# List all devices
domotix device list

# Show specific device
domotix device show <device-id>

# Control a light
domotix device turn-on <light-id>
domotix device turn-off <light-id>

# Control shutters
domotix device open <shutter-id>
domotix device close <shutter-id>

# Update sensor values
domotix device update-sensor <sensor-id> 22.5

# Search devices
domotix device search "Living Room"
```

### Database Configuration

The system uses SQLite by default, but can be configured with environment variables:

```bash
# Default SQLite database
export DATABASE_URL="sqlite:///./domotix.db"

# PostgreSQL example
export DATABASE_URL="postgresql://user:password@localhost/domotix"

# MySQL example
export DATABASE_URL="mysql://user:password@localhost/domotix"
```

### Architecture Overview

```
domotix/
├── cli/              # Command-line interface
├── commands/         # Command pattern implementations
├── controllers/      # Business logic controllers
├── core/            # Core functionality (database, singletons)
├── factories.py     # Factory pattern for object creation
├── globals/         # Enums and exceptions
├── models/          # Business entities and persistence models
└── repositories/    # Data access layer
```

### Programmatic Usage

You can also use Domotix programmatically with the factory pattern:

```python
from domotix.factories import get_light_controller, get_device_controller

# Get controllers
light_controller = get_light_controller()
device_controller = get_device_controller()

# Create and control devices
light = light_controller.create_light("Kitchen Light", "Kitchen")
light_controller.turn_on(light.id)

# List all devices
devices = device_controller.get_all_devices()
for device in devices:
    print(f"{device.name}: {device.get_status()}")
```

## 🏗️ Architecture

### Core Components

1. **Models**: Business entities (Device, Light, Shutter, Sensor)
2. **Repositories**: Data access layer with SQLAlchemy
3. **Controllers**: Business logic and operations
4. **Factories**: Dependency injection and object creation
5. **CLI**: Command-line interface with Typer

### Database Schema

```sql
CREATE TABLE devices (
    id VARCHAR(36) PRIMARY KEY,  -- UUID
    name VARCHAR(255) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    location VARCHAR(255),
    is_on BOOLEAN,              -- For lights
    is_open BOOLEAN,            -- For shutters
    value FLOAT                 -- For sensors
);
```

### Repository Pattern

The system uses the Repository pattern for clean data access:

```python
# Each device type has its specialized repository
device_repo = DeviceRepository(session)
light_repo = LightRepository(session)
shutter_repo = ShutterRepository(session)
sensor_repo = SensorRepository(session)

# CRUD operations
device = light_repo.save(light)
light = light_repo.find_by_id(device_id)
lights = light_repo.find_lights_by_location("Living Room")
```

## 🧪 Development

### Setting up Development Environment

```bash
# Clone and install
git clone https://github.com/SautiereQDev/domotix.git
cd domotix
poetry install --with dev

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests (157 tests with 80% coverage)
pytest

# Run with coverage report
pytest --cov=domotix --cov-report=html

# Run specific test categories
pytest tests/test_repositories/
pytest tests/test_controllers/
pytest tests/test_integration/

# Run with verbose output
pytest -xvs
```

### Code Quality

```bash
# Format code
black domotix/

# Sort imports
isort domotix/

# Lint code
flake8 domotix/

# Type checking (100% mypy compliant)
mypy domotix/ --config-file pyproject.toml

# Security analysis
bandit -r domotix/

# Run all pre-commit hooks
pre-commit run --all-files

# Run all quality checks
poetry run black domotix/
poetry run isort domotix/
poetry run flake8 domotix/
poetry run mypy domotix/ --config-file pyproject.toml
poetry run bandit -r domotix/
```

### Building Documentation

```bash
# Build Sphinx documentation
cd docs/
make html

# View documentation
open _build/html/index.html
```

### UML Documentation

The project includes comprehensive UML diagrams located in `docs/uml/`:

- **Class Diagram**: System architecture and relationships
- **Sequence Diagram**: Device operation workflows
- **State Diagram**: Device state transitions
- **Component Diagram**: System modules and dependencies
- **Deployment Diagram**: System deployment architecture
- **Use Case Diagram**: User interactions and scenarios
- **Activity Diagram**: Business process flows

View all diagrams: [docs/uml/README.md](docs/uml/README.md)

## 📊 Examples

### Complete Device Lifecycle

```bash
# Create devices
domotix device create light "Living Room Main Light" --location "Living Room"
# Output: ✅ Lampe 'Living Room Main Light' créée avec l'ID: abc123-...

domotix device create sensor "Temperature Sensor" --location "Living Room"
# Output: ✅ Capteur 'Temperature Sensor' créé avec l'ID: def456-...

# List all devices
domotix device list
# Output:
# 🏠 Dispositifs enregistrés (2):
# 📱 Living Room Main Light (ID: abc123-...) - Light - Living Room - OFF
# 📱 Temperature Sensor (ID: def456-...) - Sensor - Living Room - Inactive

# Control devices
domotix device turn-on abc123-...
# Output: ✅ Lampe abc123-... allumée.

domotix device update-sensor def456-... 22.5
# Output: ✅ Capteur def456-... mis à jour avec la valeur 22.5.

# Show device details
domotix device show abc123-...
# Output:
# 📱 Living Room Main Light
#    ID: abc123-...
#    Type: Light
#    Emplacement: Living Room
#    Statut: ON
```

### Python API Usage

```python
from domotix.factories import (
    get_light_controller,
    get_sensor_controller,
    get_device_controller
)

# Initialize controllers
light_ctrl = get_light_controller()
sensor_ctrl = get_sensor_controller()
device_ctrl = get_device_controller()

# Create and manage lights
light = light_ctrl.create_light("Bedroom Light", "Bedroom")
print(f"Created light: {light.id}")

# Turn on/off
success = light_ctrl.turn_on(light.id)
if success:
    print("Light turned on!")

# Create and manage sensors
sensor = sensor_ctrl.create_sensor("Humidity Sensor", "Bathroom")
sensor_ctrl.update_value(sensor.id, 65.2)

# Get all devices
all_devices = device_ctrl.get_all_devices()
for device in all_devices:
    print(f"{device.name}: {device.get_status()}")

# Search devices
living_room_devices = device_ctrl.search_devices("Living Room")
print(f"Found {len(living_room_devices)} devices in Living Room")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality checks pass
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 style guide
- Use type hints for all functions (100% mypy coverage)
- Write comprehensive docstrings for all public methods
- Maintain test coverage above 80% (currently 80%)
- Follow Repository and Factory patterns
- Use meaningful variable and function names
- Write integration tests for all major features

## 📄 License

This project is licensed under the Apache 2 License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Quentin Sautiere**

- Email: contact@quentinsautiere.com
- GitHub: [@SautiereQDev](https://github.com/SautiereQDev)

## 🙏 Acknowledgments

- Typer for making CLI development enjoyable
- The Python community for the amazing ecosystem

## 📈 Roadmap

- [x] ✅ **Persistent data storage** (SQLAlchemy + SQLite)
- [x] ✅ **Repository pattern** for clean data access
- [x] ✅ **Factory pattern** for dependency injection
- [x] ✅ **UUID-based device IDs** for uniqueness
- [x] ✅ **Comprehensive testing** (157 tests, 80% coverage)
- [x] ✅ **Type safety** (100% mypy compliance)
- [ ] 🔄 **Web-based dashboard** (React/Vue.js frontend)
- [ ] 🔄 **REST API** (FastAPI backend)
- [ ] 🔄 **MQTT integration** for IoT devices
- [ ] 🔄 **Advanced automation rules** and scheduling
- [ ] 🔄 **Plugin system** for third-party devices
- [ ] 🔄 **Docker deployment** support
- [ ] 🔄 **Multi-database support** (PostgreSQL, MySQL)

## 🐛 Bug Reports & Feature Requests

Please use the [GitHub Issues](https://github.com/SautiereQDev/domotix/issues) page to report bugs or request new features.
