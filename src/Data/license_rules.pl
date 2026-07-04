% ============================================================
% LicenseWise Expert System - Prolog Knowledge Base
% ============================================================
% All rules, helpers, and trace infrastructure.
% License metadata lives in Licenses/Families/*.json (loaded by Python).
% ============================================================

:- dynamic fact/1.
:- dynamic step/6.
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
    retractall(license_condition(_, _)),
    retractall(license_permission(_, _)),
    retractall(license_limitation(_, _)).

% ============================================================
% A. Permissive licenses
% ============================================================

% --- MIT ---
recommend('MIT') :-
    fact(closed_source),
    assert_step('A01', 'recommend_MIT_if_closed_source', 'RECOMMEND',
                ['MIT'], 'MIT does not require source disclosure, safe for closed-source projects.').

recommend('MIT') :-
    saas,
    assert_step('A02', 'recommend_MIT_if_saas', 'RECOMMEND',
                ['MIT'], 'MIT has no network copyleft, suitable for SaaS.').

recommend('MIT') :-
    fact(want_simple_permissive),
    assert_step('A03', 'recommend_MIT_if_simple_permissive', 'RECOMMEND',
                ['MIT'], 'MIT is the simplest and most widely adopted permissive license.').

warning('MIT', 'No explicit patent grant. Consider Apache-2.0.') :-
    patent,
    assert_step('A04', 'warn_MIT_no_patent_grant', 'WARN',
                ['MIT'], 'MIT does not grant patent rights.').

% --- Apache-2.0 ---
recommend('Apache-2.0') :-
    fact(closed_source),
    assert_step('A05', 'recommend_Apache_if_closed_source', 'RECOMMEND',
                ['Apache-2.0'], 'Apache-2.0 does not require source disclosure, safe for closed-source.').

recommend('Apache-2.0') :-
    patent,
    assert_step('A06', 'recommend_Apache_if_patent_protection', 'RECOMMEND',
                ['Apache-2.0'], 'Apache-2.0 includes explicit patent grant and protection.').

recommend('Apache-2.0') :-
    fact(commercial_use),
    assert_step('A07', 'recommend_Apache_if_commercial', 'RECOMMEND',
                ['Apache-2.0'], 'Apache-2.0 permits commercial use and includes patent protections.').

warning('Apache-2.0', 'Requires documenting changes in distributed works.') :-
    fact(wants_minimal_attribution),
    assert_step('A08', 'warn_Apache_document_changes', 'WARN',
                ['Apache-2.0'], 'Apache-2.0 has a condition to document changes.').

% --- BSD-2-Clause ---
recommend('BSD-2-Clause') :-
    fact(closed_source),
    assert_step('A09', 'recommend_BSD_if_closed_source', 'RECOMMEND',
                ['BSD-2-Clause'], 'BSD-2-Clause requires no source disclosure.').

recommend('BSD-2-Clause') :-
    fact(want_simple_permissive),
    assert_step('A10', 'recommend_BSD_if_simple_permissive', 'RECOMMEND',
                ['BSD-2-Clause'], 'BSD-2-Clause is a simple permissive license similar to MIT.').

warning('BSD-2-Clause', 'No patent grant. Consider Apache-2.0.') :-
    patent,
    assert_step('A11', 'warn_BSD_no_patent_grant', 'WARN',
                ['BSD-2-Clause'], 'BSD licenses offer no patent protection.').

% --- BSD-3-Clause ---
recommend('BSD-3-Clause') :-
    fact(closed_source),
    assert_step('A14', 'recommend_BSD3_if_closed_source', 'RECOMMEND',
                ['BSD-3-Clause'], 'BSD-3-Clause requires no source disclosure, safe for closed-source.').
recommend('BSD-3-Clause') :-
    fact(want_simple_permissive),
    assert_step('A15', 'recommend_BSD3_if_simple_permissive', 'RECOMMEND',
                ['BSD-3-Clause'], 'BSD-3-Clause is simple permissive with a non-endorsement clause.').
warning('BSD-3-Clause', 'No patent grant. Consider Apache-2.0.') :-
    patent,
    assert_step('A16', 'warn_BSD3_no_patent_grant', 'WARN',
                ['BSD-3-Clause'], 'BSD-3-Clause offers no patent protection.').

% --- ISC ---
recommend('ISC') :-
    fact(closed_source),
    assert_step('A17', 'recommend_ISC_if_closed_source', 'RECOMMEND',
                ['ISC'], 'ISC is functionally identical to MIT, safe for closed-source.').
recommend('ISC') :-
    fact(want_simple_permissive),
    assert_step('A18', 'recommend_ISC_if_simple_permissive', 'RECOMMEND',
                ['ISC'], 'ISC is a simple permissive license popular in the OpenBSD ecosystem.').
warning('ISC', 'No patent grant. Consider Apache-2.0.') :-
    patent,
    assert_step('A19', 'warn_ISC_no_patent_grant', 'WARN',
                ['ISC'], 'ISC offers no patent protection.').

% --- Zlib ---
recommend('Zlib') :-
    fact(closed_source),
    assert_step('A20', 'recommend_Zlib_if_closed_source', 'RECOMMEND',
                ['Zlib'], 'Zlib is permissive and allows closed-source use, commonly used for libraries.').
recommend('Zlib') :-
    fact(project_type(library)),
    assert_step('A21', 'recommend_Zlib_if_library', 'RECOMMEND',
                ['Zlib'], 'Zlib is a permissive library license similar to MIT.').

% --- MIT-0 ---
recommend('MIT-0') :-
    fact(want_simple_permissive),
    \+ fact(closed_source),
    assert_step('A22', 'recommend_MIT0_if_no_attribution', 'RECOMMEND',
                ['MIT-0'], 'MIT-0 removes the attribution requirement, maximal reuse.').
recommend('MIT-0') :-
    fact(closed_source),
    assert_step('A23', 'recommend_MIT0_if_closed_source', 'RECOMMEND',
                ['MIT-0'], 'MIT-0 does not require source disclosure, safe for closed-source.').

% --- Unlicense ---
recommend('Unlicense') :-
    fact(want_public_domain),
    assert_step('A12a', 'recommend_Unlicense', 'RECOMMEND',
                ['Unlicense'], 'Unlicense dedicates work to the public domain with no restrictions.').

% --- CC0-1.0 ---
recommend('CC0-1.0') :-
    fact(want_public_domain),
    assert_step('A12b', 'recommend_CC0', 'RECOMMEND',
                ['CC0-1.0'], 'CC0 dedicates work to the public domain with no restrictions.').

warning('Unlicense', 'Public domain dedication may not be recognized everywhere. Consider CC0.') :-
    fact(concerned_about_legal_recognition),
    assert_step('A13', 'warn_Unlicense_jurisdiction', 'WARN',
                ['Unlicense'], 'Public domain dedication may not be legally valid worldwide.').

% ============================================================
% B. Copyleft licenses
% ============================================================

% --- GPL-3.0 ---
recommend('GPL-3.0') :-
    copyleft,
    \+ fact(closed_source),
    \+ saas,
    assert_step('B01', 'recommend_GPL_if_copyleft', 'RECOMMEND',
                ['GPL-3.0'], 'GPL-3.0 ensures distributed derivatives remain open source.').

eliminate('GPL-3.0') :-
    fact(closed_source),
    assert_step('B02', 'eliminate_GPL_if_closed_source', 'ELIMINATE',
                ['GPL-3.0'], 'GPL requires source disclosure, incompatible with closed source.').

eliminate('GPL-3.0') :-
    fact(wants_relicense),
    assert_step('B03', 'eliminate_GPL_if_wants_relicense', 'ELIMINATE',
                ['GPL-3.0'], 'GPL requires same license for derivatives.').

warning('GPL-3.0', 'SaaS does not trigger GPL copyleft. Consider AGPL-3.0.') :-
    saas,
    copyleft,
    assert_step('B04', 'warn_GPL_saas_loophole', 'WARN',
                ['GPL-3.0'], 'GPL copyleft only applies on distribution, not network use.').

% --- AGPL-3.0 ---
recommend('AGPL-3.0') :-
    saas,
    copyleft,
    \+ fact(closed_source),
    assert_step('B05', 'recommend_AGPL_if_saas_copyleft', 'RECOMMEND',
                ['AGPL-3.0'], 'AGPL-3.0 closes the SaaS loophole – network use triggers copyleft.').

eliminate('AGPL-3.0') :-
    fact(closed_source),
    assert_step('B06', 'eliminate_AGPL_if_closed_source', 'ELIMINATE',
                ['AGPL-3.0'], 'AGPL requires source disclosure even for network use.').

warning('AGPL-3.0', 'Strongest copyleft. Applies to distribution AND network use.') :-
    copyleft,
    assert_step('B07', 'warn_AGPL_strongest_copyleft', 'WARN',
                ['AGPL-3.0'], 'AGPL is very restrictive; many companies prohibit its use.').

% --- GPL-2.0 ---
recommend('GPL-2.0') :-
    copyleft,
    \+ fact(closed_source),
    \+ saas,
    assert_step('B08', 'recommend_GPL2_if_copyleft', 'RECOMMEND',
                ['GPL-2.0'], 'GPL-2.0 ensures distributed derivatives remain open source.').
eliminate('GPL-2.0') :-
    fact(closed_source),
    assert_step('B09', 'eliminate_GPL2_if_closed_source', 'ELIMINATE',
                ['GPL-2.0'], 'GPL-2.0 requires source disclosure, incompatible with closed source.').
eliminate('GPL-2.0') :-
    fact(wants_relicense),
    assert_step('B10', 'eliminate_GPL2_if_wants_relicense', 'ELIMINATE',
                ['GPL-2.0'], 'GPL-2.0 requires same license for derivatives.').
warning('GPL-2.0', 'GPL-2.0 is incompatible with Apache-2.0. Consider GPL-3.0.') :-
    fact(commercial_use),
    patent,
    assert_step('B11', 'warn_GPL2_apache_incompat', 'WARN',
                ['GPL-2.0'], 'GPL-2.0 cannot be combined with Apache-2.0 code.').
warning('GPL-2.0', 'SaaS does not trigger GPL copyleft. Consider AGPL-3.0.') :-
    saas,
    copyleft,
    assert_step('B12', 'warn_GPL2_saas_loophole', 'WARN',
                ['GPL-2.0'], 'GPL-2.0 copyleft only applies on distribution, not network use.').

% --- EUPL-1.2 ---
recommend('EUPL-1.2') :-
    copyleft,
    \+ fact(closed_source),
    assert_step('B13', 'recommend_EUPL_if_copyleft', 'RECOMMEND',
                ['EUPL-1.2'], 'EUPL-1.2 is a strong copyleft license compatible with EU law and GPL.').
recommend('EUPL-1.2') :-
    fact(project_type(software)),
    fact(concerned_about_legal_recognition),
    assert_step('B14', 'recommend_EUPL_if_EU_legal', 'RECOMMEND',
                ['EUPL-1.2'], 'EUPL-1.2 is recognised by EU law and explicitly addresses copyleft scope.').
eliminate('EUPL-1.2') :-
    fact(closed_source),
    assert_step('B15', 'eliminate_EUPL_if_closed_source', 'ELIMINATE',
                ['EUPL-1.2'], 'EUPL-1.2 requires source disclosure, incompatible with closed source.').

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
    assert_step('C02', 'warn_LGPL_static_linking', 'WARN',
                ['LGPL-2.1'], 'Dynamic linking is safer for proprietary apps.').

% --- MPL-2.0 ---
recommend('MPL-2.0') :-
    fact(want_file_copyleft),
    \+ fact(closed_source),
    assert_step('C03', 'recommend_MPL_if_file_copyleft', 'RECOMMEND',
                ['MPL-2.0'], 'MPL-2.0 uses file-level copyleft – only modified files must stay open.').

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
% E. Specialized / Boost / Perl licenses
% ============================================================

% --- BSL-1.0 ---
recommend('BSL-1.0') :-
    fact(closed_source),
    assert_step('G01', 'recommend_BSL_if_closed_source', 'RECOMMEND',
                ['BSL-1.0'], 'BSL-1.0 is a permissive license requiring only retention of license notice.').
recommend('BSL-1.0') :-
    fact(project_type(library)),
    fact(want_simple_permissive),
    assert_step('G02', 'recommend_BSL_if_library_permissive', 'RECOMMEND',
                ['BSL-1.0'], 'BSL-1.0 is popular in the C++ Boost community and very permissive.').
warning('BSL-1.0', 'BSL-1.0 has an executable name change requirement in modified versions.') :-
    fact(modify_library),
    assert_step('G03', 'warn_BSL_name_change', 'WARN',
                ['BSL-1.0'], 'Modified versions must rename executables per BSL-1.0.').

% --- Artistic-2.0 ---
recommend('Artistic-2.0') :-
    fact(project_type(software)),
    fact(want_simple_permissive),
    assert_step('G04', 'recommend_Artistic_if_permissive', 'RECOMMEND',
                ['Artistic-2.0'], 'Artistic-2.0 allows distribution with modification under certain conditions.').
warning('Artistic-2.0', 'Artistic-2.0 has a copyleft option for modified standard versions.') :-
    fact(closed_source),
    assert_step('G05', 'warn_Artistic_copyleft_option', 'WARN',
                ['Artistic-2.0'], 'Modified standard versions must be shared under Artistic-2.0.').

% --- PostgreSQL ---
recommend('PostgreSQL') :-
    fact(closed_source),
    assert_step('G06', 'recommend_PostgreSQL_if_closed_source', 'RECOMMEND',
                ['PostgreSQL'], 'PostgreSQL license is very permissive, similar to MIT.').
recommend('PostgreSQL') :-
    fact(project_type(software)),
    fact(want_simple_permissive),
    assert_step('G07', 'recommend_PostgreSQL_if_simple', 'RECOMMEND',
                ['PostgreSQL'], 'PostgreSQL license is simple and permissive, widely used for databases.').

% ============================================================
% E. General elimination rules (copyleft when private mods wanted)
% ============================================================

copyleft_license('GPL-2.0').
copyleft_license('GPL-3.0').
copyleft_license('AGPL-3.0').

eliminate(License) :-
    copyleft_license(License),
    private_mods,
    assert_step('E01', 'exclude_copyleft_if_private_mods', 'ELIMINATE',
                ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0'], 'GPL and AGPL require source sharing of derivatives.').

% ============================================================
% F. Generic metadata-based rules
% ============================================================
% These rules check license metadata (conditions, permissions, limitations)
% that are asserted dynamically by Python for any license.

:- dynamic license_condition/2.
:- dynamic license_permission/2.
:- dynamic license_limitation/2.

% Elimination rules based on metadata
eliminate(License) :-
    license_condition(License, disclose_source),
    fact(closed_source),
    assert_step('F01', 'metadata_disclose_source_vs_closed', 'ELIMINATE',
                [License], 'License requires source disclosure but project is closed-source.').

eliminate(License) :-
    license_condition(License, same_license),
    fact(wants_relicense),
    assert_step('F02', 'metadata_same_license_vs_relicense', 'ELIMINATE',
                [License], 'License requires same-license derivatives but user wants to relicense.').

eliminate(License) :-
    license_condition(License, net_copyleft),
    fact(saas),
    fact(closed_source),
    assert_step('F03', 'metadata_net_copyleft_saas', 'ELIMINATE',
                [License], 'License has network copyleft incompatible with closed-source SaaS.').

eliminate(License) :-
    \+ license_permission(License, commercial_use),
    fact(commercial_use),
    assert_step('F04', 'metadata_no_commercial', 'ELIMINATE',
                [License], 'License does not grant commercial use permission.').

% Warning rules based on metadata
warning(License, 'No patent grant - consider Apache-2.0.') :-
    license_limitation(License, patent_use),
    fact(need_patent_protection),
    assert_step('F05', 'metadata_no_patent', 'WARN',
                [License], 'License offers no patent protection.').

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

get_question_explanation(Fact, Explanation) :-
    ( fact_explanation(Fact, Explanation) -> true
    ; Explanation = 'This question helps narrow down compatible licenses.'
    ).
