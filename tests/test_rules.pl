% ============================================================
% LicenseWise - Prolog Rule Tests
% ============================================================
% Test definitions as Prolog facts. Python wrapper (test_prolog_rules.py)
% loads this file, runs test_case/7, and reports pass/fail.
%
% IMPORTANT: This file does NOT consult license_rules.pl.
% The Python wrapper handles loading the engine and license metadata.
% ============================================================

:- dynamic test_result/3.
:- dynamic license_data_loaded/0.
:- dynamic license_entry/7.

% ============================================================
% Test case definitions
% ============================================================
% test_case(Id, Description, SetupFacts, ExpectedRecommended, ExpectedEliminated, ExpectedWarningPatterns, UntestedRules)
%
% License IDs must match the JSON exactly: 'MIT', 'Apache-2.0', etc.
% Atoms with special chars (hyphens, dots) MUST be single-quoted.

% --- A. Permissive rules ---

test_case(tc_a01, 'Permissive recommended when closed_source',
    [closed_source],
    ['MIT', 'Apache-2.0', 'BSD-2-Clause', 'ISC'],
    [],
    [],
    ['A01']).

test_case(tc_a02, 'Permissive recommended when saas',
    [saas],
    ['MIT', 'Apache-2.0', 'BSD-2-Clause'],
    [],
    [],
    ['A02']).

test_case(tc_a03, 'Permissive recommended when want_simple_permissive',
    [want_simple_permissive],
    ['MIT', 'BSD-2-Clause', 'ISC'],
    [],
    [],
    ['A03']).

test_case(tc_a04, 'Patent grant license recommended when need_patent_protection',
    [need_patent_protection],
    ['Apache-2.0'],
    [],
    [],
    ['A04']).

test_case(tc_a05a, 'Unlicense recommended when want_public_domain',
    [want_public_domain],
    ['Unlicense'],
    [],
    [],
    ['A05a']).

test_case(tc_a05b, 'CC0 recommended when want_public_domain',
    [want_public_domain],
    ['CC0-1.0'],
    [],
    [],
    ['A05b']).

test_case(tc_a06, 'Unlicense jurisdiction warning when want_public_domain',
    [want_public_domain],
    [],
    [],
    ['legally recognised'],
    ['A06']).

% --- B. Copyleft rules ---

test_case(tc_b01, 'Copyleft recommended when want_copyleft + not closed + not saas',
    [want_copyleft, commercial_use],
    ['GPL-2.0', 'GPL-3.0'],
    [],
    [],
    ['B01']).

test_case(tc_b02, 'Network copyleft recommended when saas + want_copyleft',
    [saas, want_copyleft, commercial_use],
    ['AGPL-3.0'],
    [],
    [],
    ['B02']).

test_case(tc_b03, 'Copyleft + saas loophole warning',
    [saas, want_copyleft, commercial_use],
    [],
    [],
    ['SaaS does not trigger'],
    ['B03']).

% --- C. Weak copyleft rules ---

test_case(tc_c01a, 'LGPL-2.1 recommended for library + weak_copyleft',
    [project_type(library), want_weak_copyleft],
    ['LGPL-2.1'],
    [],
    [],
    ['C01a']).

test_case(tc_c01b, 'LGPL-3.0 recommended for library + weak_copyleft',
    [project_type(library), want_weak_copyleft],
    ['LGPL-3.0'],
    [],
    [],
    ['C01b']).

test_case(tc_c02a, 'LGPL-2.1 static linking warning',
    [project_type(library), want_weak_copyleft, linking_type(static)],
    [],
    [],
    ['Static linking'],
    ['C02a']).

test_case(tc_c02b, 'LGPL-3.0 static linking warning',
    [project_type(library), want_weak_copyleft, linking_type(static)],
    [],
    [],
    ['Static linking'],
    ['C02b']).

test_case(tc_c03, 'MPL-2.0 recommended for file_copyleft',
    [want_file_copyleft, commercial_use],
    ['MPL-2.0'],
    [],
    [],
    ['C03']).

test_case(tc_c04, 'MPL-2.0 recommended for mixed_open_proprietary',
    [mixed_open_proprietary],
    ['MPL-2.0'],
    [],
    [],
    ['C04']).

% --- D. Content rules ---

test_case(tc_d01, 'CC-BY-NC-4.0 recommended for content + noncommercial',
    [project_type(content), commercial_use(no)],
    ['CC-BY-NC-4.0'],
    [],
    [],
    ['D01']).

test_case(tc_d02, 'CC-BY-NC-4.0 eliminated for commercial',
    [project_type(content), commercial_use],
    [],
    ['CC-BY-NC-4.0'],
    [],
    ['D02']).

test_case(tc_d03, 'CC-BY-4.0 recommended for content + commercial',
    [project_type(content), commercial_use],
    ['CC-BY-4.0'],
    [],
    [],
    ['D03']).

