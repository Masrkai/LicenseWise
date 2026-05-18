## knowledge representation method

Production Rules ***(IF-THEN rules)***

ex:

```py

    rules.append({
        "id": "A02",
        "name": "recommend_MIT_if_saas",
        "condition": lambda f, _: _saas(f),
        "action": lambda wm: wm["recommended"].add("MIT"),
        "explanation": "MIT has no network copyleft, suitable for SaaS.",
        "action_type": "RECOMMEND",
        "licenses_affected": ["MIT"]
    })
```