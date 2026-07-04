"""
families_merger
---------------
Reads every JSON file in the Families/ folder and merges them into a single
licenses JSON object in-memory.  Can be used as a library or run as a CLI
tool to dump the merged result for debugging.

Usage:
    python -m Data.families_merger
"""
import json
from pathlib import Path
from typing import Any

from ..config import LICENSES_DIR

FAMILIES_DIR = LICENSES_DIR / "Families"


def load_families(families_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """
    Load every *.json file from Families/.
    Returns a dict:  { family_name: [license, ...] }
    """
    families: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(families_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)

        # Your provided JSON files use path.stem as the fallback family name
        family_name = data.get("family", path.stem)
        licenses    = data.get("licenses", [])
        families[family_name] = licenses

    return families


def merge(families: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """
    Flatten all family lists into one deduplicated list.
    Deduplication key: spdx_id (falls back to id).
    Each license gets a 'families' list showing which files it appeared in.
    Sorted by popularity_rank ascending (unlisted ones go to the end).
    """
    seen: dict[str, dict[str, Any]] = {}   # spdx_id -> license object

    for family_name, licenses in families.items():
        for lic in licenses:
            key = lic.get("spdx_id") or lic.get("id")
            if key in seen:
                # Already present -- just append this family to its list
                seen[key].setdefault("families", [])
                if family_name not in seen[key]["families"]:
                    seen[key]["families"].append(family_name)
            else:
                entry = dict(lic)
                entry["families"] = [family_name]
                seen[key] = entry

    merged = list(seen.values())

    # Sort by popularity_rank; entries without it sort last
    merged.sort(key=lambda lic: lic.get("metadata", {}).get("popularity_rank") or 9999)
    return merged


def build_output(merged: list[dict[str, Any]], families: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    return {
        "schema_version": "1.5",
        "last_updated": "2026-04-22",
        "source": "https://spdx.org/licenses/",
        "family_files": sorted(families.keys()),
        "total_licenses": len(merged),
        "licenses": merged
    }


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def get_all_licenses(families_dir: Path | None = None) -> list[dict[str, Any]]:
    """
    Merge all family files and return the flat list of license dicts.
    This is the primary entry point for other modules that need
    the combined license dataset.
    """
    d = families_dir or FAMILIES_DIR
    if not d.is_dir():
        raise FileNotFoundError(f"Families directory not found: {d}")

    families = load_families(d)
    if not families:
        return []

    return merge(families)


def get_merged_output(families_dir: Path | None = None) -> dict[str, Any]:
    """
    Return the full merged output dict (with schema metadata wrapping the
    license list).  Useful for debugging / dump.
    """
    d = families_dir or FAMILIES_DIR
    if not d.is_dir():
        raise FileNotFoundError(f"Families directory not found: {d}")

    families = load_families(d)
    if not families:
        return {"licenses": [], "total_licenses": 0}

    merged = merge(families)
    return build_output(merged, families)


def dump_merged_json(
    output_path: str | Path,
    families_dir: Path | None = None,
) -> None:
    """
    Write the fully merged license JSON to *output_path* for inspection.
    """
    data = get_merged_output(families_dir)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ----------------------------------------------------------------------
# CLI entry point
# ----------------------------------------------------------------------


def main() -> None:
    if not FAMILIES_DIR.is_dir():
        raise FileNotFoundError(f"Families directory not found: {FAMILIES_DIR}")

    families = load_families(FAMILIES_DIR)

    if not families:
        return

    merged = merge(families)
    output = build_output(merged, families)

    final_json_string = json.dumps(output, indent=2, ensure_ascii=False)
    print(final_json_string)


if __name__ == "__main__":
    main()
