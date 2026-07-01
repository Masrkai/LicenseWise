% ============================================================
% LicenseWise Expert System - Prolog Knowledge Base
% ============================================================
% All rules, helpers, and trace infrastructure.
% License metadata lives in licenses.json (loaded by Python).
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

% --- Unlicense / CC0 ---
recommend(License) :-
    member(License, ['Unlicense', 'CC0-1.0']),
    fact(want_public_domain),
    assert_step('A12', 'recommend_public_domain', 'RECOMMEND',
                ['Unlicense', 'CC0-1.0'], 'Unlicense and CC0 dedicate work to the public domain with no restrictions.').

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

% ============================================================
% C. Weak copyleft / middle-ground
% ============================================================

% --- LGPL ---
recommend('LGPL-2.1') :-
    fact(project_type(library)),
    fact(want_weak_copyleft),
    assert_step('C01', 'recommend_LGPL_for_library', 'RECOMMEND',
                ['LGPL-2.1', 'LGPL-3.0'], 'LGPL keeps the library open but allows proprietary linking.').

recommend('LGPL-3.0') :-
    fact(project_type(library)),
    fact(want_weak_copyleft),
    assert_step('C01', 'recommend_LGPL_for_library', 'RECOMMEND',
                ['LGPL-2.1', 'LGPL-3.0'], 'LGPL keeps the library open but allows proprietary linking.').

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
