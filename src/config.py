"""Centralized paths and configuration for LicenseWise."""

from pathlib import Path

# Root directories
SRC_DIR: Path = Path(__file__).parent
PROJECT_ROOT: Path = SRC_DIR.parent

# Prolog knowledge base
RULES_DIR: Path = SRC_DIR / "Data"
PROLOG_RULES_PATH: Path = RULES_DIR / "license_rules.pl"

# License data
LICENSES_DIR: Path = PROJECT_ROOT / "Licenses"
QUESTIONS_PATH: Path = PROJECT_ROOT / "common" / "questions.json"
SUGGESTIONS_PATH: Path = PROJECT_ROOT / "common" / "suggestions.json"

# Interface
UI_DIR: Path = SRC_DIR / "interface" / "ui"
