"""Backward chaining via Prolog: check compatibility of a specific license."""

from __future__ import annotations

from typing import Any

from . import get_engine
from .prolog_engine import PrologEngine


def backward_chain(
    license_id: str,
    facts: dict[str, Any],
    licenses_data: list[dict[str, Any]],
    engine: PrologEngine | None = None,
) -> dict[str, Any]:
    """
    Check compatibility of a specific licence using Prolog rules
    with a metadata fallback for licences not covered by rules.

    Args:
        license_id: the licence to check (e.g. "GPL-3.0", "MIT")
        facts: user answers
        licenses_data: list of licence dicts
        engine: optional PrologEngine instance (for dependency injection)

    Returns:
        dict with keys: compatible, violations, explanation, how, license_info, warnings, trace
    """
    engine = engine or get_engine()
    return engine.backward_chain(license_id, facts, licenses_data)
