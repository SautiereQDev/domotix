# 🏠 Domotix

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/Poetry-2.1.3-blue.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> **Modern home automation system** designed with clean architecture, proven patterns, and robust test coverage.

Domotix is a comprehensive home automation system developed in Python that allows you to control and monitor smart home devices (lights, shutters, sensors) through a modern command-line interface and programmatic API.

## 🎯 Key Features

- **🏗️ Clean Architecture**: Clear separation between business, data, and presentation layers
- **🔒 Type Safety**: 100% MyPy coverage for reliability
- **🧪 Test-Driven**: 229 tests with rigorous TDD approach
- **🔄 Proven Patterns**: Repository, Factory, Singleton, Command
- **📦 Modularity**: Extensible and maintainable architecture
- **⚡ Performance**: Optimized session management and thread-safety

## 🚀 Quick Start

### Installation

```bash
# 📥 Clone repository
git clone https://github.com/SautiereQDev/domotix.git
cd domotix

# 🔧 Install with Poetry
poetry install
poetry shell

# 🗄️ Initialize database
poetry run python -c "from domotix.core.database import create_tables; create_tables()"
```

### Basic Usage

```bash
# 📋 General help
domotix --help

# 💡 Light management
domotix device create light "Living Room Light" --location "Living Room"
domotix device turn-on <device-id>
domotix device list

# 🪟 Shutter management
domotix device create shutter "Main Shutter" --location "Living Room"
domotix volet open <device-id>

# 🌡️ Sensor management
domotix device create sensor "Temperature Sensor" --location "Kitchen"
domotix device summary
```

## 📚 Documentation

### Detailed Documentation

- **[🏗️ Architecture Guide](architecture.md)** - Detailed system architecture, design patterns, security patterns, and extensibility
- **[🧪 Testing Guide](testing.md)** - Comprehensive testing strategy, tools, and best practices
- **[🔧 Development Guide](CONTRIBUTING.md)** - Contribution workflow, code standards, and development setup

### Quick References

| Topic | Description | Link |
|-------|-------------|------|
| **Architecture** | Design patterns, module structure, security patterns | [architecture.md](architecture.md) |
| **Testing** | 229 tests, coverage, TDD approach, tools | [testing.md](testing.md) |
| **API Reference** | Complete API documentation | [docs/](docs/) |
| **Examples** | Usage scenarios and code examples | [examples/](examples/) |

## 🧪 Quality Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|---------|
| **Tests** | 229 | 200+ | ✅  Achieved |
| **Coverage** | 41% (80%+ on main modules) | 80% | 🟨 Improving |
| **MyPy** | 100% | 100% | ✅ Achieved |
| **Type Safety** | 100% | 100% | ✅ Achieved |

## 🛠️ Development

### Essential Commands

```bash
# 🧪 Testing and Quality
poetry run pytest                    # Run tests
poetry run pytest --cov=domotix     # With coverage
poetry run black domotix/           # Format code
poetry run mypy domotix/             # Type checking
poetry run pre-commit run --all-files  # All quality checks
```

## 📈 Roadmap

### Current Version: 0.1.0 (Beta)
- [X] Complete core features (devices, CLI, persistence)
- [X] Clean architecture implementation
- [X] 100% type safety

### Next Versions
- [ ] FastAPI REST API
- [ ] Web interface
- [ ] MQTT support

## 🤝 Contributing

We welcome contributions! Please see our [Contribution Guide](CONTRIBUTING.md) for development workflow and code standards.

```bash
# Quick contribution setup
git clone https://github.com/SautiereQDev/domotix.git
cd domotix
poetry install --with dev
poetry run pre-commit install
```

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**🧑‍💻 Quentin Sautiere** - *Lead Developer & Architect*
- 📧 Email: [contact@quentinsautiere.com](mailto:contact@quentinsautiere.com)
- 🐙 GitHub: [@SautiereQDev](https://github.com/SautiereQDev)
- 💼 LinkedIn: [Quentin Sautiere](https://linkedin.com/in/quentin-sautiere)

---

<div align="center">
<br/>

**🏠 Domotix - Smart Home, Smart Code 🏠**

*Developed with ❤️ by [Quentin Sautiere](https://github.com/SautiereQDev)*

[![Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://python.org)
[![Poetry](https://img.shields.io/badge/Managed%20with-Poetry-blue.svg)](https://python-poetry.org)
[![Apache License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)

</div>
