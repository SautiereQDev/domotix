#!/usr/bin/env python3
"""
Test direct d'un workflow E2E simple pour vérifier que tout fonctionne.
"""

import os
import sys
import tempfile
import traceback

# Ajouter le chemin du projet au sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

try:
    from domotix.core.database import create_session, create_tables
    from domotix.core.factories import get_controller_factory
    from domotix.core.state_manager import StateManager
    from domotix.repositories.device_repository import DeviceRepository

    def test_simple_e2e_workflow():
        """Test E2E simple pour vérifier le fonctionnement de base."""
        print("🚀 Démarrage du test E2E simple...")

        # Configuration de l'environnement de test
        temp_dir = tempfile.mkdtemp(prefix="domotix_simple_e2e_")
        db_path = os.path.join(temp_dir, "test_simple.db")

        original_db = os.environ.get("DOMOTIX_DB_PATH")
        os.environ["DOMOTIX_DB_PATH"] = db_path

        try:
            # Initialiser le système
            StateManager.reset_instance()
            create_tables()
            print("✅ Base de données initialisée")

            # Test de création de dispositif
            session = create_session()
            try:
                controller = get_controller_factory().create_light_controller(session)
                print("✅ Contrôleur créé")

                # Créer une lampe
                light_id = controller.create_light("Lampe Test E2E", "Test Room")
                assert light_id is not None, "Création de lampe échouée"
                print(f"✅ Lampe créée avec ID: {light_id}")

                # Vérifier la lampe
                light = controller.get_light(light_id)
                assert light is not None, "Récupération de lampe échouée"
                assert light.name == "Lampe Test E2E", "Nom de lampe incorrect"
                assert light.location == "Test Room", "Localisation incorrecte"
                print("✅ Lampe vérifiée")

                # Test d'état
                success = controller.turn_on(light_id)
                assert success is True, "Allumage échoué"
                print("✅ Lampe allumée")

                # Vérifier l'état
                light_on = controller.get_light(light_id)
                assert light_on.is_on is True, "État allumé incorrect"
                print("✅ État allumé vérifié")

                # Test repository
                repo = DeviceRepository(session)

                # Compter avant la création pour avoir un référentiel
                initial_count = repo.count_all()
                print(f"Dispositifs initiaux: {initial_count}")

                # Vérifier que notre lampe existe
                our_light = repo.find_by_id(light_id)
                assert our_light is not None, "Notre lampe n'existe pas en base"
                assert our_light.name == "Lampe Test E2E", "Nom incorrect en base"
                print("✅ Repository fonctionnel")

                # Test de suppression
                success = controller.delete_light(light_id)
                assert success is True, "Suppression échouée"

                deleted_light = controller.get_light(light_id)
                assert deleted_light is None, "Lampe non supprimée"
                print("✅ Lampe supprimée")

                print("🎉 Test E2E simple réussi !")
                return True

            finally:
                session.close()

        finally:
            # Nettoyage
            StateManager.reset_instance()
            import shutil

            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

            if original_db:
                os.environ["DOMOTIX_DB_PATH"] = original_db
            else:
                os.environ.pop("DOMOTIX_DB_PATH", None)

    if __name__ == "__main__":
        try:
            success = test_simple_e2e_workflow()
            if success:
                print("\n✅ Tous les tests E2E de base sont fonctionnels !")
                sys.exit(0)
            else:
                print("\n❌ Échec des tests E2E de base")
                sys.exit(1)
        except Exception as e:
            print(f"\n💥 Erreur lors du test E2E: {e}")
            print("\nStacktrace complète:")
            traceback.print_exc()
            sys.exit(1)

except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Vérifiez que le projet est correctement configuré")
    sys.exit(1)
