"""
CLI commands module with full dependency injection.

This module contains all CLI commands for the home automation system
with modern dependency injection.

Commands:
    General: device_list, device_add, device_remove, device_status
    Lights: light_on, light_off, light_toggle, lights_list, lights_on, lights_off
    Shutters: shutter_open, shutter_close, shutter_toggle, shutter_position,
    shutters_list
    Sensors: sensor_update, sensor_reset, sensors_list, sensors_reset
    Search: devices_by_location, device_search, locations_list
    Summaries: devices_summary, devices_on, devices_off
"""

from typing import Optional

import typer

from ..core.service_provider import scoped_service_provider
from ..models import Light, Sensor, Shutter

app = typer.Typer()


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
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
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

    @staticmethod
    def create_sensor(name: str, location: Optional[str] = None):
        """Creates a new sensor."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
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


class DeviceListCommands:
    """Commands to list devices with dependency injection."""

    @staticmethod
    def list_all_devices():
        """Displays the list of all devices."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
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

    @staticmethod
    def list_lights():
        """Displays the list of all lights."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
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

    @staticmethod
    def list_shutters():
        """Displays the list of all shutters."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
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

    @staticmethod
    def list_sensors():
        """Displays the list of all sensors."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
            sensors = controller.get_all_sensors()

            if not sensors:
                print("No sensors registered.")
                return

            print(f"🌡️ Registered sensors ({len(sensors)}):")
            print("-" * 40)

            for sensor in sensors:
                status = f"Value: {sensor.value}" if sensor.value else "Inactive"
                print(f"🌡️ {sensor.name}")
                print(f"   ID: {sensor.id}")
                print(f"   Location: {sensor.location or 'Undefined'}")
                print(f"   Status: {status}")
                print()

    @staticmethod
    def show_device(device_id: str):
        """Displays the details of a device."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
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

    @staticmethod
    def list_devices_by_location(location: str):
        """Displays all devices in a location."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            # Filter by location
            filtered_devices = [
                device
                for device in devices
                if device.location and location.lower() in device.location.lower()
            ]

            if not filtered_devices:
                print(f"No devices found for location '{location}'.")
                return

            print(f"🏠 Devices in '{location}' ({len(filtered_devices)}):")
            print("-" * 50)

            for device in filtered_devices:
                device_type = type(device).__name__
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
                print(f"   Status: {status}")
                print()

    @staticmethod
    def search_devices(name: str):
        """Searches for devices by name."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            # Search by name (case-insensitive)
            found_devices = [
                device for device in devices if name.lower() in device.name.lower()
            ]

            if not found_devices:
                print(f"No devices found with the name '{name}'.")
                return

            print(f"🔍 Search results for '{name}' ({len(found_devices)}):")
            print("-" * 50)

            for device in found_devices:
                device_type = type(device).__name__
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

    @staticmethod
    def list_locations():
        """Displays the list of all locations."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            # Extract unique locations
            locations = set()
            for device in devices:
                if device.location:
                    locations.add(device.location)

            if not locations:
                print("No locations defined.")
                return

            sorted_locations = sorted(locations)
            print(f"📍 Locations ({len(sorted_locations)}):")
            print("-" * 30)

            for location in sorted_locations:
                # Count devices by location
                device_count = sum(
                    1 for device in devices if device.location == location
                )
                print(f"📍 {location} ({device_count} devices)")

    @staticmethod
    def show_devices_summary():
        """Displays a summary of all devices."""
        with scoped_service_provider.create_scope() as provider:
            device_controller = provider.get_device_controller()
            light_controller = provider.get_light_controller()
            shutter_controller = provider.get_shutter_controller()
            sensor_controller = provider.get_sensor_controller()

            # Retrieve all data
            all_devices = device_controller.get_all_devices()
            lights = light_controller.get_all_lights()
            shutters = shutter_controller.get_all_shutters()
            sensors = sensor_controller.get_all_sensors()

            print("📊 DEVICE SUMMARY")
            print("=" * 40)
            print(f"Total devices: {len(all_devices)}")
            print(f"  💡 Lights: {len(lights)}")
            print(f"  🪟 Shutters: {len(shutters)}")
            print(f"  🌡️ Sensors: {len(sensors)}")
            print()

            if lights:
                lights_on = sum(1 for light in lights if light.is_on)
                print(f"💡 Lights on: {lights_on}/{len(lights)}")

            if shutters:
                shutters_open = sum(1 for shutter in shutters if shutter.is_open)
                print(f"🪟 Shutters open: {shutters_open}/{len(shutters)}")

            if sensors:
                active_sensors = sum(
                    1 for sensor in sensors if sensor.value is not None
                )
                print(f"🌡️ Active sensors: {active_sensors}/{len(sensors)}")

    @staticmethod
    def list_active_devices():
        """Displays all active devices."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            active_devices = []
            for device in devices:
                if hasattr(device, "is_on") and device.is_on:
                    active_devices.append((device, "On"))
                elif hasattr(device, "is_open") and device.is_open:
                    active_devices.append((device, "Open"))
                elif hasattr(device, "value") and device.value is not None:
                    active_devices.append((device, f"Value: {device.value}"))

            if not active_devices:
                print("No active devices.")
                return

            print(f"🟢 Active devices ({len(active_devices)}):")
            print("-" * 40)

            for device, status in active_devices:
                device_type = type(device).__name__
                print(f"📱 {device.name} ({device_type})")
                print(f"   ID: {device.id}")
                print(f"   Location: {device.location or 'Undefined'}")
                print(f"   Status: {status}")
                print()

    @staticmethod
    def list_inactive_devices():
        """Displays all inactive devices."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            inactive_devices = []
            for device in devices:
                if hasattr(device, "is_on") and not device.is_on:
                    inactive_devices.append((device, "Off"))
                elif hasattr(device, "is_open") and not device.is_open:
                    inactive_devices.append((device, "Closed"))
                elif hasattr(device, "value") and device.value is None:
                    inactive_devices.append((device, "Inactive"))

            if not inactive_devices:
                print("No inactive devices.")
                return

            print(f"🔴 Inactive devices ({len(inactive_devices)}):")
            print("-" * 40)

            for device, status in inactive_devices:
                device_type = type(device).__name__
                print(f"📱 {device.name} ({device_type})")
                print(f"   ID: {device.id}")
                print(f"   Location: {device.location or 'Undefined'}")
                print(f"   Status: {status}")
                print()


class DeviceStateCommands:
    """Commands to manage the state of devices with dependency injection."""

    @staticmethod
    def turn_on_light(light_id: str):
        """Turns on a light."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            success = controller.turn_on(light_id)

            if success:
                print(f"✅ Light {light_id} turned on.")
            else:
                print(f"❌ Failed to turn on light {light_id}.")

    @staticmethod
    def turn_off_light(light_id: str):
        """Turns off a light."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            success = controller.turn_off(light_id)

            if success:
                print(f"✅ Light {light_id} turned off.")
            else:
                print(f"❌ Failed to turn off light {light_id}.")

    @staticmethod
    def toggle_light(light_id: str):
        """Toggles the state of a light."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            success = controller.toggle(light_id)

            if success:
                # Retrieve current state for display
                light = controller.get_light(light_id)
                if light is not None:
                    status = "on" if light.is_on else "off"
                    print(f"✅ Light {light_id} is now {status}.")
                else:
                    print(f"✅ Light {light_id} toggled.")
            else:
                print(f"❌ Failed to toggle light {light_id}.")

    @staticmethod
    def turn_on_all_lights():
        """Turns on all lights."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            lights = controller.get_all_lights()

            if not lights:
                print("No lights found.")
                return

            success_count = 0
            for light in lights:
                if controller.turn_on(light.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(lights)} lights turned on.")

    @staticmethod
    def turn_off_all_lights():
        """Turns off all lights."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            lights = controller.get_all_lights()

            if not lights:
                print("No lights found.")
                return

            success_count = 0
            for light in lights:
                if controller.turn_off(light.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(lights)} lights turned off.")

    @staticmethod
    def open_shutter(shutter_id: str):
        """Opens a shutter."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            success = controller.open(shutter_id)

            if success:
                print(f"✅ Shutter {shutter_id} opened.")
            else:
                print(f"❌ Failed to open shutter {shutter_id}.")

    @staticmethod
    def close_shutter(shutter_id: str):
        """Closes a shutter."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            success = controller.close(shutter_id)

            if success:
                print(f"✅ Shutter {shutter_id} closed.")
            else:
                print(f"❌ Failed to close shutter {shutter_id}.")

    @staticmethod
    def toggle_shutter(shutter_id: str):
        """Toggles the state of a shutter."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            shutter = controller.get_shutter(shutter_id)

            if not shutter:
                print(f"❌ Shutter {shutter_id} not found.")
                return

            # Toggle according to current state
            if shutter.is_open:
                success = controller.close(shutter_id)
                action = "closed"
            else:
                success = controller.open(shutter_id)
                action = "opened"

            if success:
                print(f"✅ Shutter {shutter_id} {action}.")
            else:
                print(f"❌ Failed to toggle shutter {shutter_id}.")

    @staticmethod
    def set_shutter_position(shutter_id: str, position: int):
        """Sets the position of a shutter."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            success = controller.set_position(shutter_id, position)

            if success:
                print(f"✅ Shutter {shutter_id} set to {position}%.")
            else:
                print(f"❌ Failed to set position of shutter {shutter_id}.")

    @staticmethod
    def open_all_shutters():
        """Opens all shutters."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            shutters = controller.get_all_shutters()

            if not shutters:
                print("No shutters found.")
                return

            success_count = 0
            for shutter in shutters:
                if controller.open(shutter.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(shutters)} shutters opened.")

    @staticmethod
    def close_all_shutters():
        """Closes all shutters."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            shutters = controller.get_all_shutters()

            if not shutters:
                print("No shutters found.")
                return

            success_count = 0
            for shutter in shutters:
                if controller.close(shutter.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(shutters)} shutters closed.")

    @staticmethod
    def update_sensor_value(sensor_id: str, value: float):
        """Updates the value of a sensor."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
            success = controller.update_value(sensor_id, value)

            if success:
                print(f"✅ Sensor {sensor_id} updated with value {value}.")
            else:
                print(f"❌ Failed to update sensor {sensor_id}.")

    @staticmethod
    def reset_sensor(sensor_id: str):
        """Resets a sensor."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
            success = controller.reset_value(sensor_id)

            if success:
                print(f"✅ Sensor {sensor_id} reset.")
            else:
                print(f"❌ Failed to reset sensor {sensor_id}.")

    @staticmethod
    def reset_all_sensors():
        """Resets all sensors."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
            sensors = controller.get_all_sensors()

            if not sensors:
                print("No sensors found.")
                return

            success_count = 0
            for sensor in sensors:
                if controller.reset_value(sensor.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(sensors)} sensors reset.")


# === COMMANDES TYPER ===


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
        device_id (str): ID of the device to remove
    """
    with scoped_service_provider.create_scope() as provider:
        controller = provider.get_device_controller()

        # Attempt to remove by type
        device = controller.get_device(device_id)
        if not device:
            print(f"❌ Device {device_id} not found.")
            return

        success = False
        if isinstance(device, Light):
            light_controller = provider.get_light_controller()
            success = light_controller.delete_light(device_id)
        elif isinstance(device, Shutter):
            shutter_controller = provider.get_shutter_controller()
            success = shutter_controller.delete_shutter(device_id)
        elif isinstance(device, Sensor):
            sensor_controller = provider.get_sensor_controller()
            success = sensor_controller.delete_sensor(device_id)

        if success:
            print(f"✅ Device {device_id} successfully removed.")
        else:
            print(f"❌ Error removing device {device_id}.")


