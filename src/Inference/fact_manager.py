"""Fact and metadata management for Prolog inference."""

from typing import Any, Dict, List, Optional, Set


class FactManager:
    """Manages asserting user facts and license metadata into Prolog."""

    def __init__(self, prolog):
        self.prolog = prolog

    def load_facts(self, facts: Dict[str, Any]) -> None:
        """Clear all state and assert user facts into the Prolog knowledge base."""
        list(self.prolog.query("clear_facts, clear_trace, clear_metadata"))
        for key, value in facts.items():
            if value is True:
                self.prolog.assertz(f"fact({key})")

    def assert_license_metadata(self, license_id: str, lic: Dict) -> None:
        """Assert license conditions, permissions, and limitations as Prolog facts."""
        for cond, val in lic.get("conditions", {}).items():
            if val:
                self.prolog.assertz(f"license_condition('{license_id}', '{cond}')")
        for perm, val in lic.get("permissions", {}).items():
            if val:
                self.prolog.assertz(f"license_permission('{license_id}', '{perm}')")
        for lim, val in lic.get("limitations", {}).items():
            if val:
                self.prolog.assertz(f"license_limitation('{license_id}', '{lim}')")
