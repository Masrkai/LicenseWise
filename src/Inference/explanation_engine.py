"""Explanation and report generation for LicenseWise inference results."""

from typing import Any, Dict, List, Optional

from Inference import get_engine
from Inference.prolog_engine import PrologEngine
from Data.report_templates import (
    REPORT_HEADER,
    SECTION_RECOMMENDED,
    SECTION_ELIMINATED,
    SECTION_WARNINGS,
    SECTION_CONFIDENCE,
    TRACE_HEADER,
    TRACE_ACTION_ICONS,
    SUMMARY_HEADER,
    SUMMARY_RECOMMENDED,
    SUMMARY_ELIMINATED,
    SUMMARY_WARNED,
    SUMMARY_FOOTER,
    NO_LICENSES_RECOMMENDED,
    NO_RULES_FIRED,
    DISCLAIMER,
    SEP,
    SEP_SHORT,
)


def explain_question(fact_name: str, engine: Optional[PrologEngine] = None) -> str:
    """Return an explanation why a particular question is asked (from Prolog KB)."""
    engine = engine or get_engine()
    return engine.get_question_explanation(fact_name)


def format_trace(trace: List[Dict]) -> str:
    """Format the reasoning trace into a human-readable string."""
    if not trace:
        return NO_RULES_FIRED

    lines = [TRACE_HEADER, SEP]

    for entry in trace:
        icon = TRACE_ACTION_ICONS.get(entry.get("action", "OTHER"), "*")
        lines.append(f"\nStep {entry['step']}: [{icon}] {entry['rule_name']}")
        lines.append(f"   Action: {entry.get('action', 'UNKNOWN')}")
        if entry.get("matched_facts"):
            lines.append("   Because you answered:")
            for fact, value in entry["matched_facts"].items():
                fact_display = fact.replace("_", " ").title()
                value_display = "Yes" if value is True else "No" if value is False else str(value)
                lines.append(f"      - {fact_display}: {value_display}")
        lines.append(f"   Why: {entry['explanation']}")
    return "\n".join(lines)


def generate_final_report(
    wm: Dict[str, Any], facts: Dict[str, Any], trace: List[Dict],
    include_trace: bool = True,
) -> str:
    """Generate the complete final report including reasoning trace."""
    lines = [SEP, REPORT_HEADER, SEP]

    if wm["recommended"]:
        lines.append(f"\n{SECTION_RECOMMENDED}")
        for lic in sorted(wm["recommended"], key=str):
            lines.append(f"   * {lic}")
    else:
        lines.append(NO_LICENSES_RECOMMENDED)

    if wm["eliminated"]:
        lines.append(f"\n{SECTION_ELIMINATED}")
        for lic in sorted(wm["eliminated"], key=str):
            lines.append(f"   * {lic}")

    if wm["warnings"]:
        lines.append(f"\n{SECTION_WARNINGS}")
        for warn in wm["warnings"]:
            lines.append(f"   * {warn}")

    # Confidence calculation
    provided = sum(1 for v in facts.values() if v is not None)
    total = len(facts)
    confidence = (
        "HIGH" if provided >= 8 and len(wm["recommended"]) >= 1
        else "MEDIUM" if provided >= 4
        else "LOW"
    )
    lines.append(f"\n{SECTION_CONFIDENCE} {confidence} (provided {provided}/{total} facts)")

    if include_trace:
        lines.append("\n" + format_trace(trace))
        lines.extend(["\n" + SEP, DISCLAIMER, SEP])
    else:
        lines.append("\n" + DISCLAIMER)
    return "\n".join(lines)


def generate_summary(
    wm: Dict[str, Any], facts: Dict[str, Any], trace: List[Dict]
) -> str:
    """Concise summary of how the conclusion was reached."""
    lines = [f"\n{SUMMARY_HEADER}", SEP_SHORT]

    recommend_steps = [e for e in trace if "RECOMMEND" in e.get("action", "")]
    eliminate_steps = [e for e in trace if "ELIMINATE" in e.get("action", "")]
    warn_steps = [e for e in trace if "WARN" in e.get("action", "")]

    if recommend_steps:
        lines.append(f"\n{SUMMARY_RECOMMENDED}")
        for step in recommend_steps:
            lines.append(f"  {step['step']}. {step['explanation']}")

    if eliminate_steps:
        lines.append(f"\n{SUMMARY_ELIMINATED}")
        for step in eliminate_steps:
            lines.append(f"  {step['step']}. {step['explanation']}")

    if warn_steps:
        lines.append(f"\n{SUMMARY_WARNED}")
        for step in warn_steps:
            lines.append(f"  {step['step']}. {step['explanation']}")

    lines.extend(["\n" + SEP_SHORT, SUMMARY_FOOTER])
    return "\n".join(lines)
