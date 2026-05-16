"""
LicenseWise – Merged Rule Engine
=================================
Unified rule base combining both rule sets with all duplicates removed.
Rules are de-duplicated by logic; where both files covered the same scenario,
the richer explanation and any extra metadata are kept.

Rules are grouped into:
  A. Permissive license selection       (MIT, Apache-2.0, BSD-2-Clause, Unlicense)
  B. Copyleft license selection         (GPL-3.0, AGPL-3.0)
  C. Weak copyleft / middle-ground      (LGPL-2.1, MPL-2.0, EPL-2.0)
  D. Content / non-software licenses    (CC-*, OFL, datasets, AI weights, fonts)
  E. Source-available / proprietary     (SSPL, BSL, Elastic, no-license)
  F. Compatibility & conflict detection
  G. SaaS / network deployment
  H. Dependency analysis
  I. Special scenarios                  (patents, government, hardware, AI)

Working Memory structure (used by forward-chaining rules):
  {
      "recommended": set(),    # Licenses that match user needs
      "eliminated":  set(),    # Licenses incompatible with user needs
      "warnings":    list(),   # Cautions / compliance notes
      "flags":       list(),   # Hard conflict identifiers
      "scores":      dict(),   # License → score for ranking
  }

Facts (user inputs) expected in the facts dictionary:
  closed_source                  bool  – will not distribute source code
  saas / network_saas            bool  – used over a network (SaaS)
  commercial_use                 bool  – used commercially
  distribution                   bool  – software is distributed to external users
  is_software                    bool  – artefact is software (vs content/data)
  need_patent_protection /
    patent_protection_needed     bool  – explicit patent grant required
  want_copyleft /
    wants_derivatives_open       bool  – derivatives must stay open source
  want_weak_copyleft             bool  – library-level copyleft only
  want_file_copyleft             bool  – file-level copyleft only
  wants_relicense /
    wants_to_keep_modifications_private bool
  want_public_domain             bool  – dedicate to public domain
  want_simple_permissive         bool  – simplest permissive license
  wants_minimal_attribution      bool  – minimal attribution requirements
  no_attribution_needed          bool  – no attribution at all required
  protect_brand_name             bool  – non-endorsement protection needed
  project_type                   str   – "software" | "library" | "content" |
                                          "academic" | "government" |
                                          "hardware_description" | "mixed"
  content_type                   str   – "documentation" | "dataset" |
                                          "educational" | "ai_model_weights" | "font"
  ecosystem                      str   – e.g. "java"
  linking_type                   str   – "dynamic" | "static"
  mixed_open_proprietary         bool  – mixed open/proprietary codebase
  modify_library                 bool  – will modify the library itself
  modify_files                   bool  – will modify the licensed files
  academic_project               bool  – academic / research project
  open_core (business_model)     bool/str
  wants_to_prevent_cloud_competition bool
  open_source_commitment         bool
  jurisdiction_specific          bool  – need jurisdiction-specific advice
  concerned_about_legal_recognition bool
  need_strong_warranty_disclaimer bool
  license_in_use                 str   – for backward-chaining / compliance checks
  project_license                str   – the project's own license
  dependency_license             str   – a dependency's license
  all_dependency_licenses        list  – full dependency license list
  dependency_licenses_include_copyleft bool
"""

from typing import Any, Callable


# ─────────────────────────────────────────────────────────────────────────────
# Rule class (forward-chaining style from file 1, extended with metadata from file 2)
# ─────────────────────────────────────────────────────────────────────────────

class Rule:
    def __init__(
        self,
        id: str,
        name: str,
        condition: Callable[[dict], bool],
        action: Callable[[dict], None],
        explanation: str,
        chain_type: str = "forward",   # "forward" | "backward"
        confidence: str = "high",       # "high" | "medium" | "low"
    ):
        self.id = id
        self.name = name
        self.condition = condition
        self.action = action
        self.explanation = explanation
        self.chain_type = chain_type
        self.confidence = confidence

    def matches(self, facts: dict) -> bool:
        return self.condition(facts)

    def fire(self, working_memory: dict) -> None:
        self.action(working_memory)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: normalise saas/network_saas fact (both field names accepted)
# ─────────────────────────────────────────────────────────────────────────────

def _saas(f: dict) -> bool:
    return f.get("saas") is True or f.get("network_saas") is True

def _copyleft(f: dict) -> bool:
    return f.get("want_copyleft") is True or f.get("wants_derivatives_open") is True

def _patent(f: dict) -> bool:
    return f.get("need_patent_protection") is True or f.get("patent_protection_needed") is True

def _private_mods(f: dict) -> bool:
    return (
        f.get("closed_source") is True
        or f.get("wants_relicense") is True
        or f.get("wants_to_keep_modifications_private") is True
    )


# ─────────────────────────────────────────────────────────────────────────────
# A. PERMISSIVE LICENSE SELECTION
# ─────────────────────────────────────────────────────────────────────────────

