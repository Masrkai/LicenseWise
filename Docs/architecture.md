# LicenseWise System Architecture

*Knowledge Base Systems · Spring 2026*

---

## 1. Overview

LicenseWise is a knowledge-based expert system for software license recommendation and compatibility analysis. It implements two inference strategies: **forward chaining** for recommendation and **backward chaining** for compatibility checking. The system encodes license properties from the SPDX standard into a rule base and applies them against user-supplied facts to produce traceable recommendations.

---

## 2. Layered Architecture

The system is organized into four layers:

| Layer | Module | Responsibility |
|-------|--------|---------------|
| **Interface** | `interface/cli.py` + `interface/gradio_app.py` | Interactive CLI and Gradio web UI; collects user facts via prompted questions |
| **Inference** | `Inference/forward_chain.py` + `Inference/backward_chain.py` | Forward chaining and backward chaining implementations |
| **Explanation** | `Inference/explanation_engine.py` | `format_trace()`, `generate_final_report()`, `generate_summary()` |
| **Knowledge** | `Rules/rules.py` + `Licenses/Families/*.json` | 27 IF-THEN rules; 9 SPDX license definitions merged at runtime |
| **Entry Point** | `main.py` | Dispatches to recommendation or analysis mode; handles `--gui` flag |
| **Tests** | `Tests/test_scenarios.py` | Unit tests for sample use-case scenarios |

---

## 3. Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  ┌──────────────┐  ┌─────────────────────────────────────────┐  │
│  │   Terminal   │  │            Web Browser                  │  │
│  │   (CLI)      │  │         (Gradio UI)                     │  │
│  └──────┬───────┘  └───────────────────┬─────────────────────┘  │
└─────────┼──────────────────────────────┼────────────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Interface Layer                             │
│  ┌──────────────────────┐  ┌─────────────────────────────────┐  │
│  │    interface/cli.py  │  │    interface/gradio_app.py      │  │
│  │  - collect_facts()   │  │  - build_interface()            │  │
│  │  - display_menu()    │  │  - recommendation_tab()         │  │
│  │  - run_recommend()   │  │  - analysis_tab()               │  │
│  │  - run_analysis()    │  │  - handle_submit()              │  │
│  └──────────┬───────────┘  └──────────────┬────────────────────┘  │
└─────────────┼─────────────────────────────┼───────────────────────┘
              │                             │
              └─────────────┬───────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Inference Layer                             │