test_case(tc_d04, 'CC-BY-4.0 recommended for content + simple_permissive',
    [project_type(content), want_simple_permissive],
    ['CC-BY-4.0'],
    [],
    [],
    ['D04']).

test_case(tc_d05, 'CC-BY-SA-4.0 recommended for content + copyleft + commercial',
    [project_type(content), want_copyleft, commercial_use],
    ['CC-BY-SA-4.0'],
    [],
    [],
    ['D05']).

test_case(tc_d06, 'CC-BY-SA-4.0 recommended for content + copyleft + noncommercial',
    [project_type(content), want_copyleft, commercial_use(no)],
    ['CC-BY-SA-4.0'],
    [],
    [],
    ['D06']).

test_case(tc_d07, 'ODbL recommended for content + copyleft',
    [project_type(content), want_copyleft, commercial_use],
    ['ODbL'],
    [],
    [],
    ['D07']).

% --- E. User preference rules ---

test_case(tc_e07, 'Attribution license recommended when wants_attribution',
    [wants_attribution, commercial_use],
    ['MIT', 'Apache-2.0', 'BSD-2-Clause'],
    [],
    [],
    ['E07']).

test_case(tc_e09, 'No-attribution license recommended when wants_attribution(no)',
    [wants_attribution(no)],
    ['Unlicense', 'CC0-1.0', 'MIT-0'],
    [],
    [],
    ['E09']).

test_case(tc_e12, 'Apache-2.0 recommended for patent_retaliation',
    [wants_patent_retaliation],
    ['Apache-2.0'],
    [],
    [],
    ['E12']).

test_case(tc_e13, 'MPL-2.0 recommended for patent_retaliation',
    [wants_patent_retaliation],
    ['MPL-2.0'],
    [],
    [],
    ['E13']).

test_case(tc_e13b, 'EPL-2.0 recommended for patent_retaliation',
    [wants_patent_retaliation, eclipse_project],
    ['EPL-2.0'],
    [],
    [],
    ['E13b']).

test_case(tc_e14, 'Copyleft recommended for dual_licensing',
    [dual_licensing, commercial_use],
    ['GPL-2.0', 'GPL-3.0'],
    [],
    [],
    ['E14']).

test_case(tc_e15, 'Dual licensing CLA warning',
    [dual_licensing, commercial_use],
    [],
    [],
    ['CLA'],
    ['E15']).

% --- F. Metadata rules ---

test_case(tc_f04, 'Non-commercial license eliminated when commercial_use',
    [commercial_use],
    [],
    ['CC-BY-NC-4.0', 'CC-BY-NC-SA-4.0'],
    [],
    ['F04']).

test_case(tc_f06, 'Document-changes license eliminated when want_no_document_changes',
    [want_no_document_changes, commercial_use],
    [],
    ['Apache-2.0', 'GPL-2.0', 'GPL-3.0', 'LGPL-2.1', 'LGPL-3.0', 'MPL-2.0', 'Zlib'],
    [],
    ['F06']).

test_case(tc_f07, 'Document-changes warning when want_no_document_changes(no)',
    [want_no_document_changes(no), commercial_use],
    [],
    [],
    ['documenting changes'],
    ['F07']).

test_case(tc_f08, 'Non-OSI license eliminated when prefer_osi_approved',
    [prefer_osi_approved, commercial_use],
    [],
    ['BSL-1.0', 'Elastic-2.0', 'Proprietary', 'CC-BY-NC-4.0', 'CC-BY-4.0',
     'CC-BY-SA-4.0', 'CC-BY-NC-SA-4.0', 'CC0-1.0', 'ODbL'],
    [],
    ['F08']).

test_case(tc_f09, 'Non-FSF license eliminated when prefer_fsf_free',
    [prefer_fsf_free, commercial_use],
    [],
    ['BSL-1.0', 'Elastic-2.0', 'Proprietary', 'CC-BY-NC-4.0', 'CC-BY-4.0',
     'CC-BY-SA-4.0', 'CC-BY-NC-SA-4.0'],
    [],
    ['F09']).

% --- G. Niche license rules ---

test_case(tc_g04a, 'Artistic-2.0 eliminated unless perl_project',
    [commercial_use],
    [],
    ['Artistic-2.0'],
    [],
    ['G04a']).

test_case(tc_g04b, 'PostgreSQL eliminated unless postgresql_project',
    [commercial_use],
    [],
    ['PostgreSQL'],
    [],
    ['G04b']).

test_case(tc_g04c, 'CDDL-1.0 eliminated unless zfs_project',
    [commercial_use],
    [],
    ['CDDL-1.0'],
    [],
    ['G04c']).

test_case(tc_g04d, 'EPL-2.0 eliminated unless eclipse_project',
    [commercial_use],
    [],
    ['EPL-2.0'],
    [],
    ['G04d']).

% --- I. Contradiction rules ---

test_case(tc_i01, 'Public domain + copyleft contradiction warning',
    [want_public_domain, want_copyleft],
    [],
    [],
    ['conflict'],
    ['I01']).

