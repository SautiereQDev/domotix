"""
Conteneur d'injection de dépendance moderne pour l'application Domotix.

Ce module implémente un conteneur IoC (Inversion of Control) suivant les
bonnes pratiques modernes d'injection de dépendance avec support Python 3.12+.

Classes:
    DIContainer: Conteneur principal d'injection de dépendance
    Scope: Énumération des portées de vie des objets
    Injectable: Décorateur pour marquer les classes injectables
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar, get_type_hints

T = TypeVar("T")


class Scope(Enum):
    """Énumération des portées de vie des objets."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class Injectable:
    """Décorateur pour marquer les classes comme injectables."""

    def __init__(self, *, scope: Scope = Scope.TRANSIENT) -> None:
        """
        Initialise le décorateur Injectable.

        Args:
            scope: Portée de vie de l'objet (par défaut TRANSIENT)
        """
        self.scope = scope

    def __call__(self, cls: type[T]) -> type[T]:
        """
        Marque une classe comme injectable.

        Args:
            cls: Classe à marquer comme injectable

        Returns:
            Classe marquée avec métadonnées d'injection
        """
        cls._injectable_scope = self.scope  # type: ignore[attr-defined]
        return cls


class ServiceDescriptor:
    """Descripteur d'un service enregistré."""

    def __init__(
        self,
        service_type: type[Any],
        *,
        implementation_type: type[Any] | None = None,
        factory: Callable[[], Any] | None = None,
        scope: Scope = Scope.TRANSIENT,
    ) -> None:
        """
        Initialise le descripteur de service.

        Args:
            service_type: Type du service (interface/classe abstraite)
            implementation_type: Type d'implémentation
            factory: Factory function pour créer l'instance
            scope: Portée de vie du service
        """
        self.service_type = service_type
        self.implementation_type = implementation_type or service_type
        self.factory = factory
        self.scope = scope
        self.instance: Any = None