│  ┌────────────────────────┐  ┌──────────────────────────────┐   │
│  │  Inference/forward_    │  │  Inference/backward_chain.py │   │
│  │       chain.py         │  │                              │   │
│  │  - forward_chain()     │  │  - backward_chain()          │   │
│  │  - evaluate_rules()    │  │  - check_conditions()        │   │
│  │  - resolve_conflicts() │  │  - generate_violations()     │   │
│  └──────────┬─────────────┘  └──────────────┬───────────────┘   │
│             │                               │                    │
│             └───────────────┬───────────────┘                    │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │         Inference/explanation_engine.py                   │    │
│  │  - explain_question(fact_name)                           │    │
│  │  - format_trace(trace)                                   │    │
│  │  - generate_final_report(wm, facts, trace)               │    │
│  │  - generate_summary(wm, facts, trace)                    │    │
│  │  - compute_confidence(facts, recommended)                │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Knowledge Layer                             │
│  ┌────────────────────────┐  ┌──────────────────────────────┐   │
│  │    Rules/rules.py      │  │   Licenses/Families/*.json   │   │
│  │                        │  │                              │   │
│  │  - RULES (27 rules)    │  │  - GPL.json                  │   │
│  │  - build_rules()       │  │  - MIT.json                  │   │
│  │  - Helper predicates   │  │  - Apache.json               │   │
│  │    (_saas, _copyleft)  │  │  - BSD.json                  │   │
│  │                        │  │  - LGPL.json                 │   │
│  │  Rule Schema:          │  │  - MPL.json                  │   │
│  │  {id, name, condition, │  │  - creative_commons.json     │   │
│  │   action, explanation, │  │  - public_domain.json        │   │
│  │   action_type}         │  │                              │   │
│  │                        │  │  License Schema:             │   │
│  │  Groups: A(13), B(7),  │  │  {id, spdx_id, conditions,  │   │
│  │  C(4), D(2), E(1)      │  │   permissions, limitations, │   │
│  │                        │  │   metadata}                  │   │
│  └──────────┬─────────────┘  └──────────────┬───────────────┘   │
│             │                               │                    │
│             └───────────────┬───────────────┘                    │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │         Licenses/families_merger.py                       │    │
│  │  - merge_all_families()                                  │    │
│  │  - load_family_json(path)                                │    │
│  │  - validate_license_data(data)                           │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Class Diagram

```
┌─────────────────────────────┐
│         <<module>>          │
│      interface/cli.py       │
├─────────────────────────────┤
│ + collect_facts()           │
│ + display_menu()            │
│ + run_recommendation()      │
│ + run_analysis()            │
│ + display_report(report)    │
└─────────────────────────────┘

┌─────────────────────────────┐
│         <<module>>          │
│   interface/gradio_app.py   │
├─────────────────────────────┤
│ + build_interface()         │
│ + recommendation_tab()      │
│ + analysis_tab()            │
│ + handle_recommend_submit() │
│ + handle_analysis_submit()  │
└─────────────────────────────┘

┌─────────────────────────────┐
│         <<module>>          │
│  Inference/forward_chain.py │
├─────────────────────────────┤
│ + forward_chain(facts,      │
│   rules, licenses_data,     │
│   trace) -> dict            │
│ - _evaluate_condition()     │
│ - _apply_action()           │
│ - _resolve_conflicts(wm)    │
└─────────────────────────────┘

┌─────────────────────────────┐
│         <<module>>          │
│ Inference/backward_chain.py │
├─────────────────────────────┤
│ + backward_chain(license_id,│
│   facts, licenses_data)     │
│   -> dict                   │
│ - _lookup_license()         │
│ - _check_disclose_source()  │
│ - _check_same_license()     │
│ - _check_net_copyleft()     │
│ - _check_commercial_use()   │
│ - _check_patent_use()       │
└─────────────────────────────┘

┌─────────────────────────────┐
│         <<module>>          │
│Inference/explanation_engine │
├─────────────────────────────┤
│ + explain_question(fact)    │
│   -> str                    │
│ + format_trace(trace)       │
│   -> str                    │
│ + generate_final_report(wm, │
│   facts, trace) -> str      │
│ + generate_summary(wm,      │
│   facts, trace) -> str      │
│ - _compute_confidence()     │
│   -> str                    │
└─────────────────────────────┘

┌─────────────────────────────┐
│         <<module>>          │
│       Rules/rules.py        │
├─────────────────────────────┤
│ RULES: list[dict]           │
│ + build_rules() -> list     │
│ - _saas(facts) -> bool      │
│ - _copyleft(facts) -> bool  │
│ - _patent(facts) -> bool    │
│ - _private_mods(facts)      │
│   -> bool                   │
└─────────────────────────────┘

┌─────────────────────────────┐
│         <<module>>          │
│  Licenses/families_merger   │
├─────────────────────────────┤
│ + merge_all_families()      │
│   -> dict                   │
│ - load_family_json(path)    │
│   -> dict                   │
│ - validate_license_data()   │
│   -> bool                   │
└─────────────────────────────┘
```

---

## 5. Sequence Diagram: Forward Chaining

```
User          CLI          forward_chain    rules.py    explanation_engine
 │              │                │              │                │
 │──start()───>│                │              │                │
 │              │──collect()───>│              │                │
 │              │                │              │                │
 │<─questions───│                │              │                │
 │──answers───>│                │              │                │
 │              │──facts───────>│              │                │
 │              │                │              │                │
 │              │                │─load RULES──>│                │
 │              │                │<─RULES───────│                │
 │              │                │              │                │
 │              │                │──for each rule:              │
 │              │                │  evaluate condition          │
 │              │                │  if true:                    │
 │              │                │    apply action to wm        │
 │              │                │    append to trace           │
 │              │                │              │                │
 │              │                │─resolve conflicts            │
 │              │                │ recommended-=eliminated      │
 │              │                │              │                │
 │              │                │─generate report─────────────>│
 │              │                │<─report──────────────────────│
 │              │                │              │                │
 │<─display─────│                │              │                │
 │              │                │              │                │
```

---

## 6. Sequence Diagram: Backward Chaining

```
User          CLI          backward_chain   families_merger  explanation_engine
 │              │                │                │                │
 │──analyze()─>│                │                │                │
 │              │─license_id───>│                │                │
 │              │─facts────────>│                │                │
 │              │                │                │                │
 │              │                │─lookup license│                │
 │              │                │──────────────>│                │
 │              │                │<─license_info──│                │
 │              │                │                │                │
 │              │                │──check conditions:             │
 │              │                │  disclose_source vs closed     │
 │              │                │  same_license vs relicense     │
 │              │                │  net_copyleft vs saas+closed   │
 │              │                │  commercial_use permission     │
 │              │                │  patent_use vs need            │
 │              │                │                │                │
 │              │                │─build result──>│                │
 │              │                │<─result────────│                │
 │              │                │                │                │
 │              │                │─format output─────────────────>│
 │              │                │<─formatted─────────────────────│
 │              │                │                │                │
 │<─display─────│                │                │                │
 │              │                │                │                │
```

---

## 7. Working Memory Structure

```python
# Working Memory (wm) - mutated by rule actions
wm = {
    "recommended": set(),  # licenses that satisfy user goals
    "eliminated": set(),   # licenses incompatible with user goals
    "warnings": list()     # caution strings appended by WARN rules
}

# Trace Entry - appended for each fired rule
trace_entry = {
    "step": int,
    "rule_id": str,
    "rule_name": str,
    "matched_facts": dict,
    "explanation": str,
    "action": str  # "RECOMMEND", "ELIMINATE", or "WARN"
}

# Backward Chain Result
result = {
    "compatible": bool,
    "violations": list[str],
    "explanation": str,
    "how": str,
    "license_info": dict | None
}
```

---

## 8. Data Flow

### 8.1 Forward Chaining Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │────>│    Facts    │────>│    Rules    │────>│   Working   │
│  Input      │     │   Dict      │     │  Engine     │     │  Memory     │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                    │
                                                                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │<────│   Report    │<────│Explanation  │<────│  Conflict   │
│   Output    │     │  Generator  │     │   Engine    │     │ Resolution  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 8.2 Backward Chaining Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   License   │────>│   License   │────>│  Condition  │────>│  Violation  │
│     ID      │     │   Lookup    │     │   Checks    │     │   List      │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                     │
                                                                     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │<────│   Report    │<────│Explanation  │<────│ Compatible  │
│   Output    │     │  Generator  │     │   Engine    │     │   Verdict   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

---

## 9. Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.12+ |
| CLI Framework | Built-in `input()` / `argparse` | stdlib |
| Web UI Framework | Gradio | latest |
| Testing | pytest | latest |
| Environment | uv (optional) / pip | latest |
| Nix Support | nix-shell | 2.x+ |

---

## 10. Deployment Options

### 10.1 Local CLI
```bash
python main.py
```

### 10.2 Local Web UI
```bash
python main.py --gui
# Access at http://127.0.0.1:7860
```

### 10.3 Gradio Share
```bash
python main.py --gui --share
# Generates a public URL via Gradio tunnel
```

---

## 11. Performance Characteristics

| Metric | Value |
|--------|-------|
| Rule evaluation time | O(n) where n = 27 rules |
| License lookup time | O(1) via dict lookup |
| Memory footprint | ~2 MB (all licenses + rules) |
| Startup time | < 1 second |
| Response time | < 100 ms per inference |

---

*Document version: 1.0 · Testing Branch · Spring 2026*
