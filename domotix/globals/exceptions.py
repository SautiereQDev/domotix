"""
Module des exceptions personnalisées du système domotique.

Ce module contient toutes les exceptions personnalisées utilisées dans
le système pour une gestion d'erreurs plus précise.

Exceptions:
    DomotixError: Exception de base pour toutes les erreurs du système
    DeviceNotFoundError: Levé quand un dispositif n'est pas trouvé
    InvalidDeviceTypeError: Levé pour un type de dispositif invalide
    CommandExecutionError: Levé quand une commande échoue
"""


class DomotixError(Exception):
    """Exception de base pour tous les erreurs du système domotique."""

    pass


class DeviceNotFoundError(DomotixError):
    """Levée quand un dispositif demandé n'est pas trouvé."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        super().__init__(f"Dispositif non trouvé : {device_id}")


class InvalidDeviceTypeError(DomotixError):
    """Levée quand un type de dispositif invalide est utilisé."""

    def __init__(self, device_type: str):
        self.device_type = device_type
        super().__init__(f"Type de dispositif invalide : {device_type}")


class CommandExecutionError(DomotixError):
    """Levée quand l'exécution d'une commande échoue."""

    def __init__(self, command: str, reason: str = ""):
        self.command = command
        self.reason = reason
        message = f"Échec de l'exécution de la commande : {command}"
        if reason:
            message += f" - {reason}"
        super().__init__(message)
