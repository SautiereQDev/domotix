"""
Module du gestionnaire d'état singleton pour les dispositifs domotiques.

Ce module contient la classe StateManager qui gère de manière centralisée
tous les dispositifs du système domotique. Elle utilise le pattern singleton
avec métaclasse pour garantir une instance unique dans toute l'application.

Classes:
    StateManager: Gestionnaire d'état singleton pour les dispositifs

Architecture:
    Le StateManager utilise une métaclasse (SingletonMeta) pour implémenter
    le pattern singleton de manière thread-safe. Tous les dispositifs sont
    stockés dans un dictionnaire avec des UUID comme clés.

Example:
    >>> from domotix.core import StateManager
    >>> from domotix.models import Light
    >>>
    >>> # Les deux instances sont identiques (singleton)
    >>> sm1 = StateManager()
    >>> sm2 = StateManager()
    >>> assert sm1 is sm2
    >>>
    >>> # Enregistrement et récupération de dispositifs
    >>> light = Light("Ma lampe")
    >>> device_id = sm1.register_device(light)
    >>> retrieved = sm2.get_device(device_id)  # Même état partagé
    >>> assert retrieved is light
"""

import uuid
from typing import Dict, Optional

from ..models.device import Device
from .singleton import SingletonMeta


class StateManager(metaclass=SingletonMeta):
    """
    Gestionnaire d'état singleton pour les dispositifs domotiques.

    Cette classe centralise la gestion de tous les dispositifs du système
    domotique. Elle utilise le pattern singleton via métaclasse pour garantir
    qu'une seule instance existe dans toute l'application, permettant un
    partage d'état cohérent entre tous les composants.

    Le StateManager est thread-safe grâce à la métaclasse SingletonMeta qui
    utilise des verrous pour contrôler la création d'instances.

    Attributes:
        _devices: Dictionnaire privé stockant les dispositifs [UUID -> Device]
        _initialized: Flag pour éviter la réinitialisation multiple

    Example:
        >>> # Création et utilisation basique
        >>> state_manager = StateManager()
        >>> light = Light("Lampe salon")
        >>> device_id = state_manager.register_device(light)
        >>>
        >>> # Récupération depuis n'importe où dans l'application
        >>> other_manager = StateManager()  # Même instance
        >>> same_light = other_manager.get_device(device_id)
        >>> assert same_light is light
    """

    def __init__(self) -> None:
        """
        Initialise le StateManager si pas déjà fait.

        Cette méthode évite la réinitialisation multiple grâce au flag
        _initialized. Elle n'est appelée qu'une seule fois même si
        StateManager() est invoqué plusieurs fois.
        """
        # Éviter la réinitialisation si déjà initialisé (pattern singleton)
        if not hasattr(self, "_initialized"):
            # Stockage des dispositifs [UUID -> Device]
            self._devices: Dict[str, Device] = {}
            self._initialized: bool = True

    def get_device(self, device_id: str) -> Device:
        """
        Récupère un dispositif par son identifiant.

        Args:
            device_id: Identifiant unique du dispositif (UUID généré automatiquement)

        Returns:
            Device: Le dispositif correspondant à l'identifiant

        Raises:
            KeyError: Si aucun dispositif ne correspond à cet identifiant

        Example:
            >>> state_manager = StateManager()
            >>> light = Light("Test")
            >>> device_id = state_manager.register_device(light)
            >>> retrieved = state_manager.get_device(device_id)
            >>> assert retrieved is light
        """
        return self._devices[device_id]

    def get_devices(self) -> Dict[str, Device]:
        """
        Récupère tous les dispositifs enregistrés.

        Returns:
            Dict[str, Device]: Copie du dictionnaire des dispositifs.
                              Clés = UUID, Valeurs = objets Device

        Note:
            Retourne une copie pour préserver l'encapsulation. Les modifications
            du dictionnaire retourné n'affectent pas l'état interne.

        Example:
            >>> state_manager = StateManager()
            >>> devices = state_manager.get_devices()
            >>> devices.clear()  # N'affecte pas l'état interne
            >>> assert state_manager.get_device_count() > 0
            # Si des dispositifs existent
        """
        return self._devices.copy()

    def register_device(self, device: Device) -> str:
        """
        Enregistre un nouveau dispositif dans le système.

        Génère automatiquement un UUID unique pour le dispositif et l'ajoute
        au dictionnaire interne. L'UUID est retourné pour permettre les
        références futures au dispositif.

        Args:
            device: Instance de Device (ou sous-classe) à enregistrer

        Returns:
            str: UUID généré pour ce dispositif (format UUID4)

        Example:
            >>> state_manager = StateManager()
            >>> light = Light("Nouvelle lampe")
            >>> device_id = state_manager.register_device(light)
            >>> print(len(device_id))  # 36 caractères (UUID4)
            36
        """
        device_id = str(uuid.uuid4())  # Génération d'un UUID unique
        self._devices[device_id] = device
        return device_id

    def unregister_device(self, device_id: str) -> bool:
        """
        Supprime un dispositif du système.

        Args:
            device_id: Identifiant du dispositif à supprimer

        Returns:
            bool: True si le dispositif a été supprimé avec succès,
                 False s'il n'existait pas

        Example:
            >>> state_manager = StateManager()
            >>> light = Light("Temp")
            >>> device_id = state_manager.register_device(light)
            >>> success = state_manager.unregister_device(device_id)
            >>> assert success == True
            >>> success = state_manager.unregister_device("invalid-id")
            >>> assert success == False
        """
        if device_id in self._devices:
            del self._devices[device_id]
            return True
        return False

    def get_device_count(self) -> int:
        """
        Retourne le nombre de dispositifs enregistrés.

        Returns:
            int: Nombre total de dispositifs dans le système

        Example:
            >>> state_manager = StateManager()
            >>> count = state_manager.get_device_count()
            >>> assert count >= 0
        """
        return len(self._devices)

    def device_exists(self, device_id: str) -> bool:
        """
        Vérifie si un dispositif existe dans le système.

        Args:
            device_id: Identifiant du dispositif à vérifier

        Returns:
            bool: True si le dispositif existe, False sinon

        Example:
            >>> state_manager = StateManager()
            >>> exists = state_manager.device_exists("non-existent")
            >>> assert exists == False
        """
        return device_id in self._devices

    def clear_all_devices(self) -> None:
        """
        Supprime tous les dispositifs enregistrés.

        Remet le StateManager dans un état vide. Utile pour les tests
        ou la réinitialisation complète du système.
        """
        self._devices.clear()

    @classmethod
    def reset_instance(cls) -> None:
        """
        Réinitialise l'instance singleton du StateManager.

        Méthode utilitaire pour les tests qui permet de repartir
        avec une instance fraîche du StateManager.
        """
        SingletonMeta.reset_instance(cls)

    @classmethod
    def has_instance(cls) -> bool:
        """
        Vérifie si une instance du StateManager existe.

        Returns:
            bool: True si une instance existe, False sinon
        """
        return SingletonMeta.has_instance(cls)

    @classmethod
    def get_current_instance(cls) -> Optional["StateManager"]:
        """
        Récupère l'instance actuelle sans en créer une nouvelle.

        Returns:
            StateManager ou None: L'instance si elle existe, None sinon
        """
        from typing import cast

        return cast(Optional["StateManager"], SingletonMeta.get_current_instance(cls))

    def __str__(self) -> str:
        """Représentation string lisible du StateManager."""
        return f"StateManager({self.get_device_count()} dispositifs)"

    def __repr__(self) -> str:
        """Représentation string détaillée pour debugging."""
        return f"StateManager(devices={list(self._devices.keys())})"
