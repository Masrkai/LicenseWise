from typing import Any, Dict, List

from Inference import get_engine


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
    engine = get_engine()
    wm = engine.forward_chain(facts, licenses_data)
    trace.extend(engine.build_trace())
    return wm
