"""Centralized paths and configuration for LicenseWise."""

from pathlib import Path

# Root directories
SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent

# Prolog knowledge base
RULES_DIR = SRC_DIR / "Rules"
PROLOG_RULES_PATH = RULES_DIR / "license_rules.pl"

# License data
LICENSES_DIR = SRC_DIR / "Licenses"
QUESTIONS_PATH = LICENSES_DIR / "questions.json"
SUGGESTIONS_PATH = LICENSES_DIR / "suggestions.json"

# Interface
UI_DIR = SRC_DIR / "interface" / "ui"
