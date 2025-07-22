```
domotix/
├── README.md
├── pyproject.toml        # ou requirements.txt si vous préférez
├── .gitignore
├── docs/                 # documentation, schémas, tutoriels
│   └── architecture.md
├── config/               # fichiers de configuration (YAML, JSON, .env)
│   └── devices.yaml
├── src/                  # code applicatif
│   └── domotix/          # package principal
│       ├── __init__.py
│       ├── main.py       # point d’entrée (if __name__ == "__main__")
│       ├── core/         # cœur métier (gestion des scénarios, règles)
│       │   ├── __init__.py
│       │   ├── scheduler.py
│       │   └── rule_engine.py
│       ├── devices/      # abstractions de vos appareils
│       │   ├── __init__.py
│       │   ├── light.py
│       │   └── thermostat.py
│       ├── comms/        # protocoles (MQTT, HTTP…)
│       │   ├── __init__.py
│       │   ├── mqtt_client.py
│       │   └── http_server.py
│       └── utils/        # utilitaires (logging, helpers)
│           ├── __init__.py
│           ├── config_loader.py
│           └── logger.py
├── scripts/              # petits scripts de tests ou de déploiement
│   └── discover_devices.py
└── tests/                # tests unitaires et d’intégration
    ├── __init__.py
    ├── test_scheduler.py
    └── test_devices.py
```
