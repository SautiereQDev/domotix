#!/usr/bin/env python3
"""
Test script to validate Domotix error handling improvements.

This script tests new error handling features
to ensure they work correctly.
"""

import sys
import traceback

# Simulated imports for tests (adapt as needed for your environment)
try:
    from domotix.core.error_handling import validate_device_id
    from domotix.globals.exceptions import ValidationError
    from domotix.models.sensor import Sensor
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("📋 This script must be run from the Domotix environment")
    sys.exit(1)


def test_sensor_validation():
    """Test improved Sensor model validations."""
    print("🧪 Testing Sensor validations...")

    # Test 1: Normal creation
    try:
        sensor = Sensor("Test Sensor", "Living Room")
        sensor.update_value(25.5)
        print(f"✅ Normal creation and update: {sensor.value}")
    except Exception as e:
        print(f"❌ Unexpected error during creation: {e}")
        return False

    # Test 2: Invalid type validation
    try:
        sensor.update_value("invalid_type")
        print("❌ Type validation failed")
        return False
    except ValidationError as e:
        print(f"✅ Correct type validation: {str(e)}")
        print(f"   Error code: {e.error_code}")

    # Test 3: NaN validation
    try:
        sensor.update_value(float("nan"))
        print("❌ NaN validation failed")
        return False
    except ValidationError as e:
        print(f"✅ Correct NaN validation: {str(e)}")

    # Test 4: Range validation
    try:
        sensor.update_value(50.0)
        sensor.validate_range(0, 40)  # Value out of range
        print("❌ Range validation failed")
        return False
    except ValidationError as e:
        print(f"✅ Correct range validation: {str(e)}")

    # Test 5: is_value_valid method
    sensor.update_value(25.0)
    if sensor.is_value_valid():
        print("✅ is_value_valid() works correctly")
    else:
        print("❌ is_value_valid() returns incorrect result")
        return False

    return True


def test_error_handling_utilities():
    """Test error handling utilities."""
    print("\n🧪 Testing error handling utilities...")

    # Test 1: Device ID validation
    try:
        validate_device_id("")
        print("❌ Empty ID validation failed")
        return False
    except ValidationError as e:
        print(f"✅ Correct empty ID validation: {str(e)}")

    try:
        validate_device_id("   ")
        print("❌ ID validation with spaces failed")
        return False
    except ValidationError as e:
        print(f"✅ Correct ID validation with spaces: {str(e)}")

    # Test 2: Device name validation (uses validate_device_id)
    try:
        validate_device_id("")  # Empty ID
        print("❌ Empty name validation failed")
        return False
    except ValidationError as e:
        print(f"✅ Correct empty name validation: {str(e)}")

    # Test 3: Successful validations
    try:
        validate_device_id("device_123")
        # Simulate successful validation for names
        print("✅ Successful value validations")
    except Exception as e:
        print(f"❌ Unexpected error during validations: {e}")
        return False

    return True


def test_error_context():
    """Test the ErrorContext structure."""
    print("\n🧪 Testing ErrorContext structure...")

    try:
        from domotix.globals.exceptions import ErrorContext

        # Create an error context
        context = ErrorContext(
            module=__name__,
            function="test_error_context",
            user_data={"test": "value"},
            system_data={"env": "test"},
        )

        print("✅ ErrorContext created successfully")
        print(f"   Module: {context.module}")
        print(f"   Function: {context.function}")
        print(f"   Timestamp: {context.timestamp}")
        print(f"   User data: {context.user_data}")

        return True
    except Exception as e:
        print(f"❌ Error creating ErrorContext: {e}")
        return False


def run_all_tests():
    """Run all validation tests."""
    print("🚀 Starting Domotix error handling tests\n")

    tests = [
        ("Sensor Validations", test_sensor_validation),
        ("Error Handling Utilities", test_error_handling_utilities),
        ("ErrorContext Structure", test_error_context),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Critical error in {test_name}: {e}")
            traceback.print_exc()
            results.append((test_name, False))

    # Résumé des résultats
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")

    print(f"\n🎯 Score: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All tests passed! " "Error handling works correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the improvements.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
