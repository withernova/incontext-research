"""Public package surface and built-in component registration."""

from .config import Config
from .registry import (
    AUXILIARY_LOSSES,
    DATASETS,
    EVALUATORS,
    HEAD_FINDERS,
    HEAD_PROBES,
    HOOKS,
    MODELS,
    RUNNERS,
)

# Import component packages for their registration side effects.
from . import attention_distillation, datasets, engine, evaluation, head_screening, models  # noqa: F401,E402

__all__ = [
    "Config",
    "AUXILIARY_LOSSES",
    "DATASETS",
    "EVALUATORS",
    "HEAD_FINDERS",
    "HEAD_PROBES",
    "HOOKS",
    "MODELS",
    "RUNNERS",
]
