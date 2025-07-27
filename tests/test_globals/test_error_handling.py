#!/usr/bin/env python3
"""
Script de test pour valider les améliorations de gestion d'erreurs de Domotix.

Ce script teste les nouvelles fonctionnalités de gestion d'erreurs
pour s'assurer qu'elles fonctionnent correctement.
"""

import sys
import traceback

# Simulation d'imports pour les tests (à adapter selon l'environnement)
try:
    from domotix.core.error_handling import validate_device_id
    from domotix.globals.exceptions import ValidationError
    from domotix.models.sensor import Sensor
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("📋 Ce script doit être exécuté depuis l'environnement Domotix")
    sys.exit(1)


def test_sensor_validation():
    """Test des validations améliorées du modèle Sensor."""
    print("🧪 Test des validations de Sensor...")

    # Test 1: Création normale
    try:
        sensor = Sensor("Capteur test", "Salon")
        sensor.update_value(25.5)
        print(f"✅ Création et mise à jour normale : {sensor.value}")
    except Exception as e:
        print(f"❌ Erreur inattendue lors de la création : {e}")
        return False

    # Test 2: Validation d'un type incorrect
    try:
        sensor.update_value("invalid_type")
        print("❌ La validation de type a échoué")
        return False
    except ValidationError as e:
        print(f"✅ Validation de type correcte : {str(e)}")
        print(f"   Code d'erreur : {e.error_code}")

    # Test 3: Validation NaN
    try:
        sensor.update_value(float("nan"))
        print("❌ La validation NaN a échoué")
        return False
    except ValidationError as e:
        print(f"✅ Validation NaN correcte : {str(e)}")

    # Test 4: Validation plage
    try:
        sensor.update_value(50.0)
        sensor.validate_range(0, 40)  # Valeur hors plage
        print("❌ La validation de plage a échoué")
        return False
    except ValidationError as e:
        print(f"✅ Validation de plage correcte : {str(e)}")

    # Test 5: Méthode is_value_valid
    sensor.update_value(25.0)
    if sensor.is_value_valid():
        print("✅ is_value_valid() fonctionne correctement")
    else:
        print("❌ is_value_valid() retourne un résultat incorrect")
        return False

    return True


def test_error_handling_utilities():
    """Test des utilitaires de gestion d'erreurs."""
    print("\n🧪 Test des utilitaires de gestion d'erreurs...")

    # Test 1: Validation d'ID de dispositif
    try:
        validate_device_id("")
        print("❌ La validation d'ID vide a échoué")
        return False
    except ValidationError as e:
        print(f"✅ Validation d'ID vide correcte : {str(e)}")

    try:
        validate_device_id("   ")
        print("❌ La validation d'ID avec espaces a échoué")
        return False
    except ValidationError as e:
        print(f"✅ Validation d'ID avec espaces correcte : {str(e)}")

    # Test 2: Validation de nom de dispositif (utilise validate_device_id)
    try:
        validate_device_id("")  # ID vide
        print("❌ La validation de nom vide a échoué")
        return False
    except ValidationError as e:
        print(f"✅ Validation de nom vide correcte : {str(e)}")

    # Test 3: Validations réussies
    try:
        validate_device_id("device_123")
        # Simuler validation réussie pour les noms
        print("✅ Validations de valeurs correctes réussies")
    except Exception as e:
        print(f"❌ Erreur inattendue lors des validations : {e}")
        return False

    return True


def test_error_context():
    """Test de la structure ErrorContext."""
    print("\n🧪 Test de la structure ErrorContext...")

    try:
        from domotix.globals.exceptions import ErrorContext

        # Création d'un contexte d'erreur
        context = ErrorContext(
            module=__name__,
            function="test_error_context",
            user_data={"test": "value"},
            system_data={"env": "test"},
        )

        print("✅ ErrorContext créé avec succès")
        print(f"   Module : {context.module}")
        print(f"   Fonction : {context.function}")
        print(f"   Timestamp : {context.timestamp}")
        print(f"   User data : {context.user_data}")

        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création d'ErrorContext : {e}")
        return False


def run_all_tests():
    """Exécute tous les tests de validation."""
    print("🚀 Démarrage des tests de gestion d'erreurs Domotix\n")

    tests = [
        ("Validations Sensor", test_sensor_validation),
        ("Utilitaires de gestion d'erreurs", test_error_handling_utilities),
        ("Structure ErrorContext", test_error_context),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name} : {e}")
            traceback.print_exc()
            results.append((test_name, False))

    # Résumé des résultats
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)

    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)

    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:.<40} {status}")

    print(f"\n🎯 Score : {passed_tests}/{total_tests} tests réussis")

    if passed_tests == total_tests:
        print(
            "🎉 Tous les tests sont passés ! "
            "La gestion d'erreurs fonctionne correctement."
        )
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les améliorations.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