class DIContainer:
    """
    Conteneur d'injection de dépendance moderne.

    Implémente les patterns Service Locator et Dependency Injection
    avec support des scopes et résolution automatique des dépendances.
    """

    def __init__(self) -> None:
        """Initialise le conteneur DI."""
        self._services: dict[type[Any], ServiceDescriptor] = {}
        self._scoped_instances: dict[type[Any], Any] = {}
        self._building_stack: set[type[Any]] = set()

    def register_singleton(
        self,
        service_type: type[T],
        *,
        implementation_type: type[T] | None = None,
        factory: Callable[[], T] | None = None,
    ) -> DIContainer:
        """
        Enregistre un service en tant que singleton.

        Args:
            service_type: Type du service
            implementation_type: Type d'implémentation (optionnel)
            factory: Factory pour créer l'instance (optionnel)

        Returns:
            Instance du conteneur pour chaînage
        """
        descriptor = ServiceDescriptor(
            service_type,
            implementation_type=implementation_type,
            factory=factory,
            scope=Scope.SINGLETON,
        )
        self._services[service_type] = descriptor
        return self

    def register_transient(
        self,
        service_type: type[T],
        *,
        implementation_type: type[T] | None = None,
        factory: Callable[[], T] | None = None,
    ) -> DIContainer:
        """
        Enregistre un service en tant que transient.

        Args:
            service_type: Type du service
            implementation_type: Type d'implémentation (optionnel)
            factory: Factory pour créer l'instance (optionnel)

        Returns:
            Instance du conteneur pour chaînage
        """
        descriptor = ServiceDescriptor(
            service_type,
            implementation_type=implementation_type,
            factory=factory,
            scope=Scope.TRANSIENT,
        )
        self._services[service_type] = descriptor
        return self

    def register_scoped(
        self,
        service_type: type[T],
        *,
        implementation_type: type[T] | None = None,
        factory: Callable[[], T] | None = None,
    ) -> DIContainer:
        """
        Enregistre un service en tant que scoped.

        Args:
            service_type: Type du service
            implementation_type: Type d'implémentation (optionnel)
            factory: Factory pour créer l'instance (optionnel)

        Returns:
            Instance du conteneur pour chaînage
        """
        descriptor = ServiceDescriptor(
            service_type,
            implementation_type=implementation_type,
            factory=factory,
            scope=Scope.SCOPED,
        )
        self._services[service_type] = descriptor
        return self

    def register_instance(self, service_type: type[T], instance: T) -> DIContainer:
        """
        Enregistre une instance existante comme singleton.

        Args:
            service_type: Type du service
            instance: Instance à enregistrer

        Returns:
            Instance du conteneur pour chaînage
        """
        descriptor = ServiceDescriptor(service_type, scope=Scope.SINGLETON)
        descriptor.instance = instance
        self._services[service_type] = descriptor
        return self

    def resolve(self, service_type: type[T]) -> T:
        """
        Résout un service et ses dépendances.

        Args:
            service_type: Type du service à résoudre

        Returns:
            Instance du service

        Raises:
            ValueError: Si le service n'est pas enregistré
            RuntimeError: Si une dépendance circulaire est détectée
        """
        if service_type in self._building_stack:
            dependency_chain = " -> ".join(
                [str(s) for s in list(self._building_stack)] + [str(service_type)]
            )
            msg = (
                f"Dépendance circulaire détectée pour {service_type}. "
                f"Chaîne de dépendances: {dependency_chain}"
            )
            raise RuntimeError(msg)

        if service_type not in self._services:
            # Tentative de résolution automatique pour les classes marquées @Injectable
            if hasattr(service_type, "_injectable_scope"):
                self._auto_register(service_type)
            else:
                msg = f"Service {service_type} n'est pas enregistré"
                raise ValueError(msg)

        descriptor = self._services[service_type]

        # Gestion des singletons
        if descriptor.scope == Scope.SINGLETON and descriptor.instance is not None:
            return descriptor.instance  # type: ignore[return-value, no-any-return]

        # Gestion des services scoped
        if descriptor.scope == Scope.SCOPED and service_type in self._scoped_instances:
            return self._scoped_instances[service_type]  # type: ignore[return-value,no-any-return]  # noqa: E501

        # Création de l'instance
        self._building_stack.add(service_type)
        try:
            instance = self._create_instance(descriptor)

            # Stockage selon le scope
            if descriptor.scope == Scope.SINGLETON:
                descriptor.instance = instance
            elif descriptor.scope == Scope.SCOPED:
                self._scoped_instances[service_type] = instance

            return instance  # type: ignore[return-value, no-any-return]
        finally:
            self._building_stack.discard(service_type)

    def _auto_register(self, service_type: type[Any]) -> None:
        """
        Enregistre automatiquement une classe marquée @Injectable.

        Args:
            service_type: Type à enregistrer automatiquement
        """
        scope = getattr(service_type, "_injectable_scope", Scope.TRANSIENT)
        descriptor = ServiceDescriptor(
            service_type,
            implementation_type=service_type,
            scope=scope,
        )
        self._services[service_type] = descriptor

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """
        Crée une instance à partir d'un descripteur.

        Args:
            descriptor: Descripteur du service

        Returns:
            Instance créée
        """
        if descriptor.factory:
            # Injection de dépendances dans la factory
            return self._inject_dependencies(descriptor.factory)

        # Injection de dépendances dans le constructeur
        return self._inject_dependencies(descriptor.implementation_type)

    def _inject_dependencies(self, target: Callable[..., Any]) -> Any:
        """
        Injecte les dépendances dans un callable (constructeur ou factory).

        Args:
            target: Callable cible

        Returns:
            Résultat de l'appel avec dépendances injectées
        """
        sig = inspect.signature(target)
        try:
            type_hints = get_type_hints(target)
        except (NameError, AttributeError):
            # Fallback aux annotations directes si get_type_hints échoue
            type_hints = getattr(target, "__annotations__", {})

        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name in type_hints:
                param_type = type_hints[param_name]
                kwargs[param_name] = self.resolve(param_type)
            elif param.annotation != inspect.Parameter.empty:
                # Utiliser l'annotation directement comme fallback
                param_type = param.annotation
                kwargs[param_name] = self.resolve(param_type)

        return target(**kwargs)

    def clear_scoped(self) -> None:
        """Efface toutes les instances scoped."""
        self._scoped_instances.clear()

    def create_scope(self) -> ScopedContainer:
        """
        Crée un nouveau scope avec des instances scoped isolées.

        Returns:
            Conteneur avec scope isolé
        """
        return ScopedContainer(self)


class ScopedContainer:
    """
    Conteneur avec scope isolé pour les instances scoped.

    Utilisé comme context manager pour gérer automatiquement
    le cycle de vie des instances scoped.
    """

    def __init__(self, parent_container: DIContainer) -> None:
        """
        Initialise le conteneur scoped.

        Args:
            parent_container: Conteneur parent
        """
        self.parent = parent_container
        self._original_scoped_instances: dict[type[Any], Any] = {}

    def __enter__(self) -> DIContainer:
        """
        Entre dans le scope.

        Returns:
            Conteneur parent
        """
        self._original_scoped_instances = self.parent._scoped_instances.copy()
        self.parent._scoped_instances.clear()
        return self.parent

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Sort du scope et restaure les instances précédentes."""
        self.parent._scoped_instances = self._original_scoped_instances


# Instance globale du conteneur
container = DIContainer()
