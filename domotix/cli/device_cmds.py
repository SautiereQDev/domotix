"""
Module des commandes CLI pour la gestion des dispositifs.

Ce module contient toutes les commandes CLI pour ajouter, lister,
supprimer et voir le statut des dispositifs avec injection de dépendance moderne.

Commands:
    device_list: Affiche la liste des dispositifs
    device_add: Ajoute un nouveau dispositif
    device_remove: Supprime un dispositif
    device_status: Affiche le statut d'un dispositif
"""

from typing import Optional

from ..core.database import create_session
from ..core.factories import get_controller_factory
from ..core.service_provider import scoped_service_provider
from ..models import Light, Sensor, Shutter
from .main import app

# Export des classes pour l'import
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
Module des commandes CLI pour la gestion des dispositifs.

Ce module contient toutes les commandes CLI pour ajouter, lister,
supprimer et voir le statut des dispositifs avec persistance.

Classes:
    DeviceCreateCommands: Commandes de création de dispositifs
    DeviceListCommands: Commandes de listage de dispositifs
    DeviceStateCommands: Commandes de gestion d'état de dispositifs
"""


class DeviceCreateCommands:
    """Commandes pour créer des dispositifs avec injection de dépendance."""

    @staticmethod
    def create_light(name: str, location: Optional[str] = None):
        """Crée une nouvelle lampe."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            light_id = controller.create_light(name, location)

            if light_id:
                light = controller.get_light(light_id)
                if light is not None:
                    print(f"✅ Lampe '{light.name}' créée avec l'ID: {light_id}")
                    if location:
                        print(f"   Emplacement: {location}")
                else:
                    print(f"✅ Lampe créée avec l'ID: {light_id}")
            else:
                print(f"❌ Erreur lors de la création de la lampe '{name}'")

    @staticmethod
    def create_shutter(name: str, location: Optional[str] = None):
        """Crée un nouveau volet."""
        session = create_session()
        try:
            controller = get_controller_factory().create_shutter_controller(session)
            shutter_id = controller.create_shutter(name, location)

            if shutter_id:
                shutter = controller.get_shutter(shutter_id)
                if shutter is not None:
                    print(f"✅ Volet '{shutter.name}' créé avec l'ID: {shutter_id}")
                    if location:
                        print(f"   Emplacement: {location}")
                else:
                    print(f"✅ Volet créé avec l'ID: {shutter_id}")
            else:
                print(f"❌ Erreur lors de la création du volet '{name}'")
        finally:
            session.close()

    @staticmethod
    def create_sensor(name: str, location: Optional[str] = None):
        """Crée un nouveau capteur."""
        session = create_session()
        try:
            controller = get_controller_factory().create_sensor_controller(session)
            sensor_id = controller.create_sensor(name, location)

            if sensor_id:
                sensor = controller.get_sensor(sensor_id)
                if sensor is not None:
                    print(f"✅ Capteur '{sensor.name}' créé avec l'ID: {sensor_id}")
                    if location:
                        print(f"   Emplacement: {location}")
                else:
                    print(f"✅ Capteur créé avec l'ID: {sensor_id}")
            else:
                print(f"❌ Erreur lors de la création du capteur '{name}'")
        finally:
            session.close()


