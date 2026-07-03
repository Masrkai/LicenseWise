"""Forward chaining via Prolog: evaluate all rules and return working memory."""

from typing import Any, Dict, List, Optional

from Inference import get_engine
from Inference.prolog_engine import PrologEngine


def forward_chain(
    facts: Dict[str, Any],
    rules: List[Dict],
    licenses_data: List[Dict],
    trace: List[Dict],
    engine: Optional[PrologEngine] = None,
) -> Dict[str, Any]:
    """
    Forward chaining via Prolog: evaluate all rules and return working memory.

    Args:
        facts: user answers (closed_source, saas, etc.)
        rules: ignored — rules live in Prolog knowledge base
        licenses_data: list of all license dicts loaded from JSON
        trace: list to append fired rule steps (modified in place)
        engine: optional PrologEngine instance (for dependency injection)

    Returns:
        working_memory dict with keys: recommended (set), eliminated (set), warnings (list)
    """
    engine = engine or get_engine()
    wm = engine.forward_chain(facts, licenses_data)
    trace.extend(engine.trace_builder.build_trace())
    return wm
