# LicenseWise – Intelligent Software License Selection & Compliance Analyzer

**Purpose:** A knowledge-based system that helps developers and organizations:

- **Select the most appropriate license** for their new software project based on goals, distribution model, and legal preferences
- **Analyze existing software licenses** to understand permissions, obligations, and restrictions before reuse/integration

---

## Knowledge Representation (Rule-Based System – Recommended)

### Core Entities

- License: {name, type, permissions, obligations, limitations}
- Project: {distribution_model, commercial_use, modification_intent, linking_type}
- User_Goals: {open_source_commitment, patent_protection, copyleft_preference}

---

## Inference Mechanism

### Recommended: **Hybrid Chaining**

- **Forward Chaining** for license recommendation:
  *User inputs project attributes → System fires rules → Narrow down license options*

- **Backward Chaining** for compliance checking:
  *User asks "Can I use Library X in my commercial app?" → System works backward to verify license conditions*

### Reasoning Trace Example

User Input:
  - Project type: Web SaaS
  - Distribution: Public
  - Commercial: Yes
  - Want to keep modifications private: Yes

Inference Steps:
1. Rule #X fires: IF SaaS + public → AGPL may apply
2. Rule #Y fires: IF keep_modifications_private → Exclude strong copyleft
3. Conflict detected: AGPL requires source disclosure vs. user goal
4. System asks clarification: "Will users interact with your software over a network?"
5. User: "Yes"
6. Rule #Z: IF network_interaction + AGPL-avoidance → Recommend "Apache-2.0 or MIT + clear attribution"
7. Final recommendation generated with justification

---

## User Interaction Design

### Input Interface (Text/CLI or Simple GUI)

```
🔹 Project Configuration:
   [ ] Will you distribute your software? → Yes/No
   [ ] Commercial use intended? → Yes/No
   [ ] Do you want derivatives to remain open? → Yes/No/Unsure
   [ ] Will you link with existing libraries? → List them
   [ ] Is patent protection important? → Yes/No

🔹 License Analysis Mode:
   [Enter license name or SPDX ID]: "LGPL-2.1"
   [Intended use]: "Static linking in proprietary app"
   → System evaluates compliance
```

### Output

```
✅ Recommended Licenses:
   1. Apache-2.0 (Best match: XXX%)
      • Allows commercial use ✅
      • Explicit patent grant ✅
      • Compatible with your dependencies ✅

⚠️ Avoid:
   • GPL-3.0: Requires source disclosure of derivatives (conflicts with your goal)

🔍 Explanation:
   "We asked about network distribution because AGPL triggers source-sharing
   requirements for SaaS applications. Since you confirmed network use but
   prefer closed modifications, we excluded strong copyleft licenses."
```

---

## Explanation Facility (Critical for Grading – 10 pts)

The system must provide:

- **Why was this question asked?**
  *"We asked about commercial use because some licenses (e.g., CC-NC) prohibit it."*

- **How was the conclusion reached?**

  ```
  Conclusion: MIT License recommended
  Reasoning Path:
  1. User wants permissive terms → Filtered to {MIT, BSD, Apache}
  2. User needs patent protection → Added Apache-2.0 to shortlist
  3. User prefers minimal attribution → Ranked MIT highest (simplest notice)
  4. No license conflicts detected → Final recommendation: MIT
  ```

- **Uncertainty handling**:
  *"Confidence: Medium. LGPL compatibility depends on dynamic vs. static linking. Consult a lawyer for production use."*

---

## 6. Implementation Plan (Python Recommended)

### Tech Stack

```txt
# Core
- Python 3.10+
- Rule engine: Pyke, Experta, or custom forward/backward chainer
- Knowledge base: JSON/YAML for rules + license data

# Optional Enhancements
- CLI: argparse + rich for formatted output
- Web UI: Flask/Streamlit for demo
- License data source: SPDX License List API (https://spdx.org/licenses/)
```

### Modular Architecture

```
LicenseWise/
├── knowledge/
│   ├── licenses.json          # License definitions
│   ├── rules.py               # 15-25 IF-THEN rules
│   └── ontology.py            # Optional: license hierarchy
├── inference/
│   ├── forward_chainer.py
│   ├── backward_chainer.py
│   └── explanation_engine.py
├── interface/
│   ├── cli.py                 # User input/output
│   └── web_demo.py            # Optional Streamlit UI
├── utils/
│   ├── spdx_fetcher.py        # Pull license data from SPDX
│   └── validator.py           # Rule consistency checks
└── main.py                    # Entry point
```

---

## Documentation Outline (Required for Submission)

1. **Problem Description**
   - Why license selection is complex; real-world pain points

2. **Knowledge Acquisition**
   - Sources: SPDX, OSI, Creative Commons, GitHub license docs, legal summaries
   - How rules were derived (e.g., "GPL compatibility matrix from FSF guidelines")

3. **Knowledge Representation**
   - Rule syntax, ontology diagram (if used), data schema

4. **Inference Mechanism**
   - Chaining strategy, conflict resolution, uncertainty handling

5. **System Architecture**
   - Component diagram, data flow, module interactions

6. **Sample Runs**
   - Screenshots/CLI logs:
     • Scenario A: Choosing a license for a new open-source library
     • Scenario B: Checking if MIT-licensed code can be used in a GPL project

7. **Limitations**
   - "Not legal advice", jurisdictional variations, evolving license interpretations
   - Scope: Focuses on popular OSI-approved licenses (not custom/enterprise licenses)

---

## Creativity & Complexity Boosters (10 pts)

- **SPDX API Integration**: Auto-fetch license metadata for up-to-date rules
- **Dependency Analyzer**: Parse `package.json`/`requirements.txt` to check license compatibility across a project's dependency tree
- **Goal-Based Profiling**: "I want my code to be widely adopted" vs. "I want to protect my commercial interests" → tailored recommendations
- **Visual License Compatibility Graph**: Show which licenses can/cannot be combined
- **Exportable Compliance Report**: Generate a markdown/PDF summary for team/legal review

---

## Alignment with Grading Rubric

| Criteria | How This Project Delivers |
|----------|---------------------------|
| Problem & Domain (10) | Real, high-impact problem with clear logic & stakeholders |
| Knowledge Representation (20) | 20+ non-trivial rules; structured license ontology; SPDX integration |
| Inference Mechanism (20) | Hybrid chaining with traceable, step-by-step reasoning |
| Implementation (20) | Clean Python architecture; modular, testable, extensible |
| Explanation Facility (10) | "Why?" and "How?" explanations at every decision point |
| Documentation (10) | Complete report structure with samples, sources, limitations |
| Creativity/Complexity (10) | SPDX API, dependency analysis, visualizations, compliance reports |

---

## Next Steps for Your Team

1. **Divide roles**: Knowledge engineer, rule developer, UI designer, tester, documentation lead
2. **Start small**: Implement 5 core rules + 3 licenses → test inference → expand
3. **Use SPDX**: <https://spdx.org/licenses/> – machine-readable license data
4. **Prototype early**: CLI version first, then enhance with explanations/UI
5. **Document as you build**: Capture rule sources, design decisions, test cases

Would you like me to help you draft the first 10 rules, design the JSON schema for licenses, or sketch the inference engine logic next? 🛠️
