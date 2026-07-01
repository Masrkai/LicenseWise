from typing import Any, Dict, List

from Inference.prolog_engine import PrologEngine

_engine = None


def _get_engine() -> PrologEngine:
    global _engine
    if _engine is None:
        _engine = PrologEngine()
    return _engine


def backward_chain(
    license_id: str,
    facts: Dict[str, Any],
    licenses_data: List[Dict],
) -> Dict[str, Any]:
    """
    Check compatibility of a specific licence using Prolog rules
    with a metadata fallback for licences not covered by rules.

    Args:
        license_id: the licence to check (e.g. "GPL-3.0", "MIT")
        facts: user answers
        licenses_data: list of licence dicts

    Returns:
        dict with keys: compatible, violations, explanation, how, license_info, warnings, trace
    """
    engine = _get_engine()
    return engine.backward_chain(license_id, facts, licenses_data)
