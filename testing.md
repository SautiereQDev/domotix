## 🧪 Comprehensive Testing Strategy

### Testing Philosophy

Domotix follows a **rigorous Test-Driven Development (TDD)** approach with a comprehensive 3-layer testing pyramid:

```
    🔺 E2E Tests (5-10%)
    🔺🔺 Integration Tests (20-30%)
  🔺🔺🔺 Unit Tests (60-70%)
```

### Testing Technologies Stack

| Framework    | Version | Purpose                                    |
| ------------ | ------- | ------------------------------------------ |
| **pytest**   | 8.4+    | Main testing framework with fixtures      |
| **faker**    | 37.4+   | Realistic test data generation             |
| **factory-boy** | 3.3+ | Test object factories                      |
| **hypothesis** | 6.136+ | Property-based testing                     |
| **pytest-cov** | 4.0+  | Code coverage analysis                     |
| **pytest-xdist** | 3.8+ | Parallel test execution                    |
| **pytest-mock** | 3.14+ | Advanced mocking capabilities              |

### 🔬 Unit Tests - Isolated Component Testing

Unit tests validate individual components in isolation with mocked dependencies.

**Current Status**: 📊 **157 unit tests** covering core business logic

```python
# Example: Light Controller Unit Test
import pytest
from faker import Faker
from unittest.mock import Mock, MagicMock

class TestLightController:
    @pytest.fixture
    def mock_repository(self):
       """Mock repository for isolated testing"""
       return Mock(spec=LightRepository)

    @pytest.fixture
    def controller(self, mock_repository):
       """Controller with mocked dependencies"""
       return LightController(mock_repository)

    @pytest.fixture
    def fake_light(self):
       """Faker-generated realistic test data"""
       fake = Faker()
       return Light(
          name=fake.sentence(nb_words=3),
          location=fake.random_element(['Living Room', 'Kitchen', 'Bedroom'])
       )

    def test_create_light_success(self, controller, mock_repository, fake_light):
       """Test successful light creation with realistic data"""
       # Arrange
       mock_repository.save.return_value = fake_light

       # Act
       result = controller.create_light(fake_light.name, fake_light.location)

       # Assert
       assert result == fake_light
       mock_repository.save.assert_called_once()
       assert isinstance(result.id, str)  # UUID validation

    def test_turn_on_nonexistent_light(self, controller, mock_repository):
       """Test error handling for non-existent devices"""
       # Arrange
       mock_repository.find_by_id.return_value = None
       device_id = "non-existent-id"

       # Act & Assert
       with pytest.raises(DeviceNotFoundError):
          controller.turn_on(device_id)
```

**Unit Test Categories**:
- 🏗️ **Model Tests**: Entity validation, business rules
- 💼 **Controller Tests**: Business logic, error handling
- 📊 **Repository Tests**: Data access patterns
- 🔧 **Utility Tests**: Helper functions, converters

### 🔗 Integration Tests - Component Interaction

Integration tests validate interactions between components with real database.

**Current Status**: 📊 **45 integration tests** with in-memory SQLite

```python
# Example: End-to-End Device Lifecycle Integration
class TestDeviceLifecycleIntegration:
    @pytest.fixture
    def session(self):
       """Real database session for integration testing"""
       engine = create_engine("sqlite:///:memory:")
       create_tables(engine)
       Session = sessionmaker(bind=engine)
       session = Session()
       yield session
       session.close()

    @pytest.fixture
    def controllers(self, session):
       """Real controllers with database session"""
       return {
          'light': ControllerFactory.create_light_controller(session),
          'sensor': ControllerFactory.create_sensor_controller(session),
          'device': ControllerFactory.create_device_controller(session)
       }

    def test_complete_smart_home_scenario(self, controllers):
       """Test realistic smart home automation scenario"""
       fake = Faker()

       # 1. Setup: Create devices in multiple rooms
       rooms = ['Living Room', 'Kitchen', 'Bedroom']
       created_devices = []

       for room in rooms:
          # Create light
          light = controllers['light'].create_light(
             f"{fake.word().title()} Light", room
          )

          # Create sensor
          sensor = controllers['sensor'].create_sensor(
             f"{room} Temperature", room
          )

          created_devices.extend([light, sensor])

       # 2. Control: Simulate evening automation
       for device in created_devices:
          if device.device_type == DeviceType.LIGHT:
             success = controllers['light'].turn_on(device.id)
             assert success is True

             # Verify state change persisted
             updated = controllers['light'].get_light(device.id)
             assert updated.is_on is True

       # 3. Monitoring: Update sensor values
       for device in created_devices:
          if device.device_type == DeviceType.SENSOR:
             temp = fake.random.uniform(18.0, 25.0)
             controllers['sensor'].update_value(device.id, temp)

             # Verify persistence
             updated = controllers['sensor'].get_sensor(device.id)
             assert updated.value == temp

       # 4. Verification: System summary
       summary = controllers['device'].get_devices_summary()
       assert "6 devices" in summary  # 3 lights + 3 sensors
       assert "3 rooms" in summary

    def test_concurrent_device_operations(self, controllers):
       """Test thread-safety and concurrent operations"""
       import concurrent.futures

       def create_and_control_light(room_name):
          light = controllers['light'].create_light(f"Test {room_name}", room_name)
          controllers['light'].turn_on(light.id)
          return controllers['light'].get_light(light.id)

       rooms = [f"Room_{i}" for i in range(10)]

       # Execute concurrent operations
       with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
          futures = [executor.submit(create_and_control_light, room) for room in rooms]
          results = [future.result() for future in futures]

       # Verify all operations succeeded
       assert len(results) == 10
       assert all(light.is_on for light in results)
```