RULES = [

    Rule(
        id="A01",
        name="Recommend MIT – Closed Source / No Source Disclosure",
        condition=lambda f: f.get("closed_source") is True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation=(
            "MIT does not require source disclosure, making it safe for closed-source "
            "projects. It is the most widely adopted permissive license."
        ),
    ),

    Rule(
        id="A02",
        name="Recommend MIT – SaaS (No Network Copyleft)",
        condition=lambda f: _saas(f),
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation=(
            "MIT has no network copyleft requirement, so using it in a SaaS product "
            "is perfectly fine without any source-sharing obligation."
        ),
    ),

    Rule(
        id="A03",
        name="Recommend MIT – Wants Relicense Freedom",
        condition=lambda f: f.get("wants_relicense") is True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation=(
            "MIT has no same-license requirement, so you can relicense or sublicense "
            "derivatives freely."
        ),
    ),

    Rule(
        id="A04",
        name="Recommend MIT – Simple Permissive",
        condition=lambda f: f.get("want_simple_permissive") is True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation=(
            "MIT is one of the simplest, most widely understood permissive licenses. "
            "ISC is functionally identical and common in the Node.js ecosystem."
        ),
    ),

    Rule(
        id="A05",
        name="Recommend MIT – Commercial Use",
        condition=lambda f: f.get("commercial_use") is True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation="MIT permits commercial use without restrictions.",
    ),

    Rule(
        id="A06",
        name="Warn MIT – No Explicit Patent Grant",
        condition=lambda f: _patent(f),
        action=lambda wm: wm["warnings"].append(
            "MIT: No explicit patent grant. Consider Apache-2.0 instead."
        ),
        explanation=(
            "MIT does not explicitly grant patent rights, leaving users potentially "
            "exposed to patent claims from contributors."
        ),
    ),

    Rule(
        id="A07",
        name="Warn MIT – No Trademark Protection",
        condition=lambda f: f.get("need_trademark_protection") is True,
        action=lambda wm: wm["warnings"].append(
            "MIT: No trademark protection clause. Consider Apache-2.0 or BSD-3-Clause."
        ),
        explanation=(
            "MIT does not include any trademark usage restrictions or non-endorsement "
            "clauses. Apache-2.0 and BSD-3-Clause both address this."
        ),
    ),

    # ── Apache-2.0 ────────────────────────────────────────────────────────────

    Rule(
        id="A08",
        name="Recommend Apache-2.0 – Closed Source",
        condition=lambda f: f.get("closed_source") is True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation=(
            "Apache-2.0 does not require source disclosure, making it safe for "
            "closed-source projects, while also providing an explicit patent grant."
        ),
    ),

    Rule(
        id="A09",
        name="Recommend Apache-2.0 – Patent Protection Needed",
        condition=lambda f: _patent(f),
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation=(
            "Apache-2.0 includes an explicit patent grant from all contributors and "
            "a patent termination clause: if a licensee sues for patent infringement "
            "they lose their Apache-2.0 rights. MIT/BSD do NOT provide this."
        ),
    ),

    Rule(
        id="A10",
        name="Recommend Apache-2.0 – Commercial Use",
        condition=lambda f: f.get("commercial_use") is True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation=(
            "Apache-2.0 permits commercial use and includes patent protections that are "
            "valuable in commercial settings."
        ),
    ),

    Rule(
        id="A11",
        name="Recommend Apache-2.0 – SaaS",
        condition=lambda f: _saas(f),
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation=(
            "Apache-2.0 has no network copyleft clause, making it fully suitable for "
            "SaaS deployments."
        ),
    ),

    Rule(
        id="A12",
        name="Recommend Apache-2.0 – Relicense Freedom",
        condition=lambda f: f.get("wants_relicense") is True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation=(
            "Apache-2.0 has no same-license requirement, allowing free relicensing of "
            "derivatives. Its patent grant makes it superior to MIT for this use case."
        ),
    ),

    Rule(
        id="A13",
        name="Recommend Apache-2.0 – Brand / Non-Endorsement Protection",
        condition=lambda f: f.get("protect_brand_name") is True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation=(
            "Apache-2.0 includes trademark usage restrictions and a non-endorsement "
            "provision, preventing others from using your project name to promote "
            "their products without permission. BSD-3-Clause does this too."
        ),
    ),

    Rule(
        id="A14",
        name="Warn Apache-2.0 – Document-Changes Requirement",
        condition=lambda f: f.get("wants_minimal_attribution") is True,
        action=lambda wm: wm["warnings"].append(
            "Apache-2.0: Requires documenting changes made to distributed files."
        ),
        explanation=(
            "Apache-2.0 Section 4(b) requires that you state significant changes made "
            "to files. This is a light obligation but heavier than MIT."
        ),
    ),

    # ── BSD-2-Clause ──────────────────────────────────────────────────────────

    Rule(
        id="A15",
        name="Recommend BSD-2-Clause – Closed Source",
        condition=lambda f: f.get("closed_source") is True,
        action=lambda wm: wm["recommended"].add("BSD-2-Clause"),
        explanation="BSD-2-Clause requires no source disclosure; safe for closed-source projects.",
    ),

    Rule(
        id="A16",
        name="Recommend BSD-2-Clause – Simple Permissive",
        condition=lambda f: f.get("want_simple_permissive") is True,
        action=lambda wm: (
            wm["recommended"].add("BSD-2-Clause"),
            wm["warnings"].append(
                "BSD-2-Clause vs MIT: Very similar. BSD-2-Clause omits the 'substantial "
                "portions' language. Either is fine for most cases."
            ),
        ),
        explanation=(
            "BSD-2-Clause is functionally equivalent to MIT. Choose based on ecosystem "
            "preference; MIT is more universally recognised."
        ),
    ),

    Rule(
        id="A17",
        name="Recommend BSD-2-Clause – Academic Project",
        condition=lambda f: f.get("academic_project") is True or f.get("project_type") == "academic",
        action=lambda wm: wm["recommended"].update(["BSD-2-Clause", "BSD-3-Clause", "MIT", "Apache-2.0"]),
        explanation=(
            "BSD-2-Clause and BSD-3-Clause are common in academic and BSD Unix-derived "
            "projects. Apache-2.0 is preferred when the research may have patent implications."
        ),
    ),

    Rule(
        id="A18",
        name="Recommend BSD-2-Clause – Commercial Use",
        condition=lambda f: f.get("commercial_use") is True,
        action=lambda wm: wm["recommended"].add("BSD-2-Clause"),
        explanation="BSD-2-Clause permits commercial use without restrictions.",
    ),

    Rule(
        id="A19",
        name="Warn BSD-2-Clause – No Patent Grant",
        condition=lambda f: _patent(f),
        action=lambda wm: wm["warnings"].append(
            "BSD-2-Clause: No explicit patent grant. Consider Apache-2.0 instead."
        ),
        explanation="BSD-2-Clause provides no patent protection.",
    ),

    Rule(
        id="A20",
        name="Recommend BSD-3-Clause – Non-Endorsement Protection",
        condition=lambda f: f.get("protect_brand_name") is True,
        action=lambda wm: wm["recommended"].add("BSD-3-Clause"),
        explanation=(
            "BSD-3-Clause's third clause explicitly prohibits using the project name "
            "to endorse or promote derivative products without written permission. "
            "MIT does NOT include this clause."
        ),
    ),

    # ── Unlicense / Public Domain ─────────────────────────────────────────────

    Rule(
        id="A21",
        name="Recommend Unlicense – Public Domain Dedication",
        condition=lambda f: f.get("want_public_domain") is True or f.get("want_maximum_freedom") is True,
        action=lambda wm: (
            wm["recommended"].add("Unlicense"),
            wm["recommended"].add("CC0-1.0"),
        ),
        explanation=(
            "Unlicense dedicates software to the public domain with no restrictions. "
            "CC0-1.0 is more legally robust internationally — it includes a fallback "
            "permissive licence for jurisdictions that do not recognise public domain "
            "dedication (e.g. France's moral rights regime)."
        ),
    ),

    Rule(
        id="A22",
        name="Recommend Unlicense – No Attribution Required",
        condition=lambda f: f.get("no_attribution_needed") is True or f.get("attribution_required") is False,
        action=lambda wm: wm["recommended"].update(["Unlicense", "CC0-1.0"]),
        explanation=(
            "Unlicense and CC0-1.0 require no attribution or license inclusion. "
            "Neither provides patent protection."
        ),
    ),

    Rule(
        id="A23",
        name="Warn Unlicense – Jurisdiction Recognition",
        condition=lambda f: f.get("concerned_about_legal_recognition") is True,
        action=lambda wm: wm["warnings"].append(
            "Unlicense: Public domain dedication is not recognised in all jurisdictions. "
            "Prefer CC0-1.0, which includes a fallback permissive licence."
        ),
        explanation=(
            "Some countries (e.g. Germany, France) do not allow waiving all copyright. "
            "CC0-1.0 handles this with a permissive fallback clause."
        ),
    ),

    Rule(
        id="A24",
        name="Warn Unlicense – No Patent Grant",
        condition=lambda f: _patent(f),
        action=lambda wm: wm["warnings"].append(
            "Unlicense/CC0: No patent grant whatsoever. Apache-2.0 is the safer choice."
        ),
        explanation="Neither Unlicense nor CC0-1.0 provides any patent protection.",
    ),

    Rule(
        id="A25",
        name="Warn Unlicense – Warranty Disclaimer Enforceability",
        condition=lambda f: f.get("need_strong_warranty_disclaimer") is True,
        action=lambda wm: wm["warnings"].append(
            "Unlicense: Warranty disclaimer exists but may be less enforceable in some "
            "jurisdictions due to its public-domain nature."
        ),
        explanation=(
            "Public domain dedication may affect the enforceability of liability/warranty "
            "limitations in certain legal systems."
        ),
    ),


    # ─────────────────────────────────────────────────────────────────────────
    # B. COPYLEFT LICENSE SELECTION
    # ─────────────────────────────────────────────────────────────────────────

    Rule(
        id="B01",
        name="Recommend GPL-3.0 – Strong Copyleft (Distributed Software)",
        condition=lambda f: _copyleft(f) and not f.get("closed_source") and not _saas(f),
        action=lambda wm: wm["recommended"].add("GPL-3.0"),
        explanation=(
            "GPL-3.0 is the modern strong copyleft licence. All distributed derivatives "
            "must remain open source under GPL-3.0. It also includes anti-tivoization "
            "and an explicit patent grant. GPL-2.0 is older and lacks these protections."
        ),
    ),

    Rule(
        id="B02",
        name="Recommend GPL-3.0 – Commercial + Copyleft",
        condition=lambda f: f.get("commercial_use") is True and _copyleft(f) and not f.get("closed_source"),
        action=lambda wm: wm["recommended"].add("GPL-3.0"),
        explanation=(
            "GPL-3.0 permits commercial use while ensuring all distributed derivatives "
            "remain open source."
        ),
    ),

    Rule(
        id="B03",
        name="Eliminate GPL-3.0 – Closed Source",
        condition=lambda f: f.get("closed_source") is True,
        action=lambda wm: (
            wm["eliminated"].add("GPL-3.0"),
            wm["eliminated"].add("GPL-2.0"),
        ),
        explanation=(
            "GPL-3.0 and GPL-2.0 require source disclosure when distributing. "
            "Completely incompatible with closed-source distribution."
        ),
    ),

    Rule(
        id="B04",
        name="Eliminate GPL-3.0 – Wants Relicense Freedom",
        condition=lambda f: f.get("wants_relicense") is True,
        action=lambda wm: wm["eliminated"].add("GPL-3.0"),
        explanation=(
            "GPL-3.0 requires the same licence for all distributed derivatives. "
            "You cannot relicense freely."
        ),
    ),

    Rule(
        id="B05",
        name="Warn GPL-3.0 – SaaS Loophole",
        condition=lambda f: _saas(f) and _copyleft(f),
        action=lambda wm: wm["warnings"].append(
            "GPL-3.0: Network use (SaaS) does NOT trigger copyleft. "
            "Consider AGPL-3.0 to close the SaaS loophole."
        ),
        explanation=(
            "GPL-3.0 copyleft only triggers on distribution, not on running the software "
            "as a service. Server-side modifications can legally remain private under GPL-3.0."
        ),
    ),

    # ── AGPL-3.0 ──────────────────────────────────────────────────────────────

    Rule(
        id="B06",
        name="Recommend AGPL-3.0 – SaaS + Copyleft",
        condition=lambda f: _saas(f) and _copyleft(f) and not f.get("closed_source"),
        action=lambda wm: wm["recommended"].add("AGPL-3.0"),
        explanation=(
            "AGPL-3.0 closes the SaaS loophole: network use triggers the same copyleft "
            "as distribution. Any user who interacts with the software over a network "
            "can demand the complete source code (AGPL Section 13)."
        ),
    ),

    Rule(
        id="B07",
        name="Recommend AGPL-3.0 – Strongest Copyleft",
        condition=lambda f: f.get("want_strongest_copyleft") is True and not f.get("closed_source"),
        action=lambda wm: wm["recommended"].add("AGPL-3.0"),
        explanation=(
            "AGPL-3.0 is the strongest OSI-approved copyleft licence, ensuring openness "
            "for both distribution and network deployments."
        ),
    ),

    Rule(
        id="B08",
        name="Recommend AGPL-3.0 – Open-Core Business Model",
        condition=lambda f: (
            f.get("business_model") == "open_core" or f.get("open_core") is True
        ) and f.get("wants_to_prevent_cloud_competition") is True and f.get("open_source_commitment") is not False,
        action=lambda wm: wm["recommended"].add("AGPL-3.0"),
        explanation=(
            "AGPL-3.0 is a common choice for open-core business models: it allows free "
            "use but makes SaaS competitors disclose their modifications, protecting your "
            "commercial advantage. This is why Google prohibits AGPL internally."
        ),
    ),

    Rule(
        id="B09",
        name="Eliminate AGPL-3.0 – Closed Source",
        condition=lambda f: f.get("closed_source") is True,
        action=lambda wm: wm["eliminated"].add("AGPL-3.0"),
        explanation=(
            "AGPL-3.0 requires source disclosure even for network use. "
            "Completely incompatible with keeping code private."
        ),
    ),

    Rule(
        id="B10",
        name="Eliminate AGPL-3.0 – Wants Relicense Freedom",
        condition=lambda f: f.get("wants_relicense") is True,
        action=lambda wm: wm["eliminated"].add("AGPL-3.0"),
        explanation="AGPL-3.0 requires the same licence for all derivatives. Cannot relicense freely.",
    ),

    Rule(
        id="B11",
        name="Warn AGPL-3.0 – SaaS Without Copyleft Intent",
        condition=lambda f: _saas(f) and not _copyleft(f),
        action=lambda wm: wm["warnings"].append(
            "AGPL-3.0: Any user accessing your SaaS can demand the complete source code. "
            "Only use AGPL if you intend copyleft obligations."
        ),
        explanation=(
            "AGPL-3.0 Section 13 triggers on network interaction. Running an AGPL-licensed "
            "service without wanting copyleft exposes you to mandatory source disclosure."
        ),
    ),

    Rule(
        id="B12",
        name="Warn AGPL-3.0 – Strongest Copyleft Implication",
        condition=lambda f: _copyleft(f),
        action=lambda wm: wm["warnings"].append(
            "AGPL-3.0: Strongest copyleft available — affects both distribution AND "
            "network use. Ensure you understand the implications before choosing."
        ),
        explanation=(
            "AGPL-3.0 is the most restrictive OSI-approved open source licence. "
            "Many enterprises (including Google) prohibit its use internally."
        ),
    ),

    Rule(
        id="B13",
        name="Exclude Copyleft – Wants Private Modifications",
        condition=lambda f: _private_mods(f),
        action=lambda wm: (
            wm["eliminated"].update(["GPL-2.0", "GPL-3.0", "AGPL-3.0"]),
            wm["recommended"].update(["MIT", "Apache-2.0", "BSD-2-Clause"]),
        ),
        explanation=(
            "GPL and AGPL require distributing source of derivatives. "
            "Permissive licences (MIT, Apache-2.0, BSD-2-Clause) allow proprietary "
            "derivatives and private modifications."
        ),
    ),


    # ─────────────────────────────────────────────────────────────────────────
    # C. WEAK COPYLEFT / MIDDLE-GROUND
    # ─────────────────────────────────────────────────────────────────────────

    Rule(
        id="C01",
        name="Recommend LGPL-2.1 – Library with Weak Copyleft",
        condition=lambda f: f.get("project_type") == "library" and f.get("want_weak_copyleft") is True,
        action=lambda wm: wm["recommended"].update(["LGPL-2.1", "LGPL-3.0"]),
        explanation=(
            "LGPL is weak copyleft at the library boundary: the library itself must stay "
            "open, but applications that merely link to it may use any licence. "
            "LGPL-3.0 is the modern version and includes GPL-3.0 patent protections."
        ),
    ),

    Rule(
        id="C02",
        name="Recommend LGPL – Library + Allow Proprietary Linking",
        condition=lambda f: (
            f.get("project_type") == "library"
            and f.get("allow_proprietary_applications") is True
            and f.get("wants_library_modifications_open") is True
        ),
        action=lambda wm: wm["recommended"].update(["LGPL-2.1", "LGPL-3.0", "MPL-2.0"]),
        explanation=(
            "LGPL allows proprietary software to link to your library. Only modifications "
            "to the library itself trigger copyleft. MPL-2.0 achieves similar goals at "
            "file level and is simpler to understand."
        ),
    ),

    Rule(
        id="C03",
        name="Recommend LGPL – Library + Commercial Use",
        condition=lambda f: (
            f.get("project_type") == "library"
            and f.get("commercial_use") is True
            and not _copyleft(f)
        ),
        action=lambda wm: wm["recommended"].add("LGPL-2.1"),
        explanation=(
            "LGPL-2.1 allows commercial applications to link to your library freely. "
            "Ideal for widely-adopted libraries that want broad adoption without giving "
            "up all copyleft protection."
        ),
    ),

    Rule(
        id="C04",
        name="Recommend LGPL – Dynamic Linking + Weak Copyleft",
        condition=lambda f: f.get("linking_type") == "dynamic" and f.get("want_weak_copyleft") is True,
        action=lambda wm: wm["recommended"].add("LGPL-2.1"),
        explanation=(
            "LGPL-2.1 is specifically designed for dynamic linking scenarios where the "
            "library remains separate from the main application."
        ),
    ),

    Rule(
        id="C05",
        name="Eliminate LGPL – Closed-Source Library Modification",
        condition=lambda f: (
            f.get("project_type") == "library"
            and f.get("closed_source") is True
            and f.get("modify_library") is True
        ),
        action=lambda wm: wm["eliminated"].update(["LGPL-2.1", "LGPL-3.0"]),
        explanation=(
            "LGPL requires source disclosure for modified versions of the library itself. "
            "Cannot keep library modifications closed."
        ),
    ),

    Rule(
        id="C06",
        name="Warn LGPL – Static Linking Risk",
        condition=lambda f: f.get("linking_type") == "static",
        action=lambda wm: wm["warnings"].append(
            "LGPL-2.1: Static linking into a proprietary binary may require the combined "
            "work to be LGPL-licensed. Dynamic linking is the safer interpretation. "
            "FSF recommends providing a relinkable object file when static-linking. "
            "Consult a lawyer for production use."
        ),
        explanation=(
            "Static linking is a legal grey area under LGPL-2.1. The FSF recommends "
            "dynamic linking to stay clearly within the licence's permissions."
        ),
        chain_type="backward",
        confidence="medium",
    ),

    Rule(
        id="C07",
        name="Warn LGPL – Not for Standalone Applications",
        condition=lambda f: f.get("project_type") == "software" and _copyleft(f),
        action=lambda wm: wm["warnings"].append(
            "LGPL-2.1/3.0: Designed for libraries, not standalone applications. "
            "Consider GPL-3.0 for applications."
        ),
        explanation=(
            "LGPL's copyleft boundary is defined by 'the library'. For standalone "
            "applications, GPL-3.0 is the correct choice."
        ),
    ),

    # ── MPL-2.0 ───────────────────────────────────────────────────────────────

    Rule(
        id="C08",
        name="Recommend MPL-2.0 – File-Level Copyleft",
        condition=lambda f: f.get("want_file_copyleft") is True and not f.get("closed_source"),
        action=lambda wm: wm["recommended"].add("MPL-2.0"),
        explanation=(
            "MPL-2.0 uses file-level copyleft: only modified MPL-licensed files must "
            "remain open. The rest of the project can be proprietary."
        ),
    ),

    Rule(
        id="C09",
        name="Recommend MPL-2.0 – Mixed Open/Proprietary Codebase",
        condition=lambda f: (
            f.get("mixed_open_proprietary") is True
            or f.get("project_type") == "mixed"
            or f.get("has_proprietary_components") is True
        ),
        action=lambda wm: wm["recommended"].update(["MPL-2.0", "EPL-2.0", "LGPL-3.0"]),
        explanation=(
            "MPL-2.0 and EPL-2.0 use file-level copyleft — only the open-licensed files "
            "need to stay open, while other files in the same project can be proprietary. "
            "This is called 'exhibit A' or 'module-based' copyleft."
        ),
    ),

    Rule(
        id="C10",
        name="Recommend MPL-2.0 – Commercial + Weak Copyleft",
        condition=lambda f: f.get("commercial_use") is True and f.get("want_weak_copyleft") is True,
        action=lambda wm: wm["recommended"].add("MPL-2.0"),
        explanation=(
            "MPL-2.0 permits commercial use while ensuring only modified files remain "
            "open source — a good middle ground."
        ),
    ),

    Rule(
        id="C11",
        name="Eliminate MPL-2.0 – Closed Source + File Modifications",
        condition=lambda f: f.get("closed_source") is True and f.get("modify_files") is True,
        action=lambda wm: wm["eliminated"].add("MPL-2.0"),
        explanation=(
            "MPL-2.0 requires disclosing source for modified files. "
            "Cannot keep modified MPL files closed."
        ),
    ),

    Rule(
        id="C12",
        name="Recommend EPL-2.0 – Java / Eclipse Ecosystem",
        condition=lambda f: f.get("ecosystem") == "java" and f.get("project_type") == "library",
        action=lambda wm: wm["recommended"].update(["EPL-2.0", "Apache-2.0", "LGPL-3.0"]),
        explanation=(
            "The Java/Eclipse ecosystem commonly uses EPL-2.0 or Apache-2.0. "
            "EPL-2.0 can be combined with GPL-2.0+ via its secondary licence option. "
            "Apache-2.0 is the most permissive and widely accepted choice."
        ),
        confidence="medium",
    ),


    # ─────────────────────────────────────────────────────────────────────────
    # D. CONTENT / NON-SOFTWARE LICENSES
    # ─────────────────────────────────────────────────────────────────────────

    Rule(
        id="D01",
        name="Recommend CC-BY-NC-4.0 – Non-Commercial Content",
        condition=lambda f: f.get("project_type") == "content" and not f.get("commercial_use"),
        action=lambda wm: wm["recommended"].add("CC-BY-NC-4.0"),
        explanation=(
            "CC-BY-NC-4.0 is designed for creative content shared for non-commercial "
            "purposes. Attribution is required; commercial use is prohibited."
        ),
    ),

    Rule(
        id="D02",
        name="Recommend CC-BY-4.0 / CC0 – Documentation",
        condition=lambda f: not f.get("is_software") and f.get("content_type") == "documentation",
        action=lambda wm: wm["recommended"].update(["CC-BY-4.0", "CC0-1.0"]),
        explanation=(
            "For documentation, tutorials, and written content, Creative Commons is the "
            "standard. CC-BY-4.0 requires attribution. CC0-1.0 waives all rights. "
            "Do NOT use software licences (MIT, GPL) for non-code content."
        ),
    ),

    Rule(
        id="D03",
        name="Recommend CC – Dataset / Training Data",
        condition=lambda f: not f.get("is_software") and f.get("content_type") == "dataset",
        action=lambda wm: wm["recommended"].update(["CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0"]),
        explanation=(
            "Datasets are not software. CC0-1.0 is preferred for maximum reuse "
            "(especially in scientific/AI research). CC-BY-4.0 requires attribution. "
            "CC-BY-SA-4.0 requires derivatives to use the same licence (ShareAlike). "
            "Note: CC-BY-NC on training data restricts AI/ML commercial use."
        ),
    ),

    Rule(
        id="D04",
        name="Recommend CC – Educational Content (Non-Commercial)",
        condition=lambda f: (
            not f.get("is_software")
            and f.get("content_type") == "educational"
            and not f.get("commercial_use")
        ),
        action=lambda wm: wm["recommended"].update(["CC-BY-NC-SA-4.0", "CC-BY-NC-4.0"]),
        explanation=(
            "Educational materials intended to remain free and non-commercial typically "
            "use CC-BY-NC-SA-4.0 (ShareAlike ensures derivatives stay educational) "
            "or CC-BY-NC-4.0 (allows any non-commercial adaptation)."
        ),
    ),

    Rule(
        id="D05",
        name="Recommend Apache-2.0 / CC-BY-4.0 – AI Model Weights",
        condition=lambda f: f.get("content_type") == "ai_model_weights",
        action=lambda wm: wm["recommended"].update(["Apache-2.0", "CC-BY-4.0", "CC0-1.0"]),
        explanation=(
            "AI model weights are a legal grey area — they may be treated as software, "
            "data, or a derivative of training data. Apache-2.0 is common (e.g. Llama "
            "variants). CC-BY-4.0 is used for some models. Custom model licences "
            "(e.g. Llama Community Licence) add usage restrictions. Traditional software "
            "licences may not map cleanly to model weights."
        ),
        confidence="medium",
    ),

    Rule(
        id="D06",
        name="Recommend OFL-1.1 – Fonts",
        condition=lambda f: f.get("content_type") == "font",
        action=lambda wm: wm["recommended"].update(["OFL-1.1", "Apache-2.0"]),
        explanation=(
            "Fonts use the SIL Open Font Licence 1.1 (OFL-1.1) as the standard. "
            "OFL allows free use, modification, and embedding, with one restriction: "
            "fonts may not be sold standalone. Apache-2.0 is also used (e.g. Noto)."
        ),
    ),

    Rule(
        id="D07",
        name="Eliminate CC-BY-NC-4.0 – Commercial Use",
        condition=lambda f: f.get("commercial_use") is True,
        action=lambda wm: wm["eliminated"].add("CC-BY-NC-4.0"),
        explanation="CC-BY-NC-4.0 explicitly prohibits commercial use.",
    ),

    Rule(
        id="D08",
        name="Eliminate CC Licences – Software Project",
        condition=lambda f: f.get("project_type") == "software" or f.get("is_software") is True,
        action=lambda wm: (
            wm["eliminated"].update(["CC-BY-NC-4.0", "CC-BY-4.0", "CC-BY-SA-4.0"]),
            wm["warnings"].append(
                "CC licences: Designed for creative content, not software. "
                "Creative Commons explicitly states their licences are NOT for code."
            ),
        ),
        explanation=(
            "CC licences do not address software-specific concerns such as binary "
            "distribution, linking, or source disclosure. Use OSI-approved licences "
            "for software. Exception: CC0-1.0 is sometimes used but OSI does not endorse it."
        ),
    ),


    # ─────────────────────────────────────────────────────────────────────────
    # E. SOURCE-AVAILABLE / PROPRIETARY
    # ─────────────────────────────────────────────────────────────────────────

    Rule(
        id="E01",
        name="Recommend SSPL / BSL / Elastic – Prevent Cloud Reselling (Non-OSI)",
        condition=lambda f: (
            f.get("wants_to_prevent_cloud_competition") is True
            and f.get("open_source_commitment") is False
            and f.get("is_software") is not False
        ),
        action=lambda wm: (
            wm["recommended"].update(["SSPL-1.0", "Elastic-2.0", "BSL-1.0"]),
            wm["warnings"].append(
                "SSPL-1.0 / Elastic-2.0 / BSL-1.0 are NOT OSI-approved open source. "
                "SSPL forces disclosure of the entire service stack. "
                "Elastic-2.0 prohibits managed-service offerings. "
                "BSL-1.0 converts to open source after a Change Date (e.g. 4 years)."
            ),
        ),
        explanation=(
            "If your primary concern is preventing cloud providers (AWS, Azure, GCP) "
            "from offering your software as a managed service, these source-available "
            "licences restrict that use. None are OSI-approved open source."
        ),
    ),

    Rule(
        id="E02",
        name="Warn – No Licence = All Rights Reserved",
        condition=lambda f: f.get("license_in_use") is None and f.get("is_software") is True,
        action=lambda wm: wm["warnings"].append(
            "No licence: A repository with no licence file is NOT open source. "
            "Default copyright applies — others cannot use, copy, modify, or distribute "
            "the work. Add a LICENSE file to make your intent clear."
        ),
        explanation=(
            "GitHub's terms allow viewing, but NOT forking for use or modification. "
            "Absence of a licence is effectively 'all rights reserved'."
        ),
        chain_type="backward",
    ),


    # ─────────────────────────────────────────────────────────────────────────
    # F. COMPATIBILITY & CONFLICT DETECTION
    # ─────────────────────────────────────────────────────────────────────────

    Rule(
        id="F01",
        name="Flag – GPL-2.0 Incompatible with Apache-2.0",
        condition=lambda f: (
            f.get("project_license") == "GPL-2.0"
            and f.get("dependency_license") == "Apache-2.0"
            and f.get("distribution") is True
        ),
        action=lambda wm: wm["flags"].append(
            "GPL2_APACHE2_INCOMPATIBLE: GPL-2.0 and Apache-2.0 are incompatible at "
            "distribution time. Apache-2.0's patent termination clause is an extra "
            "restriction GPL-2.0 does not permit (FSF confirmed). Solutions: "
            "(1) Relicence project as GPL-3.0, (2) use MIT/BSD instead of Apache-2.0, "
            "(3) obtain a commercial exception from the copyright holder."
        ),
        explanation="GPL-2.0 + Apache-2.0 = distribution conflict. See FSF guidance.",
        chain_type="backward",
    ),

    Rule(
        id="F02",
        name="Allow – GPL-3.0 Compatible with Apache-2.0",
        condition=lambda f: (
            f.get("project_license") == "GPL-3.0"
            and f.get("dependency_license") == "Apache-2.0"
            and f.get("distribution") is True
        ),
        action=lambda wm: wm["warnings"].append(
            "GPL-3.0 + Apache-2.0: Compatible. Combined work distributed under GPL-3.0. "
            "Keep Apache-2.0 notices AND provide GPL-3.0 source access."
        ),
        explanation="FSF explicitly confirms GPL-3.0 and Apache-2.0 compatibility.",
        chain_type="backward",
    ),

    Rule(
        id="F03",
        name="Allow – MIT/BSD Compatible with GPL",
        condition=lambda f: (
            f.get("project_license") in ["GPL-2.0", "GPL-3.0"]
            and f.get("dependency_license") in ["MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC"]
            and f.get("distribution") is True
        ),
        action=lambda wm: wm["warnings"].append(
            "MIT/BSD + GPL: Compatible. Combined work distributed under GPL. "
            "Retain the original MIT/BSD copyright notices in your distribution."
        ),
        explanation="MIT, BSD-2, BSD-3, and ISC are compatible with both GPL-2.0 and GPL-3.0.",
        chain_type="backward",
    ),

    Rule(
        id="F04",
        name="Flag – GPL Code in Proprietary Project",
        condition=lambda f: (
            f.get("project_license") == "Proprietary"
            and f.get("dependency_license") in ["GPL-2.0", "GPL-3.0", "AGPL-3.0"]
            and f.get("distribution") is True
        ),
        action=lambda wm: wm["flags"].append(
            "GPL_IN_PROPRIETARY_VIOLATION: Cannot distribute proprietary software that "
            "includes GPL-licensed code. GPL requires the entire combined work to be GPL. "
            "Options: (1) Remove the GPL dependency, (2) obtain a commercial licence from "
            "the copyright holder, (3) isolate the GPL component in a separate process "
            "communicating via IPC/API (contested — consult a lawyer)."
        ),
        explanation="GPL copyleft propagates to the entire distributed work.",
        chain_type="backward",
        confidence="high",
    ),

    Rule(
        id="F05",
        name="Allow – LGPL Dynamic Linking in Proprietary App",
        condition=lambda f: (
            f.get("project_license") == "Proprietary"
            and f.get("dependency_license") in ["LGPL-2.1", "LGPL-3.0"]
            and f.get("linking_type") == "dynamic"
            and f.get("distribution") is True
        ),
        action=lambda wm: wm["warnings"].append(
            "LGPL dynamic linking in proprietary app: Generally permitted. "
            "You must (1) preserve LGPL library copyright notices and (2) allow users "
            "to relink with a modified library version (distribute as shared library)."
        ),
        explanation=(
            "Dynamic linking against LGPL in a proprietary app is the intended use case. "
            "This is how most commercial software uses Qt LGPL, for example."
        ),
        chain_type="backward",
    ),

    Rule(
        id="F06",
        name="Flag – AGPL Dependency in SaaS (Source Required)",
        condition=lambda f: (
            f.get("dependency_license") == "AGPL-3.0"
            and _saas(f)
            and not f.get("distribution")
        ),
        action=lambda wm: wm["flags"].append(
            "AGPL_SAAS_SOURCE_REQUIRED: Even without distribution, AGPL-3.0 Section 13 "
            "requires offering complete source code to users who interact via a network. "
            "Provide a download link or equivalent access to all AGPL-covered source."
        ),
        explanation="AGPL-3.0 closes the SaaS loophole — network interaction triggers source disclosure.",
        chain_type="backward",
    ),

    Rule(
        id="F07",
        name="Allow – MIT in Commercial Proprietary Product",
        condition=lambda f: (
            f.get("dependency_license") == "MIT"
            and f.get("project_license") == "Proprietary"
            and f.get("distribution") is True
        ),
        action=lambda wm: wm["warnings"].append(
            "MIT in proprietary product: Allowed. You MUST include the original MIT "
            "copyright notice and licence text in your distribution "
            "(e.g. in a NOTICES or THIRD-PARTY-LICENSES file)."
        ),
        explanation="MIT's only requirement for binary distribution is retaining the copyright notice.",
        chain_type="backward",
    ),

    Rule(
        id="F08",
        name="Allow – GPL Internal Use (No Distribution, No Network)",
        condition=lambda f: (
            f.get("dependency_license") in ["GPL-2.0", "GPL-3.0"]
            and not f.get("distribution")
            and not _saas(f)
        ),
        action=lambda wm: wm["warnings"].append(
            "GPL internal use only: Copyleft does NOT trigger. GPL requires source "
            "sharing only upon distribution. Private internal use is permitted."
        ),
        explanation=(
            "Companies can legally use GPL code in internal proprietary pipelines "
            "as long as they do not distribute the combined work."
        ),
        chain_type="backward",
    ),

    Rule(
        id="F09",
        name="Flag – CDDL Incompatible with GPL",
        condition=lambda f: (
            f.get("dependency_license") == "CDDL-1.0"
            and f.get("project_license") in ["GPL-2.0", "GPL-3.0"]
            and f.get("distribution") is True
        ),
        action=lambda wm: wm["flags"].append(
            "CDDL_GPL_INCOMPATIBLE: CDDL-1.0 and GPL are incompatible — FSF explicitly "
            "states this (cf. ZFS on Linux). Keep CDDL and GPL components as separate "
            "processes communicating via API."
        ),
        explanation="This is why Linux (GPL-2.0) cannot directly include ZFS (CDDL) code.",
        chain_type="backward",
    ),

    Rule(
        id="F10",
        name="Flag – Mixed Dependency Tree Contains Copyleft",
        condition=lambda f: f.get("dependency_licenses_include_copyleft") is True,
        action=lambda wm: wm["flags"].append(
            "COPYLEFT_IN_DEPENDENCY_TREE: At least one copyleft licence found in "
            "dependencies. Audit each: Is it dynamically linked? A separate process? "
            "Internal only? Each answer determines whether copyleft propagates."
        ),
        explanation=(
            "The 'most restrictive compatible licence' principle: if distributing, "
            "copyleft terms propagate upward through the dependency tree."
        ),
        chain_type="backward",
        confidence="medium",
    ),

    Rule(
        id="F11",
        name="Allow – Permissive-Only Dependency Tree with Proprietary Project",
        condition=lambda f: (
            isinstance(f.get("all_dependency_licenses"), list)
            and all(
                lic in [
                    "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC",
                    "Zlib", "PostgreSQL", "Artistic-2.0", "Unlicense", "CC0-1.0",
                ]
                for lic in f.get("all_dependency_licenses", [])
            )
            and f.get("project_license") == "Proprietary"
        ),
        action=lambda wm: wm["warnings"].append(
            "Permissive-only dependencies: All clear for proprietary use. "
            "Collect all required attribution notices and generate a "
            "THIRD-PARTY-NOTICES or LICENSES file."
        ),
        explanation="Permissive licences are compatible with proprietary projects.",
        chain_type="backward",
    ),


    # ─────────────────────────────────────────────────────────────────────────
    # G. SAAS / NETWORK DEPLOYMENT
    # ─────────────────────────────────────────────────────────────────────────

    Rule(
        id="G01",
        name="Allow – GPL SaaS Without Distribution (ASP Loophole)",
        condition=lambda f: (
            not f.get("distribution")
            and _saas(f)
            and f.get("dependency_license") in ["GPL-2.0", "GPL-3.0"]
        ),
        action=lambda wm: wm["warnings"].append(
            "GPL SaaS loophole: Running GPL software server-side without distributing it "
            "does NOT trigger copyleft. However, if any code is AGPL-3.0, the loophole "
            "is closed and you MUST share source with network users."
        ),
        explanation=(
            "GPL applies to distribution, not usage. This is the 'ASP/SaaS loophole' "
            "that AGPL-3.0 was created to close."
        ),
        chain_type="forward",
    ),

    Rule(
        id="G02",
        name="Recommend MIT / Apache-2.0 – SaaS + Keep Modifications Private",
        condition=lambda f: _saas(f) and _private_mods(f) and not f.get("distribution"),
        action=lambda wm: wm["recommended"].update(["MIT", "Apache-2.0"]),
        explanation=(
            "For internal SaaS or tools where you want to keep modifications private, "
            "permissive licences are safest. MIT/Apache-2.0 impose no source-sharing "
            "obligations regardless of network exposure."
        ),
        confidence="medium",
    ),


    # ─────────────────────────────────────────────────────────────────────────
    # H. DEPENDENCY ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    # (Merged into section F above; no unique rules remain.)


    # ─────────────────────────────────────────────────────────────────────────
    # I. SPECIAL SCENARIOS
    # ─────────────────────────────────────────────────────────────────────────

    Rule(
        id="I01",
        name="Recommend – Government / Public Sector Project",
        condition=lambda f: f.get("project_type") == "government" and f.get("distribution") is True,
        action=lambda wm: wm["recommended"].update(["Apache-2.0", "EUPL-1.2", "MIT", "CC0-1.0"]),
        explanation=(
            "Government software has special considerations. "
            "EUPL-1.2 is legally tailored for EU public sector use and covers 22 EU languages. "
            "Apache-2.0 and MIT are widely recognised and legally simple. "
            "US government works may be public domain under 17 U.S.C. § 105 (use CC0 internationally). "
            "Avoid GPL for government software that cannot guarantee source-sharing compliance."
        ),
        confidence="medium",
    ),

    Rule(
        id="I02",
        name="Recommend – Hardware Description / FPGA / Chip Design",
        condition=lambda f: f.get("project_type") == "hardware_description",
        action=lambda wm: wm["recommended"].update(["Apache-2.0", "CERN-OHL-S-2.0", "CERN-OHL-W-2.0"]),
        explanation=(
            "Hardware description languages (VHDL, Verilog, SystemVerilog) occupy a gap "
            "between software and hardware licences. Apache-2.0 is commonly used for HDL. "
            "CERN Open Hardware Licence (OHL) was designed for hardware: "
            "OHL-S (Strongly Reciprocal) ≈ GPL; OHL-W (Weakly Reciprocal) ≈ LGPL."
        ),
        confidence="medium",
    ),

    Rule(
        id="I03",
        name="Flag – Jurisdiction-Specific Legal Advice Required",
        condition=lambda f: f.get("jurisdiction_specific") is True,
        action=lambda wm: wm["flags"].append(
            "CONSULT_LAWYER: Licence interpretation varies by jurisdiction. "
            "Software patents not enforceable in the EU (generally). "
            "GDPR may interact with data-sharing conditions. "
            "French 'droit moral' cannot be waived, affecting CC0 effectiveness. "
            "Always consult a qualified lawyer for jurisdiction-specific decisions."
        ),
        explanation=(
            "This engine provides general guidance. Jurisdiction-specific or "
            "production-critical decisions require qualified legal advice."
        ),
        chain_type="backward",
        confidence="low",
    ),

]


