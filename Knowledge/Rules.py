class Rule:
    def __init__(self, name, condition, action, explanation):
        self.name = name
        self.condition = condition
        self.action = action
        self.explanation = explanation

    def matches(self, facts):
        return self.condition(facts)

    def fire(self, working_memory):
        self.action(working_memory)


# ============================================================================
# KNOWLEDGE BASE: Open Source License Recommendation System
# ============================================================================
# 
# Facts (user inputs) expected in the facts dictionary:
#   - closed_source (bool): Project will not distribute source code
#   - saas (bool): Software will be used over a network (SaaS)
#   - commercial_use (bool): Software will be used commercially
#   - need_patent_protection (bool): Need explicit patent grant
#   - want_copyleft (bool): Want derivatives to remain open source
#   - want_weak_copyleft (bool): Want library-level copyleft only
#   - want_file_copyleft (bool): Want file-level copyleft only
#   - wants_relicense (bool): Want freedom to relicense derivatives
#   - project_type (str): "software", "library", or "content"
#   - want_public_domain (bool): Want to dedicate to public domain
#   - want_simple_permissive (bool): Want a simple permissive license
#   - concerned_about_legal_recognition (bool): Concerned about legal jurisdiction issues
#   - wants_minimal_attribution (bool): Want minimal attribution requirements
#
# Working Memory structure:
#   {
#       "recommended": set(),      # Licenses that match user needs
#       "eliminated": set(),       # Licenses incompatible with user needs
#       "warnings": list(),        # Cautions about recommended/eliminated licenses
#       "scores": dict()           # License -> score for ranking
#   }
# ============================================================================


