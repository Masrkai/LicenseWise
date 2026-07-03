"""Output formatting for LicenseWise results."""

from typing import Any, Dict, List, Optional

from interface.common import suggest_alternatives

# Declarative label maps
PERMISSION_LABELS = [
    ("commercial_use", "Commercial use"),
    ("modification", "Modification"),
    ("distribution", "Distribution"),
    ("private_use", "Private use"),
]

CONDITION_LABELS = [
    ("include_copyright", "Include copyright notice"),
    ("include_license", "Include license text"),
    ("disclose_source", "Disclose source code"),
    ("same_license", "Use same license for derivatives"),
    ("document_changes", "Document changes"),
    ("net_copyleft", "Network copyleft (AGPL-style)"),
]

LIMITATION_LABELS = [
    ("liability", "No liability warranty"),
    ("warranty", "No warranty"),
]


def format_compatibility_result(result: Dict[str, Any], license_id: str) -> str:
    """Format a backward_chain result into human-readable text."""
    lines = []

    if result["compatible"] is True:
        lines.append(f"COMPATIBLE\n\n{license_id} is compatible with your intended use.\n")
    elif result["compatible"] is False:
        lines.append(f"NOT COMPATIBLE\n\n{license_id} is not compatible with your intended use.\n")
    else:
        lines.append(f"UNCLEAR\n\nCompatibility could not be determined for {license_id}.\n")

    if result.get("violations"):
        lines.append("Violations Found\n")
        for v in result["violations"]:
            lines.append(f"  - {v}")
        lines.append("")

    if result.get("explanation"):
        lines.append(f"Analysis\n\n{result['explanation']}\n")

    if result.get("how"):
        lines.append("Reasoning\n")
        for line in result["how"].split("\n"):
            if line.strip():
                lines.append(f"  {line}")
        lines.append("")

    if result.get("warnings"):
        lines.append("Warnings\n")
        for w in result["warnings"]:
            lines.append(f"  - {w}")
        lines.append("")

    if result.get("license_info"):
        lines.extend(_format_license_info(result["license_info"]))

    if not result["compatible"] and result.get("violations"):
        suggestions = _get_suggestions(result)
        if suggestions:
            lines.append("Alternative Licenses to Consider\n")
            for sugg in suggestions:
                lines.append(f"  - {sugg}")
            lines.append("")

    lines.append("---\n")
    lines.append("Disclaimer: This analysis is for educational purposes only and does not constitute legal advice. ")
    lines.append("Consult a qualified intellectual property lawyer for production use.")

    return "\n".join(lines)


def _format_license_info(lic: Dict) -> List[str]:
    """Format license metadata into text lines."""
    lines = ["License Information\n"]
    lines.append(f"  Name: {lic.get('name', 'unknown')}")
    lines.append(f"  Type: {lic.get('type', 'unknown').title()}")
    if lic.get("description"):
        lines.append(f"  Description: {lic['description']}")

    if lic.get("permissions"):
        lines.append("\n  Permissions:")
        for key, label in PERMISSION_LABELS:
            if lic["permissions"].get(key):
                lines.append(f"    + {label}")

    if lic.get("conditions"):
        conds = lic["conditions"]
        conditions_list = [label for key, label in CONDITION_LABELS if conds.get(key)]
        if conditions_list:
            lines.append("\n  Conditions:")
            for cond in conditions_list:
                lines.append(f"    - {cond}")

    if lic.get("limitations"):
        lims = lic["limitations"]
        lines.append("\n  Limitations:")
        for key, label in LIMITATION_LABELS:
            if lims.get(key):
                lines.append(f"    ! {label}")
        if not lims.get("patent_use"):
            lines.append("    ! No patent grant")
        if not lims.get("trademark_use"):
            lines.append("    ! No trademark rights")

    lines.append("")
    return lines


def _get_suggestions(result: Dict) -> List[str]:
    """Get alternative license suggestions based on violations."""
    all_text = (
        " ".join(result["violations"]).lower()
        + " "
        + result.get("explanation", "").lower()
    )
    return suggest_alternatives(all_text, format="plain")
