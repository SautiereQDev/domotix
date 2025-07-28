"""
Modern dependency injection container for the Domotix application.

This module implements an IoC (Inversion of Control) container following
modern best practices for dependency injection with Python 3.12+ support.

Classes:
    DIContainer: Main dependency injection container
    Scope: Enumeration of object lifetimes
    Injectable: Decorator to mark classes as injectable
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar, get_type_hints

T = TypeVar("T")


class Scope(Enum):
    """Enumeration of object lifetimes."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class Injectable:
    """Decorator to mark classes as injectable."""

    def __init__(self, *, scope: Scope = Scope.TRANSIENT) -> None:
        """
        Initialise the Injectable decorator.

        Args:
            scope: Lifetime scope of the object (default TRANSIENT)
        """
        self.scope = scope

    def __call__(self, cls: type[T]) -> type[T]:
        """
        Marks a class as injectable.

        Args:
            cls: Class to be marked as injectable

        Returns:
            Marked class with injection metadata
        """
        cls._injectable_scope = self.scope  # type: ignore[attr-defined]
        return cls


class ServiceDescriptor:
    """Descriptor of a registered service."""

    def __init__(
        self,
        service_type: type[Any],
        *,
        implementation_type: type[Any] | None = None,
        factory: Callable[[], Any] | None = None,
        scope: Scope = Scope.TRANSIENT,
    ) -> None:
        """
        Initialise the service descriptor.

        Args:
            service_type: Type of the service (interface/abstract class)
            implementation_type: Implementation type
            factory: Factory function to create the instance
            scope: Lifetime scope of the service
        """
        self.service_type = service_type
        self.implementation_type = implementation_type or service_type
        self.factory = factory
        self.scope = scope
        self.instance: Any = None


class DIContainer:
    """
    Modern dependency injection container.

    Implements the Service Locator and Dependency Injection patterns
    with support for scopes and automatic dependency resolution.
    """

    def __init__(self) -> None:
        """Initialise the DI container."""
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
        Register a service as a singleton.

        Args:
            service_type: Type of the service
            implementation_type: Implementation type (optional)
            factory: Factory to create the instance (optional)

        Returns:
            Container instance for chaining
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
        Register a service as transient.

        Args:
            service_type: Type of the service
            implementation_type: Implementation type (optional)
            factory: Factory to create the instance (optional)

        Returns:
            Container instance for chaining
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
        Register a service as scoped.

        Args:
            service_type: Type of the service
            implementation_type: Implementation type (optional)
            factory: Factory to create the instance (optional)

        Returns:
            Container instance for chaining
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
        Register an existing instance as a singleton.

        Args:
            service_type: Type of the service
            instance: Instance to register

        Returns:
            Container instance for chaining
        """
        descriptor = ServiceDescriptor(service_type, scope=Scope.SINGLETON)
        descriptor.instance = instance
        self._services[service_type] = descriptor
        return self

    def resolve(self, service_type: type[T]) -> T:
        """
        Resolves a service and its dependencies.

        Args:
            service_type: Type of the service to resolve

        Returns:
            Instance of the service

        Raises:
            ValueError: If the service is not registered
            RuntimeError: If a circular dependency is detected
        """
        if service_type in self._building_stack:
            dependency_chain = " -> ".join(
                [s.__name__ for s in self._building_stack] + [service_type.__name__]
            )
            msg = (
                f"Circular dependency detected for {service_type.__name__}. "
                f"Dependency chain: {dependency_chain}"
            )
            raise RuntimeError(msg)

        if service_type not in self._services:
            # Attempt automatic resolution for classes marked with @Injectable
            if hasattr(service_type, "_injectable_scope"):
                self._auto_register(service_type)
            else:
                msg = f"Service {service_type} is not registered"
                raise ValueError(msg)

        descriptor = self._services[service_type]

        # Handle singletons
        if descriptor.scope == Scope.SINGLETON and descriptor.instance is not None:
            return descriptor.instance  # type: ignore[return-value, no-any-return]

        # Handle scoped services
        if descriptor.scope == Scope.SCOPED and service_type in self._scoped_instances:
            return self._scoped_instances[service_type]  # type: ignore[return-value,no-any-return]  # noqa: E501

        # Create the instance
        self._building_stack.add(service_type)
        try:
            instance = self._create_instance(descriptor)

            # Store according to the scope
            if descriptor.scope == Scope.SINGLETON:
                descriptor.instance = instance
            elif descriptor.scope == Scope.SCOPED:
                self._scoped_instances[service_type] = instance

            return instance  # type: ignore[return-value, no-any-return]
        finally:
            self._building_stack.discard(service_type)

    def _auto_register(self, service_type: type[Any]) -> None:
        """
        Automatically registers a class marked with @Injectable.

        Args:
            service_type: Type to register automatically
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
        Creates an instance from a descriptor.

        Args:
            descriptor: Descriptor of the service

        Returns:
            Created instance
        """
        if descriptor.factory:
            # Inject dependencies into the factory
            return self._inject_dependencies(descriptor.factory)

        # Inject dependencies into the constructor
        return self._inject_dependencies(descriptor.implementation_type)

    def _inject_dependencies(self, target: Callable[..., Any]) -> Any:
        """
        Injects dependencies into a callable (constructor or factory).

        Args:
            target: Target callable

        Returns:
            Result of the call with injected dependencies
        """
        sig = inspect.signature(target)
        try:
            type_hints = get_type_hints(target)
        except (NameError, AttributeError):
            # Fallback to direct annotations if get_type_hints fails
            type_hints = getattr(target, "__annotations__", {})

        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name in type_hints:
                param_type = type_hints[param_name]
                kwargs[param_name] = self.resolve(param_type)
            elif param.annotation != inspect.Parameter.empty:
                # Use the annotation directly as a fallback
                param_type = param.annotation
                kwargs[param_name] = self.resolve(param_type)

        return target(**kwargs)

    def clear_scoped(self) -> None:
        """Clears all scoped instances."""
        self._scoped_instances.clear()

    def create_scope(self) -> ScopedContainer:
        """
        Creates a new scope with isolated scoped instances.

        Returns:
            Container with isolated scope
        """
        return ScopedContainer(self)


class ScopedContainer:
    """
    Container with isolated scope for scoped instances.

    Used as a context manager to automatically manage
    the lifecycle of scoped instances.
    """

    def __init__(self, parent_container: DIContainer) -> None:
        """
        Initialise the scoped container.

        Args:
            parent_container: Parent container
        """
        self.parent = parent_container
        self._original_scoped_instances: dict[type[Any], Any] = {}

    def __enter__(self) -> DIContainer:
        """
        Enters the scope.

        Returns:
            Parent container
        """
        self._original_scoped_instances = self.parent._scoped_instances.copy()
        self.parent._scoped_instances.clear()
        return self.parent

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exits the scope and restores previous instances."""
        self.parent._scoped_instances = self._original_scoped_instances


# Global instance of the container
container = DIContainer()
