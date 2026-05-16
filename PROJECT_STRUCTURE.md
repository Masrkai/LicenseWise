# LicenseWise – Project Structure & Setup Guide

## 📁 Directory Structure

```
LicenseWise/
├── knowledge/                    # KNOWLEDGE BASE LAYER
│   ├── __init__.py
│   ├── licenses.json            # SPDX license data (9 licenses)
│   └── rules.py                 # 57 IF-THEN rules
│
├── inference/                    # INFERENCE ENGINE LAYER
│   ├── __init__.py
│   ├── engine.py                # Forward/backward chaining
│   └── explanation.py           # Explanation trace generator
│
├── explanation/                  # EXPLANATION FACILITY LAYER
│   ├── __init__.py
│   └── explanation_engine.py    # Why/How/Confidence explanations
│
├── interface/                    # USER INTERFACE LAYER
│   ├── __init__.py
│   └── cli.py                   # Interactive CLI
│
├── tests/                        # TESTING LAYER
│   ├── __init__.py
│   └── test_scenarios.py        # Unit tests for sample cases
│
├── main.py                       # ENTRY POINT
├── README.md                     # PROJECT DOCUMENTATION
└── requirements.txt              # DEPENDENCIES (empty – stdlib only)
```

## 🚀 Quick Start

### 1. Setup

```bash
# Create project structure
mkdir -p LicenseWise/{knowledge,inference,explanation,interface,tests}

# Copy all generated files into place
cp licenses.json LicenseWise/knowledge/
cp rules.py LicenseWise/knowledge/
cp engine.py LicenseWise/inference/
cp explanation_engine.py LicenseWise/explanation/
cp cli.py LicenseWise/interface/
cp main.py LicenseWise/
cp README.md LicenseWise/

# Create empty __init__.py files
touch LicenseWise/{knowledge,inference,explanation,interface,tests}/__init__.py

# Create requirements.txt
echo "# No external dependencies required" > LicenseWise/requirements.txt
```

### 2. Run

```bash
cd LicenseWise
python main.py
```

## 🧩 Module Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                         (cli.py)                             │
│     • Collects facts from user                              │
│     • Displays results and explanations                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ passes facts
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   INFERENCE ENGINE                           │
│                      (engine.py)                             │
│     • Forward chaining: Facts → Rules → Working Memory      │
│     • Backward chaining: Goal → Verification → Result       │
└──────────────────────────┬──────────────────────────────────┘
                           │ fires matching rules
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE BASE                           │
│              (licenses.json + rules.py)                      │
│     • License definitions (permissions, conditions, limits) │
│     • 57 IF-THEN rules (recommend/eliminate/warn)           │
└──────────────────────────┬──────────────────────────────────┘
                           │ updates working memory
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  EXPLANATION FACILITY                        │
│                 (explanation_engine.py)                      │
│     • Records reasoning trace for every fired rule          │
│     • Generates "Why?" and "How?" explanations              │
│     • Calculates confidence levels                          │
└─────────────────────────────────────────────────────────────┘
```

## 📝 Fact Dictionary Reference

All facts collected from the user:

| Fact | Type | Default | Description |
|------|------|---------|-------------|
| `closed_source` | bool | None | Won't distribute source code |
| `saas` | bool | None | Software used over a network |
| `commercial_use` | bool | None | Commercial purpose intended |
| `need_patent_protection` | bool | None | Need explicit patent grant |
| `want_copyleft` | bool | None | Want strong copyleft |
| `want_weak_copyleft` | bool | None | Want library-level copyleft |
| `want_file_copyleft` | bool | None | Want file-level copyleft |
| `wants_relicense` | bool | None | Want freedom to relicense |
| `project_type` | str | None | "software", "library", "content" |
| `want_public_domain` | bool | None | Want public domain dedication |
| `want_simple_permissive` | bool | None | Want simple permissive license |
| `academic_project` | bool | None | Academic/research project |
| `mixed_open_proprietary` | bool | None | Mixed open/proprietary codebase |
| `linking_type` | str | None | "dynamic" or "static" |
| `modify_library` | bool | None | Will modify the library |
| `concerned_about_legal_recognition` | bool | None | Concerned about legal jurisdictions |

## 🧠 Working Memory Structure

```python
{
    "recommended": set(),   # Licenses that match user needs
    "eliminated": set(),    # Licenses incompatible with user needs
    "warnings": list(),     # Cautions about licenses
}
```

## 🔧 Rule Naming Convention

```
{action}_{license}_{condition_description}

Actions:
  recommend_   → Add license to recommended set
  eliminate_   → Add license to eliminated set
  warn_        → Append warning message

Examples:
  recommend_MIT_if_closed_source
  eliminate_GPL_if_closed_source
  warn_MIT_no_patent_grant
```

## 🎯 Test Scenarios

### Scenario 1: Closed-Source SaaS with Patent Protection
```python
facts = {
    "closed_source": True,
    "saas": True,
    "commercial_use": True,
    "need_patent_protection": True,
    "want_copyleft": False,
    "wants_relicense": True,
    "project_type": "software"
}
# Expected: Apache-2.0 recommended, GPL/AGPL eliminated
```

### Scenario 2: Open-Source Library (Weak Copyleft)
```python
facts = {
    "project_type": "library",
    "want_weak_copyleft": True,
    "linking_type": "dynamic",
    "modify_library": True,
    "commercial_use": True,
    "closed_source": False
}
# Expected: LGPL-2.1 recommended
```

### Scenario 3: Public Domain Dedication
```python
facts = {
    "want_public_domain": True,
    "no_attribution_needed": True,
    "want_maximum_freedom": True,
    "closed_source": True
}
# Expected: Unlicense recommended, warning about jurisdiction
```

### Scenario 4: Strong Copyleft Application
```python
facts = {
    "want_copyleft": True,
    "closed_source": False,
    "saas": True,
    "commercial_use": True,
    "project_type": "software"
}
# Expected: AGPL-3.0 recommended (closes SaaS loophole)
```

### Scenario 5: Academic Project (Simple Permissive)
```python
facts = {
    "academic_project": True,
    "want_simple_permissive": True,
    "closed_source": False,
    "commercial_use": True
}
# Expected: MIT or BSD-2-Clause recommended
```

## 📊 Grading Rubric Alignment

| Rubric Item | How LicenseWise Delivers |
|-------------|--------------------------|
| **Problem & Domain (10 pts)** | Real-world software licensing complexity; clear stakeholders (developers, legal teams) |
| **Knowledge Representation (20 pts)** | 57 non-trivial rules; structured JSON ontology; SPDX integration |
| **Inference Mechanism (20 pts)** | Hybrid forward/backward chaining with traceable reasoning |
| **Implementation (20 pts)** | Clean modular Python; testable; extensible architecture |
| **Explanation Facility (10 pts)** | "Why?" questions explained; "How?" reasoning traces; confidence scoring |
| **Documentation (10 pts)** | Complete README, inline comments, architecture diagrams |
| **Creativity/Complexity (10 pts)** | 9 licenses, conflict detection, backward chaining analysis mode |

## ⚠️ Known Limitations

1. No dependency tree parsing (package.json/requirements.txt)
2. No dual-licensing support
3. No jurisdiction-specific legal advice
4. Limited to 9 pre-defined licenses
5. Static analysis only (no runtime behavior)

## 📚 References

- SPDX License List: https://spdx.org/licenses/
- OSI Approved Licenses: https://opensource.org/licenses
- GNU License Summaries: https://www.gnu.org/licenses/license-list.html
- Choose a License: https://choosealicense.com/
- FSF License Categories: https://www.gnu.org/licenses/license-list.html
