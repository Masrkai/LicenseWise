"""Shared utilities for LicenseWise interface modules."""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any

# ----------------------------------------------------------------------
# Constants for UI consistency
# ----------------------------------------------------------------------
YES_NO_SKIP_CHOICES = ["yes", "no", "skip"]
SKIP_VALUE = "skip"


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
    1. Look for licenses.json in project root
    2. Look for licenses.json in Licenses/ directory
    3. Load all *.json files from Licenses/ directory

    Results are cached after the first call.
    Raises FileNotFoundError if no license data can be found.
    """
    global _LICENSES_DATA_CACHE
    if _LICENSES_DATA_CACHE is None:
        # This file is in interface/ -> parent.parent = project root
        project_root = Path(__file__).parent.parent

        # Strategy 1: Check for licenses.json in project root
        root_licenses_json = project_root / "licenses.json"
        if root_licenses_json.exists():
            _LICENSES_DATA_CACHE = load_licenses_from_json(root_licenses_json)
            return _LICENSES_DATA_CACHE

        # Strategy 2: Check for licenses.json in Licenses/ directory
        licenses_dir = project_root / "Licenses"
        licenses_json = licenses_dir / "licenses.json"
        if licenses_json.exists():
            _LICENSES_DATA_CACHE = load_licenses_from_json(licenses_json)
            return _LICENSES_DATA_CACHE

        # Strategy 3: Load all *.json files from Licenses/ directory
        if licenses_dir.exists():
            _LICENSES_DATA_CACHE = load_all_licenses(licenses_dir)
            if _LICENSES_DATA_CACHE:
                return _LICENSES_DATA_CACHE

        # No license data found
        raise FileNotFoundError(
            f"No license data found. Tried:\n"
            f"  1. {root_licenses_json}\n"
            f"  2. {licenses_json}\n"
            f"  3. *.json files in {licenses_dir}\n"
            "Make sure at least one of these exists."
        )

    return _LICENSES_DATA_CACHE
