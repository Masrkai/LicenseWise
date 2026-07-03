"""License metadata lookup utilities."""

from typing import Any, Dict, List, Optional, Set


def find_license(license_id: str, licenses_data: List[Dict]) -> Optional[Dict]:
    """Find a license dict by id or spdx_id."""
    return next(
        (lic for lic in licenses_data
         if lic.get("id") == license_id or lic.get("spdx_id") == license_id),
        None,
    )


def get_possible_ids(license_id: str, lic: Optional[Dict]) -> Set[str]:
    """Build set of possible IDs to check (original + spdx variants)."""
    ids = {license_id}
    if lic:
        if lic.get("id"):
            ids.add(lic["id"])
        if lic.get("spdx_id"):
            ids.add(lic["spdx_id"])
    return ids