@app.command()
def device_status(device_id: str):
    """
    Displays the status of a device.

    Args:
        device_id (str): Device ID
    """
    DeviceListCommands.show_device(device_id)


# === COMMANDES POUR LES LAMPES ===


@app.command()
def light_on(light_id: str):
    """
    Turns on a light.

    Args:
        light_id (str): Light ID
    """
    DeviceStateCommands.turn_on_light(light_id)


@app.command()
def light_off(light_id: str):
    """
    Turns off a light.

    Args:
        light_id (str): Light ID
    """
    DeviceStateCommands.turn_off_light(light_id)


@app.command()
def light_toggle(light_id: str):
    """
    Toggles the state of a light (on <-> off).

    Args:
        light_id (str): Light ID
    """
    DeviceStateCommands.toggle_light(light_id)


@app.command()
def lights_list():
    """Displays the list of all lights."""
    DeviceListCommands.list_lights()


@app.command()
def lights_on():
    """Turns on all lights."""
    DeviceStateCommands.turn_on_all_lights()


@app.command()
def lights_off():
    """Turns off all lights."""
    DeviceStateCommands.turn_off_all_lights()


# === COMMANDES POUR LES VOLETS ===


@app.command()
def shutter_open(shutter_id: str):
    """
    Opens a shutter.

    Args:
        shutter_id (str): Shutter ID
    """
    DeviceStateCommands.open_shutter(shutter_id)


