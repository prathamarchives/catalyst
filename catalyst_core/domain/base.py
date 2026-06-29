"""Small model compatibility layer.

The core prefers Pydantic when installed but must run from a fresh checkout with
only the Python standard library. The fallback implements the tiny subset of
model behavior used by the kernel.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from typing import Any
from uuid import uuid4

try:  # pragma: no cover - exercised only when pydantic is installed
    from pydantic import BaseModel, Field

    if not hasattr(BaseModel, "model_dump"):  # pydantic v1 compatibility
        BaseModel.model_dump = lambda self: self.dict()
    if not hasattr(BaseModel, "model_validate"):  # pydantic v1 compatibility
        BaseModel.model_validate = classmethod(lambda cls, data: cls.parse_obj(data or {}))
except Exception:  # pragma: no cover - fallback is covered indirectly
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
            if isinstance(data, cls):
                return data
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


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


def to_json(value: Any) -> str:
    return json.dumps(value or {}, ensure_ascii=False, sort_keys=True)


def from_json(value: str | None, default=None):
    if not value:
        return {} if default is None else default
    try:
        return json.loads(value)
    except Exception:
        return {} if default is None else default


def dump_model(value):
    return value.model_dump() if hasattr(value, "model_dump") else dict(value or {})
