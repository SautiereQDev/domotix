"""
Singleton metaclass for creating thread-safe singleton classes.

This module provides a reusable metaclass to implement
the singleton pattern in a clean and thread-safe way.

Classes:
    SingletonMeta: Thread-safe metaclass for implementing the singleton pattern

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
    Thread-safe metaclass for implementing the singleton pattern.

    This metaclass ensures that only one instance of each class
    using it will be created, even in a multi-threaded environment.

    Attributes:
        _instances: Private dictionary storing instances [Class -> Instance]
        _lock: Lock to ensure thread-safety

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
        Controls instance creation and implements the singleton pattern.

        Returns:
            The unique instance of the class
        """
        if cls not in cls._instances:
            with cls._lock:
                # Double-check to avoid race conditions
                if cls not in cls._instances:
                    instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def reset_instance(mcs, cls1: Type) -> None:
        """
        Resets the singleton instance of a specific class.

        Args:
            cls1: The class whose instance should be reset

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
        Checks if an instance exists for a given class.

        Args:
            cls1: The class to check

        Returns:
            bool: True if an instance exists, False otherwise
        """
        return cls1 in mcs._instances

    @classmethod
    def get_current_instance(mcs, cls1: Type) -> Any:
        """
        Retrieves the current instance of a class without creating a new one.

        Args:
            cls1: The class of which we want the instance

        Returns:
            The instance if it exists, None otherwise
        """
        return mcs._instances.get(cls1, None)
