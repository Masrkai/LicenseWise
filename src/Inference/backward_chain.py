from typing import Dict, List, Any
from Rules.rules import RULES
from Inference.forward_chain import forward_chain

def backward_chain(
    license_id: str,
    facts: Dict[str, Any],
    licenses_data: List[Dict],
) -> Dict[str, Any]:
    """
    Check compatibility of a specific licence by running the same forward rules
    and interpreting the result for that licence.

    Args:
        license_id: the licence to check (e.g. "GPL-3.0", "MIT")
        facts: user answers
        licenses_data: list of licence dicts

    Returns:
        dict with keys: compatible, violations, explanation, how, license_info, trace
    """
    # 1. Run the forward engine – exact same rules, exact same logic
    trace: List[Dict] = []
    wm = forward_chain(facts, RULES, licenses_data, trace)

    # 2. Determine status of the requested licence
    recommended = wm.get("recommended", set())
    eliminated  = wm.get("eliminated", set())
    warnings    = wm.get("warnings", [])

    # 3. Find the licence object (for metadata in the result)
    lic = None
    for l in licenses_data:
        if l.get("id") == license_id or l.get("spdx_id") == license_id:
            lic = l
            break

    # Normalize license_id to match what might be in the rules
    # Check both the original ID and the spdx_id from the license object
    possible_ids = {license_id}
    if lic:
        possible_ids.add(lic.get("id"))
        possible_ids.add(lic.get("spdx_id"))
    possible_ids.discard(None)

    # 4. Interpret the working memory for this licence
    is_eliminated = any(pid in eliminated for pid in possible_ids)
    is_recommended = any(pid in recommended for pid in possible_ids)

    if is_eliminated:
        # It was eliminated by at least one rule
        compatible = False
        # Collect violations from trace steps that eliminated this licence
        violation_steps = [
            s for s in trace 
            if s["action"] == "ELIMINATE" 
            and any(pid in s.get("licenses_affected", []) for pid in possible_ids)
        ]
        violations = [s["explanation"] for s in violation_steps]
        how_steps = [f"Step {s['step']}: {s['explanation']}" for s in violation_steps]
        explanation = "\n".join(violations) if violations else f"{license_id} was eliminated by the rules."
        how = "\n".join(how_steps)
        
    elif is_recommended:
        compatible = True
        rec_steps = [
            s for s in trace 
            if s["action"] == "RECOMMEND" 
            and any(pid in s.get("licenses_affected", []) for pid in possible_ids)
        ]
        explanation = f"{license_id} is recommended based on your answers."
        how = "\n".join(
            f"Step {s['step']}: {s['explanation']}" for s in rec_steps
        ) if rec_steps else "Forward rules did not explicitly recommend this licence."
        violations = []
        
    else:
        # Licence was neither recommended nor eliminated
        # Fall back to direct metadata check
        if lic is None:
            return {
                "compatible": False,
                "violations": [f"License '{license_id}' not found in the database."],
                "explanation": f"Unknown licence: {license_id}",
                "how": "This license is not in our database. Please check the spelling or use a valid SPDX ID.",
                "license_info": None,
                "trace": trace
            }
        
        # Direct check using license metadata
        violations = []
        how_steps = []
        conds = lic.get("conditions", {})
        perms = lic.get("permissions", {})
        lims = lic.get("limitations", {})
        
        # Check for conflicts
        if conds.get("disclose_source") and facts.get("closed_source"):
            violations.append("License requires source disclosure, but you want closed-source")
            how_steps.append(f"{license_id} requires disclose_source=true, but you answered closed_source=true")
            
        if conds.get("same_license") and facts.get("wants_relicense"):
            violations.append("License requires derivatives to use the same license, but you want to relicense")
            how_steps.append(f"{license_id} requires same_license=true, but you answered wants_relicense=true")
            
        if conds.get("net_copyleft") and facts.get("saas") and facts.get("closed_source"):
            violations.append("License has network copyleft, incompatible with closed-source SaaS")
            how_steps.append(f"{license_id} has net_copyleft=true, but you want SaaS + closed-source")
            
        if not perms.get("commercial_use") and facts.get("commercial_use"):
            violations.append("License prohibits commercial use, but you need it")
            how_steps.append(f"{license_id} has commercial_use=false, but you answered commercial_use=true")
        
        # Warnings (not violations)
        if facts.get("need_patent_protection") and not lims.get("patent_use"):
            how_steps.append(f"{license_id} offers no patent protection (patent_use=false) - consider this carefully")
        
        compatible = len(violations) == 0
        explanation = "\n".join(violations) if violations else f"{license_id} appears compatible based on metadata."
        how = "\n".join(how_steps) if how_steps else "No conflicts found in direct metadata check."

    # Add relevant warnings for this license
    relevant_warnings = []
    for step in trace:
        if (step["action"] == "WARN" 
            and any(pid in step.get("licenses_affected", []) for pid in possible_ids)):
            relevant_warnings.append(step["explanation"])

    return {
        "compatible": compatible,
        "violations": violations,
        "explanation": explanation,
        "how": how,
        "license_info": lic,
        "warnings": relevant_warnings,
        "trace": trace
    }