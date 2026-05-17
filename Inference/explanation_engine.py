from typing import Dict, List, Any

def explain_question(fact_name: str) -> str:
    """Return an explanation why a particular question is asked."""
    explanations = {
        "closed_source": (
            "We need to know if you'll distribute source code because strong copyleft "
            "licenses (GPL-3.0, AGPL-3.0) REQUIRE source disclosure. If you keep code private, "
            "these licenses are incompatible."
        ),
        "saas": (
            "Network deployment matters because AGPL-3.0 triggers copyleft when users interact "
            "over a network – even without distribution. This closes the 'SaaS loophole'."
        ),
        "commercial_use": (
            "Some licenses explicitly prohibit commercial use (e.g., CC-BY-NC-4.0). Most open source "
            "licenses allow it, but we must confirm to eliminate non‑commercial licenses."
        ),
        "need_patent_protection": (
            "Patent protection is not offered by all licenses. MIT and BSD have no patent grant; "
            "Apache-2.0 includes a strong patent clause."
        ),
        "want_copyleft": (
            "Copyleft ensures that modified versions remain open source. Strong copyleft (GPL, AGPL) "
            "affects the whole work; weak copyleft (LGPL, MPL) only affects certain parts."
        ),
        "want_weak_copyleft": (
            "Weak copyleft is ideal for libraries: the library stays open but applications linking to it "
            "can be proprietary."
        ),
        "want_file_copyleft": (
            "File‑level copyleft (MPL‑2.0) means only modified files must stay open – good for mixed codebases."
        ),
        "wants_relicense": (
            "Some licenses (GPL, AGPL) require derivatives to use the same license. If you want to relicense "
            "freely, we avoid those."
        ),
        "project_type": (
            "Licenses are designed for specific types of work: software, libraries, or creative content. "
            "This affects copyleft scope and compatibility."
        ),
        "want_public_domain": (
            "Public domain dedication (Unlicense) imposes no conditions but may not be legally recognised "
            "everywhere. CC0 is a safer alternative."
        ),
        "want_simple_permissive": (
            "Simple permissive licenses (MIT, BSD) only require retaining the copyright notice. "
            "They are the easiest to comply with but offer no patent protection."
        ),
        "academic_project": (
            "Academic projects often prefer BSD‑2‑Clause due to its history in research settings."
        ),
        "mixed_open_proprietary": (
            "MPL‑2.0 is designed for mixed open/proprietary codebases – file‑level copyleft keeps modified "
            "files open while allowing proprietary additions."
        ),
        "linking_type": (
            "LGPL‑2.1 compliance depends on linking type: dynamic linking is generally safe for proprietary "
            "apps; static linking may require open sourcing the combined work."
        ),
        "modify_library": (
            "If you modify a copyleft library, you must share those modifications. This affects whether LGPL "
            "or stronger copyleft applies."
        ),
        "concerned_about_legal_recognition": (
            "Some licenses (Unlicense) rely on public domain, which is not recognised in all countries. "
            "We need to know if legal certainty is a priority."
        ),
    }
    return explanations.get(fact_name, "This question helps narrow down compatible licenses.")


def format_trace(trace: List[Dict]) -> str:
    """Format the reasoning trace into a human-readable string."""
    if not trace:
        return "No rules were fired during inference."

    lines = []
    lines.append("🔍 HOW THE ENGINE REACHED THIS CONCLUSION:")
    lines.append("=" * 60)

    for entry in trace:
        icon = {"RECOMMEND": "✅", "ELIMINATE": "❌", "WARN": "⚠️"}.get(entry.get("action", "OTHER"), "•")
        lines.append(f"\nStep {entry['step']}: {icon} {entry['rule_name']}")
        lines.append(f"   Action: {entry.get('action', 'UNKNOWN')}")
        if entry.get("matched_facts"):
            lines.append("   Because you answered:")
            for fact, value in entry["matched_facts"].items():
                fact_display = fact.replace("_", " ").title()
                value_display = "Yes" if value is True else "No" if value is False else str(value)
                lines.append(f"      • {fact_display}: {value_display}")
        lines.append(f"   Why: {entry['explanation']}")
    return "\n".join(lines)


def generate_final_report(wm: Dict[str, Any], facts: Dict[str, Any], trace: List[Dict]) -> str:
    """Generate the complete final report including reasoning trace."""
    lines = []
    lines.append("=" * 60)
    lines.append("📋 LICENSEWISE FINAL REPORT")
    lines.append("=" * 60)

    if wm["recommended"]:
        lines.append("\n✅ RECOMMENDED LICENSES:")
        for lic in sorted(wm["recommended"]):
            lines.append(f"   • {lic}")
    else:
        lines.append("\n⚠️ No licenses were recommended. Please review your project goals.")

    if wm["eliminated"]:
        lines.append("\n❌ ELIMINATED LICENSES:")
        for lic in sorted(wm["eliminated"]):
            lines.append(f"   • {lic}")

    if wm["warnings"]:
        lines.append("\n⚠️ WARNINGS:")
        for warn in wm["warnings"]:
            lines.append(f"   • {warn}")

    # Confidence calculation (simple heuristic)
    provided = sum(1 for v in facts.values() if v is not None)
    total = len(facts)
    confidence = "HIGH" if provided >= 8 and len(wm["recommended"]) >= 1 else "MEDIUM" if provided >= 4 else "LOW"
    lines.append(f"\n🎯 CONFIDENCE: {confidence} (provided {provided}/{total} facts)")

    lines.append("\n" + format_trace(trace))

    lines.append("\n" + "=" * 60)
    lines.append("⚠️ DISCLAIMER: This is not legal advice. Consult a lawyer for production use.")
    lines.append("=" * 60)
    return "\n".join(lines)


def generate_summary(wm: Dict[str, Any], facts: Dict[str, Any], trace: List[Dict]) -> str:
    """Concise summary of how the conclusion was reached."""
    lines = []
    lines.append("\n📖 EXPLANATION: How did the engine get this result?")
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
    lines.append("Each step above was triggered by matching your answers against the rule base.")
    return "\n".join(lines)