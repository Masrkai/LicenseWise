# LicenseWise – Intelligent Software License Selection & Compliance Analyzer

> **A knowledge-based system that helps developers and organizations select the most appropriate open-source license and analyze license compatibility.**

---

## ⚠️ DISCLAIMER

This project was created by **CS students** as part of a Knowledge Base Systems course. **We are not lawyers**, and this tool has **not been reviewed by legal professionals**.

Our goal is to **de-mystify software licensing** so developers can have informed conversations with legal teams. **Do not take the results as definitive legal advice.** We are **not responsible** for how anyone uses this software.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
  - [License Recommendation Mode](#license-recommendation-mode)
  - [License Analysis Mode](#license-analysis-mode)
- [Knowledge Base](#knowledge-base)
  - [Facts (User Inputs)](#facts-user-inputs)
  - [Rules](#rules)
  - [Working Memory](#working-memory)
- [Explanation Facility](#explanation-facility)
- [Inference Engine](#inference-engine)
- [Sample Scenarios](#sample-scenarios)
- [Limitations](#limitations)
- [Team & Course Info](#team--course-info)

---

## 🎯 Overview

Choosing the right software license is complex. The wrong choice can:
- Force you to open-source proprietary code
- Expose you to patent litigation
- Create legal conflicts with dependencies
- Prevent commercial use

**LicenseWise** solves this by encoding license properties into a rule-based expert system that:
1. **Recommends** licenses based on your project goals
2. **Warns** about hidden obligations and risks
3. **Eliminates** incompatible options
4. **Explains** every decision with traceable reasoning

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **License Recommendation** | Forward-chaining rule engine narrows down licenses from 9+ options |
| ⚠️ **Compliance Checking** | Backward-chaining verifies if a license fits your intended use |
| 🧠 **Explanation Facility** | Every recommendation includes "Why?" and "How?" reasoning |
| 📊 **Conflict Detection** | Identifies when user goals contradict license requirements |
| 🏷️ **SPDX Integration** | Uses official SPDX license data for accuracy |
| 🖥️ **CLI Interface** | Interactive command-line interface for quick use |

---

## 🏗️ Architecture

```
LicenseWise/
├── knowledge/
│   ├── licenses.json          # SPDX-based license definitions (9 licenses)
│   └── rules.py               # 57 IF-THEN rules covering all licenses
├── inference/
│   ├── engine.py              # Forward/backward chaining engine
│   └── explanation.py         # Explanation trace generator
├── interface/
│   └── cli.py                 # Interactive CLI for user input
├── tests/
│   └── test_scenarios.py      # Unit tests for sample use cases
├── README.md                  # This file
└── main.py                    # Entry point
```

### Core Components

1. **Knowledge Base**: License properties encoded from SPDX data
2. **Rule Engine**: 57 rules covering recommendation, elimination, and warnings
3. **Inference Engine**: Hybrid forward/backward chaining
4. **Explanation Facility**: Step-by-step reasoning traces

---

## 🚀 Installation

### Requirements
- Python 3.10+
- No external dependencies (stdlib only)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-team/licensewise.git
cd licensewise

# Run the system
python main.py
```

---

## 🎮 Usage

### License Recommendation Mode

The system asks you a series of questions about your project, then recommends licenses with full explanations.

```bash
$ python main.py --recommend

🔹 LicenseWise – License Recommendation
─────────────────────────────────────────

Will you distribute your software to others? (yes/no): no
Will the software be used over a network (SaaS)? (yes/no): yes
Is commercial use intended? (yes/no): yes
Do you need patent protection? (yes/no): yes
Do you want derivatives to remain open source? (yes/no): no
What type of project is this? (software/library/content): software

✅ Recommended Licenses:
   1. Apache-2.0
      • Allows commercial use ✅
      • Explicit patent grant ✅
      • No source disclosure required ✅
      • Network-safe (no copyleft trigger) ✅

   2. MIT
      • Simple and widely adopted ✅
      • No source disclosure required ✅
      • Network-safe ✅
      ⚠️ No explicit patent grant

⚠️ Avoid:
   • GPL-3.0: Requires source disclosure of derivatives
   • AGPL-3.0: Network use triggers source disclosure

🔍 Explanation:
   1. You indicated closed-source distribution → Eliminated all strong copyleft licenses
   2. You need patent protection → Prioritized Apache-2.0 (has patent grant)
   3. SaaS deployment confirmed → Verified no network copyleft requirements
   4. Commercial use confirmed → All recommended licenses permit this
```

### License Analysis Mode

Check if a specific license is compatible with your intended use.

```bash
$ python main.py --analyze

🔹 LicenseWise – License Analysis
──────────────────────────────────

Enter license name or SPDX ID: GPL-3.0

What is your intended use?
  [1] Use in commercial closed-source application
  [2] Use in open-source project with different license
  [3] Modify and distribute without sharing source
  [4] Use in SaaS without sharing source

Choice: 3

❌ NOT COMPATIBLE

GPL-3.0 requires:
  • disclose_source = true
  • same_license = true

Your intended use violates:
  • Source disclosure obligation
  • Same-license requirement for derivatives

💡 Recommendation: Consider MIT or Apache-2.0 if you need to distribute
   without sharing source code.
```

---

## 🧠 Knowledge Base

### Facts (User Inputs)

The system collects the following facts from the user:

| Fact | Type | Description |
|------|------|-------------|
| `closed_source` | bool | Won't distribute source code |
| `saas` | bool | Software used over a network |
| `commercial_use` | bool | Commercial purpose intended |
| `need_patent_protection` | bool | Need explicit patent grant |
| `want_copyleft` | bool | Want strong copyleft (all derivatives open) |
| `want_weak_copyleft` | bool | Want library-level copyleft only |
| `want_file_copyleft` | bool | Want file-level copyleft only |
| `wants_relicense` | bool | Want freedom to relicense derivatives |
| `project_type` | str | `"software"`, `"library"`, or `"content"` |
| `want_public_domain` | bool | Want public domain dedication |
| `want_simple_permissive` | bool | Want a simple permissive license |
| `academic_project` | bool | Academic or research project |
| `mixed_open_proprietary` | bool | Mixed open/proprietary codebase |
| `linking_type` | str | `"dynamic"` or `"static"` (for libraries) |
| `modify_library` | bool | Will modify the library |
| `concerned_about_legal_recognition` | bool | Concerned about legal jurisdiction issues |

### Rules

The system contains **57 rules** organized by license:

| License | Recommend | Eliminate | Warn | Total |
|---------|-----------|-----------|------|-------|
| MIT | 5 | 0 | 3 | 8 |
| Apache-2.0 | 5 | 0 | 2 | 7 |
| GPL-3.0 | 2 | 2 | 2 | 6 |
| AGPL-3.0 | 2 | 3 | 2 | 7 |
| LGPL-2.1 | 3 | 1 | 2 | 6 |
| MPL-2.0 | 3 | 1 | 1 | 5 |
| BSD-2-Clause | 5 | 0 | 2 | 7 |
| CC-BY-NC-4.0 | 1 | 2 | 2 | 5 |
| Unlicense | 4 | 0 | 3 | 7 |

**Rule Types:**
- **Recommendation Rules**: `IF condition THEN add_to_recommended`
- **Elimination Rules**: `IF condition THEN add_to_eliminated`
- **Warning Rules**: `IF condition THEN append_warning`

### Working Memory

During inference, the working memory tracks:

```python
{
    "recommended": set(),      # Licenses that match user needs
    "eliminated": set(),       # Licenses incompatible with user needs
    "warnings": list(),        # Cautions about recommended/eliminated licenses
    "reasoning_trace": list()  # Step-by-step explanation of each fired rule
}
```

---

## 💬 Explanation Facility

Every recommendation includes a **reasoning trace** showing:

### 1. Why Was This Question Asked?

```
Q: "Will users interact with your software over a network?"
A: We asked this because AGPL-3.0 triggers source-sharing requirements
   for network/SaaS deployments. Your answer helps us determine if
   strong copyleft licenses are compatible with your goals.
```

### 2. How Was the Conclusion Reached?

```
Conclusion: Apache-2.0 recommended

Reasoning Path:
1. User wants closed-source distribution
   → Rule: eliminate_GPL_if_closed_source fired
   → Rule: eliminate_AGPL_if_closed_source fired
   → Result: Removed GPL-3.0, AGPL-3.0 from consideration

2. User needs patent protection
   → Rule: recommend_Apache_if_patent_protection fired
   → Result: Added Apache-2.0 to recommended set

3. User confirmed SaaS deployment
   → Rule: recommend_Apache_if_saas fired
   → Result: Confirmed Apache-2.0 has no network copyleft

4. No conflicts detected
   → Final recommendation: Apache-2.0 (best match)
```

### 3. Confidence & Uncertainty

```
Confidence: HIGH
All user goals are fully compatible with Apache-2.0 properties.
No conflicting requirements detected.
```

Or:

```
Confidence: MEDIUM
LGPL-2.1 compatibility depends on dynamic vs. static linking.
You selected "static linking" which may require additional care.
Consult a lawyer for production use.
```

---

## ⚙️ Inference Engine

### Forward Chaining (Recommendation Mode)

```
Facts → Match Rules → Fire Actions → Update Working Memory → Repeat → Output
```

1. Collect user facts
2. Iterate through all rules
3. For each matching rule, fire its action
4. Update working memory (recommended/eliminated/warnings)
5. Present results with explanations

### Backward Chaining (Analysis Mode)

```
Goal (Can I use X?) → Check Required Facts → Ask User → Verify → Output
```

1. User asks: "Can I use GPL-3.0 in a closed-source app?"
2. System checks GPL-3.0 conditions: `disclose_source = true`
3. User fact: `closed_source = true`
4. Conflict detected: closed_source contradicts disclose_source
5. Output: Not compatible + explanation

---

## 🧪 Sample Scenarios

### Scenario A: New Open-Source Library

**User Profile:**
- Building a Python library
- Want it widely adopted
- Don't mind if proprietary apps use it
- Need to modify it over time

**Input Facts:**
```python
{
    "project_type": "library",
    "want_weak_copyleft": True,
    "linking_type": "dynamic",
    "modify_library": True,
    "commercial_use": True
}
```

**Result:**
```
✅ Recommended: LGPL-2.1
   • Weak copyleft: library stays open, linking apps stay free
   • Dynamic linking is safe
   • Allows commercial use

⚠️ Warning: If you later switch to static linking, consult a lawyer.
```

### Scenario B: SaaS Startup (Closed Source)

**User Profile:**
- Building a SaaS product
- Keeping code private
- Need patent protection
- Commercial use

**Input Facts:**
```python
{
    "saas": True,
    "closed_source": True,
    "need_patent_protection": True,
    "commercial_use": True
}
```

**Result:**
```
✅ Recommended: Apache-2.0
   • No source disclosure required
   • Explicit patent grant
   • Network-safe (no copyleft trigger)
   • Permits commercial use

⚠️ Avoid:
   • AGPL-3.0: Network use triggers source disclosure
   • GPL-3.0: Requires source disclosure on distribution
```

### Scenario C: Public Domain Dedication

**User Profile:**
- Small utility script
- Don't care about attribution
- Want maximum freedom for users

**Input Facts:**
```python
{
    "want_public_domain": True,
    "no_attribution_needed": True,
    "want_maximum_freedom": True
}
```

**Result:**
```
✅ Recommended: Unlicense
   • No restrictions whatsoever
   • No attribution required
   • Maximum freedom for users

⚠️ Warning: Public domain dedication not recognized in all jurisdictions.
   Consider adding a fallback permissive license if this is a concern.
```

---

## ⚠️ Limitations

1. **Not Legal Advice**: This system encodes general license properties but cannot account for:
   - Jurisdictional variations in law
   - Evolving license interpretations
   - Custom or enterprise licenses
   - Specific contractual obligations

2. **Scope**: Focuses on 9 popular OSI-approved/commonly-used licenses:
   MIT, Apache-2.0, GPL-3.0, AGPL-3.0, LGPL-2.1, MPL-2.0, BSD-2-Clause, CC-BY-NC-4.0, Unlicense

3. **Dual Licensing**: Does not handle dual-licensing scenarios

4. **Dependency Analysis**: Basic compatibility checking only; does not parse `package.json` or `requirements.txt`

5. **Static vs. Dynamic Linking**: LGPL-2.1 rules distinguish these, but real-world cases may be more nuanced

---

## 👥 Team & Course Info

**Course:** Knowledge Base Systems  
**Institution:** [Your University]  
**Semester:** Spring 2026  

**Team Members:**
- [Member 1] – Knowledge Engineer & Rule Developer
- [Member 2] – Inference Engine & Explanation Facility
- [Member 3] – User Interface & Testing
- [Member 4] – Documentation & Validation

**Data Sources:**
- [SPDX License List](https://spdx.org/licenses/)
- [Open Source Initiative](https://opensource.org/licenses)
- [GNU License Summaries](https://www.gnu.org/licenses/license-list.html)
- [Choose a License](https://choosealicense.com/)

---

## 📄 License

This project itself is licensed under [MIT License](LICENSE).

> **Irony noted** 😄
