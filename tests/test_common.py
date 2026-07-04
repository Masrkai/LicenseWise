"""Tests for interface.common utilities."""

from src.interface.common import (
    yes_no_to_bool,
    distribute_to_closed_source,
    apply_closed_source_derivation,
)


class TestYesNoToBool:
    def test_yes_variants(self):
        assert yes_no_to_bool("yes") is True
        assert yes_no_to_bool("y") is True
        assert yes_no_to_bool("YES") is True
        assert yes_no_to_bool("Yes") is True

    def test_no_variants(self):
        assert yes_no_to_bool("no") is False
        assert yes_no_to_bool("n") is False
        assert yes_no_to_bool("NO") is False

    def test_skip_returns_none(self):
        assert yes_no_to_bool("skip") is None
        assert yes_no_to_bool("") is None
        assert yes_no_to_bool(None) is None

    def test_unknown_returns_none(self):
        assert yes_no_to_bool("maybe") is None
        assert yes_no_to_bool("123") is None


class TestDistributeToClosedSource:
    def test_distribute_true(self):
        assert distribute_to_closed_source(True) is False

    def test_distribute_false(self):
        assert distribute_to_closed_source(False) is True

    def test_distribute_none(self):
        assert distribute_to_closed_source(None) is None


class TestApplyClosedSourceDerivation:
    def test_removes_distribute_and_sets_closed_source(self):
        facts = {"distribute": True}
        apply_closed_source_derivation(facts)
        assert facts == {"closed_source": False}

    def test_none_distribute(self):
        facts = {"distribute": None}
        apply_closed_source_derivation(facts)
        assert facts == {"closed_source": None}

    def test_preserves_other_facts(self):
        facts = {"distribute": False, "saas": True}
        apply_closed_source_derivation(facts)
        assert facts == {"closed_source": True, "saas": True}
