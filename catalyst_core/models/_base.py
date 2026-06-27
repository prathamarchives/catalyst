"""Small Pydantic compatibility layer.

Catalyst prefers Pydantic models when the dependency is installed, but the local
engine must still run from a fresh checkout with no Python package install. The
fallback implements the tiny subset we need for validation-shaped data objects.
"""
from __future__ import annotations

from copy import deepcopy

try:  # pragma: no cover - exercised only when pydantic is installed
    from pydantic import BaseModel, Field
    if not hasattr(BaseModel, "model_dump"):  # pydantic v1 compatibility
        BaseModel.model_dump = lambda self: self.dict()
except Exception:  # pragma: no cover - simple fallback is covered indirectly
    _MISSING = object()

    def Field(default=_MISSING, default_factory=None, **_kwargs):
        if default_factory is not None:
            return default_factory()
        if default is _MISSING:
            return None
        return default

    class BaseModel:
        def __init__(self, **data):
            annotations = getattr(self, "__annotations__", {})
            for key in annotations:
                if key in data:
                    value = data[key]
                else:
                    value = deepcopy(getattr(self.__class__, key, None))
                setattr(self, key, value)
            for key, value in data.items():
                if key not in annotations:
                    setattr(self, key, value)

        @classmethod
        def model_validate(cls, data):
            return cls(**(data or {}))

        def model_dump(self):
            def dump(value):
                if hasattr(value, "model_dump"):
                    return value.model_dump()
                if isinstance(value, list):
                    return [dump(v) for v in value]
                if isinstance(value, dict):
                    return {k: dump(v) for k, v in value.items()}
                return value

            return {k: dump(v) for k, v in self.__dict__.items()}
