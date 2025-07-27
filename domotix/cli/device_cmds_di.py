"""
Module des commandes CLI complètes avec injection de dépendance.

Ce module contient toutes les commandes CLI pour le système domotique
avec injection de dépendance moderne.

Commands:
    Générales: device_list, device_add, device_remove, device_status
    Lampes: light_on, light_off, light_toggle, lights_list, lights_on, lights_off
    Volets: shutter_open, shutter_close, shutter_toggle, shutter_position, shutters_list
    Capteurs: sensor_update, sensor_reset, sensors_list, sensors_reset
    Recherche: devices_by_location, device_search, locations_list
    Résumés: devices_summary, devices_on, devices_off
"""

from typing import Optional

import typer

from ..core.service_provider import scoped_service_provider
from ..models import Light, Sensor, Shutter

app = typer.Typer()


class DeviceCreateCommands:
    """Commandes pour créer des dispositifs avec injection de dépendance."""

    @staticmethod
    def create_light(name: str, location: Optional[str] = None):
        """Crée une nouvelle lampe avec gestion d'erreurs améliorée."""
        try:
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

        except ValueError as e:
            print(f"❌ Paramètres invalides: {e}")
            print("💡 Vérifiez que le nom n'est pas vide")

        except Exception as e:
            # Import local pour éviter les dépendances circulaires
            from domotix.core.error_handling import format_error_for_user

            # Affichage d'erreur avec informations contextuelles
            if hasattr(e, "error_code"):
                print(f"❌ Erreur [{e.error_code.value}]: {format_error_for_user(e)}")
            else:
                print(f"❌ Erreur lors de la création de la lampe '{name}': {e}")

            # Suggestions contextuelles selon le type d'erreur
            if "contrainte" in str(e).lower():
                print("💡 Un dispositif avec ce nom existe peut-être déjà")
            elif "connexion" in str(e).lower():
                print("💡 Vérifiez la connexion à la base de données")
            elif "validation" in str(e).lower():
                print("💡 Vérifiez que tous les paramètres sont corrects")

    @staticmethod
    def create_shutter(name: str, location: Optional[str] = None):
        """Crée un nouveau volet."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
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

    @staticmethod
    def create_sensor(name: str, location: Optional[str] = None):
        """Crée un nouveau capteur."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
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