**Integration Test Categories**:
- 🔄 **Repository-Database**: ORM mapping, queries, transactions
- 🏭 **Factory-Controller**: Dependency injection, object creation
- 🗄️ **Session Management**: Connection handling, rollbacks
- ⚡ **Performance**: Query optimization, bulk operations

### 🌐 End-to-End Tests - Complete User Workflows

E2E tests validate complete user workflows through CLI and API interfaces.

**Current Status**: 📊 **27 E2E tests** covering real user scenarios

```python
# Example: CLI End-to-End Test
import subprocess
import json
from pathlib import Path

class TestCLIEndToEnd:
    @pytest.fixture
    def clean_database(self):
       """Fresh database for E2E testing"""
       test_db = Path("test_e2e.db")
       if test_db.exists():
          test_db.unlink()

       # Set test database
       os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
       yield

       # Cleanup
       if test_db.exists():
          test_db.unlink()

    def test_complete_home_automation_workflow(self, clean_database):
       """Test complete user workflow through CLI"""
       fake = Faker()

       # 1. Create smart home setup
       devices = []
       for room in ['Living Room', 'Kitchen', 'Bedroom']:
          # Create light via CLI
          result = subprocess.run([
             'poetry', 'run', 'domotix', 'device', 'create', 'light',
             f"{fake.word().title()} Light", '--location', room
          ], capture_output=True, text=True)

          assert result.returncode == 0
          assert f"Created light" in result.stdout

          # Extract device ID from output
          device_id = self._extract_device_id(result.stdout)
          devices.append(device_id)

       # 2. Control devices
       for device_id in devices:
          # Turn on light
          result = subprocess.run([
             'poetry', 'run', 'domotix', 'device', 'turn-on', device_id
          ], capture_output=True, text=True)

          assert result.returncode == 0
          assert "turned on" in result.stdout.lower()

       # 3. Verify system state
       result = subprocess.run([
          'poetry', 'run', 'domotix', 'device', 'summary'
       ], capture_output=True, text=True)

       assert result.returncode == 0
       assert "3 devices" in result.stdout
       assert "3 rooms" in result.stdout

    def test_error_handling_workflow(self, clean_database):
       """Test CLI error handling and user feedback"""
       # Try to control non-existent device
       result = subprocess.run([
          'poetry', 'run', 'domotix', 'device', 'turn-on', 'invalid-uuid'
       ], capture_output=True, text=True)

       assert result.returncode != 0
       assert "not found" in result.stderr.lower()

    @staticmethod
    def _extract_device_id(output: str) -> str:
       """Extract device ID from CLI output"""
       import re
       match = re.search(r'ID: ([a-f0-9-]{36})', output)
       return match.group(1) if match else ""
```

**E2E Test Categories**:
- 🖥️ **CLI Workflows**: Complete command sequences
- 🌐 **API Endpoints**: REST API integration (future)
- 🔄 **Data Persistence**: Cross-session state validation
- 👤 **User Scenarios**: Real-world usage patterns

### 🎯 Property-Based Testing with Hypothesis

Advanced testing with generated inputs to find edge cases:

```python
from hypothesis import given, strategies as st

class TestDevicePropertyBased:
    @given(
       name=st.text(min_size=1, max_size=100),
       location=st.text(min_size=1, max_size=50)
    )
    def test_device_creation_with_any_valid_input(self, name, location):
       """Test device creation with any valid string input"""
       # Filter invalid characters for realistic testing
       assume(name.strip() and location.strip())
       assume(not any(char in name for char in ['<', '>', '"', "'", '&']))

       with create_session() as session:
          controller = ControllerFactory.create_light_controller(session)
          light = controller.create_light(name.strip(), location.strip())

          assert light is not None
          assert light.name == name.strip()
          assert light.location == location.strip()
          assert len(light.id) == 36  # UUID length

    @given(
       temperature=st.floats(min_value=-50.0, max_value=50.0, allow_nan=False)
    )
    def test_sensor_value_bounds(self, temperature):
       """Test sensor accepts any reasonable temperature value"""
       with create_session() as session:
          controller = ControllerFactory.create_sensor_controller(session)
          sensor = controller.create_sensor("Test Sensor", "Test Room")

          # Should not raise exception for reasonable values
          success = controller.update_value(sensor.id, temperature)
          assert success is True

          updated = controller.get_sensor(sensor.id)
          assert updated.value == temperature
```

### 📊 Test Execution and Coverage

#### Running All Tests

```bash
# 🚀 Complete test suite (229 tests)
poetry run pytest

# 📊 With coverage report
poetry run pytest --cov=domotix --cov-report=html --cov-report=term-missing

# ⚡ Parallel execution (faster)
poetry run pytest -n auto

# 🎯 By test category
poetry run pytest tests/test_unit/          # Unit tests only
poetry run pytest tests/test_integration/   # Integration tests
poetry run pytest tests/test_e2e/          # E2E tests

# 🔍 Verbose output for debugging
poetry run pytest -xvs tests/test_specific_file.py

# 🏃‍♂️ Stop on first failure
poetry run pytest -x

# 🔄 Watch mode for TDD
poetry run pytest-watch
```

#### Coverage Analysis

**Current Metrics**:
- 📊 **Overall Coverage**: 41% (target: 80%)
- 🎯 **Critical Paths**: 85% (controllers, models)
- 🔧 **Utilities**: 60% (helpers, converters)
- 🗄️ **Database Layer**: 55% (repositories, sessions)

**Coverage Report Example**:
```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
domotix/models/device_model.py    45      3    93%   123-125
domotix/controllers/light.py      67      8    88%   89-92, 145-148
domotix/repositories/base.py      34     12    65%   67-78
domotix/core/database.py          23      5    78%   45-49
------------------------------------------------------------
TOTAL                           1247    502    60%
```

### 🎭 Test Data Management with Factories

```python
# Factory Boy for consistent test data
import factory
from factory import Faker

class LightFactory(factory.Factory):
    class Meta:
       model = Light

    name = Faker('sentence', nb_words=3)
    location = Faker('random_element', elements=['Living Room', 'Kitchen', 'Bedroom'])

class SensorFactory(factory.Factory):
    class Meta:
       model = Sensor

    name = Faker('sentence', nb_words=2)
    location = Faker('random_element', elements=['Living Room', 'Kitchen', 'Bedroom'])
    value = Faker('random_uniform', a=18.0, b=25.0)

# Usage in tests
def test_with_realistic_data():
    light = LightFactory()
    sensor = SensorFactory()

    # Realistic, consistent test data automatically generated
    assert light.name != sensor.name
    assert light.location in ['Living Room', 'Kitchen', 'Bedroom']
```

### 🚀 Quality Metrics and Goals

| Metric                  | Current | Target Q2 2025 | Status         |
| ----------------------- | ------- | -------------- | -------------- |
| **Total Tests**         | 229     | 400+           | 🟨 Progressing |
| **Unit Tests**          | 157     | 280+           | 🟨 On track    |
| **Integration Tests**   | 45      | 80+            | 🟨 Expanding   |
| **E2E Tests**          | 27      | 40+            | ✅ Good        |
| **Code Coverage**       | 41%     | 80%            | 🟨 Improving   |
| **Critical Path Coverage** | 85%  | 95%            | ✅ Excellent   |
| **Test Execution Time** | 12s     | <10s           | 🟨 Optimizing  |

**Test Quality Standards**:
- ✅ **100% MyPy compliance** in test code
- ✅ **Realistic test data** with Faker
- ✅ **Isolated unit tests** with mocked dependencies
- ✅ **Database cleanup** in integration tests
- ✅ **Parallel execution** support
- ✅ **Property-based testing** for edge cases