@app.command()
def shutter_close(shutter_id: str):
    """
    Closes a shutter.

    Args:
        shutter_id (str): Shutter ID
    """
    DeviceStateCommands.close_shutter(shutter_id)


@app.command()
def shutter_toggle(shutter_id: str):
    """
    Toggles the state of a shutter (open <-> closed).

    Args:
        shutter_id (str): Shutter ID
    """
    DeviceStateCommands.toggle_shutter(shutter_id)


@app.command()
def shutter_position(shutter_id: str, position: int):
    """
    Sets the position of a shutter.

    Args:
        shutter_id (str): Shutter ID
        position (int): Position in percentage (0-100)
    """
    DeviceStateCommands.set_shutter_position(shutter_id, position)


@app.command()
def shutters_list():
    """Displays the list of all shutters."""
    DeviceListCommands.list_shutters()


@app.command()
def shutters_open():
    """Opens all shutters."""
    DeviceStateCommands.open_all_shutters()


@app.command()
def shutters_close():
    """Closes all shutters."""
    DeviceStateCommands.close_all_shutters()


# === COMMANDES POUR LES CAPTEURS ===


@app.command()
def sensor_update(sensor_id: str, value: float):
    """
    Updates the value of a sensor.

    Args:
        sensor_id (str): Sensor ID
        value (float): New sensor value
    """
    DeviceStateCommands.update_sensor_value(sensor_id, value)


