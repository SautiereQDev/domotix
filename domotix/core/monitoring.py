"""
Metrics and monitoring system for Domotix.

This module implements a modern monitoring system with:
- Real-time performance metrics
- System health monitoring
- Usage statistics collection
- Export for external monitoring systems

Classes:
    MetricType: Supported metric types
    Metric: Metric representation
    MetricsCollector: Thread-safe metrics collector
    HealthChecker: System health checker
"""

from __future__ import annotations

import statistics
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar
from weakref import WeakSet

from domotix.core.config import get_config
from domotix.core.logging_system import get_logger

T = TypeVar("T")

logger = get_logger(__name__)


class MetricType(str, Enum):
    """Types de métriques supportées."""

    COUNTER = "counter"  # Compteur incrémental
    GAUGE = "gauge"  # Valeur instantanée
    HISTOGRAM = "histogram"  # Distribution de valeurs
    TIMER = "timer"  # Mesure de temps
    RATE = "rate"  # Taux par seconde


@dataclass(slots=True)
class Metric:
    """
    Représentation d'une métrique avec métadonnées.

    Encapsule une mesure avec son contexte et ses labels
    pour permettre l'agrégation et l'analyse.
    """

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    labels: dict[str, str] = field(default_factory=dict)
    unit: str = ""
    help_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        """
        Convertit la métrique en dictionnaire.

        Returns:
            Dictionnaire représentant la métrique
        """
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "unit": self.unit,
            "help": self.help_text,
        }


class MetricsCollector:
    """
    Collecteur de métriques thread-safe avec agrégation automatique.

    Gère la collecte, l'agrégation et l'export des métriques
    de performance de l'application.
    """

    def __init__(self, max_history: int = 1000) -> None:
        """
        Initialise le collecteur de métriques.

        Args:
            max_history: Nombre maximum d'entrées à conserver en historique
        """
        self._metrics: dict[str, deque[Metric]] = defaultdict(
            lambda: deque(maxlen=max_history)
        )
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = defaultdict(float)
        self._lock = threading.RLock()
        self._observers: WeakSet[Callable[[Metric], None]] = WeakSet()

    def increment_counter(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """
        Incrémente un compteur.

        Args:
            name: Nom du compteur
            value: Valeur à ajouter
            labels: Labels optionnels
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value

            metric = Metric(
                name=name,
                value=self._counters[key],
                metric_type=MetricType.COUNTER,
                labels=labels or {},
            )

            self._record_metric(metric)

    def set_gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """
        Définit la valeur d'une jauge.

        Args:
            name: Nom de la jauge
            value: Nouvelle valeur
            labels: Labels optionnels
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value

            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.GAUGE,
                labels=labels or {},
            )

            self._record_metric(metric)

    def record_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """
        Enregistre une valeur dans un histogramme.

        Args:
            name: Nom de l'histogramme
            value: Valeur à enregistrer
            labels: Labels optionnels
        """
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            labels=labels or {},
        )

        self._record_metric(metric)

    def record_timer(
        self, name: str, duration: float, labels: dict[str, str] | None = None
    ) -> None:
        """
        Enregistre une durée.

        Args:
            name: Nom du timer
            duration: Durée en secondes
            labels: Labels optionnels
        """
        metric = Metric(
            name=name,
            value=duration,
            metric_type=MetricType.TIMER,
            labels=labels or {},
            unit="seconds",
        )

        self._record_metric(metric)

    @contextmanager
    def time_context(
        self, name: str, labels: dict[str, str] | None = None
    ) -> Iterator[None]:
        """
        Gestionnaire de contexte pour mesurer le temps d'exécution.

        Args:
            name: Nom de la métrique
            labels: Labels optionnels

        Yields:
            None

        Example:
            with collector.time_context("database_query"):
                # Code à mesurer
                execute_query()
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            self.record_timer(name, duration, labels)

    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """
        Crée une clé unique pour une métrique avec ses labels.

        Args:
            name: Nom de la métrique
            labels: Labels de la métrique

        Returns:
            Clé unique
        """
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _record_metric(self, metric: Metric) -> None:
        """
        Enregistre une métrique et notifie les observateurs.

        Args:
            metric: Métrique à enregistrer
        """
        with self._lock:
            key = self._make_key(metric.name, metric.labels)
            self._metrics[key].append(metric)

        # Notification asynchrone des observateurs
        for observer in self._observers:
            try:
                observer(metric)
            except Exception as e:
                logger.warning(f"Erreur lors de la notification d'observateur: {e}")

    def get_metrics(
        self, name_pattern: str | None = None, since: datetime | None = None
    ) -> list[Metric]:
        """
        Récupère les métriques selon des critères.

        Args:
            name_pattern: Pattern de nom (contient la chaîne)
            since: Timestamp minimum

        Returns:
            Liste des métriques correspondantes
        """
        with self._lock:
            result = []

            for key, metrics in self._metrics.items():
                if name_pattern and name_pattern not in key:
                    continue

                for metric in metrics:
                    if since and metric.timestamp < since:
                        continue
                    result.append(metric)

            return sorted(result, key=lambda m: m.timestamp)

    def get_statistics(self, name: str) -> dict[str, float]:
        """
        Calcule des statistiques pour une métrique.

        Args:
            name: Nom de la métrique

        Returns:
            Dictionnaire des statistiques
        """
        with self._lock:
            values: list[float] = []

            for key, metrics in self._metrics.items():
                if not key.startswith(name):
                    continue

                values.extend(m.value for m in metrics)

            if not values:
                return {}

            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
            }

    def add_observer(self, observer: Callable[[Metric], None]) -> None:
        """
        Ajoute un observateur de métriques.

        Args:
            observer: Fonction appelée à chaque nouvelle métrique
        """
        self._observers.add(observer)

    def export_prometheus(self) -> str:
        """
        Exporte les métriques au format Prometheus.

        Returns:
            Métriques formatées pour Prometheus
        """
        with self._lock:
            lines = []

            # Export des compteurs
            for key, value in self._counters.items():
                lines.append(f"{key} {value}")

            # Export des jauges
            for key, value in self._gauges.items():
                lines.append(f"{key} {value}")

            return "\n".join(lines)


@dataclass(slots=True)
class HealthStatus:
    """Status de santé d'un composant du système."""

    component: str
    is_healthy: bool
    status: str
    last_check: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convertit le status en dictionnaire."""
        return {
            "component": self.component,
            "healthy": self.is_healthy,
            "status": self.status,
            "last_check": self.last_check.isoformat(),
            "details": self.details,
        }


class HealthChecker:
    """
    Vérificateur de santé du système.

    Surveille l'état des composants critiques de l'application
    et fournit un rapport de santé global.
    """

    def __init__(self) -> None:
        """Initialise le vérificateur de santé."""
        self._health_checks: dict[str, Callable[[], HealthStatus]] = {}
        self._last_results: dict[str, HealthStatus] = {}
        self._lock = threading.RLock()

    def register_check(self, name: str, check_func: Callable[[], HealthStatus]) -> None:
        """
        Enregistre une vérification de santé.

        Args:
            name: Nom du composant
            check_func: Fonction de vérification
        """
        with self._lock:
            self._health_checks[name] = check_func

    def check_all(self) -> dict[str, HealthStatus]:
        """
        Exécute toutes les vérifications de santé.

        Returns:
            Dictionnaire des résultats par composant
        """
        with self._lock:
            results = {}

            for name, check_func in self._health_checks.items():
                try:
                    status = check_func()
                    results[name] = status
                    self._last_results[name] = status
                except Exception as e:
                    logger.exception(f"Erreur lors de la vérification de {name}")
                    results[name] = HealthStatus(
                        component=name, is_healthy=False, status=f"Erreur: {e}"
                    )

            return results

    def is_system_healthy(self) -> bool:
        """
        Vérifie si le système global est en bonne santé.

        Returns:
            True si tous les composants sont sains
        """
        results = self.check_all()
        return all(status.is_healthy for status in results.values())

    def get_health_summary(self) -> dict[str, Any]:
        """
        Génère un résumé de santé du système.

        Returns:
            Résumé avec statut global et détails des composants
        """
        results = self.check_all()
        healthy_count = sum(1 for s in results.values() if s.is_healthy)
        total_count = len(results)

        return {
            "overall_healthy": healthy_count == total_count,
            "healthy_components": healthy_count,
            "total_components": total_count,
            "components": {name: status.to_dict() for name, status in results.items()},
            "timestamp": datetime.now().isoformat(),
        }


# Instance globale du collecteur de métriques
_metrics_collector = MetricsCollector()
_health_checker = HealthChecker()


def get_metrics_collector() -> MetricsCollector:
    """
    Récupère l'instance globale du collecteur de métriques.

    Returns:
        Collecteur de métriques
    """
    return _metrics_collector


def get_health_checker() -> HealthChecker:
    """
    Récupère l'instance globale du vérificateur de santé.

    Returns:
        Vérificateur de santé
    """
    return _health_checker


# Décorateur pour mesurer automatiquement les performances
def timed(metric_name: str | None = None, labels: dict[str, str] | None = None):
    """
    Décorateur pour mesurer automatiquement le temps d'exécution.

    Args:
        metric_name: Nom de la métrique (par défaut nom de la fonction)
        labels: Labels optionnels

    Returns:
        Décorateur configuré

    Example:
        @timed("api_request", {"endpoint": "/devices"})
        def get_devices():
            # Code de la fonction
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        name = metric_name or f"{func.__module__}.{func.__name__}"

        def wrapper(*args: Any, **kwargs: Any) -> T:
            with _metrics_collector.time_context(name, labels):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Fonction d'initialisation du monitoring
