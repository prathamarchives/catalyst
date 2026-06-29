"""Catalyst Core Layer 2.

Catalyst Core is a headless cognitive kernel for agents. It owns the event log,
typed cognitive objects, graph, retrieval, evaluation, feedback learning, and
packet compilation. Product surfaces are clients, not part of the core.
"""
from __future__ import annotations

from .api.core_api import CatalystCore

__all__ = ["CatalystCore"]

