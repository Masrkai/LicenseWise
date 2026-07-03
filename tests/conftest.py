"""Shared test fixtures for LicenseWise tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_facts():
    """Sample user facts for testing."""
    return {
        "closed_source": True,
        "saas": False,
        "commercial_use": True,
        "need_patent_protection": False,
        "wants_relicense": False,
    }


@pytest.fixture
def sample_license():
    """Sample license metadata for testing."""
    return {
        "id": "MIT",
        "spdx_id": "MIT",
        "name": "MIT License",
        "type": "permissive",
        "description": "A permissive license.",
        "permissions": {
            "commercial_use": True,
            "modification": True,
            "distribution": True,
            "private_use": True,
        },
        "conditions": {
            "include_copyright": True,
            "include_license": True,
        },
        "limitations": {
            "liability": True,
            "warranty": True,
        },
    }


@pytest.fixture
def mock_prolog():
    """Mock Prolog instance for testing without SWI-Prolog."""
    mock = MagicMock()
    mock.query.return_value = []
    return mock
