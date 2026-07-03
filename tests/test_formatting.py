"""Tests for interface.formatting utilities."""

from interface.formatting import format_compatibility_result, _format_license_info


class TestFormatCompatibilityResult:
    def test_compatible(self):
        result = {"compatible": True, "violations": [], "explanation": "All good."}
        output = format_compatibility_result(result, "MIT")
        assert "COMPATIBLE" in output
        assert "MIT" in output

    def test_incompatible(self):
        result = {"compatible": False, "violations": ["Source disclosure required"], "explanation": "Not allowed."}
        output = format_compatibility_result(result, "GPL-3.0")
        assert "NOT COMPATIBLE" in output
        assert "Source disclosure required" in output

    def test_unknown(self):
        result = {"compatible": None, "explanation": "Could not determine."}
        output = format_compatibility_result(result, "Unknown-1.0")
        assert "UNCLEAR" in output

    def test_includes_disclaimer(self):
        result = {"compatible": True}
        output = format_compatibility_result(result, "MIT")
        assert "Disclaimer" in output
        assert "legal advice" in output


class TestFormatLicenseInfo:
    def test_basic_info(self):
        lic = {"name": "MIT", "type": "permissive"}
        lines = _format_license_info(lic)
        assert any("MIT" in line for line in lines)
        assert any("Permissive" in line for line in lines)

    def test_permissions(self):
        lic = {
            "name": "MIT",
            "type": "permissive",
            "permissions": {"commercial_use": True, "modification": True},
        }
        lines = _format_license_info(lic)
        output = "\n".join(lines)
        assert "Commercial use" in output
        assert "Modification" in output
