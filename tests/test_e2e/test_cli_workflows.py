"""
Tests End-to-End (E2E) pour les workflows CLI de Domotix.


Ces tests valident l'ensemble du parcours utilisateur depuis les commandes
CLI jusqu'à la persistance en base de données, en simulant des scenarios
d'utilisation réels.

Test Coverage:
    - Création de dispositifs via CLI
    - Listage et recherche de dispositifs
    - Contrôle d'état des dispositifs
    - Suppression de dispositifs
    - Workflows complets utilisateur
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from domotix.core.database import create_session, create_tables
from domotix.repositories.device_repository import DeviceRepository


class CliTestRunner:
    """Helper pour exécuter les commandes CLI en mode test."""

    def __init__(self, test_db_path):
        """Initialise le runner CLI avec le chemin de la base de données de test."""
        self.test_db_path = test_db_path
        self.project_root = Path(__file__).parent.parent.parent
        self.cli_script = self.project_root / "domotix" / "cli" / "main.py"

    def run_cli_command(self, args):
        """Execute domotix CLI command."""
        # Utiliser Poetry pour exécuter avec les bonnes dépendances
        cmd = ["poetry", "run", "python", "-m", "domotix.cli.main"] + args
        env = {**os.environ, "DOMOTIX_DB_PATH": self.test_db_path}

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
                check=False,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)


@pytest.fixture
def cli_runner(test_db_path):
    """Fixture qui fournit un runner CLI configuré."""
    return CliTestRunner(test_db_path)


@pytest.fixture
def test_db_path():
    """Fixture pour créer une base de données temporaire isolée pour chaque test."""
    # Créer une base de données temporaire unique pour ce test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    # Configurer l'environnement
    original_db_path = os.environ.get("DOMOTIX_DB_PATH")
    os.environ["DOMOTIX_DB_PATH"] = db_path

    # Forcer la reconfiguration de la base de données
    from domotix.core.database import reconfigure_database

    reconfigure_database()
    create_tables()

    yield db_path

    # Nettoyage après le test
    try:
        os.unlink(db_path)
    except OSError:
        pass

    # Restaurer l'environnement
    if original_db_path:
        os.environ["DOMOTIX_DB_PATH"] = original_db_path
    else:
        os.environ.pop("DOMOTIX_DB_PATH", None)

    # Forcer une nouvelle reconfiguration
    reconfigure_database()


class TestDeviceCreationWorkflows:
    """Tests E2E pour les workflows de création de dispositifs."""

    def test_create_light_via_cli(self, cli_runner, test_db_path):
        """Test E2E: Création d'une lampe via CLI."""
        # Étape 1: Créer une lampe
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "light", "Lampe Salon", "--location", "Salon"]
        )

        # Vérifier que la commande a réussi
        assert return_code == 0, f"CLI failed: {stderr}"
        assert "Lampe 'Lampe Salon' créée" in stdout
        assert "Salon" in stdout

        # Étape 2: Vérifier que la lampe est dans la base
        session = create_session()
        try:
            repo = DeviceRepository(session)
            devices = repo.find_all()

            # Vérifier qu'il y a exactement un dispositif
            assert len(devices) == 1

            device = devices[0]
            assert device.name == "Lampe Salon"
            assert device.location == "Salon"
            assert device.device_type.value == "LIGHT"
        finally:
            session.close()

    def test_create_shutter_via_cli(self, cli_runner, test_db_path):
        """Test E2E: Création d'un volet via CLI."""
        # Créer un volet
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "shutter", "Volet Chambre", "--location", "Chambre"]
        )

        assert return_code == 0, f"CLI failed: {stderr}"
        assert "Volet 'Volet Chambre' créé" in stdout

        # Vérifier la persistance
        session = create_session()
        try:
            repo = DeviceRepository(session)
            devices = repo.find_by_location("Chambre")

            assert len(devices) == 1
            assert devices[0].name == "Volet Chambre"
            assert devices[0].device_type.value == "SHUTTER"
        finally:
            session.close()

    def test_create_sensor_via_cli(self, cli_runner, test_db_path):
        """Test E2E: Création d'un capteur via CLI."""
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "sensor", "Capteur Température", "--location", "Cuisine"]
        )

        assert return_code == 0, f"CLI failed: {stderr}"
        assert "Capteur 'Capteur Température' créé" in stdout

        # Vérifier la persistance
        session = create_session()
        try:
            repo = DeviceRepository(session)
            devices = repo.search_by_name("Température")

            assert len(devices) == 1
            assert devices[0].name == "Capteur Température"
            assert devices[0].device_type.value == "SENSOR"
        finally:
            session.close()


