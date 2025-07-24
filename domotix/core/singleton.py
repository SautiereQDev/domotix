"""
Métaclasse singleton pour créer des classes singleton thread-safe.

Ce module fournit une métaclasse réutilisable pour implémenter
le pattern singleton de manière propre et thread-safe.

Classes:
    SingletonMeta: Métaclasse thread-safe pour implémenter le pattern singleton

Example:
    >>> class MySingleton(metaclass=SingletonMeta):
    ...     def __init__(self):
    ...         self.value = 42
    >>>
    >>> s1 = MySingleton()
    >>> s2 = MySingleton()
    >>> assert s1 is s2
    >>> print(s1.value)
    42
"""

import threading
from typing import Any, Dict, Type


class SingletonMeta(type):
    """
    Métaclasse thread-safe pour implémenter le pattern singleton.

    Cette métaclasse garantit qu'une seule instance de chaque classe
    qui l'utilise sera créée, même dans un environnement multi-threadé.

    Attributes:
        _instances: Dictionnaire privé stockant les instances [Classe -> Instance]
        _lock: Verrou pour garantir la thread-safety

    Example:
        >>> class Logger(metaclass=SingletonMeta):
        ...     pass
        >>>
        >>> logger1 = Logger()
        >>> logger2 = Logger()
        >>> assert logger1 is logger2
    """

    _instances: Dict[Type, Any] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Contrôle la création d'instances et implémente le pattern singleton.

        Returns:
            L'instance unique de la classe
        """
        if cls not in cls._instances:
            with cls._lock:
                # Double vérification pour éviter les conditions de course
                if cls not in cls._instances:
                    instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def reset_instance(mcs, cls1: Type) -> None:
        """
        Réinitialise l'instance singleton d'une classe spécifique.

        Args:
            cls1: La classe dont l'instance doit être réinitialisée

        Example:
            >>> class Logger(metaclass=SingletonMeta):
            ...     pass
            >>> logger1 = Logger()
            >>> SingletonMeta.reset_instance(Logger)
            >>> logger2 = Logger()
            >>> assert logger1 is not logger2
        """
        with mcs._lock:
            if cls1 in mcs._instances:
                del mcs._instances[cls1]

    @classmethod
    def has_instance(mcs, cls1: Type) -> bool:
        """
        Vérifie si une instance existe pour une classe donnée.

        Args:
            cls1: La classe à vérifier

        Returns:
            bool: True si une instance existe, False sinon
        """
        return cls1 in mcs._instances

    @classmethod
    def get_current_instance(mcs, cls1: Type) -> Any:
        """
        Récupère l'instance actuelle d'une classe sans en créer une nouvelle.

        Args:
            cls1: La classe dont on veut l'instance

        Returns:
            L'instance si elle existe, None sinon
        """
        return mcs._instances.get(cls1, None)
