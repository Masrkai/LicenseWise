"""Shared utilities for LicenseWise interface modules."""

from __future__ import annotations

import json
from typing import Any

from ..config import QUESTIONS_PATH, SUGGESTIONS_PATH
from ..Data.families_merger import get_all_licenses


def yes_no_to_bool(value: str) -> bool | None:
    """
    Convert 'yes'/'no' (or 'y'/'n') to boolean.
    Returns None for any other value (including 'skip').
    """
    if value is None:
        return None
    v = str(value).strip().lower()
    if v in ("yes", "y"):
        return True
    if v in ("no", "n"):
        return False
    return None


def distribute_to_closed_source(distribute: bool | None) -> bool | None:
    """
    Convert distribution answer to closed_source fact.
    closed_source = not distribute, with None propagation.
    """
    if distribute is None:
        return None
    return not distribute


def apply_closed_source_derivation(facts: dict[str, Any]) -> None:
    """Derive closed_source from distribute and remove the raw distribute key."""
    facts["closed_source"] = distribute_to_closed_source(facts.get("distribute"))
    facts.pop("distribute", None)


# ----------------------------------------------------------------------
# Questions loader
# ----------------------------------------------------------------------

_QUESTIONS_CACHE: dict[str, list[dict[str, Any]]] | None = None


def load_questions() -> dict[str, list[dict[str, Any]]]:
    """Load questions from questions.json. Returns dict with 'recommendation' and 'analysis' keys."""
    global _QUESTIONS_CACHE
    if _QUESTIONS_CACHE is None:
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            _QUESTIONS_CACHE = json.load(f)
    return _QUESTIONS_CACHE


# ----------------------------------------------------------------------
# Suggestion engine
# ----------------------------------------------------------------------

def suggest_alternatives(
    violation_text: str, format: str = "plain"
) -> list[str]:
    """
    Suggest alternative licenses based on violation/explanation text.

    Args:
        violation_text: combined violation and explanation text (lowercase)
        format: 'plain' for CLI, 'markdown' for GUI (wraps license IDs in bold)

    Returns:
        Deduplicated list of suggestion strings.
    """
    rules: list[dict[str, Any]] = []
    with open(SUGGESTIONS_PATH, "r", encoding="utf-8") as f:
        rules = json.load(f)
    suggestions: list[str] = []
    seen: set[str] = set()

    for rule in rules:
        if any(kw in violation_text for kw in rule["keywords"]):
            for sugg in rule["suggestions"]:
                if format == "markdown":
                    text = f"**{sugg['id']}** \u2013 {sugg['note']}"
                else:
                    text = f"{sugg['id']} \u2013 {sugg['note']}"
                if text not in seen:
                    suggestions.append(text)
                    seen.add(text)

    return suggestions


# ----------------------------------------------------------------------
# Facts construction for analysis mode
# ----------------------------------------------------------------------


def build_analysis_facts(
    distribute: str | None = None,
    saas: str | None = None,
    commercial_use: str | None = None,
    need_patent: str | None = None,
    wants_relicense: str | None = None,
) -> dict[str, Any]:
    """
    Build a facts dict for backward-chain analysis mode.

    Args:
        distribute: 'yes'/'no'/'skip' string from user input
        saas: 'yes'/'no'/'skip' string
        commercial_use: 'yes'/'no'/'skip' string
        need_patent: 'yes'/'no'/'skip' string
        wants_relicense: 'yes'/'no'/'skip' string

    Returns:
        facts dict ready for backward_chain()
    """
    facts: dict[str, Any] = {}
    dist_bool = yes_no_to_bool(distribute)
    facts["closed_source"] = distribute_to_closed_source(dist_bool)
    facts["saas"] = yes_no_to_bool(saas)
    facts["commercial_use"] = yes_no_to_bool(commercial_use)
    facts["need_patent_protection"] = yes_no_to_bool(need_patent)
    facts["wants_relicense"] = yes_no_to_bool(wants_relicense)
    return facts


# ----------------------------------------------------------------------
# Centralized license dataset loader with caching
# ----------------------------------------------------------------------

_LICENSES_DATA_CACHE: list[dict[str, Any]] | None = None


def get_licenses_data() -> list[dict[str, Any]]:
    """
    Load all license data by merging the family JSON files in Licenses/Families/.
    Results are cached after the first call.
    Raises FileNotFoundError if no license data can be found.
    """
    global _LICENSES_DATA_CACHE
    if _LICENSES_DATA_CACHE is None:
        try:
            _LICENSES_DATA_CACHE = get_all_licenses()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"No license data found. {e}\n"
                "Make sure Licenses/Families/ exists and contains *.json files."
            ) from e

    return _LICENSES_DATA_CACHE
