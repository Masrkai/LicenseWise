"""
merge_families.py
-----------------
Reads every JSON file in the Families/ folder and merges them into a single
licenses JSON object in-memory, then prints the final result instead of
writing it to a new file.

Usage:
    python merge_families.py
"""
import json
from pathlib import Path

from config import LICENSES_DIR

FAMILIES_DIR = LICENSES_DIR / "Families"


def load_families(families_dir: Path) -> dict[str, list]:
    """
    Load every *.json file from Families/.
    Returns a dict:  { family_name: [license, ...] }
    """
    families = {}
    for path in sorted(families_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # Your provided JSON files use path.stem as the fallback family name
        family_name = data.get("family", path.stem)
        licenses    = data.get("licenses", [])
        families[family_name] = licenses

    return families


def merge(families: dict[str, list]) -> list[dict]:
    """
    Flatten all family lists into one deduplicated list.
    Deduplication key: spdx_id (falls back to id).
    Each license gets a 'families' list showing which files it appeared in.
    Sorted by popularity_rank ascending (unlisted ones go to the end).
    """
    seen: dict[str, dict] = {}   # spdx_id -> license object

    for family_name, licenses in families.items():
        for lic in licenses:
            key = lic.get("spdx_id") or lic.get("id")
            if key in seen:
                # Already present — just append this family to its list
                seen[key].setdefault("families", [])
                if family_name not in seen[key]["families"]:
                    seen[key]["families"].append(family_name)
            else:
                entry = dict(lic)
                entry["families"] = [family_name]
                seen[key] = entry

    merged = list(seen.values())

    # Sort by popularity_rank; entries without it sort last
    merged.sort(key=lambda l: l.get("metadata", {}).get("popularity_rank") or 9999)
    return merged


def build_output(merged: list[dict], families: dict[str, list]) -> dict:
    return {
        "schema_version": "1.5",
        "last_updated": "2026-04-22",
        "source": "https://spdx.org/licenses/",
        "family_files": sorted(families.keys()),
        "total_licenses": len(merged),
        "licenses": merged
    }


def main():
    if not FAMILIES_DIR.is_dir():
        raise FileNotFoundError(f"Families directory not found: {FAMILIES_DIR}")

    families = load_families(FAMILIES_DIR)

    if not families:
        return

    merged  = merge(families)
    output  = build_output(merged, families)

    # Instead of writing to an OUTPUT_FILE, we convert the final object
    # to a string and print it out directly.
    final_json_string = json.dumps(output, indent=2, ensure_ascii=False)
    print(final_json_string)


if __name__ == "__main__":
    main()