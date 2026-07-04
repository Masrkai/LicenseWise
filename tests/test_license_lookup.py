"""Tests for Inference.license_lookup utilities."""

from src.Inference.license_lookup import find_license, get_possible_ids


class TestFindLicense:
    def test_find_by_id(self):
        licenses = [
            {"id": "MIT", "spdx_id": "MIT"},
            {"id": "GPL-3.0", "spdx_id": "GPL-3.0-only"},
        ]
        result = find_license("MIT", licenses)
        assert result is not None
        assert result["id"] == "MIT"

    def test_find_by_spdx_id(self):
        licenses = [
            {"id": "MIT", "spdx_id": "MIT"},
            {"id": "GPL-3.0", "spdx_id": "GPL-3.0-only"},
        ]
        result = find_license("GPL-3.0-only", licenses)
        assert result is not None
        assert result["id"] == "GPL-3.0"

    def test_not_found(self):
        licenses = [{"id": "MIT", "spdx_id": "MIT"}]
        result = find_license("Apache-2.0", licenses)
        assert result is None


class TestGetPossibleIds:
    def test_original_id_always_included(self):
        result = get_possible_ids("MIT", None)
        assert result == {"MIT"}

    def test_includes_spdx_id(self):
        lic = {"id": "GPL-3.0", "spdx_id": "GPL-3.0-only"}
        result = get_possible_ids("GPL-3.0", lic)
        assert "GPL-3.0" in result
        assert "GPL-3.0-only" in result

    def test_no_duplicates(self):
        lic = {"id": "MIT", "spdx_id": "MIT"}
        result = get_possible_ids("MIT", lic)
        assert result == {"MIT"}
