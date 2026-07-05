"""Pytest wrapper for Prolog rule tests defined in test_rules.pl.

The test logic lives entirely in Prolog (tests/test_rules.pl).
This file is a thin Python wrapper that:
1. Loads the PrologEngine (which consults license_rules.pl)
2. Consults test_rules.pl (test case definitions + runner predicates)
3. Asserts license metadata from JSON into Prolog
4. Runs run_all_tests/1 and parses results into pytest assertions
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from src.Inference.prolog_engine import PrologEngine
from src.interface.common import get_licenses_data

TESTS_DIR = Path(__file__).parent
TEST_RULES_PL = str(TESTS_DIR / "test_rules.pl")


@pytest.fixture(scope="session")
def prolog_engine() -> PrologEngine:
    """Session-scoped Prolog engine. Loads license_rules.pl once."""
    return PrologEngine()


@pytest.fixture(scope="session")
def license_data() -> list[dict[str, Any]]:
    """Session-scoped license metadata from JSON files."""
    return get_licenses_data()


@pytest.fixture(scope="session")
def prolog_test_results(
    prolog_engine: PrologEngine,
    license_data: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run all Prolog test cases and return structured results.

    Returns dict with keys:
        cases: dict mapping test_id -> {passed, description, message}
        passed_count: int
        failed_count: int
        tested_rules: list of rule IDs covered
        missing_rules: list of rule IDs not yet tested
    """
    pro = prolog_engine.prolog

    # Consult test_rules.pl (test definitions + runner)
    pro.consult(TEST_RULES_PL)

    # Assert license metadata into Prolog so rules can fire
    for lic in license_data:
        lid = lic.get("id")
        if lid:
            prolog_engine.fact_manager.assert_license_metadata(lid, lic)

    # Collect all test case IDs from the Prolog file
    test_ids: list[str] = []
    for sol in pro.query("test_case(Id, _, _, _, _, _, _)"):
        test_ids.append(str(sol["Id"]))

    # Run each test individually
    results: list[dict[str, Any]] = []
    for tid in test_ids:
        query = f"run_test({tid}, Passed, Message)"
        for sol in pro.query(query):
            passed = sol["Passed"] is True or str(sol["Passed"]) == "true"
            message = str(sol["Message"])
            results.append({
                "id": tid,
                "passed": passed,
                "message": message,
            })

    cases = {r["id"]: r for r in results}
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = sum(1 for r in results if not r["passed"])

    # Get coverage info
    tested_rules: list[str] = []
    for sol in pro.query("get_tested_rules(R)"):
        tested_rules = [str(r) for r in sol["R"]]

    missing_rules: list[str] = []
    for sol in pro.query("check_coverage(Missing)"):
        missing_rules = [str(m) for m in sol["Missing"]]

    return {
        "cases": cases,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "tested_rules": tested_rules,
        "missing_rules": missing_rules,
    }


# ============================================================
# Parametrized test: one per test_case in test_rules.pl
# ============================================================

# All test case IDs defined in test_rules.pl
TEST_IDS = [
    # A. Permissive rules
    "tc_a01", "tc_a02", "tc_a03", "tc_a04", "tc_a05a", "tc_a05b", "tc_a06",
    # B. Copyleft rules
    "tc_b01", "tc_b02", "tc_b03",
    # C. Weak copyleft rules
    "tc_c01a", "tc_c01b", "tc_c02a", "tc_c02b", "tc_c03", "tc_c04",
    # D. Content rules
    "tc_d01", "tc_d02", "tc_d03", "tc_d04", "tc_d05", "tc_d06", "tc_d07",
    # E. User preference rules
    "tc_e07", "tc_e09", "tc_e12", "tc_e13", "tc_e13b", "tc_e14", "tc_e15",
    # F. Metadata rules
    "tc_f04", "tc_f06", "tc_f07", "tc_f08", "tc_f09",
    # G. Niche license rules
    "tc_g04a", "tc_g04b", "tc_g04c", "tc_g04d",
    # I. Contradiction rules
    "tc_i01", "tc_i02",
    # Combined scenarios
    "tc_combo_01", "tc_combo_02", "tc_combo_03", "tc_combo_04",
]


@pytest.mark.parametrize("test_id", TEST_IDS)
def test_prolog_rule(
    test_id: str,
    prolog_test_results: dict[str, Any],
) -> None:
    """Run a single Prolog test case defined in test_rules.pl."""
    cases = prolog_test_results["cases"]
    assert test_id in cases, f"Test case {test_id} not found in Prolog results"

    result = cases[test_id]
    assert result["passed"], result["message"]


def test_rule_coverage(
    prolog_test_results: dict[str, Any],
    request: pytest.FixtureRequest,
) -> None:
    """Verify that all major rule sections have at least one test."""
    missing = prolog_test_results["missing_rules"]
    assert not missing, f"Untested rule sections: {missing}"


def test_all_tests_passed(
    prolog_test_results: dict[str, Any],
) -> None:
    """Final summary: ensure all Prolog test cases passed."""
    passed = prolog_test_results["passed_count"]
    failed = prolog_test_results["failed_count"]
    total = passed + failed
    assert failed == 0, f"{failed}/{total} Prolog tests failed"
