"""
Factories pour la génération de données de test avec Factory Boy.

Ce module fournit des factories Factory Boy pour créer facilement
des instances de test des modèles Domotix (Light, Sensor, Shutter).

Compatible avec les vraies signatures des modèles Domotix.

Usage:
    from tests.fixtures.device_factories import LightFactory, SensorFactory

    # Créer un appareil avec des données aléatoires
    light = LightFactory()

    # Créer avec des attributs spécifiques
    sensor = SensorFactory(name="Mon capteur", location="Salon")

    # Créer une configuration complète de maison de test
    devices = create_test_home_setup()

Voir tests/fixtures/examples.py pour plus d'exemples d'utilisation.
"""

import factory  # pylint: disable=import-error
from faker import Faker  # pylint: disable=import-error

from domotix.models.light import Light  # pylint: disable=import-error
from domotix.models.sensor import Sensor  # pylint: disable=import-error
from domotix.models.shutter import Shutter  # pylint: disable=import-error

fake = Faker("fr_FR")  # Données en français

# Constantes pour éviter la duplication
STANDARD_LOCATIONS = ("Salon", "Chambre", "Cuisine", "Bureau", "Salle de bain")


class LightFactory(factory.Factory):
    """Factory pour créer des lampes de test."""

    class Meta:
        model = Light

    name = factory.LazyFunction(lambda: f"Lampe {fake.word()}")
    location = factory.LazyFunction(
        lambda: fake.random_element(elements=STANDARD_LOCATIONS)
    )


class ShutterFactory(factory.Factory):
    """Factory pour créer des volets de test."""

    class Meta:
        model = Shutter

    name = factory.LazyFunction(lambda: f"Volet {fake.word()}")
    location = factory.LazyFunction(
        lambda: fake.random_element(elements=STANDARD_LOCATIONS)
    )


class SensorFactory(factory.Factory):
    """Factory pour créer des capteurs de test."""

    class Meta:
        model = Sensor

    name = factory.LazyFunction(lambda: f"Capteur {fake.word()}")
    location = factory.LazyFunction(
        lambda: fake.random_element(elements=STANDARD_LOCATIONS)
    )


class TemperatureSensorFactory(SensorFactory):
    """Factory spécialisée pour capteurs de température."""

    name = factory.LazyFunction(lambda: "Capteur Température")


class HumiditySensorFactory(SensorFactory):
    """Factory spécialisée pour capteurs d'humidité."""

    name = factory.LazyFunction(lambda: "Capteur Humidité")


class MotionSensorFactory(SensorFactory):
    """Factory spécialisée pour capteurs de mouvement."""

    name = factory.LazyFunction(lambda: "Détecteur Mouvement")


def create_test_home_setup():
    """Crée une configuration de maison de test réaliste."""
    return [
        # Lumières
        LightFactory(name="Lampe salon", location="Salon"),
        LightFactory(name="Plafonnier chambre", location="Chambre"),
        LightFactory(name="Spot cuisine", location="Cuisine"),
        LightFactory(name="Lampe bureau", location="Bureau"),
        # Volets
        ShutterFactory(name="Volet salon", location="Salon"),
        ShutterFactory(name="Volet chambre", location="Chambre"),
        ShutterFactory(name="Store cuisine", location="Cuisine"),
        # Capteurs
        TemperatureSensorFactory(name="Thermomètre salon", location="Salon"),
        TemperatureSensorFactory(name="Thermomètre chambre", location="Chambre"),
        HumiditySensorFactory(
            name="Hygromètre salle de bain", location="Salle de bain"
        ),
        MotionSensorFactory(name="Détecteur entrée", location="Entrée"),
        MotionSensorFactory(name="Détecteur garage", location="Garage"),
    ]


def create_batch_devices(device_type: str, count: int = 10):
    """Crée un lot d'appareils du type spécifié."""
    factory_map = {
        "light": LightFactory,
        "shutter": ShutterFactory,
        "sensor": SensorFactory,
        "temperature": TemperatureSensorFactory,
        "humidity": HumiditySensorFactory,
        "motion": MotionSensorFactory,
    }

    factory_class = factory_map.get(device_type.lower())
    if not factory_class:
        raise ValueError(f"Type d'appareil non supporté: {device_type}")

    return [factory_class() for _ in range(count)]


def create_random_home(num_rooms: int = 5, devices_per_room: int = 3):
    """Génère aléatoirement une configuration de maison."""
    rooms = [f"Pièce {i + 1}" for i in range(num_rooms)]
    devices = []

    for room in rooms:
        for _ in range(devices_per_room):
            device_type = fake.random_element(elements=["light", "shutter", "sensor"])
            factory_class = {
                "light": LightFactory,
                "shutter": ShutterFactory,
                "sensor": SensorFactory,
            }[device_type]

            devices.append(factory_class(location=room))

    return devices
