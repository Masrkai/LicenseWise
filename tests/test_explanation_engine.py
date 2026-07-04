"""Tests for Inference.explanation_engine report generation."""

from unittest.mock import MagicMock

from src.Inference.explanation_engine import (
    format_trace,
    generate_final_report,
    generate_summary,
)
from src.Data.report_templates import (
    NO_LICENSES_RECOMMENDED,
    NO_RULES_FIRED,
    REPORT_HEADER,
)


class FakeVariable:
    """Simulate a PySWIP Variable object for testing."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Variable({self.name})"


class TestGenerateFinalReport:
    def test_with_normal_strings(self):
        wm = {"recommended": {"MIT"}, "eliminated": {"GPL-3.0"}, "warnings": []}
        facts = {"saas": True}
        trace = [{"step": 1, "rule_name": "r1", "action": "RECOMMEND", "explanation": "e"}]
        report = generate_final_report(wm, facts, trace)
        assert "MIT" in report
        assert "GPL-3.0" not in report or "ELIMINATED" in report

    def test_with_mixed_variable_and_string(self):
        wm = {
            "recommended": {"MIT"},
            "eliminated": {"GPL-3.0", FakeVariable("AGPL-3.0")},
            "warnings": [],
        }
        facts = {}
        trace = []
        report = generate_final_report(wm, facts, trace)
        assert REPORT_HEADER in report
        assert "MIT" in report
        assert "AGPL-3.0" in report

    def test_with_all_variable_objects(self):
        wm = {
            "recommended": {FakeVariable("MIT"), FakeVariable("Apache-2.0")},
            "eliminated": {FakeVariable("GPL-3.0")},
            "warnings": [],
        }
        facts = {}
        trace = []
        report = generate_final_report(wm, facts, trace)
        assert "Apache-2.0" in report
        assert "MIT" in report
        assert "GPL-3.0" in report

    def test_empty_working_memory(self):
        wm = {"recommended": set(), "eliminated": set(), "warnings": []}
        facts = {}
        trace = []
        report = generate_final_report(wm, facts, trace)
        assert NO_LICENSES_RECOMMENDED in report

    def test_with_trace_excluded(self):
        wm = {"recommended": {"MIT"}, "eliminated": set(), "warnings": []}
        facts = {"saas": True}
        trace = [{"step": 1, "rule_name": "r1", "action": "RECOMMEND",
                  "explanation": "test explanation", "matched_facts": {}}]
        report = generate_final_report(wm, facts, trace, include_trace=False)
        assert "MIT" in report
        assert "HOW THE ENGINE REACHED" not in report

    def test_with_trace_included_by_default(self):
        wm = {"recommended": {"MIT"}, "eliminated": set(), "warnings": []}
        facts = {"saas": True}
        trace = [{"step": 1, "rule_name": "r1", "action": "RECOMMEND",
                  "explanation": "test explanation", "matched_facts": {}}]
        report = generate_final_report(wm, facts, trace)
        assert "MIT" in report
        assert "HOW THE ENGINE REACHED" in report


class TestFormatTrace:
    def test_empty_trace(self):
        assert format_trace([]) == NO_RULES_FIRED

    def test_single_step(self):
        trace = [
            {
                "step": 1,
                "rule_name": "rec_permissive",
                "action": "RECOMMEND",
                "explanation": "MIT matches criteria",
                "matched_facts": {"saas": True},
            }
        ]
        result = format_trace(trace)
        assert "Step 1" in result
        assert "MIT matches criteria" in result
        assert "Saas: Yes" in result


class TestGenerateSummary:
    def test_with_recommend_and_eliminate(self):
        wm = {"recommended": {"MIT"}, "eliminated": {"GPL-3.0"}, "warnings": []}
        facts = {}
        trace = [
            {"step": 1, "rule_name": "r1", "action": "RECOMMEND", "explanation": "rec reason"},
            {"step": 2, "rule_name": "r2", "action": "ELIMINATE", "explanation": "elim reason"},
        ]
        summary = generate_summary(wm, facts, trace)
        assert "rec reason" in summary
        assert "elim reason" in summary