@app.command()
def sensor_reset(sensor_id: str):
    """
    Resets a sensor.

    Args:
        sensor_id (str): Sensor ID
    """
    DeviceStateCommands.reset_sensor(sensor_id)


@app.command()
def sensors_list():
    """Displays the list of all sensors."""
    DeviceListCommands.list_sensors()


@app.command()
def sensors_reset():
    """Resets all sensors."""
    DeviceStateCommands.reset_all_sensors()


# === COMMANDES DE RECHERCHE ET FILTRAGE ===


@app.command()
def devices_by_location(location: str):
    """
    Displays all devices in a location.

    Args:
        location (str): Location name
    """
    DeviceListCommands.list_devices_by_location(location)


@app.command()
def device_search(name: str):
    """
    Searches for devices by name.

    Args:
        name (str): Name or part of the name to search
    """
    DeviceListCommands.search_devices(name)


@app.command()
def locations_list():
    """Displays the list of all locations."""
    DeviceListCommands.list_locations()


# === COMMANDES D'ÉTAT ET STATISTIQUES ===


@app.command()
def devices_summary():
    """Displays a summary of all devices."""
    DeviceListCommands.show_devices_summary()


@app.command()
def devices_on():
    """Displays all turned on/open/active devices."""
    DeviceListCommands.list_active_devices()


@app.command()
def devices_off():
    """Displays all turned off/closed/inactive devices."""
    DeviceListCommands.list_inactive_devices()


# Export des classes pour l'import et compatibilité
__all__ = [
    "DeviceCreateCommands",
    "DeviceListCommands",
    "DeviceStateCommands",
    "device_list",
    "device_add",
    "device_remove",
    "device_status",
    "light_on",
    "light_off",
    "light_toggle",
    "lights_list",
    "lights_on",
    "lights_off",
    "shutter_open",
    "shutter_close",
    "shutter_toggle",
    "shutter_position",
    "shutters_list",
    "shutters_open",
    "shutters_close",
    "sensor_update",
    "sensor_reset",
    "sensors_list",
    "sensors_reset",
    "devices_by_location",
    "device_search",
    "locations_list",
    "devices_summary",
    "devices_on",
    "devices_off",
]