class DeviceListCommands:
    """Commandes pour lister les dispositifs avec injection de dépendance."""

    @staticmethod
    def list_all_devices():
        """Affiche la liste de tous les dispositifs."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
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

    @staticmethod
    def list_lights():
        """Affiche la liste de toutes les lampes."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
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

    @staticmethod
    def list_shutters():
        """Affiche la liste de tous les volets."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
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

    @staticmethod
    def list_sensors():
        """Affiche la liste de tous les capteurs."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
            sensors = controller.get_all_sensors()

            if not sensors:
                print("Aucun capteur enregistré.")
                return

            print(f"🌡️ Capteurs enregistrés ({len(sensors)}):")
            print("-" * 40)

            for sensor in sensors:
                status = f"Valeur: {sensor.value}" if sensor.value else "Inactif"
                print(f"🌡️ {sensor.name}")
                print(f"   ID: {sensor.id}")
                print(f"   Emplacement: {sensor.location or 'Non défini'}")
                print(f"   Statut: {status}")
                print()

    @staticmethod
    def show_device(device_id: str):
        """Affiche les détails d'un dispositif."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
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

    @staticmethod
    def list_devices_by_location(location: str):
        """Affiche tous les dispositifs d'un emplacement."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            # Filtrer par emplacement
            filtered_devices = [
                device
                for device in devices
                if device.location and location.lower() in device.location.lower()
            ]

            if not filtered_devices:
                print(f"Aucun dispositif trouvé pour l'emplacement '{location}'.")
                return

            print(f"🏠 Dispositifs dans '{location}' ({len(filtered_devices)}):")
            print("-" * 50)

            for device in filtered_devices:
                device_type = type(device).__name__
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
                print(f"   Statut: {status}")
                print()

    @staticmethod
    def search_devices(name: str):
        """Recherche des dispositifs par nom."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            # Recherche par nom (insensible à la casse)
            found_devices = [
                device for device in devices if name.lower() in device.name.lower()
            ]

            if not found_devices:
                print(f"Aucun dispositif trouvé avec le nom '{name}'.")
                return

            print(f"🔍 Résultats de recherche pour '{name}' ({len(found_devices)}):")
            print("-" * 50)

            for device in found_devices:
                device_type = type(device).__name__
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

    @staticmethod
    def list_locations():
        """Affiche la liste de tous les emplacements."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            # Extraire les emplacements uniques
            locations = set()
            for device in devices:
                if device.location:
                    locations.add(device.location)

            if not locations:
                print("Aucun emplacement défini.")
                return

            sorted_locations = sorted(locations)
            print(f"📍 Emplacements ({len(sorted_locations)}):")
            print("-" * 30)

            for location in sorted_locations:
                # Compter les dispositifs par emplacement
                device_count = sum(
                    1 for device in devices if device.location == location
                )
                print(f"📍 {location} ({device_count} dispositifs)")

    @staticmethod
    def show_devices_summary():
        """Affiche un résumé de tous les dispositifs."""
        with scoped_service_provider.create_scope() as provider:
            device_controller = provider.get_device_controller()
            light_controller = provider.get_light_controller()
            shutter_controller = provider.get_shutter_controller()
            sensor_controller = provider.get_sensor_controller()

            # Récupérer toutes les données
            all_devices = device_controller.get_all_devices()
            lights = light_controller.get_all_lights()
            shutters = shutter_controller.get_all_shutters()
            sensors = sensor_controller.get_all_sensors()

            print("📊 RÉSUMÉ DES DISPOSITIFS")
            print("=" * 40)
            print(f"Total dispositifs: {len(all_devices)}")
            print(f"  💡 Lampes: {len(lights)}")
            print(f"  🪟 Volets: {len(shutters)}")
            print(f"  🌡️ Capteurs: {len(sensors)}")
            print()

            if lights:
                lights_on = sum(1 for light in lights if light.is_on)
                print(f"💡 Lampes allumées: {lights_on}/{len(lights)}")

            if shutters:
                shutters_open = sum(1 for shutter in shutters if shutter.is_open)
                print(f"🪟 Volets ouverts: {shutters_open}/{len(shutters)}")

            if sensors:
                active_sensors = sum(
                    1 for sensor in sensors if sensor.value is not None
                )
                print(f"🌡️ Capteurs actifs: {active_sensors}/{len(sensors)}")

    @staticmethod
    def list_active_devices():
        """Affiche tous les dispositifs actifs."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            active_devices = []
            for device in devices:
                if hasattr(device, "is_on") and device.is_on:
                    active_devices.append((device, "Allumée"))
                elif hasattr(device, "is_open") and device.is_open:
                    active_devices.append((device, "Ouvert"))
                elif hasattr(device, "value") and device.value is not None:
                    active_devices.append((device, f"Valeur: {device.value}"))

            if not active_devices:
                print("Aucun dispositif actif.")
                return

            print(f"🟢 Dispositifs actifs ({len(active_devices)}):")
            print("-" * 40)

            for device, status in active_devices:
                device_type = type(device).__name__
                print(f"📱 {device.name} ({device_type})")
                print(f"   ID: {device.id}")
                print(f"   Emplacement: {device.location or 'Non défini'}")
                print(f"   Statut: {status}")
                print()

    @staticmethod
    def list_inactive_devices():
        """Affiche tous les dispositifs inactifs."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_device_controller()
            devices = controller.get_all_devices()

            inactive_devices = []
            for device in devices:
                if hasattr(device, "is_on") and not device.is_on:
                    inactive_devices.append((device, "Éteinte"))
                elif hasattr(device, "is_open") and not device.is_open:
                    inactive_devices.append((device, "Fermé"))
                elif hasattr(device, "value") and device.value is None:
                    inactive_devices.append((device, "Inactif"))

            if not inactive_devices:
                print("Aucun dispositif inactif.")
                return

            print(f"🔴 Dispositifs inactifs ({len(inactive_devices)}):")
            print("-" * 40)

            for device, status in inactive_devices:
                device_type = type(device).__name__
                print(f"📱 {device.name} ({device_type})")
                print(f"   ID: {device.id}")
                print(f"   Emplacement: {device.location or 'Non défini'}")
                print(f"   Statut: {status}")
                print()