class TestDeviceListingWorkflows:
    """Tests E2E pour les workflows de listage de dispositifs."""

    def test_list_all_devices_workflow(self, cli_runner, test_db_path):
        """Test E2E: Workflow complet de création et listage."""
        # Étape 1: Créer plusieurs dispositifs
        devices_to_create = [
            (["device-add", "light", "Lampe1", "--location", "Salon"], "Lampe1"),
            (["device-add", "shutter", "Volet1", "--location", "Chambre"], "Volet1"),
            (["device-add", "sensor", "Capteur1", "--location", "Cuisine"], "Capteur1"),
        ]

        for cmd, expected_name in devices_to_create:
            return_code, stdout, stderr = cli_runner.run_cli_command(cmd)
            assert return_code == 0, f"Failed to create {expected_name}: {stderr}"
            assert expected_name in stdout

        # Étape 2: Lister tous les dispositifs
        return_code, stdout, stderr = cli_runner.run_cli_command(["device-list"])

        assert return_code == 0, f"List command failed: {stderr}"

        # Vérifier que tous les dispositifs créés apparaissent dans la liste
        for _, expected_name in devices_to_create:
            assert expected_name in stdout

        # Vérifier que les localisations apparaissent
        assert "Salon" in stdout
        assert "Chambre" in stdout
        assert "Cuisine" in stdout

    def test_list_devices_by_type(self, cli_runner, test_db_path):
        """Test E2E: Listage de dispositifs par type."""
        # Créer des dispositifs de différents types
        cli_runner.run_cli_command(["device-add", "light", "Lampe1"])
        cli_runner.run_cli_command(["device-add", "light", "Lampe2"])
        cli_runner.run_cli_command(["device-add", "shutter", "Volet1"])

        # Lister seulement les lampes
        return_code, stdout, stderr = cli_runner.run_cli_command(["lights-list"])

        assert return_code == 0, f"List lights failed: {stderr}"
        assert "Lampe1" in stdout
        assert "Lampe2" in stdout
        assert "Volet1" not in stdout  # Les volets ne doivent pas apparaître


class TestDeviceStateWorkflows:
    """Tests E2E pour les workflows de contrôle d'état."""

    def test_light_control_workflow(self, cli_runner, test_db_path):
        """Test E2E: Workflow complet de contrôle d'une lampe."""
        # Étape 1: Créer une lampe
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "light", "Lampe Test"]
        )
        assert return_code == 0

        # Extraire l'ID de la lampe créée (supposé être dans stdout)
        lines = stdout.strip().split("\n")
        device_id = None
        for line in lines:
            if "ID:" in line:
                device_id = line.split("ID:")[-1].strip()
                break

        assert device_id is not None, "Device ID not found in creation output"

        # Étape 2: Allumer la lampe
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["light-on", device_id]
        )
        assert return_code == 0, f"Turn on failed: {stderr}"

        # Étape 3: Vérifier l'état via CLI
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-status", device_id]
        )
        assert return_code == 0, f"Status check failed: {stderr}"
        assert "ON" in stdout.upper() or "allumé" in stdout.lower()

        # Étape 4: Éteindre la lampe
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["light-off", device_id]
        )
        assert return_code == 0, f"Turn off failed: {stderr}"

        # Étape 5: Vérifier l'état final
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-status", device_id]
        )
        assert return_code == 0, f"Final status check failed: {stderr}"
        assert "OFF" in stdout.upper() or "éteint" in stdout.lower()