# ─────────────────────────────────────────────────────────────────────────────
# COMPATIBILITY MATRIX
# True  = compatible (can be combined in a distributed work)
# False = incompatible
# None  = situational / requires analysis
# Source: FSF, SPDX, OSI compatibility notes
# ─────────────────────────────────────────────────────────────────────────────

COMPATIBILITY_MATRIX: dict[tuple[str, str], bool | None] = {
    ("MIT",          "GPL-2.0"):   True,
    ("MIT",          "GPL-3.0"):   True,
    ("MIT",          "AGPL-3.0"):  True,
    ("MIT",          "LGPL-2.1"):  True,
    ("MIT",          "LGPL-3.0"):  True,
    ("MIT",          "Apache-2.0"):True,
    ("MIT",          "MPL-2.0"):   True,
    ("BSD-2-Clause", "GPL-2.0"):   True,
    ("BSD-2-Clause", "GPL-3.0"):   True,
    ("BSD-3-Clause", "GPL-2.0"):   True,
    ("BSD-3-Clause", "GPL-3.0"):   True,
    ("Apache-2.0",   "GPL-2.0"):   False,   # Incompatible — FSF confirmed
    ("Apache-2.0",   "GPL-3.0"):   True,
    ("Apache-2.0",   "LGPL-3.0"):  True,
    ("Apache-2.0",   "MPL-2.0"):   True,
    ("GPL-2.0",      "GPL-3.0"):   False,   # Only compatible if 'or later' present
    ("GPL-2.0",      "AGPL-3.0"):  False,
    ("GPL-3.0",      "AGPL-3.0"):  True,    # AGPL-3.0 ⊃ GPL-3.0
    ("GPL-3.0",      "LGPL-3.0"):  True,
    ("GPL-3.0",      "MPL-2.0"):   True,
    ("LGPL-2.1",     "GPL-2.0"):   True,
    ("LGPL-2.1",     "GPL-3.0"):   None,    # Needs upgrade to LGPL-3.0
    ("LGPL-3.0",     "GPL-3.0"):   True,
    ("MPL-2.0",      "GPL-2.0"):   True,    # MPL Section 3.3
    ("MPL-2.0",      "GPL-3.0"):   True,
    ("CDDL-1.0",     "GPL-2.0"):   False,   # FSF explicitly incompatible
    ("CDDL-1.0",     "GPL-3.0"):   False,
    ("EPL-2.0",      "GPL-2.0"):   None,    # Complex — EPL-2.0 secondary licence needed
    ("EPL-2.0",      "GPL-3.0"):   True,    # With secondary GPL-3.0 option
    ("EUPL-1.2",     "GPL-2.0"):   True,
    ("EUPL-1.2",     "GPL-3.0"):   True,
    ("EUPL-1.2",     "AGPL-3.0"):  True,
    ("SSPL-1.0",     "GPL-3.0"):   False,   # SSPL is not OSI-approved
    ("BSL-1.0",      "GPL-3.0"):   False,   # BSL is not open source
}


