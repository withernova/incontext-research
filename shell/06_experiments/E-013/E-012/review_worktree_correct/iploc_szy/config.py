"""Python configuration loading with recursive ``_base_`` inheritance."""

import ast
import runpy
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Union

PathLike = Union[str, Path]


class Config(dict):
    """Dictionary configuration loaded from executable Python files."""

    @classmethod
    def fromfile(cls, path: PathLike) -> "Config":
        """Load a config and recursively merge its declared base configs."""
        config_path = Path(path).resolve()
        namespace = runpy.run_path(str(config_path))
        local_values = {
            key: value for key, value in namespace.items() if not key.startswith("__")
        }

        base_paths = local_values.pop("_base_", [])
        if isinstance(base_paths, (str, Path)):
            base_paths = [base_paths]

        merged: Dict[str, Any] = {}
        sources = {str(config_path): config_path.read_text(encoding="utf-8")}
        for base_path in base_paths:
            base = cls.fromfile(config_path.parent / base_path)
            merged = cls._merge(merged, base)
            sources.update(base.source_files)
        result = cls(cls._merge(merged, local_values))
        result.source_files = sources
        return result

    @staticmethod
    def _merge(base: Mapping[str, Any], child: Mapping[str, Any]) -> Dict[str, Any]:
        """Recursively merge ``child`` onto ``base`` without mutating either."""
        output = deepcopy(dict(base))
        for key, raw_value in child.items():
            value = deepcopy(raw_value)
            delete_base = isinstance(value, dict) and value.pop("_delete_", False)
            if (
                isinstance(value, dict)
                and isinstance(output.get(key), dict)
                and not delete_base
            ):
                output[key] = Config._merge(output[key], value)
            else:
                output[key] = value
        return output

    def merge_options(self, options: Iterable[str]) -> "Config":
        """Apply command-line overrides such as ``runner.max_steps=10``."""
        for option in options or []:
            if "=" not in option:
                raise ValueError(f"config override must be key=value, got {option!r}")
            dotted_key, raw_value = option.split("=", 1)
            value = self._parse_override(raw_value)
            self._set_dotted(dotted_key, value)
        return self

    @staticmethod
    def _parse_override(raw_value: str) -> Any:
        """Parse Python literals while leaving ordinary strings unchanged."""
        try:
            return ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            return raw_value

    def _set_dotted(self, dotted_key: str, value: Any) -> None:
        parts = dotted_key.split(".")
        current: MutableMapping[str, Any] = self
        for part in parts[:-1]:
            child = current.setdefault(part, {})
            if not isinstance(child, MutableMapping):
                raise TypeError(f"cannot set {dotted_key!r}: {part!r} is not a mapping")
            current = child
        current[parts[-1]] = value
