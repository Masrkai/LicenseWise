"""Centralized paths and configuration for LicenseWise."""

from pathlib import Path

# Root directories
SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent

# Prolog knowledge base
RULES_DIR = SRC_DIR / "Data"
PROLOG_RULES_PATH = RULES_DIR / "license_rules.pl"

# License data
LICENSES_DIR = PROJECT_ROOT / "Licenses"
QUESTIONS_PATH = PROJECT_ROOT / "common" / "questions.json"
SUGGESTIONS_PATH = PROJECT_ROOT / "common" / "suggestions.json"

# Interface
UI_DIR = PROJECT_ROOT / "ui"
