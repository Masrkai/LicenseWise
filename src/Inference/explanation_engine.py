from typing import Any, Dict, List

from Inference.prolog_engine import PrologEngine

_engine = None


def _get_engine() -> PrologEngine:
    global _engine
    if _engine is None:
        _engine = PrologEngine()
    return _engine


def explain_question(fact_name: str) -> str:
    """Return an explanation why a particular question is asked (from Prolog KB)."""
    engine = _get_engine()
    return engine.get_question_explanation(fact_name)


def format_trace(trace: List[Dict]) -> str:
    """Format the reasoning trace into a human-readable string."""
    if not trace:
        return "No rules were fired during inference."

    lines = []
    lines.append("HOW THE ENGINE REACHED THIS CONCLUSION:")
    lines.append("=" * 60)

    for entry in trace:
        icon = {"RECOMMEND": "+", "ELIMINATE": "x", "WARN": "!"}.get(
            entry.get("action", "OTHER"), "*"
        )
        lines.append(f"\nStep {entry['step']}: [{icon}] {entry['rule_name']}")
        lines.append(f"   Action: {entry.get('action', 'UNKNOWN')}")
        if entry.get("matched_facts"):
            lines.append("   Because you answered:")
            for fact, value in entry["matched_facts"].items():
                fact_display = fact.replace("_", " ").title()
                value_display = (
                    "Yes" if value is True else "No" if value is False else str(value)
                )
                lines.append(f"      - {fact_display}: {value_display}")
        lines.append(f"   Why: {entry['explanation']}")
    return "\n".join(lines)


def generate_final_report(
    wm: Dict[str, Any], facts: Dict[str, Any], trace: List[Dict]
) -> str:
    """Generate the complete final report including reasoning trace."""
    lines = []
    lines.append("=" * 60)
    lines.append("LICENSEWISE FINAL REPORT")
    lines.append("=" * 60)

    if wm["recommended"]:
        lines.append("\nRECOMMENDED LICENSES:")
        for lic in sorted(wm["recommended"]):
            lines.append(f"   * {lic}")
    else:
        lines.append(
            "\nNo licenses were recommended. Please review your project goals."
        )

    if wm["eliminated"]:
        lines.append("\nELIMINATED LICENSES:")
        for lic in sorted(wm["eliminated"]):
            lines.append(f"   * {lic}")

    if wm["warnings"]:
        lines.append("\nWARNINGS:")
        for warn in wm["warnings"]:
            lines.append(f"   * {warn}")

    # Confidence calculation (simple heuristic)
    provided = sum(1 for v in facts.values() if v is not None)
    total = len(facts)
    confidence = (
        "HIGH"
        if provided >= 8 and len(wm["recommended"]) >= 1
        else "MEDIUM"
        if provided >= 4
        else "LOW"
    )
    lines.append(f"\nCONFIDENCE: {confidence} (provided {provided}/{total} facts)")

    lines.append("\n" + format_trace(trace))

    lines.append("\n" + "=" * 60)
    lines.append(
        "DISCLAIMER: This is not legal advice. Consult a lawyer for production use."
    )
    lines.append("=" * 60)
    return "\n".join(lines)


def generate_summary(
    wm: Dict[str, Any], facts: Dict[str, Any], trace: List[Dict]
) -> str:
    """Concise summary of how the conclusion was reached."""
    lines = []
    lines.append("\nEXPLANATION: How did the engine get this result?")
    lines.append("-" * 50)

    recommend_steps = [e for e in trace if "RECOMMEND" in e.get("action", "")]
    eliminate_steps = [e for e in trace if "ELIMINATE" in e.get("action", "")]
    warn_steps = [e for e in trace if "WARN" in e.get("action", "")]

    if recommend_steps:
        lines.append("\nThe engine RECOMMENDED licenses because:")
        for step in recommend_steps:
            lines.append(f"  {step['step']}. {step['explanation']}")

    if eliminate_steps:
        lines.append("\nThe engine ELIMINATED licenses because:")
        for step in eliminate_steps:
            lines.append(f"  {step['step']}. {step['explanation']}")

    if warn_steps:
        lines.append("\nThe engine WARNED because:")
        for step in warn_steps:
            lines.append(f"  {step['step']}. {step['explanation']}")

    lines.append("\n" + "-" * 50)
    lines.append(
        "Each step above was triggered by matching your answers against the rule base."
    )
    return "\n".join(lines)
