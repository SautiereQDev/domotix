# 🤝 Contributing to Domotix

Thank you for your interest in contributing to Domotix! This guide will help you get started with contributing to our home automation system.

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Code Standards](#-code-standards)
- [Testing Guidelines](#-testing-guidelines)
- [Documentation](#-documentation)
- [Submitting Changes](#-submitting-changes)
- [Release Process](#-release-process)

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

### Our Standards

- **Respectful Communication**: Be considerate and respectful in discussions
- **Constructive Feedback**: Provide helpful and constructive feedback
- **Inclusive Language**: Use inclusive language and be mindful of diverse perspectives
- **Collaborative Spirit**: Work together toward common goals

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** (latest features support)
- **Poetry** (for dependency management)
- **Git** (for version control)

### Fork and Clone

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork locally
git clone https://github.com/your-username/domotix.git
cd domotix

# 3. Add upstream remote
git remote add upstream https://github.com/SautiereQDev/domotix.git
```

### Development Environment Setup

```bash
# Install dependencies
poetry install --with dev

# Activate virtual environment
poetry shell

# Install pre-commit hooks
poetry run pre-commit install

# Initialize database
poetry run python -c "from domotix.core.database import create_tables; create_tables()"

# Verify installation
poetry run domotix --help
```

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
# Update your main branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow our [coding standards](#-code-standards) and ensure your changes align with the project architecture.

### 3. Test Your Changes

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=domotix --cov-report=term-missing

# Run specific test files
poetry run pytest tests/test_your_module.py -v
```

### 4. Quality Checks

```bash
# Code formatting
poetry run black domotix/
poetry run isort domotix/

# Type checking
poetry run mypy domotix/ --config-file pyproject.toml

# Linting
poetry run flake8 domotix/

# Security check
poetry run bandit -r domotix/

# Run all pre-commit hooks
poetry run pre-commit run --all-files
```

### 5. Commit and Push

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add new device type support"

# Push to your fork
git push origin feature/your-feature-name
```

## 📏 Code Standards

### Style Guidelines

We follow strict coding standards to maintain code quality and consistency:

#### Code Formatting

```bash
# Use Black for formatting (line length 88)
poetry run black domotix/ --line-length 88

# Use isort for import sorting
poetry run isort domotix/ --profile black
```

#### Type Safety (100% Required)

```python
# ✅ CORRECT: All functions must have type hints
def create_device(self, name: str, location: str) -> Optional[Device]:
    """Create a new device with proper typing."""
    pass

# ❌ INCORRECT: Missing type hints
def create_device(name, location):
    pass
```

#### Architecture Patterns

Follow the established architecture patterns:

```python
# ✅ CORRECT: Use Factory pattern
session = create_session()
try:
    controller = ControllerFactory.create_light_controller(session)
    # operations...
finally:
    session.close()

# ✅ OPTIMAL: Use context manager
with create_session() as session:
    controller = ControllerFactory.create_light_controller(session)
    # Session automatically closed
```

### Naming Conventions

- **Classes**: PascalCase (`LightController`, `DeviceRepository`)
- **Functions/Methods**: snake_case (`create_device`, `turn_on`)
- **Variables**: snake_case (`device_id`, `light_controller`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`, `MAX_RETRIES`)
- **Files**: snake_case (`device_controller.py`, `light_repository.py`)

### Documentation Requirements

```python
def create_device(self, name: str, location: str) -> Optional[Device]:
    """
    Create a new device in the system.

    Args:
        name: Descriptive name of the device (1-100 characters)
        location: Room or zone where the device is located

    Returns:
        Created device instance or None if creation failed

    Raises:
        ValidationError: If name or location is invalid
        ControllerError: If database operation fails

    Example:
        >>> controller = ControllerFactory.create_light_controller(session)
        >>> light = controller.create_device("Living Room LED", "Living Room")
        >>> print(f"Created: {light.name} ({light.id})")
    """
```

### Additional Best Practices

For comprehensive Python best practices, refer to this excellent guide: **[A Guide of Best Practices for Python](https://gist.github.com/ruimaranhao/4e18cbe3dad6f68040c32ed6709090a3)**

This guide covers essential topics including:

- **General Development Guidelines** (following PEP 20 principles)
- **Naming Conventions** (variables, classes, methods)
- **Code Style** (indentation, imports, documentation)
- **Python-specific Best Practices** (list comprehensions, context managers, etc.)

Key principles from this guide that align with Domotix standards:

- **"Explicit is better than implicit"** - Clear, readable code
- **"Readability counts"** - Self-documenting code over excessive comments
- **Consistent naming** and **proper imports** organization
- **Use of context managers** (`with` statements) for resource management

## 🧪 Testing Guidelines

### Testing Philosophy

Domotix follows **Test-Driven Development (TDD)** with comprehensive test coverage:

```text
    🔺 E2E Tests (5-10%)
    🔺🔺 Integration Tests (20-30%)
  🔺🔺🔺 Unit Tests (60-70%)
```

### Writing Tests

#### Unit Tests (Required for all public methods)

```python
def test_create_light_success():
    """Test successful light creation."""
    with create_session() as session:
        controller = ControllerFactory.create_light_controller(session)
        light = controller.create_light("Test Light", "Test Room")

        assert light is not None
        assert light.name == "Test Light"
        assert light.location == "Test Room"
        assert isinstance(light.id, str)

def test_create_light_invalid_name():
    """Test light creation with invalid name."""
    with create_session() as session:
        controller = ControllerFactory.create_light_controller(session)

        with pytest.raises(ValidationError):
            controller.create_light("", "Test Room")
```

#### Integration Tests (Required for workflows)

```python
def test_full_device_lifecycle():
    """Test complete device lifecycle."""
    with create_session() as session:
        controller = ControllerFactory.create_light_controller(session)

        # Creation
        light = controller.create_light("Integration Test", "Test Room")
        assert light is not None

        # Control
        assert controller.turn_on(light.id) is True
        assert controller.turn_off(light.id) is True

        # Retrieval
        retrieved = controller.get_light(light.id)
        assert retrieved is not None
        assert retrieved.name == "Integration Test"
```

#### Test Organization

```text
tests/
├── test_models/              # Model unit tests
├── test_controllers/         # Controller unit tests
├── test_repositories/        # Repository unit tests
├── test_cli/                 # CLI unit tests
├── test_integration/         # Integration tests
└── conftest.py              # Test configuration
```

### Test Requirements

- **Minimum 80% coverage** for new code
- **All public methods** must have unit tests
- **Critical workflows** must have integration tests
- **Use proper fixtures** for test data
- **Mock external dependencies** appropriately

## 📚 Documentation

### Code Documentation

- **All public classes and methods** must have docstrings
- **Use Google-style docstrings** with Args, Returns, Raises
- **Include examples** for complex functions
- **Document architectural decisions** in code comments

### Architecture Documentation

When adding new features, update relevant documentation:

- **[architecture.md](architecture.md)** - For design patterns and technical architecture
- **[testing.md](testing.md)** - For testing strategies and tools
- **API docs** - Auto-generated from docstrings

### Documentation Generation

```bash
# Generate Sphinx documentation
cd docs/
poetry run make html

# View locally
open _build/html/index.html
```

## 📝 Submitting Changes

### Pull Request Process

1. **Create Feature Branch** from `develop`
2. **Make Changes** following our standards
3. **Add/Update Tests** for your changes
4. **Update Documentation** if needed
5. **Run Quality Checks** and ensure they pass
6. **Submit Pull Request** with clear description

### Pull Request Template

```markdown
## Description
Brief description of the changes and why they're needed.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Code coverage maintained/improved

## Quality Checks
- [ ] Code formatted with Black
- [ ] Imports sorted with isort
- [ ] Type checking passes (MyPy 100%)
- [ ] Linting passes (flake8)
- [ ] Security check passes (bandit)
- [ ] Pre-commit hooks pass

## Documentation
- [ ] Code is documented (docstrings)
- [ ] Architecture docs updated if needed
- [ ] README updated if needed

## Additional Notes
Any additional information or context.
```

### Review Process

1. **Automated Checks** must pass (CI/CD pipeline)
2. **Code Review** by maintainers
3. **Testing** on different environments
4. **Documentation Review** if applicable
5. **Approval** and merge to `develop`

## 🚀 Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features

### Release Checklist

- [ ] All tests pass on `develop`
- [ ] Documentation updated
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG updated
- [ ] Create release branch
- [ ] Final testing
- [ ] Merge to `main`
- [ ] Tag release
- [ ] Deploy to production

## 🆘 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussions
- **Email**: [contact@quentinsautiere.com](maito:contact@quentinsautiere.com) (for sensitive issues)

### Additional Resources

- **[Python Best Practices Guide](https://gist.github.com/ruimaranhao/4e18cbe3dad6f68040c32ed6709090a3)** - Comprehensive Python development guidelines
- **[PEP 8](https://www.python.org/dev/peps/pep-0008/)** - Official Python Style Guide
- **[PEP 20](https://www.python.org/dev/peps/pep-0020/)** - The Zen of Python

### Issue Templates

#### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. See error

**Expected Behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.12.1]
- Domotix version: [e.g., 0.1.0]

**Additional Context**
Any other relevant information.
```

#### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature you'd like to see.

**Use Case**
Why would this feature be useful?

**Proposed Solution**
How would you like this feature to work?

**Alternatives Considered**
Alternative solutions you've considered.

**Additional Context**
Any other relevant information.
```

## 🙏 Recognition

### Contributors

We recognize and appreciate all contributions:

- **Code Contributors**: Listed in `CONTRIBUTORS.md`
- **Documentation Contributors**: Credited in docs
- **Issue Reporters**: Acknowledged in changelogs
- **Community Helpers**: Recognized in discussions

### How to Get Recognized

- **Consistent contributions** to code, docs, or community
- **Help other contributors** in discussions
- **Report and help fix bugs**
- **Improve documentation** and examples

## 📄 License

By contributing to Domotix, you agree that your contributions will be licensed under the Apache License 2.0.

---

## 📞 Contact

**🧑‍💻 Quentin Sautiere** - *Lead Developer & Maintainer*

- 📧 Email: [contact@quentinsautiere.com](mailto:contact@quentinsautiere.com)
- 🐙 GitHub: [@SautiereQDev](https://github.com/SautiereQDev)
- 💼 LinkedIn: [Quentin Sautiere](https://linkedin.com/in/quentin-sautiere)

---

<div align="center">

**Thank you for contributing to Domotix! 🏠💝**

*Let's build the future of home automation together*

</div>
