"""Shared utilities for LicenseWise interface modules."""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import QUESTIONS_PATH, SUGGESTIONS_PATH, LICENSES_DIR


def yes_no_to_bool(value: str) -> Optional[bool]:
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


def distribute_to_closed_source(distribute: Optional[bool]) -> Optional[bool]:
    """
    Convert distribution answer to closed_source fact.
    closed_source = not distribute, with None propagation.
    """
    if distribute is None:
        return None
    return not distribute


def apply_closed_source_derivation(facts: Dict[str, Any]) -> None:
    """Derive closed_source from distribute and remove the raw distribute key."""
    facts["closed_source"] = distribute_to_closed_source(facts.get("distribute"))
    facts.pop("distribute", None)


# ----------------------------------------------------------------------
# Questions loader
# ----------------------------------------------------------------------

_QUESTIONS_CACHE = None


def load_questions() -> Dict[str, List[Dict]]:
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
) -> List[str]:
    """
    Suggest alternative licenses based on violation/explanation text.

    Args:
        violation_text: combined violation and explanation text (lowercase)
        format: 'plain' for CLI, 'markdown' for GUI (wraps license IDs in bold)

    Returns:
        Deduplicated list of suggestion strings.
    """
    rules = []
    with open(SUGGESTIONS_PATH, "r", encoding="utf-8") as f:
        rules = json.load(f)
    suggestions = []
    seen = set()

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
    distribute: Optional[str] = None,
    saas: Optional[str] = None,
    commercial_use: Optional[str] = None,
    need_patent: Optional[str] = None,
    wants_relicense: Optional[str] = None,
) -> Dict[str, Any]:
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
    facts = {}
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

_LICENSES_DATA_CACHE = None


def load_licenses_from_json(json_path: Path) -> List[Dict[str, Any]]:
    """Load licenses from a single merged JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("licenses", [])


def load_all_licenses(licenses_dir: Path) -> List[Dict[str, Any]]:
    """Load all JSON files from the Licenses/ directory and return a list of license dicts."""
    all_licenses = []
    for json_file in licenses_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            licenses = data.get("licenses", [])
            all_licenses.extend(licenses)
    return all_licenses


def get_licenses_data() -> List[Dict[str, Any]]:
    """
    Load all license data. Tries multiple strategies:
    1. Look for licenses.json in Licenses/ directory
    2. Load all *.json files from Licenses/ directory

    Results are cached after the first call.
    Raises FileNotFoundError if no license data can be found.
    """
    global _LICENSES_DATA_CACHE
    if _LICENSES_DATA_CACHE is None:
        # Strategy 1: Check for licenses.json in Licenses/ directory
        licenses_json = LICENSES_DIR / "licenses.json"
        if licenses_json.exists():
            _LICENSES_DATA_CACHE = load_licenses_from_json(licenses_json)
            return _LICENSES_DATA_CACHE

        # Strategy 2: Load all *.json files from Licenses/ directory
        if LICENSES_DIR.exists():
            _LICENSES_DATA_CACHE = load_all_licenses(LICENSES_DIR)
            if _LICENSES_DATA_CACHE:
                return _LICENSES_DATA_CACHE

        # No license data found
        raise FileNotFoundError(
            f"No license data found. Tried:\n"
            f"  1. {licenses_json}\n"
            f"  2. *.json files in {LICENSES_DIR}\n"
            "Make sure at least one of these exists."
        )

    return _LICENSES_DATA_CACHE