class DeviceListCommands:
    """Commandes pour lister les dispositifs."""

    @staticmethod
    def list_all_devices():
        """Affiche la liste de tous les dispositifs."""
        session = create_session()
        try:
            controller = get_controller_factory().create_device_controller(session)
            devices = controller.get_all_devices()

            if not devices:
                print("Aucun dispositif enregistré.")
                return

            print(f"🏠 Dispositifs enregistrés ({len(devices)}):")
            print("-" * 50)

            for device in devices:
                device_type = type(device).__name__
                # Construire le statut selon le type
                if hasattr(device, "is_on"):
                    status = "ON" if device.is_on else "OFF"
                elif hasattr(device, "is_open"):
                    status = "OUVERT" if device.is_open else "FERMÉ"
                elif hasattr(device, "value"):
                    status = f"Valeur: {device.value}" if device.value else "Inactif"
                else:
                    status = "Inconnu"

                print(f"📱 {device.name}")
                print(f"   ID: {device.id}")
                print(f"   Type: {device_type}")
                print(f"   Emplacement: {device.location or 'Non défini'}")
                print(f"   Statut: {status}")
                print()
        finally:
            session.close()

    @staticmethod
    def list_lights():
        """Affiche la liste des lampes."""
        session = create_session()
        try:
            controller = get_controller_factory().create_light_controller(session)
            lights = controller.get_all_lights()

            if not lights:
                print("Aucune lampe enregistrée.")
                return

            print(f"💡 Lampes enregistrées ({len(lights)}):")
            print("-" * 40)

            for light in lights:
                status = "ON" if light.is_on else "OFF"
                print(f"💡 {light.name}")
                print(f"   ID: {light.id}")
                print(f"   Emplacement: {light.location or 'Non défini'}")
                print(f"   Statut: {status}")
                print()
        finally:
            session.close()

    @staticmethod
    def list_shutters():
        """Affiche la liste des volets."""
        session = create_session()
        try:
            controller = get_controller_factory().create_shutter_controller(session)
            shutters = controller.get_all_shutters()

            if not shutters:
                print("Aucun volet enregistré.")
                return

            print(f"🪟 Volets enregistrés ({len(shutters)}):")
            print("-" * 40)

            for shutter in shutters:
                status = "OUVERT" if shutter.is_open else "FERMÉ"
                print(f"🪟 {shutter.name}")
                print(f"   ID: {shutter.id}")
                print(f"   Emplacement: {shutter.location or 'Non défini'}")
                print(f"   Statut: {status}")
                print()
        finally:
            session.close()

    @staticmethod
    def list_sensors():
        """Affiche la liste des capteurs."""
        session = create_session()
        try:
            controller = get_controller_factory().create_sensor_controller(session)
            sensors = controller.get_all_sensors()

            if not sensors:
                print("Aucun capteur enregistré.")
                return

            print(f"📊 Capteurs enregistrés ({len(sensors)}):")
            print("-" * 40)

            for sensor in sensors:
                status = f"Valeur: {sensor.value}" if sensor.value else "Inactif"
                print(f"📊 {sensor.name}")
                print(f"   ID: {sensor.id}")
                print(f"   Emplacement: {sensor.location or 'Non défini'}")
                print(f"   Statut: {status}")
                print()
        finally:
            session.close()

    @staticmethod
    def show_device(device_id: str):
        """Affiche les détails d'un dispositif."""
        session = create_session()
        try:
            controller = get_controller_factory().create_device_controller(session)
            device = controller.get_device(device_id)

            if not device:
                print(f"❌ Dispositif avec l'ID {device_id} introuvable.")
                return

            device_type = type(device).__name__

            # Construire le statut selon le type
            if hasattr(device, "is_on"):
                status = "ON" if device.is_on else "OFF"
            elif hasattr(device, "is_open"):
                status = "OUVERT" if device.is_open else "FERMÉ"
            elif hasattr(device, "value"):
                status = f"Valeur: {device.value}" if device.value else "Inactif"
            else:
                status = "Inconnu"

            print(f"📱 {device.name}")
            print(f"   ID: {device.id}")
            print(f"   Type: {device_type}")
            print(f"   Emplacement: {device.location or 'Non défini'}")
            print(f"   Statut: {status}")
        finally:
            session.close()


