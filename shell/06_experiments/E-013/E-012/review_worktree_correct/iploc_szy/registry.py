"""Lightweight component registries inspired by MMEngine."""

from copy import deepcopy
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

T = TypeVar("T")


class Registry:
    """Map configuration ``type`` names to Python classes.

    The API intentionally mirrors the small subset of MMEngine's Registry used
    by this project. Keeping it local avoids making model training depend on a
    specific MMEngine release.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._items: Dict[str, Type[Any]] = {}

    def register_module(
        self,
        obj: Optional[Type[T]] = None,
        *,
        name: Optional[str] = None,
    ) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
        """Register a class directly or as a decorator."""

        def decorator(cls: Type[T]) -> Type[T]:
            """Store one class under its explicit or inferred registry name."""
            key = name or cls.__name__
            if key in self._items:
                raise KeyError(f"{key!r} is already registered in {self.name!r}")
            self._items[key] = cls
            return cls

        return decorator(obj) if obj is not None else decorator

    def get(self, key: str) -> Type[Any]:
        """Return one registered class with an actionable error on failure."""
        if key not in self._items:
            choices = sorted(self._items)
            raise KeyError(
                f"{key!r} is not registered in {self.name!r}; choices={choices}"
            )
        return self._items[key]

    def build(self, cfg: Any, **defaults: Any) -> Any:
        """Instantiate an object from a configuration dictionary.

        Non-dictionary values are returned unchanged. This allows already-built
        objects to pass through builders during tests and custom integrations.
        """
        if cfg is None:
            return None
        if not isinstance(cfg, dict):
            return cfg

        arguments = deepcopy(cfg)
        component_type = arguments.pop("type")
        cls = self.get(component_type) if isinstance(component_type, str) else component_type
        for key, value in defaults.items():
            arguments.setdefault(key, value)
        return cls(**arguments)


DATASETS = Registry("dataset")
AUXILIARY_LOSSES = Registry("auxiliary_loss")
MODELS = Registry("model")
EVALUATORS = Registry("evaluator")
HEAD_FINDERS = Registry("head_finder")
HEAD_PROBES = Registry("head_probe")
HOOKS = Registry("hook")
RUNNERS = Registry("runner")
