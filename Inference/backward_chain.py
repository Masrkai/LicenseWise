from typing import Dict, List, Any

def backward_chain(
    license_id: str,
    facts: Dict[str, Any],
    licenses_data: List[Dict]
) -> Dict[str, Any]:
    """
    Check compatibility of a specific license with user facts.

    Args:
        license_id: SPDX id or id of the license (e.g., "GPL-3.0", "MIT")
        facts: user answers (closed_source, saas, commercial_use, wants_relicense, need_patent_protection)
        licenses_data: list of all license dicts from JSON

    Returns:
        dict with keys: compatible (bool), violations (list), explanation (str), how (str), license_info (dict)
    """
    # Find license
    license_info = None
    for lic in licenses_data:
        if lic.get("id") == license_id or lic.get("spdx_id") == license_id:
            license_info = lic
            break

    if not license_info:
        return {
            "compatible": False,
            "violations": [f"License '{license_id}' not found in knowledge base."],
            "explanation": "Unknown license identifier.",
            "how": "The engine could not find this license in the SPDX database.",
            "license_info": None
        }

    violations = []
    explanations = []
    how_steps = []

    conditions = license_info.get("conditions", {})
    permissions = license_info.get("permissions", {})

    # 1. Source disclosure check
    if conditions.get("disclose_source") and facts.get("closed_source"):
        violations.append("source_disclosure_required")
        explanations.append(
            f"{license_id} requires disclosing source code (disclose_source=true), "
            f"but you indicated closed_source=true."
        )
        how_steps.append(
            f"Checked condition disclose_source=true in {license_id}; your answer closed_source=true → violation."
        )

    # 2. Same license check
    if conditions.get("same_license") and facts.get("wants_relicense"):
        violations.append("same_license_required")
        explanations.append(
            f"{license_id} requires derivatives to use the same license (same_license=true), "
            f"but you want freedom to relicense."
        )
        how_steps.append(
            f"Checked condition same_license=true in {license_id}; your answer wants_relicense=true → violation."
        )

    # 3. Network copyleft check
    if conditions.get("net_copyleft") and facts.get("saas") and facts.get("closed_source"):
        violations.append("network_copyleft_conflict")
        explanations.append(
            f"{license_id} triggers copyleft on network use (net_copyleft=true). "
            f"Running as closed-source SaaS violates this condition."
        )
        how_steps.append(
            f"Checked condition net_copyleft=true in {license_id}; your answers saas=true and closed_source=true → violation."
        )

    # 4. Commercial use check
    if not permissions.get("commercial_use") and facts.get("commercial_use"):
        violations.append("commercial_use_prohibited")
        explanations.append(
            f"{license_id} does not permit commercial use (commercial_use=false)."
        )
        how_steps.append(
            f"Checked permission commercial_use=false in {license_id}; your answer commercial_use=true → violation."
        )

    # 5. Patent protection warning (not a violation)
    if facts.get("need_patent_protection") and not license_info.get("limitations", {}).get("patent_use"):
        explanations.append(
            f"⚠️ {license_id} does not include an explicit patent grant. "
            f"Consider Apache-2.0 if patent protection is critical."
        )
        how_steps.append(
            f"Checked limitation patent_use=false in {license_id}; your need_patent_protection=true → warning generated."
        )

    compatible = len(violations) == 0
    how_text = "\n".join(how_steps) if how_steps else (
        f"No conflicts found: All conditions and permissions of {license_id} are satisfied by your answers."
    )

    return {
        "compatible": compatible,
        "violations": violations,
        "explanation": "\n".join(explanations) if explanations else f"{license_id} is compatible with your intended use.",
        "how": how_text,
        "license_info": license_info
    }