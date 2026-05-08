"""
Utilitaires MLflow pour initialiser et tracer les experiences.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from omegaconf import DictConfig, OmegaConf

from .config_loader import PROJECT_ROOT

logger = logging.getLogger(__name__)

try:
    import mlflow
except ImportError:  # pragma: no cover - dependance optionnelle
    mlflow = None


def _require_mlflow() -> None:
    if mlflow is None:
        raise ImportError(
            "MLflow n'est pas installe. Installez-le avec `pip install mlflow` "
            "avant d'utiliser le tracking."
        )


def is_mlflow_enabled(cfg: DictConfig) -> bool:
    """Retourne l'etat d'activation du tracking MLflow."""
    return bool(cfg.mlflow.tracking.get("enabled", True))


def _resolve_tracking_uri(uri: str) -> str:
    """Convertit une URI locale relative en chemin absolu stable."""
    if uri.startswith("file:./"):
        resolved = (PROJECT_ROOT / uri.replace("file:./", "", 1)).resolve()
        return resolved.as_uri()
    return uri


def _flatten_config(data: Any, prefix: str = "") -> dict[str, Any]:
    """Aplatit une config imbriquee pour simplifier le logging des params."""
    if isinstance(data, DictConfig):
        data = OmegaConf.to_container(data, resolve=True)

    if isinstance(data, dict):
        flattened: dict[str, Any] = {}
        for key, value in data.items():
            nested_prefix = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(_flatten_config(value, nested_prefix))
        return flattened

    if isinstance(data, list):
        return {prefix: ",".join(map(str, data))}

    return {prefix: data}


def configure_mlflow(cfg: DictConfig) -> str:
    """
    Initialise MLflow a partir de la configuration Hydra.
    Retourne l'URI effectivement utilisee.
    """
    if not is_mlflow_enabled(cfg):
        logger.info("MLflow desactive dans la configuration.")
        return ""

    _require_mlflow()

    tracking_uri = _resolve_tracking_uri(cfg.mlflow.tracking.uri)
    experiment_name = cfg.mlflow.tracking.experiment_name

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    logger.info("MLflow configure (tracking_uri=%s, experiment=%s)", tracking_uri, experiment_name)
    return tracking_uri


@contextmanager
def start_mlflow_run(
    cfg: DictConfig,
    run_name: str | None = None,
    tags: dict[str, Any] | None = None,
) -> Iterator[Any]:
    """
    Ouvre un run MLflow avec les tags par defaut de la configuration.
    """
    _require_mlflow()
    if not is_mlflow_enabled(cfg):
        yield None
        return

    configure_mlflow(cfg)

    default_tags = dict(cfg.mlflow.run.tags)
    if tags:
        default_tags.update(tags)

    active_run = mlflow.start_run(run_name=run_name, tags=default_tags)
    try:
        yield active_run
    finally:
        mlflow.end_run()


def log_config_params(cfg: DictConfig, section_name: str | None = None) -> None:
    """
    Loggue une section de config ou l'ensemble de la config en params MLflow.
    """
    _require_mlflow()

    target_cfg: Any = cfg
    if section_name:
        target_cfg = cfg.get(section_name)
        if target_cfg is None:
            logger.warning("Section de configuration introuvable pour MLflow: %s", section_name)
            return

    params = _flatten_config(target_cfg, prefix=section_name or "")
    sanitized_params = {key: str(value)[:500] for key, value in params.items() if key}

    if sanitized_params:
        mlflow.log_params(sanitized_params)


def log_metrics(metrics: dict[str, float], step: int | None = None) -> None:
    """Loggue un dictionnaire de metriques numeriques."""
    _require_mlflow()
    clean_metrics = {key: float(value) for key, value in metrics.items()}
    mlflow.log_metrics(clean_metrics, step=step)


def log_artifact(path: str | Path, artifact_path: str | None = None) -> None:
    """Loggue un fichier local comme artefact MLflow."""
    _require_mlflow()
    path = Path(path)
    if not path.exists():
        logger.warning("Artefact MLflow introuvable: %s", path)
        return
    mlflow.log_artifact(str(path), artifact_path=artifact_path)
