# Before you edit the Json File let's understand what is going on here first

A license is a way to represent what you are allowed to do and not allowed to do

block like

```json
    {
      "id": "MIT",
      "spdx_id": "MIT",
      "name": "MIT License",
      "type": "permissive",
      "description": "Short and simple permissive license with only one requirement.",
      "attributes": {
        "allows_commercial": true,
        "allows_modification": true,
        "allows_distribution": true,
        "allows_private_use": true,
        "requires_attribution": true,
        "requires_source_disclosure": false,
        "requires_same_license": false,
        "includes_patent_grant": false,
        "has_network_copyleft": false,
        "disclaims_liability_warranty": true
      },
      "compatibility": {
        "compatible_with": ["Apache-2.0", "BSD-3-Clause", "GPL-3.0", "LGPL-3.0", "MPL-2.0"],
        "incompatible_with": ["CC-BY-NC-4.0"],
        "notes": "One-way compatible with GPL-3.0"
      },
      "metadata": {
        "osi_approved": true,
        "fsf_free": true,
        "popularity_rank": 1,
        "explanation_hint": "Best for maximum adoption with minimal legal overhead."
      }
    },

```

BEFORE you add a license check it here:
- https://spdx.org/licenses/