test_case(tc_i02, 'Public domain + non-commercial contradiction warning',
    [want_public_domain, commercial_use(no)],
    [],
    [],
    ['conflict'],
    ['I02']).

% --- Combined scenarios ---

test_case(tc_combo_01, 'Closed source + SaaS eliminates copyleft and AGPL',
    [closed_source, saas, commercial_use],
    ['MIT', 'Apache-2.0'],
    ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0', 'LGPL-2.1', 'LGPL-3.0'],
    [],
    []).

test_case(tc_combo_02, 'File copyleft + no doc changes eliminates MPL',
    [want_file_copyleft, want_no_document_changes, commercial_use],
    [],
    ['MPL-2.0'],
    [],
    []).

test_case(tc_combo_03, 'Academic + copyleft does not recommend BSD',
    [academic_project, want_copyleft, commercial_use],
    ['GPL-2.0', 'GPL-3.0'],
    [],
    [],
    []).

test_case(tc_combo_04, 'Patent protection + copyleft + OSI',
    [need_patent_protection, want_copyleft, prefer_osi_approved, commercial_use],
    ['GPL-3.0', 'Apache-2.0', 'MPL-2.0'],
    [],
    [],
    []).

% ============================================================
% Test runner
% ============================================================

% Run a single test case - returns Passed, Message as separate variables
run_test(Id, Passed, Message) :-
    test_case(Id, Desc, Facts, ExpectedRec, ExpectedElim, ExpectedWarnPatterns, _),
    clear_facts,
    clear_trace,
    assert_setup_facts(Facts),
    findall(L, recommend(L), RecRaw),
    findall(L, eliminate(L), ElimRaw),
    findall(Msg, warning(_, Msg), WarnRaw),
    list_to_set(RecRaw, RecSet),
    list_to_set(ElimRaw, ElimSet),
    subtract(RecSet, ElimSet, Rec),
    check_expected_items(Rec, ExpectedRec, 'recommended', RecMsg),
    check_expected_items(ElimSet, ExpectedElim, 'eliminated', ElimMsg),
    check_warning_patterns(WarnRaw, ExpectedWarnPatterns, WarnMsg),
    ( RecMsg == '' , ElimMsg == '' , WarnMsg == '' ->
        Passed = true,
        format(atom(Message), 'PASS: ~w', [Desc])
    ;
        Passed = false,
        format(atom(Message), 'FAIL: ~w~n  Rec: ~w~n  Elim: ~w~n  Warn: ~w',
               [Desc, RecMsg, ElimMsg, WarnMsg])
    ).

% ============================================================
% Helpers
% ============================================================

assert_setup_facts([]).
assert_setup_facts([F|Rest]) :-
    assertz(fact(F)),
    assert_setup_facts(Rest).

check_expected_items(_, [], _, '').
check_expected_items(Actual, [Expected|Rest], Category, Msg) :-
    ( member(Expected, Actual) ->
        check_expected_items(Actual, Rest, Category, Msg)
    ;
        format(atom(M1), '~w missing from ~w', [Expected, Category]),
        check_expected_items(Actual, Rest, Category, M2),
        ( M2 == '' ->
            Msg = M1
        ;
            format(atom(Msg), '~w; ~w', [M1, M2])
        )
    ).

check_warning_patterns(_, [], '').
check_warning_patterns(Warnings, [Pattern|Rest], Msg) :-
    ( any_contains(Warnings, Pattern) ->
        check_warning_patterns(Warnings, Rest, Msg)
    ;
        format(atom(M1), 'No warning containing "~w"', [Pattern]),
        check_warning_patterns(Warnings, Rest, M2),
        ( M2 == '' ->
            Msg = M1
        ;
            format(atom(Msg), '~w; ~w', [M1, M2])
        )
    ).

any_contains([], _) :- fail.
any_contains([H|T], Sub) :-
    ( sub_string(H, _, _, _, Sub) ->
        true
    ;
        any_contains(T, Sub)
    ).

% Get all tested rule IDs for coverage check
get_tested_rules(RuleIds) :-
    findall(R, test_case(_, _, _, _, _, _, R), Nested),
    flatten(Nested, RuleIds).

% Check rule coverage
check_coverage(Missing) :-
    get_tested_rules(Tested),
    list_to_set(Tested, TestedSet),
    Required = ['A01', 'A02', 'A03', 'A04', 'A05a', 'A05b', 'A06',
                'B01', 'B02', 'B03',
                'C01a', 'C01b', 'C02a', 'C02b', 'C03', 'C04',
                'D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07',
                'E07', 'E09', 'E12', 'E13', 'E13b', 'E14', 'E15',
                'F04', 'F06', 'F07', 'F08', 'F09',
                'G04a', 'G04b', 'G04c', 'G04d',
                'I01', 'I02'],
    subtract(Required, TestedSet, Missing).