class TestCompleteUserWorkflows:
    """Tests E2E pour des workflows utilisateur complets et réalistes."""

    def test_home_automation_scenario(self, cli_runner, test_db_path):
        """
        Test E2E: Scenario complet d'automatisation maison.

        Simule un utilisateur qui configure son système domotique complet.
        """
        # Scenario: Configuration d'un appartement avec salon, chambre, cuisine

        # Phase 1: Configuration du salon
        salon_devices = [
            ["device-add", "light", "Lampe Principale", "--location", "Salon"],
            ["device-add", "light", "Lampe d'Appoint", "--location", "Salon"],
            ["device-add", "shutter", "Volet Salon", "--location", "Salon"],
        ]

        for cmd in salon_devices:
            return_code, stdout, stderr = cli_runner.run_cli_command(cmd)
            assert return_code == 0, f"Failed salon setup: {stderr}"

        # Phase 2: Configuration de la chambre
        chambre_devices = [
            ["device-add", "light", "Lampe Chevet", "--location", "Chambre"],
            ["device-add", "shutter", "Volet Chambre", "--location", "Chambre"],
            ["device-add", "sensor", "Capteur Température", "--location", "Chambre"],
        ]

        for cmd in chambre_devices:
            return_code, stdout, stderr = cli_runner.run_cli_command(cmd)
            assert return_code == 0, f"Failed chambre setup: {stderr}"

        # Phase 3: Vérification de l'installation complète
        return_code, stdout, stderr = cli_runner.run_cli_command(["device-list"])
        assert return_code == 0

        # Vérifier que tous les dispositifs sont présents
        expected_devices = [
            "Lampe Principale",
            "Lampe d'Appoint",
            "Volet Salon",
            "Lampe Chevet",
            "Volet Chambre",
            "Capteur Température",
        ]

        for device_name in expected_devices:
            assert device_name in stdout, f"Device {device_name} not found in listing"

        # Phase 4: Test de contrôle groupé par location
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["devices-by-location", "Salon"]
        )
        assert return_code == 0
        assert "Lampe Principale" in stdout
        assert "Lampe d'Appoint" in stdout
        assert "Volet Salon" in stdout
        assert "Lampe Chevet" not in stdout  # Ne doit pas être dans le salon

        # Vérifier la persistance finale en base
        session = create_session()
        try:
            repo = DeviceRepository(session)
            all_devices = repo.find_all()

            assert len(all_devices) == 6  # 6 dispositifs créés

            salon_devices_db = repo.find_by_location("Salon")
            assert len(salon_devices_db) == 3

            chambre_devices_db = repo.find_by_location("Chambre")
            assert len(chambre_devices_db) == 3

        finally:
            session.close()

    def test_error_handling_workflow(self, cli_runner, test_db_path):
        """Test E2E: Gestion d'erreurs dans les workflows."""
        # Test 1: Créer un dispositif avec un nom vide (peut être accepté)
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "light", ""]
        )
        # Un nom vide pourrait être accepté, on teste juste que ça ne crash pas

        # Test 2: Essayer de contrôler un dispositif inexistant
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["light-on", "inexistent-id-12345"]
        )
        # Vérifier qu'une erreur est reportée (dans stdout ou stderr)
        assert (
            "Échec" in stdout or "erreur" in stderr.lower() or "error" in stderr.lower()
        )

        # Test 3: Créer un dispositif avec un type invalide
        return_code, stdout, stderr = cli_runner.run_cli_command(
            ["device-add", "invalid-type", "Test Device"]
        )
        # Vérifier que le type invalide est rejeté
        assert "non supporté" in stdout or "not supported" in stderr or return_code != 0

        # Vérifier qu'aucun dispositif invalide n'a été créé
        session = create_session()
        try:
            repo = DeviceRepository(session)
            devices = repo.find_all()
            # Seul le dispositif avec nom vide pourrait exister (si accepté)
            assert len(devices) <= 1
            if len(devices) == 1:
                # Si un dispositif a été créé, ce doit être celui avec le nom vide
                assert devices[0].name == ""
        finally:
            session.close()
