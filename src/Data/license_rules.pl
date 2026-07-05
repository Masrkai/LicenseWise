% ============================================================
% LicenseWise Expert System - Prolog Knowledge Base
% ============================================================
% All rules, helpers, and trace infrastructure.
% License metadata lives in Licenses/Families/*.json (loaded by Python).
% ============================================================

:- dynamic fact/1.
:- dynamic step/6.
:- dynamic license_id/1.
:- dynamic license_type/2.
:- discontiguous recommend/1.
:- discontiguous eliminate/1.
:- discontiguous warning/2.

% ============================================================
% Helper predicates
% ============================================================

saas :-
    fact(saas).
saas :-
    fact(network_saas).

copyleft :-
    fact(want_copyleft).
copyleft :-
    fact(wants_derivatives_open).

patent :-
    fact(need_patent_protection).
patent :-
    fact(patent_protection_needed).

private_mods :-
    fact(closed_source).
private_mods :-
    fact(wants_relicense).
private_mods :-
    fact(wants_to_keep_modifications_private).

% ============================================================
% Trace infrastructure
% ============================================================

assert_step(Id, Name, Type, Affected, Explanation) :-
    findall(F, fact(F), Facts),
    assertz(step(Id, Name, Type, Facts, Affected, Explanation)).

clear_facts :-
    retractall(fact(_)).

clear_trace :-
    retractall(step(_, _, _, _, _, _)).

clear_metadata :-
    retractall(license_id(_)),
    retractall(license_type(_, _)),
    retractall(license_condition(_, _)),
    retractall(license_permission(_, _)),
    retractall(license_limitation(_, _)),
    retractall(metadata_osi_approved(_, _)),
    retractall(metadata_fsf_free(_, _)).

% ============================================================
% A. Permissive licenses (generic, metadata-driven)
% ============================================================

% Safe for closed-source projects -- no source disclosure requirement
recommend(License) :-
    license_type(License, permissive),
    fact(closed_source),
    assert_step('A01', 'recommend_permissive_if_closed_source', 'RECOMMEND',
                [License], 'Permissive licenses do not require source disclosure, safe for closed-source projects.').

% Safe for SaaS -- no network copyleft
recommend(License) :-
    license_type(License, permissive),
    saas,
    assert_step('A02', 'recommend_permissive_if_saas', 'RECOMMEND',
                [License], 'Permissive licenses have no network copyleft, suitable for SaaS.').

% Simple permissive -- minimal requirements
recommend(License) :-
    license_type(License, permissive),
    fact(want_simple_permissive),
    assert_step('A03', 'recommend_permissive_if_simple', 'RECOMMEND',
                [License], 'Permissive licenses have minimal requirements - just retain the copyright notice.').

% Any license with a patent grant -- for users who need patent protection
recommend(License) :-
    license_id(License),
    license_permission(License, patent_grant),
    patent,
    assert_step('A04', 'recommend_patent_grant_license', 'RECOMMEND',
                [License], 'This license includes an explicit patent grant for your protection.').

% --- Public domain ---
recommend('Unlicense') :-
    fact(want_public_domain),
    assert_step('A05a', 'recommend_Unlicense_if_public_domain', 'RECOMMEND',
                ['Unlicense'], 'Unlicense dedicates your work to the public domain.').
recommend('CC0-1.0') :-
    fact(want_public_domain),
    assert_step('A05b', 'recommend_CC0_if_public_domain', 'RECOMMEND',
                ['CC0-1.0'], 'CC0 dedicates your work to the public domain with a legal fallback. Safer than Unlicense internationally.').

% --- Unlicense warning (public domain may not be recognized everywhere) ---
warning('Unlicense', 'Unlicense is a public domain dedication and may not be legally recognised everywhere. Consider CC0-1.0 for better international coverage.') :-
    fact(want_public_domain),
    assert_step('A06', 'warn_unlicense_jurisdiction', 'WARN',
                ['Unlicense'], 'Unlicense public domain dedication may not be legally valid worldwide.').

% ============================================================
% B. Copyleft licenses (generic, metadata-driven)
% ============================================================

% Strong copyleft -- project-level scope, no closed source, no SaaS loophole
recommend(License) :-
    license_condition(License, same_license),
    \+ license_condition(License, net_copyleft),
    copyleft,
    \+ fact(closed_source),
    \+ saas,
    assert_step('B01', 'recommend_copyleft_if_wanted', 'RECOMMEND',
                [License], 'Strong copyleft ensures distributed derivatives remain open source.').

% Network copyleft -- AGPL-like, for SaaS + copyleft needs
recommend(License) :-
    license_condition(License, net_copyleft),
    saas,
    copyleft,
    \+ fact(closed_source),
    assert_step('B02', 'recommend_network_copyleft_if_saas', 'RECOMMEND',
                [License], 'Network copyleft closes the SaaS loophole, ensuring users can access source.').

% Copyleft for closed source -- already eliminated by E01, but warn
warning(License, 'SaaS does not trigger copyleft. Consider network copyleft.') :-
    license_condition(License, same_license),
    \+ license_condition(License, net_copyleft),
    saas,
    copyleft,
    assert_step('B03', 'warn_copyleft_saas_loophole', 'WARN',
                [License], 'Copyleft only applies on distribution, not network use.').

% ============================================================
% C. Weak copyleft / middle-ground
% ============================================================

% --- LGPL ---
recommend('LGPL-2.1') :-
    fact(project_type(library)),
    fact(want_weak_copyleft),
    assert_step('C01a', 'recommend_LGPL21_for_library', 'RECOMMEND',
                ['LGPL-2.1'], 'LGPL-2.1 keeps the library open but allows proprietary linking.').

recommend('LGPL-3.0') :-
    fact(project_type(library)),
    fact(want_weak_copyleft),
    assert_step('C01b', 'recommend_LGPL30_for_library', 'RECOMMEND',
                ['LGPL-3.0'], 'LGPL-3.0 keeps the library open but allows proprietary linking.').

warning('LGPL-2.1', 'Static linking may require the combined work to be LGPL.') :-
    fact(linking_type(static)),
    assert_step('C02a', 'warn_LGPL21_static_linking', 'WARN',
                ['LGPL-2.1'], 'Dynamic linking is safer for proprietary apps.').

warning('LGPL-3.0', 'Static linking may require the combined work to be LGPL.') :-
    fact(linking_type(static)),
    assert_step('C02b', 'warn_LGPL30_static_linking', 'WARN',
                ['LGPL-3.0'], 'Dynamic linking is safer for proprietary apps.').

% --- MPL-2.0 ---
recommend('MPL-2.0') :-
    fact(want_file_copyleft),
    \+ fact(closed_source),
    assert_step('C03', 'recommend_MPL_if_file_copyleft', 'RECOMMEND',
                ['MPL-2.0'], 'MPL-2.0 uses file-level copyleft - only modified files must stay open.').

recommend('MPL-2.0') :-
    fact(mixed_open_proprietary),
    assert_step('C04', 'recommend_MPL_if_mixed_codebase', 'RECOMMEND',
                ['MPL-2.0'], 'MPL-2.0 is ideal for mixed open/proprietary codebases.').

% ============================================================
% D. Content / non-software licenses
% ============================================================

recommend('CC-BY-NC-4.0') :-
    fact(project_type(content)),
    \+ fact(commercial_use),
    assert_step('D01', 'recommend_CC_BY_NC_if_content_noncommercial', 'RECOMMEND',
                ['CC-BY-NC-4.0'], 'CC-BY-NC-4.0 is for non-commercial creative content.').

eliminate('CC-BY-NC-4.0') :-
    fact(commercial_use),
    assert_step('D02', 'eliminate_CC_BY_NC_if_commercial', 'ELIMINATE',
                ['CC-BY-NC-4.0'], 'CC-BY-NC-4.0 prohibits commercial use.').

% --- CC-BY-4.0 ---
recommend('CC-BY-4.0') :-
    fact(project_type(content)),
    fact(commercial_use),
    assert_step('D03', 'recommend_CC_BY_if_content_commercial', 'RECOMMEND',
                ['CC-BY-4.0'], 'CC-BY-4.0 permits commercial use with attribution only.').
recommend('CC-BY-4.0') :-
    fact(project_type(content)),
    fact(want_simple_permissive),
    assert_step('D04', 'recommend_CC_BY_if_simple', 'RECOMMEND',
                ['CC-BY-4.0'], 'CC-BY-4.0 is the simplest Creative Commons license, attribution only.').

% --- CC-BY-SA-4.0 ---
recommend('CC-BY-SA-4.0') :-
    fact(project_type(content)),
    fact(want_copyleft),
    fact(commercial_use),
    assert_step('D05', 'recommend_CC_BY_SA_if_content_copyleft', 'RECOMMEND',
                ['CC-BY-SA-4.0'], 'CC-BY-SA-4.0 ensures derivatives remain under the same license, permits commercial use.').
recommend('CC-BY-SA-4.0') :-
    fact(project_type(content)),
    fact(want_copyleft),
    \+ fact(commercial_use),
    assert_step('D06', 'recommend_CC_BY_SA_if_content_copyleft_noncommercial', 'RECOMMEND',
                ['CC-BY-SA-4.0'], 'CC-BY-SA-4.0 ensures derivatives remain under the same license.').

% --- ODbL ---
recommend('ODbL') :-
    fact(project_type(content)),
    fact(want_copyleft),
    assert_step('D07', 'recommend_ODbL_if_database_copyleft', 'RECOMMEND',
                ['ODbL'], 'ODbL is the standard open database license used by OpenStreetMap.').

% ============================================================
% E. User preference rules (wired from questions.json)
% ============================================================

% --- Attribution preference ---
% User wants attribution from redistributors
recommend(License) :-
    license_condition(License, include_copyright),
    license_condition(License, include_license),
    fact(wants_attribution),
    assert_step('E07', 'recommend_if_attribution_wanted', 'RECOMMEND',
                [License], 'License requires attribution notices, matching your preference.').
% Prefer no-attribution licenses when user explicitly says NO to attribution
recommend(License) :-
    license_type(License, permissive),
    \+ license_condition(License, include_copyright),
    \+ license_condition(License, include_license),
    fact(wants_attribution(no)),
    assert_step('E09', 'recommend_no_attribution_license', 'RECOMMEND',
                [License], 'License requires no attribution, matching your preference.').

% --- Patent retaliation preference ---
% User wants patent retaliation clauses -- recommend licenses that have them
recommend('Apache-2.0') :-
    fact(wants_patent_retaliation),
    assert_step('E12', 'recommend_apache_patent_retaliation', 'RECOMMEND',
                ['Apache-2.0'], 'Apache-2.0 includes patent retaliation -- if you sue for patent infringement, your license terminates.').
recommend('MPL-2.0') :-
    fact(wants_patent_retaliation),
    assert_step('E13', 'recommend_mpl_patent_retaliation', 'RECOMMEND',
                ['MPL-2.0'], 'MPL-2.0 includes patent retaliation clauses as requested.').
recommend('EPL-2.0') :-
    fact(wants_patent_retaliation),
    assert_step('E13b', 'recommend_epl_patent_retaliation', 'RECOMMEND',
                ['EPL-2.0'], 'EPL-2.0 includes patent retaliation clauses as requested.').

% --- Dual licensing preference ---
% Dual licensing requires copyleft (enables dual-license business model)
recommend(License) :-
    license_condition(License, same_license),
    \+ license_condition(License, net_copyleft),
    fact(dual_licensing),
    \+ fact(closed_source),
    assert_step('E14', 'recommend_copyleft_for_dual_licensing', 'RECOMMEND',
                [License], 'Copyleft license enables dual licensing: open-source version + commercial license under a CLA.').
warning(License, 'Dual licensing typically requires a Contributor License Agreement (CLA).') :-
    license_condition(License, same_license),
    fact(dual_licensing),
    assert_step('E15', 'warn_dual_licensing_cla', 'WARN',
                [License], 'Dual licensing with copyleft requires a CLA to grant commercial licenses.').

% ============================================================
% I. Contradiction detection
% ============================================================

% Public domain + copyleft is contradictory
warning('Unlicense', 'You selected both public domain and copyleft. Public domain dedication has no copyleft requirement -- these goals conflict.') :-
    fact(want_public_domain),
    fact(want_copyleft),
    assert_step('I01', 'warn_pd_copyleft_contradiction', 'WARN',
                ['Unlicense'], 'Public domain (no restrictions) contradicts copyleft (keep derivatives open).').

% Public domain + non-commercial is contradictory
warning('CC0-1.0', 'You selected both public domain and non-commercial use. Public domain dedication allows commercial use -- these goals conflict.') :-
    fact(want_public_domain),
    fact(commercial_use(no)),
    assert_step('I02', 'warn_pd_noncommercial_contradiction', 'WARN',
                ['CC0-1.0'], 'Public domain (no restrictions) contradicts non-commercial use.').

% Eliminate ecosystem-specific licenses from generic recommendations
% These are only relevant for specific projects (Perl, PostgreSQL, etc.)
eliminate('Artistic-2.0') :-
    \+ fact(perl_project),
    assert_step('G04a', 'eliminate_Artistic_niche', 'ELIMINATE',
                ['Artistic-2.0'], 'Artistic-2.0 is a Perl-specific license. Use MIT or BSD for general projects.').
eliminate('PostgreSQL') :-
    \+ fact(postgresql_project),
    assert_step('G04b', 'eliminate_PostgreSQL_niche', 'ELIMINATE',
                ['PostgreSQL'], 'PostgreSQL license is only used by the PostgreSQL project itself.').
eliminate('CDDL-1.0') :-
    \+ fact(zfs_project),
    assert_step('G04c', 'eliminate_CDDL_niche', 'ELIMINATE',
                ['CDDL-1.0'], 'CDDL-1.0 is primarily used for ZFS. Use MPL-2.0 for general file-level copyleft.').
eliminate('EPL-2.0') :-
    \+ fact(eclipse_project),
    assert_step('G04d', 'eliminate_EPL_niche', 'ELIMINATE',
                ['EPL-2.0'], 'EPL-2.0 is primarily used for Eclipse/Java projects. Use MPL-2.0 for general file-level copyleft.').

% --- BSL-1.0 ---
warning('BSL-1.0', 'BSL-1.0 has an executable name change requirement in modified versions.') :-
    fact(modify_library),
    assert_step('G03', 'warn_BSL_name_change', 'WARN',
                ['BSL-1.0'], 'Modified versions must rename executables per BSL-1.0.').

% --- Artistic-2.0 ---
warning('Artistic-2.0', 'Artistic-2.0 has a copyleft option for modified standard versions.') :-
    fact(closed_source),
    assert_step('G05', 'warn_Artistic_copyleft_option', 'WARN',
                ['Artistic-2.0'], 'Modified standard versions must be shared under Artistic-2.0.').

% ============================================================
% E. General elimination rules (metadata-driven)
% ============================================================

eliminate(License) :-
    license_condition(License, disclose_source),
    fact(closed_source),
    assert_step('E01', 'exclude_copyleft_if_private_mods', 'ELIMINATE',
                [License], 'License requires source disclosure but project is closed-source.').

eliminate(License) :-
    license_condition(License, same_license),
    fact(wants_relicense),
    assert_step('E02', 'exclude_copyleft_if_wants_relicense', 'ELIMINATE',
                [License], 'License requires same-license derivatives but user wants to relicense.').

% ============================================================
% F. Generic metadata-based rules
% ============================================================
% These rules check license metadata (conditions, permissions, limitations)
% that are asserted dynamically by Python for any license.

:- dynamic license_condition/2.
:- dynamic license_permission/2.
:- dynamic license_limitation/2.
:- dynamic metadata_osi_approved/2.
:- dynamic metadata_fsf_free/2.

% Elimination: network copyleft + closed-source SaaS
eliminate(License) :-
    license_condition(License, net_copyleft),
    fact(saas),
    fact(closed_source),
    assert_step('F03', 'metadata_net_copyleft_saas', 'ELIMINATE',
                [License], 'License has network copyleft incompatible with closed-source SaaS.').

% Elimination: no commercial use permission
eliminate(License) :-
    license_id(License),
    \+ license_permission(License, commercial_use),
    fact(commercial_use),
    assert_step('F04', 'metadata_no_commercial', 'ELIMINATE',
                [License], 'License does not grant commercial use permission.').

% Warning: no patent grant
warning(License, 'No patent grant - consider Apache-2.0.') :-
    license_id(License),
    \+ license_permission(License, patent_grant),
    fact(need_patent_protection),
    assert_step('F05', 'metadata_no_patent', 'WARN',
                [License], 'License offers no patent protection.').

% Elimination: document_changes required but user does not want it
eliminate(License) :-
    license_condition(License, document_changes),
    fact(want_no_document_changes),
    assert_step('F06', 'metadata_document_changes', 'ELIMINATE',
                [License], 'License requires documenting changes but you want to avoid this obligation.').
warning(License, 'This license requires documenting changes.') :-
    license_condition(License, document_changes),
    fact(want_no_document_changes(no)),
    assert_step('F07', 'warn_document_changes', 'WARN',
                [License], 'Apache-2.0, GPL, and LGPL require documenting changes to licensed files.').

% Elimination: not OSI-approved when user prefers OSI
eliminate(License) :-
    license_id(License),
    metadata_osi_approved(License, false),
    fact(prefer_osi_approved),
    assert_step('F08', 'metadata_not_osi_approved', 'ELIMINATE',
                [License], 'License is not OSI-approved and you prefer OSI-recognized licenses.').

% Elimination: not FSF-free when user prefers FSF
eliminate(License) :-
    license_id(License),
    metadata_fsf_free(License, false),
    fact(prefer_fsf_free),
    assert_step('F09', 'metadata_not_fsf_free', 'ELIMINATE',
                [License], 'License is not FSF-recognized as free software.').
warning(License, 'This license is not FSF-recognized as free software.') :-
    license_id(License),
    metadata_fsf_free(License, false),
    fact(prefer_fsf_free(no)),
    assert_step('F10', 'warn_not_fsf_free', 'WARN',
                [License], 'License is not listed as free by the FSF.').

% ============================================================
% G. Cross-license compatibility warnings
% ============================================================

warning('GPL-2.0', 'GPL-2.0 is incompatible with Apache-2.0 for combined works.') :-
    fact(commercial_use),
    assert_step('H01', 'warn_gpl2_apache_combined', 'WARN',
                ['GPL-2.0'], 'GPL-2.0 cannot be combined with Apache-2.0 code in a single work.').
warning('GPL-3.0', 'GPL-3.0 is incompatible with OpenSSL exception under GPL-2.0.') :-
    fact(project_type(software)),
    assert_step('H02', 'warn_gpl3_openssl', 'WARN',
                ['GPL-3.0'], 'GPL-3.0 combined with OpenSSL may trigger GPL copyleft on linked code.').
warning('AGPL-3.0', 'AGPL-3.0 is incompatible with most proprietary codebases.') :-
    fact(closed_source),
    assert_step('H03', 'warn_agpl_proprietary', 'WARN',
                ['AGPL-3.0'], 'AGPL-3.0 cannot be used in closed-source projects due to network copyleft.').

% ============================================================
% H. Jurisdiction / context recommendations
% ============================================================

recommend('EUPL-1.2') :-
    fact(concerned_about_legal_recognition),
    \+ fact(closed_source),
    assert_step('J01', 'recommend_EUPL_if_EU_context', 'RECOMMEND',
                ['EUPL-1.2'], 'EUPL-1.2 is explicitly recognised by EU law, preferred in European public sector projects.').
recommend('BSD-2-Clause') :-
    fact(academic_project),
    \+ fact(want_copyleft),
    assert_step('J02', 'recommend_BSD_if_academic', 'RECOMMEND',
                ['BSD-2-Clause'], 'BSD-2-Clause is widely used in academic and research settings.').

% ============================================================
% Utility predicates
% ============================================================

collect_recommended(Licenses) :-
    findall(L, recommend(L), Raw),
    list_to_set(Raw, Licenses).

collect_eliminated(Licenses) :-
    findall(L, eliminate(L), Raw),
    list_to_set(Raw, Licenses).

collect_warnings(Warnings) :-
    findall(_{license: L, message: M}, warning(L, M), Warnings).

% Backward chain: check specific license
compatible(License, Result) :-
    ( recommend(License) -> Result = compatible
    ; eliminate(License)  -> Result = incompatible
    ; Result = unknown
    ).

% Active recommendations: elimination-wins semantics
collect_active_recommendations(L) :-
    recommend(L),
    \+ eliminate(L).

% Active warnings: skip warnings for eliminated licenses
collect_active_warnings(L, Msg) :-
    warning(L, Msg),
    \+ eliminate(L).

% Copyleft conflict detection: user wants copyleft but no copyleft license survives
warning('CONFLICT', Msg) :-
    fact(want_copyleft),
    \+ (license_condition(L, same_license), recommend(L), \+ eliminate(L)),
    \+ (license_condition(L, net_copyleft), recommend(L), \+ eliminate(L)),
    Msg = 'CONFLICT: No copyleft license satisfies all your constraints. Consider relaxing constraints.'.

% File copyleft conflict detection
warning('CONFLICT', Msg) :-
    fact(want_file_copyleft),
    \+ (license_condition(L, copyleft_scope), license_id(L), recommend(L), \+ eliminate(L)),
    Msg = 'CONFLICT: No file-level copyleft license satisfies all your constraints. MPL-2.0 requires documenting changes.'.

% Trace extraction: relevant steps for a specific license
relevant_elimination_trace(License, Steps) :-
    findall(explanation(Explanation),
        (step(_, _, 'ELIMINATE', _, Affected, Explanation), member(License, Affected)),
        Steps).

relevant_recommendation_trace(License, Steps) :-
    findall(explanation(Explanation),
        (step(_, _, 'RECOMMEND', _, Affected, Explanation), member(License, Affected)),
        Steps).

relevant_warning_trace(License, Steps) :-
    findall(explanation(Explanation),
        (step(_, _, 'WARN', _, Affected, Explanation), member(License, Affected)),
        Steps).

% ============================================================
% Question explanations (why each fact is asked)
% ============================================================

fact_explanation(closed_source,
    'We need to know if you''ll distribute source code because strong copyleft licenses (GPL-3.0, AGPL-3.0) REQUIRE source disclosure. If you keep code private, these licenses are incompatible.').
fact_explanation(saas,
    'Network deployment matters because AGPL-3.0 triggers copyleft when users interact over a network - even without distribution. This closes the ''SaaS loophole''.').
fact_explanation(commercial_use,
    'Some licenses explicitly prohibit commercial use (e.g., CC-BY-NC-4.0). Most open source licenses allow it, but we must confirm to eliminate non-commercial licenses.').
fact_explanation(need_patent_protection,
    'Patent protection is not offered by all licenses. MIT and BSD have no patent grant; Apache-2.0 includes a strong patent clause.').
fact_explanation(want_copyleft,
    'Copyleft ensures that modified versions remain open source. Strong copyleft (GPL, AGPL) affects the whole work; weak copyleft (LGPL, MPL) only affects certain parts.').
fact_explanation(want_weak_copyleft,
    'Weak copyleft is ideal for libraries: the library stays open but applications linking to it can be proprietary.').
fact_explanation(want_file_copyleft,
    'File-level copyleft (MPL-2.0) means only modified files must stay open - good for mixed codebases.').
fact_explanation(wants_relicense,
    'Some licenses (GPL, AGPL) require derivatives to use the same license. If you want to relicense freely, we avoid those.').
fact_explanation(project_type,
    'Licenses are designed for specific types of work: software, libraries, or creative content. This affects copyleft scope and compatibility.').
fact_explanation(want_public_domain,
    'Public domain dedication (Unlicense) imposes no conditions but may not be legally recognised everywhere. CC0 is a safer alternative.').
fact_explanation(want_simple_permissive,
    'Simple permissive licenses (MIT, BSD) only require retaining the copyright notice. They are the easiest to comply with but offer no patent protection.').
fact_explanation(academic_project,
    'Academic projects often prefer BSD-2-Clause due to its history in research settings.').
fact_explanation(mixed_open_proprietary,
    'MPL-2.0 is designed for mixed open/proprietary codebases - file-level copyleft keeps modified files open while allowing proprietary additions.').
fact_explanation(linking_type,
    'LGPL-2.1 compliance depends on linking type: dynamic linking is generally safe for proprietary apps; static linking may require open sourcing the combined work.').
fact_explanation(modify_library,
    'If you modify a copyleft library, you must share those modifications. This affects whether LGPL or stronger copyleft applies.').
fact_explanation(concerned_about_legal_recognition,
    'Some licenses (Unlicense) rely on public domain, which is not recognised in all countries. We need to know if legal certainty is a priority.').
fact_explanation(wants_attribution,
    'Attribution requirements vary: MIT/BSD require keeping the copyright notice, while Unlicense/MIT-0 impose no attribution. This affects compliance complexity.').
fact_explanation(wants_patent_retaliation,
    'Patent retaliation clauses terminate the license if the recipient sues for patent infringement. Apache-2.0, MPL-2.0, and EPL-2.0 include these.').
fact_explanation(dual_licensing,
    'Dual licensing means offering the same software under two licenses (e.g., GPL + commercial). This requires a Contributor License Agreement (CLA).').
fact_explanation(want_no_document_changes,
    'Apache-2.0, GPL, LGPL, and Zlib require documenting changes to licensed files. If you want to avoid this, choose MIT or BSD instead.').
fact_explanation(prefer_osi_approved,
    'The Open Source Initiative approves licenses that meet the Open Source Definition. Non-OSI licenses (BSL, Elastic, CC) are excluded.').
fact_explanation(prefer_fsf_free,
    'The Free Software Foundation maintains a list of licenses it considers free software. Some licenses (CC, Elastic, BSL) are not FSF-recognized.').

get_question_explanation(Fact, Explanation) :-
    ( fact_explanation(Fact, Explanation) -> true
    ; Explanation = 'This question helps narrow down compatible licenses.'
    ).
