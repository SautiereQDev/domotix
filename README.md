# Domotix

A comprehensive home automation system built with Python, providing a unified interface to control and monitor various smart home devices.

## 🏠 About

Domotix is a modern home automation system that allows you to control lights, shutters, sensors, and other smart home devices through a clean command-line interface and API. The system is designed with modularity, extensibility, and ease of use in mind.

## 🚀 Features

- **Device Management**: Control lights, shutters, and sensors
- **Command-Line Interface**: Easy-to-use CLI powered by Typer
- **Extensible Architecture**: Plugin-based system for adding new device types
- **Configuration Management**: YAML-based configuration files
- **Real-time Monitoring**: Track device states and sensor readings

## 🛠️ Technologies Used

- **Python 3.13+**: Core programming language
- **Typer**: Modern CLI framework
- **PyYAML**: Configuration file parsing
- **Poetry**: Dependency management and packaging

### Development Tools

- **pytest**: Testing framework
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

The Domotix CLI provides easy access to all system functions:

```bash
# Show help
domotix --help

# List all devices
domotix device list

# Control a light
domotix light turn-on living-room-light
domotix light turn-off living-room-light

# Control shutters
domotix shutter open bedroom-shutter
domotix shutter close bedroom-shutter

# Check sensor status
domotix sensor status temperature-sensor
```

### Configuration

Create a configuration file to define your devices:

```yaml
# config/devices.yaml
devices:
  lights:
    - id: living-room-light
      name: "Living Room Light"
      type: "dimmer"
      mqtt_topic: "home/lights/living-room"

  shutters:
    - id: bedroom-shutter
      name: "Bedroom Shutter"
      type: "motorized"
      mqtt_topic: "home/shutters/bedroom"

  sensors:
    - id: temperature-sensor
      name: "Living Room Temperature"
      type: "temperature"
      mqtt_topic: "home/sensors/temperature"
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
# Run all tests
pytest

# Run with coverage
pytest --cov=domotix --cov-report=html

# Run specific test file
pytest tests/test_device.py
```

### Code Quality

```bash
# Format code
black domotix/

# Sort imports
isort domotix/

# Lint code
flake8 domotix/

# Type checking
mypy domotix/

# Security analysis
bandit -r domotix/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Building Documentation

```bash
# Build Sphinx documentation
cd docs/
make html

# View documentation
open _build/html/index.html
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
- Use type hints for all functions
- Write docstrings for all public methods
- Maintain test coverage above 80%

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

- [ ] Persistant data
- [ ] Web-based dashboard
- [ ] Advanced automation rules

## 🐛 Bug Reports & Feature Requests

Please use the [GitHub Issues](https://github.com/SautiereQDev/domotix/issues) page to report bugs or request new features.
