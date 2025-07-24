"""
Module des commandes CLI pour la gestion des dispositifs.

Ce module contient toutes les commandes CLI pour ajouter, lister,
supprimer et voir le statut des dispositifs.

Commands:
    device_list: Affiche la liste des dispositifs
    device_add: Ajoute un nouveau dispositif
    device_remove: Supprime un dispositif
    device_status: Affiche le statut d'un dispositif
"""

from typing import Union

from ..core import StateManager
from ..models import Light, Sensor, Shutter
from .main import app


@app.command()
def device_list():
    """Affiche la liste des devices."""
    state_manager = StateManager()
    devices = state_manager.get_devices()

    if not devices:
        print("Aucun dispositif enregistré.")
        return

    print(f"🏠 Dispositifs enregistrés ({state_manager.get_device_count()}):")
    print("-" * 50)

    for device_id, device in devices.items():
        device_type = type(device).__name__
        # Utiliser get_state() et construire le statut
        state = device.get_state()
        if hasattr(device, "is_on"):
            status = "ON" if device.is_on else "OFF"
        elif hasattr(device, "position"):
            status = f"Position: {device.position}%"
        else:
            status = str(state)
        print(f"📱 {device.name}")
        print(f"   ID: {device_id}")
        print(f"   Type: {device_type}")
        print(f"   Statut: {status}")
        print()


@app.command()
def device_add(device_type: str, name: str):
    """
    Ajoute un nouveau dispositif.

    Args:
        device_type (str): Type de dispositif (light, shutter, sensor)
        name (str): Nom du dispositif
    """
    state_manager = StateManager()

    device_type = device_type.lower()

    device: Union[Light, Shutter, Sensor]
    if device_type == "light":
        device = Light(name=name)
    elif device_type == "shutter":
        device = Shutter(name=name)
    elif device_type == "sensor":
        device = Sensor(name=name)
    else:
        print(f"❌ Type de dispositif non supporté: {device_type}")
        print("Types supportés: light, shutter, sensor")
        return

    device_id = state_manager.register_device(device)
    print(f"✅ Dispositif '{name}' ajouté avec l'ID: {device_id}")


@app.command()
def device_remove(device_id: str):
    """
    Supprime un dispositif par son ID.

    Args:
        device_id (str): Identifiant du dispositif à supprimer
    """
    state_manager = StateManager()

    if state_manager.unregister_device(device_id):
        print(f"✅ Dispositif {device_id} supprimé avec succès.")
    else:
        print(f"❌ Dispositif {device_id} non trouvé.")


@app.command()
def device_status(device_id: str):
    """
    Affiche le statut d'un dispositif.

    Args:
        device_id (str): Identifiant du dispositif
    """
    state_manager = StateManager()

    try:
        device = state_manager.get_device(device_id)
        print(f"📱 {device.name}")
        print(f"   Type: {type(device).__name__}")
        # Utiliser get_state() au lieu de get_status()
        state = device.get_state()
        if hasattr(device, "is_on"):
            status = "ON" if device.is_on else "OFF"
        elif hasattr(device, "position"):
            status = f"Position: {device.position}%"
        else:
            status = str(state)
        print(f"   Statut: {status}")
    except KeyError:
        print(f"❌ Dispositif {device_id} non trouvé.")
