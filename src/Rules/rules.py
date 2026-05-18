from typing import Dict, List

# Helper to check common facts
def _saas(facts: Dict) -> bool:
    return facts.get("saas") is True or facts.get("network_saas") is True

def _copyleft(facts: Dict) -> bool:
    return facts.get("want_copyleft") is True or facts.get("wants_derivatives_open") is True

def _patent(facts: Dict) -> bool:
    return facts.get("need_patent_protection") is True or facts.get("patent_protection_needed") is True

def _private_mods(facts: Dict) -> bool:
    return (facts.get("closed_source") is True or
            facts.get("wants_relicense") is True or
            facts.get("wants_to_keep_modifications_private") is True)

# ----------------------------------------------------------------------
# Rule definitions: each rule is a dict with keys:
#   id, name, condition, action, explanation, action_type (RECOMMEND/ELIMINATE/WARN)
#   licenses_affected: list of license IDs this action applies to
# Condition signature: condition(facts, licenses_data) -> bool
# Action signature: action(working_memory) -> None
# ----------------------------------------------------------------------

def build_rules() -> List[Dict]:
    rules = []

    # ----- A. Permissive licenses -----
    # MIT
    rules.append({
        "id": "A01",
        "name": "recommend_MIT_if_closed_source",
        "condition": lambda f, _: f.get("closed_source") is True,
        "action": lambda wm: wm["recommended"].add("MIT"),
        "explanation": "MIT does not require source disclosure, safe for closed-source projects.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["MIT"]
    })
    rules.append({
        "id": "A02",
        "name": "recommend_MIT_if_saas",
        "condition": lambda f, _: _saas(f),
        "action": lambda wm: wm["recommended"].add("MIT"),
        "explanation": "MIT has no network copyleft, suitable for SaaS.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["MIT"]
    })
    rules.append({
        "id": "A03",
        "name": "recommend_MIT_if_simple_permissive",
        "condition": lambda f, _: f.get("want_simple_permissive") is True,
        "action": lambda wm: wm["recommended"].add("MIT"),
        "explanation": "MIT is the simplest and most widely adopted permissive license.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["MIT"]
    })
    rules.append({
        "id": "A04",
        "name": "warn_MIT_no_patent_grant",
        "condition": lambda f, _: _patent(f),
        "action": lambda wm: wm["warnings"].append("MIT: No explicit patent grant. Consider Apache-2.0."),
        "explanation": "MIT does not grant patent rights.",
        "action_type": "WARN",
        "licenses_affected": ["MIT"]
    })

    # Apache-2.0
    rules.append({
        "id": "A05",
        "name": "recommend_Apache_if_closed_source",
        "condition": lambda f, _: f.get("closed_source") is True,
        "action": lambda wm: wm["recommended"].add("Apache-2.0"),
        "explanation": "Apache-2.0 does not require source disclosure, safe for closed-source.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["Apache-2.0"]
    })
    rules.append({
        "id": "A06",
        "name": "recommend_Apache_if_patent_protection",
        "condition": lambda f, _: _patent(f),
        "action": lambda wm: wm["recommended"].add("Apache-2.0"),
        "explanation": "Apache-2.0 includes explicit patent grant and protection.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["Apache-2.0"]
    })
    rules.append({
        "id": "A07",
        "name": "recommend_Apache_if_commercial",
        "condition": lambda f, _: f.get("commercial_use") is True,
        "action": lambda wm: wm["recommended"].add("Apache-2.0"),
        "explanation": "Apache-2.0 permits commercial use and includes patent protections.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["Apache-2.0"]
    })
    rules.append({
        "id": "A08",
        "name": "warn_Apache_document_changes",
        "condition": lambda f, _: f.get("wants_minimal_attribution") is True,
        "action": lambda wm: wm["warnings"].append("Apache-2.0: Requires documenting changes in distributed works."),
        "explanation": "Apache-2.0 has a condition to document changes.",
        "action_type": "WARN",
        "licenses_affected": ["Apache-2.0"]
    })

    # BSD-2-Clause
    rules.append({
        "id": "A09",
        "name": "recommend_BSD_if_closed_source",
        "condition": lambda f, _: f.get("closed_source") is True,
        "action": lambda wm: wm["recommended"].add("BSD-2-Clause"),
        "explanation": "BSD-2-Clause requires no source disclosure.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["BSD-2-Clause"]
    })
    rules.append({
        "id": "A10",
        "name": "recommend_BSD_if_simple_permissive",
        "condition": lambda f, _: f.get("want_simple_permissive") is True,
        "action": lambda wm: wm["recommended"].add("BSD-2-Clause"),
        "explanation": "BSD-2-Clause is a simple permissive license similar to MIT.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["BSD-2-Clause"]
    })
    rules.append({
        "id": "A11",
        "name": "warn_BSD_no_patent_grant",
        "condition": lambda f, _: _patent(f),
        "action": lambda wm: wm["warnings"].append("BSD-2-Clause: No patent grant. Consider Apache-2.0."),
        "explanation": "BSD licenses offer no patent protection.",
        "action_type": "WARN",
        "licenses_affected": ["BSD-2-Clause"]
    })

    # Unlicense / CC0
    rules.append({
        "id": "A12",
        "name": "recommend_Unlicense_if_public_domain",
        "condition": lambda f, _: f.get("want_public_domain") is True,
        "action": lambda wm: wm["recommended"].update(["Unlicense", "CC0-1.0"]),
        "explanation": "Unlicense and CC0 dedicate work to the public domain with no restrictions.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["Unlicense", "CC0-1.0"]
    })
    rules.append({
        "id": "A13",
        "name": "warn_Unlicense_jurisdiction",
        "condition": lambda f, _: f.get("concerned_about_legal_recognition") is True,
        "action": lambda wm: wm["warnings"].append("Unlicense: Not recognized in all jurisdictions. Consider CC0."),
        "explanation": "Public domain dedication may not be legally valid worldwide.",
        "action_type": "WARN",
        "licenses_affected": ["Unlicense"]
    })

    # ----- B. Copyleft licenses -----
    # GPL-3.0
    rules.append({
        "id": "B01",
        "name": "recommend_GPL_if_copyleft",
        "condition": lambda f, _: _copyleft(f) and not f.get("closed_source") and not _saas(f),
        "action": lambda wm: wm["recommended"].add("GPL-3.0"),
        "explanation": "GPL-3.0 ensures distributed derivatives remain open source.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["GPL-3.0"]
    })
    rules.append({
        "id": "B02",
        "name": "eliminate_GPL_if_closed_source",
        "condition": lambda f, _: f.get("closed_source") is True,
        "action": lambda wm: wm["eliminated"].add("GPL-3.0"),
        "explanation": "GPL requires source disclosure, incompatible with closed source.",
        "action_type": "ELIMINATE",
        "licenses_affected": ["GPL-3.0"]
    })
    rules.append({
        "id": "B03",
        "name": "eliminate_GPL_if_wants_relicense",
        "condition": lambda f, _: f.get("wants_relicense") is True,
        "action": lambda wm: wm["eliminated"].add("GPL-3.0"),
        "explanation": "GPL requires same license for derivatives.",
        "action_type": "ELIMINATE",
        "licenses_affected": ["GPL-3.0"]
    })
    rules.append({
        "id": "B04",
        "name": "warn_GPL_saas_loophole",
        "condition": lambda f, _: _saas(f) and _copyleft(f),
        "action": lambda wm: wm["warnings"].append("GPL-3.0: SaaS use does NOT trigger copyleft. Consider AGPL-3.0."),
        "explanation": "GPL's copyleft only applies on distribution, not network use.",
        "action_type": "WARN",
        "licenses_affected": ["GPL-3.0"]
    })

    # AGPL-3.0
    rules.append({
        "id": "B05",
        "name": "recommend_AGPL_if_saas_copyleft",
        "condition": lambda f, _: _saas(f) and _copyleft(f) and not f.get("closed_source"),
        "action": lambda wm: wm["recommended"].add("AGPL-3.0"),
        "explanation": "AGPL-3.0 closes the SaaS loophole – network use triggers copyleft.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["AGPL-3.0"]
    })
    rules.append({
        "id": "B06",
        "name": "eliminate_AGPL_if_closed_source",
        "condition": lambda f, _: f.get("closed_source") is True,
        "action": lambda wm: wm["eliminated"].add("AGPL-3.0"),
        "explanation": "AGPL requires source disclosure even for network use.",
        "action_type": "ELIMINATE",
        "licenses_affected": ["AGPL-3.0"]
    })
    rules.append({
        "id": "B07",
        "name": "warn_AGPL_strongest_copyleft",
        "condition": lambda f, _: _copyleft(f),
        "action": lambda wm: wm["warnings"].append("AGPL-3.0: Strongest copyleft – affects distribution AND network use."),
        "explanation": "AGPL is very restrictive; many companies prohibit its use.",
        "action_type": "WARN",
        "licenses_affected": ["AGPL-3.0"]
    })

    # ----- C. Weak copyleft / middle-ground -----
    # LGPL-2.1
    rules.append({
        "id": "C01",
        "name": "recommend_LGPL_for_library",
        "condition": lambda f, _: f.get("project_type") == "library" and f.get("want_weak_copyleft") is True,
        "action": lambda wm: wm["recommended"].update(["LGPL-2.1", "LGPL-3.0"]),
        "explanation": "LGPL keeps the library open but allows proprietary linking.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["LGPL-2.1", "LGPL-3.0"]
    })
    rules.append({
        "id": "C02",
        "name": "warn_LGPL_static_linking",
        "condition": lambda f, _: f.get("linking_type") == "static",
        "action": lambda wm: wm["warnings"].append("LGPL-2.1: Static linking may require the combined work to be LGPL."),
        "explanation": "Dynamic linking is safer for proprietary apps.",
        "action_type": "WARN",
        "licenses_affected": ["LGPL-2.1"]
    })

    # MPL-2.0
    rules.append({
        "id": "C03",
        "name": "recommend_MPL_if_file_copyleft",
        "condition": lambda f, _: f.get("want_file_copyleft") is True and not f.get("closed_source"),
        "action": lambda wm: wm["recommended"].add("MPL-2.0"),
        "explanation": "MPL-2.0 uses file-level copyleft – only modified files must stay open.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["MPL-2.0"]
    })
    rules.append({
        "id": "C04",
        "name": "recommend_MPL_if_mixed_codebase",
        "condition": lambda f, _: f.get("mixed_open_proprietary") is True,
        "action": lambda wm: wm["recommended"].add("MPL-2.0"),
        "explanation": "MPL-2.0 is ideal for mixed open/proprietary codebases.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["MPL-2.0"]
    })

    # ----- D. Content / non-software licenses -----
    rules.append({
        "id": "D01",
        "name": "recommend_CC_BY_NC_if_content_noncommercial",
        "condition": lambda f, _: f.get("project_type") == "content" and not f.get("commercial_use"),
        "action": lambda wm: wm["recommended"].add("CC-BY-NC-4.0"),
        "explanation": "CC-BY-NC-4.0 is for non-commercial creative content.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["CC-BY-NC-4.0"]
    })
    rules.append({
        "id": "D02",
        "name": "eliminate_CC_BY_NC_if_commercial",
        "condition": lambda f, _: f.get("commercial_use") is True,
        "action": lambda wm: wm["eliminated"].add("CC-BY-NC-4.0"),
        "explanation": "CC-BY-NC-4.0 prohibits commercial use.",
        "action_type": "ELIMINATE",
        "licenses_affected": ["CC-BY-NC-4.0"]
    })

    # ----- E. General elimination rules (copyleft when private mods wanted) -----
    rules.append({
        "id": "E01",
        "name": "exclude_copyleft_if_private_mods",
        "condition": lambda f, _: _private_mods(f),
        "action": lambda wm: wm["eliminated"].update(["GPL-2.0", "GPL-3.0", "AGPL-3.0"]),
        "explanation": "GPL and AGPL require source sharing of derivatives.",
        "action_type": "ELIMINATE",
        "licenses_affected": ["GPL-2.0", "GPL-3.0", "AGPL-3.0"]
    })

    return rules

# Pre‑build the rule list for import
RULES = build_rules()