# ─────────────────────────────────────────────────────────────────────────────
# LICENSE TYPE HIERARCHY
# ─────────────────────────────────────────────────────────────────────────────

LICENSE_HIERARCHY: dict[str, dict] = {
    "permissive": {
        "description": "Minimal restrictions. Source disclosure NOT required.",
        "members": [
            "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
            "ISC", "Unlicense", "CC0-1.0", "Zlib", "PostgreSQL", "Artistic-2.0",
        ],
    },
    "weak_copyleft": {
        "description": (
            "Copyleft applies to the modified file/module only, not the entire project."
        ),
        "members": ["LGPL-2.1", "LGPL-3.0", "MPL-2.0", "EPL-2.0", "EUPL-1.2", "CDDL-1.0", "CPAL-1.0"],
    },
    "strong_copyleft": {
        "description": "Copyleft infects the entire distributed work.",
        "members": ["GPL-2.0", "GPL-3.0"],
    },
    "network_copyleft": {
        "description": "Copyleft triggers on network use (SaaS), not just distribution.",
        "members": ["AGPL-3.0", "SSPL-1.0"],
    },
    "source_available": {
        "description": "Source is visible but use/distribution is restricted. NOT open source.",
        "members": ["SSPL-1.0", "BSL-1.0", "Elastic-2.0"],
    },
    "proprietary": {
        "description": "All rights reserved. No reuse without explicit permission.",
        "members": ["Proprietary"],
    },
    "content_license": {
        "description": "Designed for creative works, not software code.",
        "members": [
            "CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-NC-4.0",
            "CC-BY-NC-SA-4.0", "CC0-1.0", "OFL-1.1",
        ],
    },
    "hardware_license": {
        "description": "Designed for open hardware / HDL projects.",
        "members": ["CERN-OHL-S-2.0", "CERN-OHL-W-2.0", "CERN-OHL-P-2.0"],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Inference engine
# ─────────────────────────────────────────────────────────────────────────────

def run_engine(facts: dict) -> dict:
    """
    Run all rules against the provided facts and return the working memory.

    Parameters
    ----------
    facts : dict
        User-supplied attributes describing the project and its requirements.

    Returns
    -------
    dict with keys:
        recommended – set of suggested licences
        eliminated  – set of incompatible licences
        warnings    – list of advisory messages
        flags       – list of hard-conflict identifiers
        scores      – dict for optional ranking (not populated here)
    """
    wm: dict[str, Any] = {
        "recommended": set(),
        "eliminated":  set(),
        "warnings":    [],
        "flags":       [],
        "scores":      {},
    }

    for rule in RULES:
        try:
            if rule.matches(facts):
                rule.fire(wm)
        except Exception as exc:  # noqa: BLE001
            wm["warnings"].append(f"[Rule {rule.id} error]: {exc}")

    # Remove eliminated licences from recommendations
    wm["recommended"] -= wm["eliminated"]

    return wm


# ─────────────────────────────────────────────────────────────────────────────
# Quick demo
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    # Example: open-source SaaS library with copyleft intent and patent concerns
    demo_facts = {
        "is_software":           True,
        "project_type":          "library",
        "saas":                  True,
        "commercial_use":        True,
        "closed_source":         False,
        "want_copyleft":         True,
        "need_patent_protection":True,
        "distribution":          True,
    }

    result = run_engine(demo_facts)

    print("=== LicenseWise Results ===\n")
    print("Recommended :", sorted(result["recommended"]))
    print("Eliminated  :", sorted(result["eliminated"]))
    print("\nWarnings:")
    for w in result["warnings"]:
        print(" •", w)
    print("\nFlags:")
    for f in result["flags"]:
        print(" ⚠", f)