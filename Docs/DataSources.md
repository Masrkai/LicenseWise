##  Knowledge acquisition (sources of knowledge) 

we have collected data from three sources:

- spdx (Software Package Data Exchange)
- OSI (Open source initiative)
- FSF (free software foundation)

we make something very clear here which is because A is named in `FSF` or `OSI` something doesn't mean i will get the same naming across the board
what made most sense when giving ids to the curated licenses was the `spdx` data because it belongs to the "Linux Foundation" and we search for the license in FSF and OSI data to check if it's approved by either, none or both

as we discuss now these are some of our research into how to automate the processing of that license data it's structured inside "src/Licenses"

the template is defined as:

```json
{
  "id": "<internal_identifier>",
  "spdx_id": "<SPDX_SHORT_IDENTIFIER>",
  "name": "<Human Readable License Name>",
  "type": "<permissive|copyleft|weak_copyleft|proprietary|other>",
  "description": "<Concise one-sentence summary>",

  "permissions": {
    "commercial_use": <boolean>,
    "distribution": <boolean>,
    "modification": <boolean>,
    "private_use": <boolean>
  },

  "conditions": {
    "include_copyright": <boolean>,
    "document_changes": <boolean>,
    "disclose_source": <boolean>,
    "include_license": <boolean>,
    "net_copyleft": <boolean>,
    "same_license": <boolean>
  },

  "limitations": {
    "liability": <boolean>,
    "trademark_use": <boolean>,
    "warranty": <boolean>,
    "patent_use": <boolean>
  },

  "metadata": {
    "osi_approved": <boolean>,
    "fsf_free": <boolean>,
    "popularity_rank": <integer_or_null>,
    "explanation_hint": "<Optional practical guidance>"
  }
}
```

ex apache-2.0

```json

    {
      "id": "Apache-2.0",
      "spdx_id": "Apache-2.0",
      "name": "Apache License 2.0",
      "type": "permissive",
      "description": "Permissive license with an explicit patent grant and protection against contributor patent claims.",
      "permissions": {
        "commercial_use": true,
        "distribution": true,
        "modification": true,
        "private_use": true
      },
      "conditions": {
        "include_copyright": true,
        "document_changes": true,
        "disclose_source": false,
        "include_license": true,
        "net_copyleft": false,
        "same_license": false
      },
      "limitations": {
        "liability": true,
        "trademark_use": true,
        "warranty": true,
        "patent_use": false
      },
      "metadata": {
        "osi_approved": true,
        "fsf_free": true,
        "popularity_rank": 2,
        "explanation_hint": "Best permissive choice when patent protection matters, e.g. corporate or hardware-adjacent projects."
      }
    },

```