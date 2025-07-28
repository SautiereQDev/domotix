"""
CLI commands module for device management.

This module contains all CLI commands to add, list,
delete, and view the status of devices with modern dependency injection.

Commands:
    device_list: Displays the list of devices
    device_add: Adds a new device
    device_remove: Removes a device
    device_status: Displays the status of a device
"""

from typing import Optional

from ..core.database import create_session
from ..core.factories import get_controller_factory
from ..core.service_provider import scoped_service_provider
from ..models import Light, Sensor, Shutter
from .main import app

# Export classes for import
__all__ = [
    "DeviceCreateCommands",
    "DeviceListCommands",
    "DeviceStateCommands",
    "device_list",
    "device_add",
    "device_remove",
    "device_status",
]

"""
CLI commands module for device management.

This module contains all CLI commands to add, list,
delete, and view the status of devices with persistence.

Classes:
    DeviceCreateCommands: Device creation commands
    DeviceListCommands: Device listing commands
    DeviceStateCommands: Device state management commands
"""


class DeviceCreateCommands:
    """Commands to create devices with dependency injection."""

    @staticmethod
    def create_light(name: str, location: Optional[str] = None):
        """Creates a new light."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            light_id = controller.create_light(name, location)

            if light_id:
                light = controller.get_light(light_id)
                if light is not None:
                    print(f"✅ Light '{light.name}' created with ID: {light_id}")
                    if location:
                        print(f"   Location: {location}")
                else:
                    print(f"✅ Light created with ID: {light_id}")
            else:
                print(f"❌ Error creating light '{name}'")

    @staticmethod
    def create_shutter(name: str, location: Optional[str] = None):
        """Creates a new shutter."""
        session = create_session()
        try:
            controller = get_controller_factory().create_shutter_controller(session)
            shutter_id = controller.create_shutter(name, location)

            if shutter_id:
                shutter = controller.get_shutter(shutter_id)
                if shutter is not None:
                    print(f"✅ Shutter '{shutter.name}' created with ID: {shutter_id}")
                    if location:
                        print(f"   Location: {location}")
                else:
                    print(f"✅ Shutter created with ID: {shutter_id}")
            else:
                print(f"❌ Error creating shutter '{name}'")
        finally:
            session.close()

    @staticmethod
    def create_sensor(name: str, location: Optional[str] = None):
        """Creates a new sensor."""
        session = create_session()
        try:
            controller = get_controller_factory().create_sensor_controller(session)
            sensor_id = controller.create_sensor(name, location)

            if sensor_id:
                sensor = controller.get_sensor(sensor_id)
                if sensor is not None:
                    print(f"✅ Sensor '{sensor.name}' created with ID: {sensor_id}")
                    if location:
                        print(f"   Location: {location}")
                else:
                    print(f"✅ Sensor created with ID: {sensor_id}")
            else:
                print(f"❌ Error creating sensor '{name}'")
        finally:
            session.close()


class DeviceListCommands:
    """Commands to list devices."""

    @staticmethod
    def list_all_devices():
        """Displays the list of all devices."""
        session = create_session()
        try:
            controller = get_controller_factory().create_device_controller(session)
            devices = controller.get_all_devices()

            if not devices:
                print("No devices registered.")
                return

            print(f"🏠 Registered devices ({len(devices)}):")
            print("-" * 50)

            for device in devices:
                device_type = type(device).__name__
                # Build status according to type
                if hasattr(device, "is_on"):
                    status = "ON" if device.is_on else "OFF"
                elif hasattr(device, "is_open"):
                    status = "OPEN" if device.is_open else "CLOSED"
                elif hasattr(device, "value"):
                    status = f"Value: {device.value}" if device.value else "Inactive"
                else:
                    status = "Unknown"

                print(f"📱 {device.name}")
                print(f"   ID: {device.id}")
                print(f"   Type: {device_type}")
                print(f"   Location: {device.location or 'Undefined'}")
                print(f"   Status: {status}")
                print()
        finally:
            session.close()

    @staticmethod
    def list_lights():
        """Displays the list of lights."""
        session = create_session()
        try:
            controller = get_controller_factory().create_light_controller(session)
            lights = controller.get_all_lights()

            if not lights:
                print("No lights registered.")
                return

            print(f"💡 Registered lights ({len(lights)}):")
            print("-" * 40)

            for light in lights:
                status = "ON" if light.is_on else "OFF"
                print(f"💡 {light.name}")
                print(f"   ID: {light.id}")
                print(f"   Location: {light.location or 'Undefined'}")
                print(f"   Status: {status}")
                print()
        finally:
            session.close()

    @staticmethod
    def list_shutters():
        """Displays the list of shutters."""
        session = create_session()
        try:
            controller = get_controller_factory().create_shutter_controller(session)
            shutters = controller.get_all_shutters()

            if not shutters:
                print("No shutters registered.")
                return

            print(f"🪟 Registered shutters ({len(shutters)}):")
            print("-" * 40)

            for shutter in shutters:
                status = "OPEN" if shutter.is_open else "CLOSED"
                print(f"🪟 {shutter.name}")
                print(f"   ID: {shutter.id}")
                print(f"   Location: {shutter.location or 'Undefined'}")
                print(f"   Status: {status}")
                print()
        finally:
            session.close()

    @staticmethod
    def list_sensors():
        """Displays the list of sensors."""
        session = create_session()
        try:
            controller = get_controller_factory().create_sensor_controller(session)
            sensors = controller.get_all_sensors()

            if not sensors:
                print("No sensors registered.")
                return

            print(f"📊 Registered sensors ({len(sensors)}):")
            print("-" * 40)

            for sensor in sensors:
                status = f"Value: {sensor.value}" if sensor.value else "Inactive"
                print(f"📊 {sensor.name}")
                print(f"   ID: {sensor.id}")
                print(f"   Location: {sensor.location or 'Undefined'}")
                print(f"   Status: {status}")
                print()
        finally:
            session.close()

    @staticmethod
    def show_device(device_id: str):
        """Displays the details of a device."""
        session = create_session()
        try:
            controller = get_controller_factory().create_device_controller(session)
            device = controller.get_device(device_id)

            if not device:
                print(f"❌ Device with ID {device_id} not found.")
                return

            device_type = type(device).__name__

            # Build status according to type
            if hasattr(device, "is_on"):
                status = "ON" if device.is_on else "OFF"
            elif hasattr(device, "is_open"):
                status = "OPEN" if device.is_open else "CLOSED"
            elif hasattr(device, "value"):
                status = f"Value: {device.value}" if device.value else "Inactive"
            else:
                status = "Unknown"

            print(f"📱 {device.name}")
            print(f"   ID: {device.id}")
            print(f"   Type: {device_type}")
            print(f"   Location: {device.location or 'Undefined'}")
            print(f"   Status: {status}")
        finally:
            session.close()


class DeviceStateCommands:
    """Commands to manage the state of devices."""

    @staticmethod
    def turn_on_light(light_id: str):
        """Turns on a light."""
        session = create_session()
        try:
            controller = get_controller_factory().create_light_controller(session)
            success = controller.turn_on(light_id)

            if success:
                print(f"✅ Light {light_id} turned on.")
            else:
                print(f"❌ Failed to turn on light {light_id}.")
        finally:
            session.close()

    @staticmethod
    def turn_off_light(light_id: str):
        """Turns off a light."""
        session = create_session()
        try:
            controller = get_controller_factory().create_light_controller(session)
            success = controller.turn_off(light_id)

            if success:
                print(f"✅ Light {light_id} turned off.")
            else:
                print(f"❌ Failed to turn off light {light_id}.")
        finally:
            session.close()

    @staticmethod
    def toggle_light(light_id: str):
        """Toggles the state of a light."""
        session = create_session()
        try:
            controller = get_controller_factory().create_light_controller(session)
            success = controller.toggle(light_id)

            if success:
                # Retrieve current state to display
                light = controller.get_light(light_id)
                if light is not None:
                    status = "on" if light.is_on else "off"
                    print(f"✅ Light {light_id} is now {status}.")
                else:
                    print(f"✅ Light {light_id} toggled.")
            else:
                print(f"❌ Failed to toggle light {light_id}.")
        finally:
            session.close()

    @staticmethod
    def open_shutter(shutter_id: str):
        """Opens a shutter."""
        session = create_session()
        try:
            controller = get_controller_factory().create_shutter_controller(session)
            success = controller.open(shutter_id)

            if success:
                print(f"✅ Shutter {shutter_id} opened.")
            else:
                print(f"❌ Failed to open shutter {shutter_id}.")
        finally:
            session.close()

    @staticmethod
    def close_shutter(shutter_id: str):
        """Closes a shutter."""
        session = create_session()
        try:
            controller = get_controller_factory().create_shutter_controller(session)
            success = controller.close(shutter_id)

            if success:
                print(f"✅ Shutter {shutter_id} closed.")
            else:
                print(f"❌ Failed to close shutter {shutter_id}.")
        finally:
            session.close()

    @staticmethod
    def update_sensor_value(sensor_id: str, value: float):
        """Updates the value of a sensor."""
        session = create_session()
        try:
            controller = get_controller_factory().create_sensor_controller(session)
            success = controller.update_value(sensor_id, value)

            if success:
                print(f"✅ Sensor {sensor_id} updated with value {value}.")
            else:
                print(f"❌ Failed to update sensor {sensor_id}.")
        finally:
            session.close()

    @staticmethod
    def reset_sensor(sensor_id: str):
        """Resets a sensor."""
        session = create_session()
        try:
            controller = get_controller_factory().create_sensor_controller(session)
            success = controller.reset_value(sensor_id)

            if success:
                print(f"✅ Sensor {sensor_id} reset.")
            else:
                print(f"❌ Failed to reset sensor {sensor_id}.")
        finally:
            session.close()


# Typer commands (for compatibility with the old system)
@app.command()
def device_list():
    """Displays the list of devices."""
    DeviceListCommands.list_all_devices()


@app.command()
def device_add(device_type: str, name: str, location: Optional[str] = None):
    """
    Adds a new device.

    Args:
        device_type (str): Device type (light, shutter, sensor)
        name (str): Device name
        location (str, optional): Device location
    """
    device_type = device_type.lower()

    if device_type == "light":
        DeviceCreateCommands.create_light(name, location)
    elif device_type == "shutter":
        DeviceCreateCommands.create_shutter(name, location)
    elif device_type == "sensor":
        DeviceCreateCommands.create_sensor(name, location)
    else:
        print(f"❌ Unsupported device type: {device_type}")
        print("Supported types: light, shutter, sensor")


@app.command()
def device_remove(device_id: str):
    """
    Removes a device by its ID.

    Args:
        device_id (int): Identifier of the device to remove
    """
    session = create_session()
    try:
        controller = get_controller_factory().create_device_controller(session)

        # Attempt to delete by type
        device = controller.get_device(device_id)
        if not device:
            print(f"❌ Device {device_id} not found.")
            return

        success = False
        if isinstance(device, Light):
            light_controller = get_controller_factory().create_light_controller(session)
            success = light_controller.delete_light(device_id)
        elif isinstance(device, Shutter):
            shutter_controller = get_controller_factory().create_shutter_controller(
                session
            )
            success = shutter_controller.delete_shutter(device_id)
        elif isinstance(device, Sensor):
            sensor_controller = get_controller_factory().create_sensor_controller(
                session
            )
            success = sensor_controller.delete_sensor(device_id)

        if success:
            print(f"✅ Device {device_id} removed successfully.")
        else:
            print(f"❌ Error removing device {device_id}.")
    finally:
        session.close()


@app.command()
def device_status(device_id: str):
    """
    Displays the status of a device.

    Args:
        device_id (int): Device identifier
    """
    DeviceListCommands.show_device(device_id)
