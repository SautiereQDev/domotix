# Tests End-to-End (E2E) pour Domotix

Cette suite de tests E2E valide le fonctionnement complet du système Domotix depuis l'interface CLI jusqu'à la persistance en base de données.

## Structure des Tests E2E

```
tests/test_e2e/
├── run_e2e_tests.py           # Script principal pour lancer les tests
├── simple_e2e_test.py         # Test simple pour validation rapide
├── pytest.ini                # Configuration pytest spécifique E2E
├── test_cli_workflows.py      # Tests des workflows CLI
├── test_device_workflows.py   # Tests des workflows de dispositifs
├── test_error_recovery.py     # Tests de récupération d'erreur
└── test_performance_scenarios.py # Tests de performance
```

## Types de Tests Inclus

### 1. Tests CLI Workflows (`test_cli_workflows.py`)
- **Création de dispositifs** via commandes CLI
- **Listage et recherche** de dispositifs
- **Contrôle d'état** des dispositifs
- **Workflows utilisateur complets**
- **Gestion d'erreurs** en ligne de commande

### 2. Tests Device Workflows (`test_device_workflows.py`)
- **Cycle de vie complet** des dispositifs (création → utilisation → suppression)
- **Opérations multi-dispositifs**
- **Requêtes et recherches complexes**
- **Intégrité des données** lors d'opérations concurrentes
- **Consistance** entre contrôleurs et repositories

### 3. Tests Error Recovery (`test_error_recovery.py`)
- **Récupération** après pannes de base de données
- **Gestion des données corrompues**
- **Validation des entrées** utilisateur
- **Accès concurrent** et gestion des conflits
- **Limitations de ressources**

### 4. Tests Performance Scenarios (`test_performance_scenarios.py`)
- **Création en masse** de dispositifs
- **Performance des requêtes** sur grands datasets
- **Opérations d'état fréquentes**
- **Benchmarks de temps de réponse**
- **Tests de scalabilité**

## Utilisation

### Lancement de tous les tests E2E

```bash
# Méthode 1: Script personnalisé (recommandé)
python3 tests/test_e2e/run_e2e_tests.py

# Méthode 2: Avec verbosité
python3 tests/test_e2e/run_e2e_tests.py --verbose

# Méthode 3: Filtrage par pattern
python3 tests/test_e2e/run_e2e_tests.py --pattern="cli*"
```

### Lancement de tests spécifiques

```bash
# Test simple pour validation rapide
python3 tests/test_e2e/simple_e2e_test.py

# Tests CLI uniquement
python3 tests/test_e2e/run_e2e_tests.py --pattern="test_cli*"

# Tests de performance uniquement
python3 tests/test_e2e/run_e2e_tests.py --pattern="*performance*"
```

### Liste des modules disponibles

```bash
python3 tests/test_e2e/run_e2e_tests.py --list
```

## Configuration

### Variables d'Environnement

Les tests E2E utilisent des variables d'environnement spécifiques :

```bash
DOMOTIX_E2E_MODE=1              # Active le mode E2E
DOMOTIX_TEST_DB=/path/to/db     # Base de données temporaire
DOMOTIX_LOG_LEVEL=WARNING       # Réduit les logs pour les tests
```

### Base de Données Temporaire

Chaque exécution des tests E2E :
1. **Crée** une base de données temporaire
2. **Initialise** les tables nécessaires
3. **Exécute** les tests dans un environnement isolé
4. **Nettoie** automatiquement les fichiers temporaires

## Scenarios Testés

### Scenario 1: Configuration Maison Complète
```
1. Création de dispositifs pour salon, chambre, cuisine
2. Contrôle groupé par localisation
3. Workflows de contrôle d'état
4. Vérification de persistance
```

### Scenario 2: Gestion d'Erreurs
```
1. Simulation de pannes de connexion DB
2. Gestion des entrées utilisateur invalides
3. Récupération après erreurs système
4. Tests de robustesse sous charge
```

### Scenario 3: Performance sous Charge
```
1. Création de 100+ dispositifs
2. Requêtes concurrentes multi-threads
3. Opérations d'état haute fréquence
4. Benchmarks de temps de réponse
```

## Métriques de Performance

Les tests de performance mesurent :

- **Temps de création** de dispositifs (< 1s par dispositif)
- **Temps de requête** (< 2s pour find_all sur 100+ dispositifs)
- **Opérations d'état** (< 500ms pour turn_on/turn_off)
- **Accès par ID** (< 200ms)
- **Débit concurrent** (> 5 opérations/seconde)

## Intégration Continue

### Configuration GitHub Actions

```yaml
- name: Tests End-to-End
  run: |
    python3 tests/test_e2e/run_e2e_tests.py --verbose
```

### Critères de Réussite

✅ **Tous les workflows CLI** fonctionnent
✅ **Cycle de vie des dispositifs** complet
✅ **Récupération d'erreur** gracieuse
✅ **Performance** dans les seuils acceptables
✅ **Intégrité des données** préservée

## Diagnostic et Debug

### Logs Détaillés

```bash
# Avec logs détaillés
DOMOTIX_LOG_LEVEL=DEBUG python3 tests/test_e2e/run_e2e_tests.py --verbose
```

### Test Simple de Validation

```bash
# Validation rapide du système
python3 tests/test_e2e/simple_e2e_test.py
```

### Analyse des Échecs

Les tests E2E fournissent :
- **Messages d'erreur détaillés**
- **Stacktraces complètes**
- **État de la base de données** au moment de l'échec
- **Métriques de performance** pour diagnostic

## Contribution

Pour ajouter de nouveaux tests E2E :

1. **Créer** un nouveau fichier `test_*.py` dans `tests/test_e2e/`
2. **Suivre** les patterns existants (fixtures, assertions)
3. **Ajouter** le module à `E2E_TEST_MODULES` dans `run_e2e_tests.py`
4. **Tester** avec le runner E2E
5. **Documenter** les nouveaux scenarios

## Maintenance

### Mise à Jour des Seuils

Les seuils de performance peuvent être ajustés dans :
- `test_performance_scenarios.py` : Seuils de temps
- `pytest.ini` : Configuration globale
- `run_e2e_tests.py` : Options par défaut

### Nettoyage des Données de Test

Les tests E2E nettoient automatiquement :
- Fichiers de base de données temporaires
- Variables d'environnement de test
- Instances singleton en mémoire
