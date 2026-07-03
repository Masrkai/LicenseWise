"""Backward chaining via Prolog: check compatibility of a specific license."""

from typing import Any, Dict, List, Optional

from Inference import get_engine
from Inference.prolog_engine import PrologEngine


def backward_chain(
    license_id: str,
    facts: Dict[str, Any],
    licenses_data: List[Dict],
    engine: Optional[PrologEngine] = None,
) -> Dict[str, Any]:
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
