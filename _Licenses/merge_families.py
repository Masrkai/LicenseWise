"""
merge_families.py
-----------------
Reads every JSON file in the Families/ folder and merges them into a single
licenses.json at the _Licenses/ root.

Usage:
    python merge_families.py

Output:
    _Licenses/licenses.json   (deduplicated, sorted by popularity_rank)
"""
import os
import json
from pathlib import Path

FAMILIES_DIR = Path(__file__).parent / "Families"
OUTPUT_FILE  = Path(__file__).parent / "licenses.json"


def load_families(families_dir: Path) -> dict[str, list]:
    """
    Load every *.json file from Families/.
    Returns a dict:  { family_name: [license, ...] }
    """
    families = {}
    for path in sorted(families_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        family_name = data.get("family", path.stem)
        licenses    = data.get("licenses", [])
        families[family_name] = licenses
        print(f"  Loaded {len(licenses):>2} licenses from {path.name}  (family: {family_name})")

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
    print(f"\nScanning: {FAMILIES_DIR}")
    if not FAMILIES_DIR.is_dir():
        raise FileNotFoundError(f"Families directory not found: {FAMILIES_DIR}")

    families = load_families(FAMILIES_DIR)

    if not families:
        print("No family JSON files found. Nothing to merge.")
        return

    merged  = merge(families)
    output  = build_output(merged, families)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Merged {len(merged)} unique licenses from {len(families)} families")
    print(f"✓ Written to: {OUTPUT_FILE}\n")

    # Quick duplicate check
    ids = [l.get("spdx_id") or l.get("id") for l in merged]
    dupes = [x for x in ids if ids.count(x) > 1]
    if dupes:
        print(f"⚠ Duplicate IDs still present (should not happen): {set(dupes)}")
    else:
        print("✓ No duplicates detected")


if __name__ == "__main__":
    main()
