"""
Tests pour les nouvelles fonctionnalités de gestion d'erreurs du modèle Sensor.
"""

import pytest

from domotix.globals.exceptions import ErrorCode, ValidationError
from domotix.models.sensor import Sensor


def test_sensor_validation_nan():
    """Test que la validation NaN fonctionne."""
    sensor = Sensor("Test NaN", "Test")

    with pytest.raises(ValidationError) as exc_info:
        sensor.update_value(float("nan"))

    assert "NaN" in str(exc_info.value)
    assert exc_info.value.error_code == ErrorCode.VALIDATION_INVALID_FORMAT


def test_sensor_validation_infinity():
    """Test que la validation des valeurs infinies fonctionne."""
    sensor = Sensor("Test Infinity", "Test")

    with pytest.raises(ValidationError) as exc_info:
        sensor.update_value(float("inf"))

    assert "infinie" in str(exc_info.value)
    assert exc_info.value.error_code == ErrorCode.VALIDATION_OUT_OF_RANGE


def test_sensor_validate_range():
    """Test de la nouvelle méthode validate_range."""
    sensor = Sensor("Test Range", "Test")

    # Test avec valeur dans la plage
    sensor.update_value(25.0)
    sensor.validate_range(0, 50)  # Ne doit pas lever d'exception

    # Test avec valeur hors plage
    sensor.update_value(100.0)
    with pytest.raises(ValidationError) as exc_info:
        sensor.validate_range(0, 50)

    assert "hors de la plage" in str(exc_info.value)
    assert exc_info.value.error_code == ErrorCode.VALIDATION_OUT_OF_RANGE


def test_sensor_validate_range_no_value():
    """Test validate_range sans valeur définie."""
    sensor = Sensor("Test No Value", "Test")

    with pytest.raises(ValidationError) as exc_info:
        sensor.validate_range(0, 100)

    assert "aucune valeur définie" in str(exc_info.value)
    assert exc_info.value.error_code == ErrorCode.VALIDATION_REQUIRED_FIELD


def test_sensor_is_value_valid():
    """Test de la méthode is_value_valid."""
    sensor = Sensor("Test Valid", "Test")

    # Sans valeur
    assert not sensor.is_value_valid()

    # Avec valeur normale
    sensor.update_value(42.0)
    assert sensor.is_value_valid()

    # Avec valeur NaN (directement via l'attribut pour contourner la validation)
    sensor.value = float("nan")
    assert not sensor.is_value_valid()

    # Avec valeur infinie (directement via l'attribut pour contourner la validation)
    sensor.value = float("inf")
    assert not sensor.is_value_valid()


def test_sensor_error_context():
    """Test que le contexte d'erreur est correctement créé."""
    sensor = Sensor("Test Context", "Location Test")

    with pytest.raises(ValidationError) as exc_info:
        sensor.update_value("string")

    error = exc_info.value
    assert error.context is not None
    assert error.context.user_data["device_id"] == sensor.id
    assert error.context.user_data["device_name"] == "Test Context"
    assert error.context.user_data["value_type"] == "str"
    assert "str" in error.context.user_data["value"]
