"""Trace building for Prolog inference steps."""

from __future__ import annotations

from typing import Any


class TraceBuilder:
    """Builds reasoning traces from Prolog step facts."""

    def __init__(self, prolog: Any) -> None:
        self.prolog = prolog

    def build_trace(self) -> list[dict[str, Any]]:
        """Query step/6 facts and build trace preserving original format."""
        return [
            {
                "step": idx + 1,
                "rule_id": sol["Id"],
                "rule_name": sol["Name"],
                "matched_facts": {f: True for f in sol["Facts"]},
                "explanation": sol["Explanation"],
                "action": sol["Type"],
                "licenses_affected": sol["Affected"],
            }
            for idx, sol in enumerate(
                self.prolog.query("step(Id, Name, Type, Facts, Affected, Explanation)")
            )
        ]