class DeviceStateCommands:
    """Commandes pour gérer l'état des dispositifs avec injection de dépendance."""

    @staticmethod
    def turn_on_light(light_id: str):
        """Allume une lampe avec gestion d'erreurs améliorée."""
        try:
            with scoped_service_provider.create_scope() as provider:
                controller = provider.get_light_controller()
                success = controller.turn_on(light_id)

                if success:
                    print(f"✅ Lampe {light_id} allumée.")
                else:
                    print(f"❌ Échec de l'allumage de la lampe {light_id}.")
                    print("💡 Vérifiez que l'ID est correct et que la lampe existe")

        except ValueError as e:
            print(f"❌ ID invalide: {e}")
            print("💡 L'ID doit être un identifiant valide non vide")

        except Exception as e:
            from domotix.core.error_handling import format_error_for_user

            if hasattr(e, "error_code"):
                print(f"❌ Erreur [{e.error_code.value}]: {format_error_for_user(e)}")
            else:
                print(f"❌ Erreur lors de l'allumage de la lampe {light_id}: {e}")

            # Suggestions selon le type d'erreur
            if "not found" in str(e).lower() or "introuvable" in str(e).lower():
                print("💡 Utilisez 'device-list' pour voir les dispositifs disponibles")
            elif "database" in str(e).lower():
                print(
                    "💡 Problème de base de données, réessayez dans quelques instants"
                )

    @staticmethod
    def turn_off_light(light_id: str):
        """Éteint une lampe."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            success = controller.turn_off(light_id)

            if success:
                print(f"✅ Lampe {light_id} éteinte.")
            else:
                print(f"❌ Échec de l'extinction de la lampe {light_id}.")

    @staticmethod
    def toggle_light(light_id: str):
        """Bascule l'état d'une lampe."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
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

    @staticmethod
    def turn_on_all_lights():
        """Allume toutes les lampes."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            lights = controller.get_all_lights()

            if not lights:
                print("Aucune lampe trouvée.")
                return

            success_count = 0
            for light in lights:
                if controller.turn_on(light.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(lights)} lampes allumées.")

    @staticmethod
    def turn_off_all_lights():
        """Éteint toutes les lampes."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_light_controller()
            lights = controller.get_all_lights()

            if not lights:
                print("Aucune lampe trouvée.")
                return

            success_count = 0
            for light in lights:
                if controller.turn_off(light.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(lights)} lampes éteintes.")

    @staticmethod
    def open_shutter(shutter_id: str):
        """Ouvre un volet."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            success = controller.open(shutter_id)

            if success:
                print(f"✅ Volet {shutter_id} ouvert.")
            else:
                print(f"❌ Échec de l'ouverture du volet {shutter_id}.")

    @staticmethod
    def close_shutter(shutter_id: str):
        """Ferme un volet."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            success = controller.close(shutter_id)

            if success:
                print(f"✅ Volet {shutter_id} fermé.")
            else:
                print(f"❌ Échec de la fermeture du volet {shutter_id}.")

    @staticmethod
    def toggle_shutter(shutter_id: str):
        """Bascule l'état d'un volet."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            shutter = controller.get_shutter(shutter_id)

            if not shutter:
                print(f"❌ Volet {shutter_id} non trouvé.")
                return

            # Basculer selon l'état actuel
            if shutter.is_open:
                success = controller.close(shutter_id)
                action = "fermé"
            else:
                success = controller.open(shutter_id)
                action = "ouvert"

            if success:
                print(f"✅ Volet {shutter_id} {action}.")
            else:
                print(f"❌ Échec du basculement du volet {shutter_id}.")

    @staticmethod
    def set_shutter_position(shutter_id: str, position: int):
        """Définit la position d'un volet."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            success = controller.set_position(shutter_id, position)

            if success:
                print(f"✅ Volet {shutter_id} positionné à {position}%.")
            else:
                print(f"❌ Échec du positionnement du volet {shutter_id}.")

    @staticmethod
    def open_all_shutters():
        """Ouvre tous les volets."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            shutters = controller.get_all_shutters()

            if not shutters:
                print("Aucun volet trouvé.")
                return

            success_count = 0
            for shutter in shutters:
                if controller.open(shutter.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(shutters)} volets ouverts.")

    @staticmethod
    def close_all_shutters():
        """Ferme tous les volets."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_shutter_controller()
            shutters = controller.get_all_shutters()

            if not shutters:
                print("Aucun volet trouvé.")
                return

            success_count = 0
            for shutter in shutters:
                if controller.close(shutter.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(shutters)} volets fermés.")

    @staticmethod
    def update_sensor_value(sensor_id: str, value: float):
        """Met à jour la valeur d'un capteur."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
            success = controller.update_value(sensor_id, value)

            if success:
                print(f"✅ Capteur {sensor_id} mis à jour avec la valeur {value}.")
            else:
                print(f"❌ Échec de la mise à jour du capteur {sensor_id}.")

    @staticmethod
    def reset_sensor(sensor_id: str):
        """Remet à zéro un capteur."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
            success = controller.reset_value(sensor_id)

            if success:
                print(f"✅ Capteur {sensor_id} remis à zéro.")
            else:
                print(f"❌ Échec de la remise à zéro du capteur {sensor_id}.")

    @staticmethod
    def reset_all_sensors():
        """Remet à zéro tous les capteurs."""
        with scoped_service_provider.create_scope() as provider:
            controller = provider.get_sensor_controller()
            sensors = controller.get_all_sensors()

            if not sensors:
                print("Aucun capteur trouvé.")
                return

            success_count = 0
            for sensor in sensors:
                if controller.reset_value(sensor.id):
                    success_count += 1

            print(f"✅ {success_count}/{len(sensors)} capteurs remis à zéro.")