Rules = [

# ============================================================================
# MIT LICENSE
# ============================================================================
# Type: permissive
# Key properties: No source disclosure, no network copyleft, no same-license
# Limitations: No explicit patent grant
# ============================================================================

    Rule(
        name="recommend_MIT_if_closed_source",
        condition=lambda facts: facts.get("closed_source") == True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation="MIT does not require source disclosure, making it safe for closed-source projects."
    ),

    Rule(
        name="recommend_MIT_if_saas",
        condition=lambda facts: facts.get("saas") == True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation="MIT has no network copyleft requirement, so using it in a SaaS product is perfectly fine."
    ),

    Rule(
        name="recommend_MIT_if_wants_relicense",
        condition=lambda facts: facts.get("wants_relicense") == True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation="MIT has no same-license requirement, so you can relicense derivatives freely."
    ),

    Rule(
        name="recommend_MIT_if_simple_permissive",
        condition=lambda facts: facts.get("want_simple_permissive") == True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation="MIT is one of the simplest and most widely adopted permissive licenses."
    ),

    Rule(
        name="recommend_MIT_if_commercial",
        condition=lambda facts: facts.get("commercial_use") == True,
        action=lambda wm: wm["recommended"].add("MIT"),
        explanation="MIT permits commercial use without restrictions."
    ),

    Rule(
        name="warn_MIT_no_patent_grant",
        condition=lambda facts: facts.get("need_patent_protection") == True,
        action=lambda wm: wm["warnings"].append("MIT: No explicit patent grant. Consider Apache-2.0 instead."),
        explanation="MIT does not explicitly grant patent rights, leaving you potentially exposed to patent claims."
    ),

    Rule(
        name="warn_MIT_no_trademark_protection",
        condition=lambda facts: facts.get("need_trademark_protection") == True,
        action=lambda wm: wm["warnings"].append("MIT: No trademark protection clause."),
        explanation="MIT does not include any trademark usage restrictions or protections."
    ),


# ============================================================================
# APACHE-2.0 LICENSE
# ============================================================================
# Type: permissive
# Key properties: Explicit patent grant, document changes required
# Best for: Corporate/hardware projects where patent protection matters
# ============================================================================

    Rule(
        name="recommend_Apache_if_closed_source",
        condition=lambda facts: facts.get("closed_source") == True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation="Apache-2.0 does not require source disclosure, safe for closed-source projects."
    ),

    Rule(
        name="recommend_Apache_if_patent_protection",
        condition=lambda facts: facts.get("need_patent_protection") == True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation="Apache-2.0 includes an explicit patent grant and protection against contributor patent claims."
    ),

    Rule(
        name="recommend_Apache_if_commercial",
        condition=lambda facts: facts.get("commercial_use") == True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation="Apache-2.0 permits commercial use and includes patent protections valuable in commercial settings."
    ),

    Rule(
        name="recommend_Apache_if_saas",
        condition=lambda facts: facts.get("saas") == True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation="Apache-2.0 has no network copyleft, making it suitable for SaaS deployments."
    ),

    Rule(
        name="recommend_Apache_if_wants_relicense",
        condition=lambda facts: facts.get("wants_relicense") == True,
        action=lambda wm: wm["recommended"].add("Apache-2.0"),
        explanation="Apache-2.0 has no same-license requirement, allowing free relicensing of derivatives."
    ),

    Rule(
        name="warn_Apache_document_changes",
        condition=lambda facts: facts.get("wants_minimal_attribution") == True,
        action=lambda wm: wm["warnings"].append("Apache-2.0: Requires documenting changes in distributed works."),
        explanation="Apache-2.0 condition: document_changes = true. You must notify recipients of modified files."
    ),

    Rule(
        name="warn_Apache_trademark_clause",
        condition=lambda facts: facts.get("wants_trademark_freedom") == True,
        action=lambda wm: wm["warnings"].append("Apache-2.0: Includes trademark usage restrictions."),
        explanation="Apache-2.0 explicitly mentions trademark rights, which may limit certain uses."
    ),


# ============================================================================
# GPL-3.0 LICENSE
# ============================================================================
# Type: copyleft (strong)
# Key properties: Same license required, source disclosure required
# Best for: Ensuring all downstream modifications stay open
# ============================================================================

    Rule(
        name="recommend_GPL_if_copyleft",
        condition=lambda facts: facts.get("want_copyleft") == True and facts.get("closed_source") != True,
        action=lambda wm: wm["recommended"].add("GPL-3.0"),
        explanation="GPL-3.0 is strong copyleft: ensures all distributed derivatives remain open source."
    ),

    Rule(
        name="recommend_GPL_if_commercial_copyleft",
        condition=lambda facts: facts.get("commercial_use") == True and facts.get("want_copyleft") == True and facts.get("closed_source") != True,
        action=lambda wm: wm["recommended"].add("GPL-3.0"),
        explanation="GPL-3.0 permits commercial use while ensuring derivatives stay open through copyleft."
    ),

    Rule(
        name="eliminate_GPL_if_closed_source",
        condition=lambda facts: facts.get("closed_source") == True,
        action=lambda wm: wm["eliminated"].add("GPL-3.0"),
        explanation="GPL-3.0 requires source disclosure (disclose_source = true). Incompatible with closed-source distribution."
    ),

    Rule(
        name="eliminate_GPL_if_wants_relicense",
        condition=lambda facts: facts.get("wants_relicense") == True,
        action=lambda wm: wm["eliminated"].add("GPL-3.0"),
        explanation="GPL-3.0 requires the same license for all derivatives (same_license = true). You cannot relicense freely."
    ),

    Rule(
        name="warn_GPL_saas_loophole",
        condition=lambda facts: facts.get("saas") == True and facts.get("want_copyleft") == True,
        action=lambda wm: wm["warnings"].append("GPL-3.0: Network use (SaaS) does NOT trigger copyleft. Consider AGPL-3.0 for server-side copyleft."),
        explanation="GPL-3.0 only triggers on distribution, not network use. The 'SaaS loophole' means server-side modifications can remain private."
    ),

    Rule(
        name="warn_GPL_same_license",
        condition=lambda facts: facts.get("wants_relicense") == True,
        action=lambda wm: wm["warnings"].append("GPL-3.0: Requires same license for derivatives."),
        explanation="GPL-3.0 condition: same_license = true. All distributed derivatives must use GPL-3.0."
    ),


# ============================================================================
# AGPL-3.0 LICENSE
# ============================================================================
# Type: copyleft (strongest)
# Key properties: Network copyleft - source disclosure triggered by network use
# Best for: Server-side software where you want to close the SaaS loophole
# ============================================================================

    Rule(
        name="recommend_AGPL_if_saas_copyleft",
        condition=lambda facts: facts.get("saas") == True and facts.get("want_copyleft") == True and facts.get("closed_source") != True,
        action=lambda wm: wm["recommended"].add("AGPL-3.0"),
        explanation="AGPL-3.0 closes the SaaS loophole: network use triggers source disclosure, keeping server-side code open."
    ),

    Rule(
        name="recommend_AGPL_if_strongest_copyleft",
        condition=lambda facts: facts.get("want_strongest_copyleft") == True and facts.get("closed_source") != True,
        action=lambda wm: wm["recommended"].add("AGPL-3.0"),
        explanation="AGPL-3.0 is the strongest copyleft license available, ensuring openness even for network deployments."
    ),

    Rule(
        name="eliminate_AGPL_if_closed_source",
        condition=lambda facts: facts.get("closed_source") == True,
        action=lambda wm: wm["eliminated"].add("AGPL-3.0"),
        explanation="AGPL-3.0 requires source disclosure for network use (net_copyleft = true). Completely incompatible with keeping code private."
    ),

    Rule(
        name="eliminate_AGPL_if_keep_server_private",
        condition=lambda facts: facts.get("saas") == True and facts.get("closed_source") == True,
        action=lambda wm: wm["eliminated"].add("AGPL-3.0"),
        explanation="AGPL-3.0 triggers copyleft on network access. If you run a SaaS and want to keep server code private, AGPL is not suitable."
    ),

    Rule(
        name="eliminate_AGPL_if_wants_relicense",
        condition=lambda facts: facts.get("wants_relicense") == True,
        action=lambda wm: wm["eliminated"].add("AGPL-3.0"),
        explanation="AGPL-3.0 requires same license for derivatives (same_license = true). Cannot relicense freely."
    ),

    Rule(
        name="warn_AGPL_avoid_if_private_saas",
        condition=lambda facts: facts.get("saas") == True and facts.get("want_copyleft") != True,
        action=lambda wm: wm["warnings"].append("AGPL-3.0: Using AGPL in SaaS without wanting copyleft is risky - any user accessing your service can demand the source code."),
        explanation="AGPL-3.0 net_copyleft = true. Anyone who interacts with your software over a network can request the complete source code."
    ),

    Rule(
        name="warn_AGPL_strongest_copyleft",
        condition=lambda facts: facts.get("want_copyleft") == True,
        action=lambda wm: wm["warnings"].append("AGPL-3.0: Strongest copyleft available. Ensure you understand the implications before choosing."),
        explanation="AGPL-3.0 is the most restrictive open source license. It affects both distribution AND network use."
    ),


# ============================================================================
# LGPL-2.1 LICENSE
# ============================================================================
# Type: weak_copyleft
# Key properties: Copyleft applies to library only; linking apps stay free
# Best for: Libraries you want to keep open while allowing proprietary use
# ============================================================================

    Rule(
        name="recommend_LGPL_for_library",
        condition=lambda facts: facts.get("project_type") == "library" and facts.get("want_weak_copyleft") == True,
        action=lambda wm: wm["recommended"].add("LGPL-2.1"),
        explanation="LGPL-2.1 is weak copyleft: the library itself stays open, but applications that link to it may use any license."
    ),

    Rule(
        name="recommend_LGPL_if_library_commercial",
        condition=lambda facts: facts.get("project_type") == "library" and facts.get("commercial_use") == True and facts.get("want_copyleft") != True,
        action=lambda wm: wm["recommended"].add("LGPL-2.1"),
        explanation="LGPL-2.1 allows proprietary applications to link to your library, making it ideal for widely-adopted libraries."
    ),

    Rule(
        name="recommend_LGPL_if_dynamic_linking",
        condition=lambda facts: facts.get("linking_type") == "dynamic" and facts.get("want_weak_copyleft") == True,
        action=lambda wm: wm["recommended"].add("LGPL-2.1"),
        explanation="LGPL-2.1 is designed for dynamic linking scenarios where the library remains separate from the main application."
    ),

    Rule(
        name="eliminate_LGPL_if_closed_source_library_modification",
        condition=lambda facts: facts.get("project_type") == "library" and facts.get("closed_source") == True and facts.get("modify_library") == True,
        action=lambda wm: wm["eliminated"].add("LGPL-2.1"),
        explanation="LGPL-2.1 requires source disclosure for modified versions of the library itself (disclose_source = true)."
    ),

    Rule(
        name="warn_LGPL_static_linking",
        condition=lambda facts: facts.get("linking_type") == "static",
        action=lambda wm: wm["warnings"].append("LGPL-2.1: Static linking may require the combined work to be LGPL-licensed. Dynamic linking is generally safer."),
        explanation="LGPL-2.1 explanation hint: Dynamic linking is generally safe; static linking may require more care to comply."
    ),

    Rule(
        name="warn_LGPL_not_for_applications",
        condition=lambda facts: facts.get("project_type") == "software" and facts.get("want_copyleft") == True,
        action=lambda wm: wm["warnings"].append("LGPL-2.1: Designed for libraries, not standalone applications. Consider GPL-3.0 for applications."),
        explanation="LGPL-2.1 is specifically designed for libraries. Using it for standalone applications may not achieve your copyleft goals."
    ),


# ============================================================================
# MPL-2.0 LICENSE
# ============================================================================
# Type: weak_copyleft
# Key properties: File-level copyleft; modified files stay open, rest can be proprietary
# Best for: Mixed open/proprietary codebases
# ============================================================================

    Rule(
        name="recommend_MPL_if_file_copyleft",
        condition=lambda facts: facts.get("want_file_copyleft") == True and facts.get("closed_source") != True,
        action=lambda wm: wm["recommended"].add("MPL-2.0"),
        explanation="MPL-2.0 uses file-level copyleft: only modified files must stay open, the rest of the project can be proprietary."
    ),

    Rule(
        name="recommend_MPL_if_mixed_codebase",
        condition=lambda facts: facts.get("mixed_open_proprietary") == True,
        action=lambda wm: wm["recommended"].add("MPL-2.0"),
        explanation="MPL-2.0 is the ideal middle ground for mixed open/proprietary codebases."
    ),

    Rule(
        name="recommend_MPL_if_commercial_weak_copyleft",
        condition=lambda facts: facts.get("commercial_use") == True and facts.get("want_weak_copyleft") == True,
        action=lambda wm: wm["recommended"].add("MPL-2.0"),
        explanation="MPL-2.0 permits commercial use while ensuring modified files remain open source."
    ),

    Rule(
        name="eliminate_MPL_if_closed_source_modifications",
        condition=lambda facts: facts.get("closed_source") == True and facts.get("modify_files") == True,
        action=lambda wm: wm["eliminated"].add("MPL-2.0"),
        explanation="MPL-2.0 requires disclosing source for modified files (disclose_source = true). Cannot keep modified files closed."
    ),

    Rule(
        name="warn_MPL_trademark",
        condition=lambda facts: facts.get("need_trademark_protection") == True,
        action=lambda wm: wm["warnings"].append("MPL-2.0: Includes trademark clause. Review if trademark freedom is important."),
        explanation="MPL-2.0 limitations: trademark_use = true. The license includes trademark usage restrictions."
    ),


# ============================================================================
# BSD-2-CLAUSE LICENSE
# ============================================================================
# Type: permissive
# Key properties: Similar to MIT, slightly different attribution, no patent grant
# Common in: Academic and BSD Unix-derived projects
# ============================================================================

    Rule(
        name="recommend_BSD_if_closed_source",
        condition=lambda facts: facts.get("closed_source") == True,
        action=lambda wm: wm["recommended"].add("BSD-2-Clause"),
        explanation="BSD-2-Clause does not require source disclosure, safe for closed-source projects."
    ),

    Rule(
        name="recommend_BSD_if_simple_permissive",
        condition=lambda facts: facts.get("want_simple_permissive") == True,
        action=lambda wm: wm["recommended"].add("BSD-2-Clause"),
        explanation="BSD-2-Clause is very similar to MIT - a simple, widely-understood permissive license."
    ),

    Rule(
        name="recommend_BSD_if_academic",
        condition=lambda facts: facts.get("academic_project") == True,
        action=lambda wm: wm["recommended"].add("BSD-2-Clause"),
        explanation="BSD-2-Clause is common in academic and BSD Unix-derived projects."
    ),

    Rule(
        name="recommend_BSD_if_commercial",
        condition=lambda facts: facts.get("commercial_use") == True,
        action=lambda wm: wm["recommended"].add("BSD-2-Clause"),
        explanation="BSD-2-Clause permits commercial use without restrictions."
    ),

    Rule(
        name="recommend_BSD_if_wants_relicense",
        condition=lambda facts: facts.get("wants_relicense") == True,
        action=lambda wm: wm["recommended"].add("BSD-2-Clause"),
        explanation="BSD-2-Clause has no same-license requirement, allowing free relicensing."
    ),

    Rule(
        name="warn_BSD_no_patent_grant",
        condition=lambda facts: facts.get("need_patent_protection") == True,
        action=lambda wm: wm["warnings"].append("BSD-2-Clause: No explicit patent grant. Consider Apache-2.0 instead."),
        explanation="BSD-2-Clause limitations: patent_use = false. No patent protection is provided."
    ),

    Rule(
        name="warn_BSD_vs_MIT",
        condition=lambda facts: facts.get("want_simple_permissive") == True,
        action=lambda wm: wm["warnings"].append("BSD-2-Clause vs MIT: Very similar. BSD-2-Clause omits the 'substantial portions' language. Either is fine for most cases."),
        explanation="BSD-2-Clause and MIT are functionally equivalent for most projects. Choose based on community preference."
    ),


# ============================================================================
# CC-BY-NC-4.0 LICENSE
# ============================================================================
# Type: other (not software license)
# Key properties: Non-commercial only, designed for creative content
# NOT suitable for: Software projects (not OSI approved, not FSF free)
# ============================================================================

    Rule(
        name="recommend_CC_BY_NC_if_content_noncommercial",
        condition=lambda facts: facts.get("project_type") == "content" and facts.get("commercial_use") != True,
        action=lambda wm: wm["recommended"].add("CC-BY-NC-4.0"),
        explanation="CC-BY-NC-4.0 is designed for creative content shared for non-commercial purposes."
    ),

    Rule(
        name="eliminate_CC_BY_NC_if_commercial",
        condition=lambda facts: facts.get("commercial_use") == True,
        action=lambda wm: wm["eliminated"].add("CC-BY-NC-4.0"),
        explanation="CC-BY-NC-4.0 explicitly prohibits commercial use (permissions.commercial_use = false)."
    ),

    Rule(
        name="eliminate_CC_BY_NC_if_software",
        condition=lambda facts: facts.get("project_type") == "software",
        action=lambda wm: wm["eliminated"].add("CC-BY-NC-4.0"),
        explanation="CC-BY-NC-4.0 is designed for creative content, not software. Not OSI approved, not FSF free."
    ),

    Rule(
        name="warn_CC_BY_NC_not_for_software",
        condition=lambda facts: facts.get("project_type") == "software",
        action=lambda wm: wm["warnings"].append("CC-BY-NC-4.0: Designed for creative content, not software. Avoid for code."),
        explanation="CC-BY-NC-4.0 metadata: osi_approved = false, fsf_free = false. This is not a software license."
    ),

    Rule(
        name="warn_CC_BY_NC_noncommercial_restriction",
        condition=lambda facts: facts.get("commercial_use") == True,
        action=lambda wm: wm["warnings"].append("CC-BY-NC-4.0: Explicitly prohibits commercial use."),
        explanation="CC-BY-NC-4.0 permissions: commercial_use = false. Any commercial use violates this license."
    ),


# ============================================================================
# UNLICENSE
# ============================================================================
# Type: permissive (public domain dedication)
# Key properties: No restrictions whatsoever, no attribution required
# Caution: Public domain not recognized in all jurisdictions
# ============================================================================

    Rule(
        name="recommend_Unlicense_if_public_domain",
        condition=lambda facts: facts.get("want_public_domain") == True,
        action=lambda wm: wm["recommended"].add("Unlicense"),
        explanation="Unlicense dedicates software to the public domain with no restrictions whatsoever."
    ),

    Rule(
        name="recommend_Unlicense_if_no_attribution",
        condition=lambda facts: facts.get("no_attribution_needed") == True,
        action=lambda wm: wm["recommended"].add("Unlicense"),
        explanation="Unlicense does not require any attribution or license inclusion (include_copyright = false, include_license = false)."
    ),

    Rule(
        name="recommend_Unlicense_if_maximum_freedom",
        condition=lambda facts: facts.get("want_maximum_freedom") == True,
        action=lambda wm: wm["recommended"].add("Unlicense"),
        explanation="Unlicense provides maximum freedom - essentially public domain with no conditions."
    ),

    Rule(
        name="recommend_Unlicense_if_closed_source",
        condition=lambda facts: facts.get("closed_source") == True,
        action=lambda wm: wm["recommended"].add("Unlicense"),
        explanation="Unlicense imposes no conditions, making it compatible with any use including closed source."
    ),

    Rule(
        name="warn_Unlicense_jurisdiction",
        condition=lambda facts: facts.get("concerned_about_legal_recognition") == True,
        action=lambda wm: wm["warnings"].append("Unlicense: Public domain dedication is not recognized in all jurisdictions. Consider CC0 or a permissive license as fallback."),
        explanation="Unlicense metadata note: 'Not recognized in all jurisdictions.' Some countries do not allow dedicating works to the public domain."
    ),

    Rule(
        name="warn_Unlicense_no_patent_grant",
        condition=lambda facts: facts.get("need_patent_protection") == True,
        action=lambda wm: wm["warnings"].append("Unlicense: No patent grant whatsoever."),
        explanation="Unlicense limitations: patent_use = false. There is absolutely no patent protection."
    ),

    Rule(
        name="warn_Unlicense_no_warranty_disclaimer_enforcement",
        condition=lambda facts: facts.get("need_strong_warranty_disclaimer") == True,
        action=lambda wm: wm["warnings"].append("Unlicense: Warranty disclaimer exists but may be less enforceable in some jurisdictions due to public domain nature."),
        explanation="Unlicense includes liability/warranty limitations, but public domain status may affect enforceability in some legal systems."
    ),

]
