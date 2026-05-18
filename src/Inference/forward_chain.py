from typing import Dict, List, Any


def forward_chain(
    facts: Dict[str, Any],
    rules: List[Dict],
    licenses_data: List[Dict],
    trace: List[Dict],
) -> Dict[str, Any]:
    """
    Forward chaining: evaluate all rules and return working memory.

    Args:
        facts: user answers (closed_source, saas, etc.)
        rules: list of rule dicts with keys: id, condition, action, explanation, ...
        licenses_data: list of all license dicts loaded from JSON
        trace: list to append fired rule steps (modified in place)

    Returns:
        working_memory dict with keys: recommended (set), eliminated (set), warnings (list)
    """
    wm = {
        "recommended": set(),
        "eliminated": set(),
        "warnings": [],
    }

    for rule in rules:
        try:
            if rule["condition"](facts, licenses_data):
                # Record step
                step = {
                    "step": len(trace) + 1,
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "matched_facts": {k: v for k, v in facts.items() if v is not None},
                    "explanation": rule["explanation"],
                    "action": rule.get("action_type", "UNKNOWN"),
                    "licenses_affected": rule.get("licenses_affected", [])
                }
                trace.append(step)

                # Execute action
                rule["action"](wm)
        except Exception:
            # Skip rules that fail due to missing data
            continue

    # Remove eliminated from recommended
    wm["recommended"] -= wm["eliminated"]
    return wm