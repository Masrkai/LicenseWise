from typing import Any, Dict, List

from Inference.prolog_engine import PrologEngine

_engine = None


def _get_engine() -> PrologEngine:
    global _engine
    if _engine is None:
        _engine = PrologEngine()
    return _engine


def forward_chain(
    facts: Dict[str, Any],
    rules: List[Dict],
    licenses_data: List[Dict],
    trace: List[Dict],
) -> Dict[str, Any]:
    """
    Forward chaining via Prolog: evaluate all rules and return working memory.

    Args:
        facts: user answers (closed_source, saas, etc.)
        rules: ignored — rules live in Prolog knowledge base
        licenses_data: list of all license dicts loaded from JSON
        trace: list to append fired rule steps (modified in place)

    Returns:
        working_memory dict with keys: recommended (set), eliminated (set), warnings (list)
    """
    engine = _get_engine()
    wm = engine.forward_chain(facts, licenses_data)
    trace.extend(engine._build_trace())
    return wm