# === COMMANDES TYPER ===


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
        device_id (str): Identifiant du dispositif à supprimer
    """
    with scoped_service_provider.create_scope() as provider:
        controller = provider.get_device_controller()

        # Tenter de supprimer selon le type
        device = controller.get_device(device_id)
        if not device:
            print(f"❌ Dispositif {device_id} non trouvé.")
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
            print(f"✅ Dispositif {device_id} supprimé avec succès.")
        else:
            print(f"❌ Erreur lors de la suppression du dispositif {device_id}.")


@app.command()
def device_status(device_id: str):
    """
    Affiche le statut d'un dispositif.

    Args:
        device_id (str): Identifiant du dispositif
    """
    DeviceListCommands.show_device(device_id)


# === COMMANDES POUR LES LAMPES ===


@app.command()
def light_on(light_id: str):
    """
    Allume une lampe.

    Args:
        light_id (str): Identifiant de la lampe
    """
    DeviceStateCommands.turn_on_light(light_id)


@app.command()
def light_off(light_id: str):
    """
    Éteint une lampe.

    Args:
        light_id (str): Identifiant de la lampe
    """
    DeviceStateCommands.turn_off_light(light_id)


@app.command()
def light_toggle(light_id: str):
    """
    Bascule l'état d'une lampe (allumée <-> éteinte).

    Args:
        light_id (str): Identifiant de la lampe
    """
    DeviceStateCommands.toggle_light(light_id)


@app.command()
def lights_list():
    """Affiche la liste de toutes les lampes."""
    DeviceListCommands.list_lights()


@app.command()
def lights_on():
    """Allume toutes les lampes."""
    DeviceStateCommands.turn_on_all_lights()


@app.command()
def lights_off():
    """Éteint toutes les lampes."""
    DeviceStateCommands.turn_off_all_lights()


# === COMMANDES POUR LES VOLETS ===


@app.command()
def shutter_open(shutter_id: str):
    """
    Ouvre un volet.

    Args:
        shutter_id (str): Identifiant du volet
    """
    DeviceStateCommands.open_shutter(shutter_id)


@app.command()
def shutter_close(shutter_id: str):
    """
    Ferme un volet.

    Args:
        shutter_id (str): Identifiant du volet
    """
    DeviceStateCommands.close_shutter(shutter_id)


@app.command()
def shutter_toggle(shutter_id: str):
    """
    Bascule l'état d'un volet (ouvert <-> fermé).

    Args:
        shutter_id (str): Identifiant du volet
    """
    DeviceStateCommands.toggle_shutter(shutter_id)


@app.command()
def shutter_position(shutter_id: str, position: int):
    """
    Définit la position d'un volet.

    Args:
        shutter_id (str): Identifiant du volet
        position (int): Position en pourcentage (0-100)
    """
    DeviceStateCommands.set_shutter_position(shutter_id, position)


@app.command()
def shutters_list():
    """Affiche la liste de tous les volets."""
    DeviceListCommands.list_shutters()


@app.command()
def shutters_open():
    """Ouvre tous les volets."""
    DeviceStateCommands.open_all_shutters()


@app.command()
def shutters_close():
    """Ferme tous les volets."""
    DeviceStateCommands.close_all_shutters()


# === COMMANDES POUR LES CAPTEURS ===


@app.command()
def sensor_update(sensor_id: str, value: float):
    """
    Met à jour la valeur d'un capteur.

    Args:
        sensor_id (str): Identifiant du capteur
        value (float): Nouvelle valeur du capteur
    """
    DeviceStateCommands.update_sensor_value(sensor_id, value)


@app.command()
def sensor_reset(sensor_id: str):
    """
    Remet à zéro un capteur.

    Args:
        sensor_id (str): Identifiant du capteur
    """
    DeviceStateCommands.reset_sensor(sensor_id)


@app.command()
def sensors_list():
    """Affiche la liste de tous les capteurs."""
    DeviceListCommands.list_sensors()


@app.command()
def sensors_reset():
    """Remet à zéro tous les capteurs."""
    DeviceStateCommands.reset_all_sensors()


# === COMMANDES DE RECHERCHE ET FILTRAGE ===


@app.command()
def devices_by_location(location: str):
    """
    Affiche tous les dispositifs d'un emplacement.

    Args:
        location (str): Nom de l'emplacement
    """
    DeviceListCommands.list_devices_by_location(location)


@app.command()
def device_search(name: str):
    """
    Recherche des dispositifs par nom.

    Args:
        name (str): Nom ou partie du nom à rechercher
    """
    DeviceListCommands.search_devices(name)


@app.command()
def locations_list():
    """Affiche la liste de tous les emplacements."""
    DeviceListCommands.list_locations()


# === COMMANDES D'ÉTAT ET STATISTIQUES ===


@app.command()
def devices_summary():
    """Affiche un résumé de tous les dispositifs."""
    DeviceListCommands.show_devices_summary()


@app.command()
def devices_on():
    """Affiche tous les dispositifs allumés/ouverts/actifs."""
    DeviceListCommands.list_active_devices()


@app.command()
def devices_off():
    """Affiche tous les dispositifs éteints/fermés/inactifs."""
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