class DeviceStateCommands:
    """Commandes pour gérer l'état des dispositifs."""

    @staticmethod
    def turn_on_light(light_id: str):
        """Allume une lampe."""
        session = create_session()
        try:
            controller = get_controller_factory().create_light_controller(session)
            success = controller.turn_on(light_id)

            if success:
                print(f"✅ Lampe {light_id} allumée.")
            else:
                print(f"❌ Échec de l'allumage de la lampe {light_id}.")
        finally:
            session.close()

    @staticmethod
    def turn_off_light(light_id: str):
        """Éteint une lampe."""
        session = create_session()
        try:
            controller = get_controller_factory().create_light_controller(session)
            success = controller.turn_off(light_id)

            if success:
                print(f"✅ Lampe {light_id} éteinte.")
            else:
                print(f"❌ Échec de l'extinction de la lampe {light_id}.")
        finally:
            session.close()

    @staticmethod
    def toggle_light(light_id: str):
        """Bascule l'état d'une lampe."""
        session = create_session()
        try:
            controller = get_controller_factory().create_light_controller(session)
            success = controller.toggle(light_id)

            if success:
                # Récupérer l'état actuel pour l'afficher
                light = controller.get_light(light_id)
                if light is not None:
                    status = "allumée" if light.is_on else "éteinte"
                    print(f"✅ Lampe {light_id} {status}.")
                else:
                    print(f"✅ Lampe {light_id} basculée.")
            else:
                print(f"❌ Échec du basculement de la lampe {light_id}.")
        finally:
            session.close()

    @staticmethod
    def open_shutter(shutter_id: str):
        """Ouvre un volet."""
        session = create_session()
        try:
            controller = get_controller_factory().create_shutter_controller(session)
            success = controller.open(shutter_id)

            if success:
                print(f"✅ Volet {shutter_id} ouvert.")
            else:
                print(f"❌ Échec de l'ouverture du volet {shutter_id}.")
        finally:
            session.close()

    @staticmethod
    def close_shutter(shutter_id: str):
        """Ferme un volet."""
        session = create_session()
        try:
            controller = get_controller_factory().create_shutter_controller(session)
            success = controller.close(shutter_id)

            if success:
                print(f"✅ Volet {shutter_id} fermé.")
            else:
                print(f"❌ Échec de la fermeture du volet {shutter_id}.")
        finally:
            session.close()

    @staticmethod
    def update_sensor_value(sensor_id: str, value: float):
        """Met à jour la valeur d'un capteur."""
        session = create_session()
        try:
            controller = get_controller_factory().create_sensor_controller(session)
            success = controller.update_value(sensor_id, value)

            if success:
                print(f"✅ Capteur {sensor_id} mis à jour avec la valeur {value}.")
            else:
                print(f"❌ Échec de la mise à jour du capteur {sensor_id}.")
        finally:
            session.close()

    @staticmethod
    def reset_sensor(sensor_id: str):
        """Remet à zéro un capteur."""
        session = create_session()
        try:
            controller = get_controller_factory().create_sensor_controller(session)
            success = controller.reset_value(sensor_id)

            if success:
                print(f"✅ Capteur {sensor_id} remis à zéro.")
            else:
                print(f"❌ Échec de la remise à zéro du capteur {sensor_id}.")
        finally:
            session.close()


# Commandes Typer (pour la compatibilité avec l'ancien système)
@app.command()
def device_list():
    """Affiche la liste des dispositifs."""
    DeviceListCommands.list_all_devices()


@app.command()
def device_add(device_type: str, name: str, location: Optional[str] = None):
    """
    Ajoute un nouveau dispositif.

    Args:
        device_type (str): Type de dispositif (light, shutter, sensor)
        name (str): Nom du dispositif
        location (str, optional): Emplacement du dispositif
    """
    device_type = device_type.lower()

    if device_type == "light":
        DeviceCreateCommands.create_light(name, location)
    elif device_type == "shutter":
        DeviceCreateCommands.create_shutter(name, location)
    elif device_type == "sensor":
        DeviceCreateCommands.create_sensor(name, location)
    else:
        print(f"❌ Type de dispositif non supporté: {device_type}")
        print("Types supportés: light, shutter, sensor")


@app.command()
def device_remove(device_id: str):
    """
    Supprime un dispositif par son ID.

    Args:
        device_id (int): Identifiant du dispositif à supprimer
    """
    session = create_session()
    try:
        controller = get_controller_factory().create_device_controller(session)

        # Tenter de supprimer selon le type
        device = controller.get_device(device_id)
        if not device:
            print(f"❌ Dispositif {device_id} non trouvé.")
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
            print(f"✅ Dispositif {device_id} supprimé avec succès.")
        else:
            print(f"❌ Erreur lors de la suppression du dispositif {device_id}.")
    finally:
        session.close()


@app.command()
def device_status(device_id: str):
    """
    Affiche le statut d'un dispositif.

    Args:
        device_id (int): Identifiant du dispositif
    """
    DeviceListCommands.show_device(device_id)
