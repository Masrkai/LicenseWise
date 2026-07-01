import json
import os
from collections import Counter, defaultdict


def find_duplicates(json_file):
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    licenses = data.get("licenses", [])

    ids = []
    spdx_ids = []
    names = []

    duplicate_entries = defaultdict(list)

    for index, license_item in enumerate(licenses):
        license_id = license_item.get("id")
        spdx_id = license_item.get("spdx_id")
        name = license_item.get("name")

        if license_id:
            ids.append(license_id)
            duplicate_entries[f"id:{license_id}"].append(index)

        if spdx_id:
            spdx_ids.append(spdx_id)
            duplicate_entries[f"spdx_id:{spdx_id}"].append(index)

        if name:
            names.append(name)
            duplicate_entries[f"name:{name}"].append(index)

    id_duplicates = {k: v for k, v in Counter(ids).items() if v > 1}
    spdx_duplicates = {k: v for k, v in Counter(spdx_ids).items() if v > 1}
    name_duplicates = {k: v for k, v in Counter(names).items() if v > 1}

    print("=" * 50)
    print("DUPLICATE CHECK RESULTS")
    print("=" * 50)

    if not (id_duplicates or spdx_duplicates or name_duplicates):
        print("No duplicates found.")
        return

    if id_duplicates:
        print("\nDuplicate IDs:")
        for key, count in id_duplicates.items():
            print(f"{key} -> {count} times")

    if spdx_duplicates:
        print("\nDuplicate SPDX IDs:")
        for key, count in spdx_duplicates.items():
            print(f"{key} -> {count} times")

    if name_duplicates:
        print("\nDuplicate Names:")
        for key, count in name_duplicates.items():
            print(f"{key} -> {count} times")


# Get current script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build full path automatically
json_path = os.path.join(BASE_DIR, "licenses.json")

find_duplicates(json_path)