def setup_monitoring() -> None:
    """
    Configure le système de monitoring avec les vérifications de santé de base.
    """

    def check_database_health() -> HealthStatus:
        """Vérifie la santé de la base de données."""
        try:
            from domotix.core.database import create_session

            with create_session() as session:
                # Test simple de connexion
                session.execute("SELECT 1")

            return HealthStatus(
                component="database", is_healthy=True, status="Connected and responsive"
            )
        except Exception as e:
            return HealthStatus(
                component="database", is_healthy=False, status=f"Connection failed: {e}"
            )

    def check_memory_health() -> HealthStatus:
        """Vérifie l'utilisation mémoire."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            is_healthy = memory_percent < 90  # Seuil à 90%
            status = f"Memory usage: {memory_percent:.1f}%"

            return HealthStatus(
                component="memory",
                is_healthy=is_healthy,
                status=status,
                details={
                    "percent_used": memory_percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3),
                },
            )
        except ImportError:
            return HealthStatus(
                component="memory",
                is_healthy=True,
                status="psutil not available - monitoring disabled",
            )
        except Exception as e:
            return HealthStatus(
                component="memory", is_healthy=False, status=f"Memory check failed: {e}"
            )

    # Enregistrement des vérifications de santé
    _health_checker.register_check("database", check_database_health)
    _health_checker.register_check("memory", check_memory_health)

    logger.info("Système de monitoring initialisé")


# Configuration automatique si en mode debug
if get_config().debug:
    setup_monitoring()
