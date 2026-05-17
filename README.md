# LicenseWise – KBS License Advisor

**LicenseWise** is a knowledge‑based system (KBS) that helps developers and organizations choose the right open‑source license for their projects. It uses forward chaining to recommend licenses based on your project goals, and backward chaining to check if a specific license is compatible with your intended use.

---

## Features

- **Forward Chaining (Recommendation Mode)**
  Answer a set of questions about your project (distribution, SaaS, copyleft preferences, patent needs, etc.). The engine applies inference rules to suggest the most suitable licenses.

- **Backward Chaining (Analysis Mode)**
  Pick a license (e.g., `GPL-3.0`, `MIT`) and answer a few key questions. The engine verifies whether the license’s conditions are compatible with your usage.

- **Explanation Facility**
  Every inference step is recorded. The system explains *why* a license was recommended, eliminated, or why a warning was issued – including the exact rule that fired.

- **Two Interfaces**
  - **CLI** – Lightweight terminal wizard.
  - **Gradio Web UI** – Full‑featured browser interface with tabs for recommendation and analysis.

- **Rich License Knowledge Base**
  Licenses are stored as JSON files grouped by family (GPL, BSD, Creative Commons, etc.). The system includes metadata such as conditions, permissions, and limitations, as well as popularity rankings.

---

## Installation

### Using `uv` (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd KBS/Project

# Create a virtual environment and install dependencies
uv venv .venv --python python3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

> If you prefer `pip`, activate your virtual environment and run `pip install -r requirements.txt`.

### Using Nix (NixOS / nix-shell)

A `shell.nix` is provided that sets up Python 3.12, `uv`, and all necessary libraries (including CUDA support, though not required). Just run:

```bash
nix-shell
```

The shell hook will automatically create a `.venv` and activate it.

---

## Usage

### Command‑Line Interface (CLI)

Run the main entry point without any arguments:

```bash
python main.py
```

You will see a menu:

```
Select mode:
[1] License Recommendation – Find the best license for your project
[2] License Analysis – Check if a specific license fits your needs
[3] Exit
```

- **Mode 1** asks a series of questions and produces a report with recommended licenses, eliminated ones, warnings, and a complete inference trace.
- **Mode 2** asks for a license identifier (e.g., `MIT`, `Apache-2.0`, `GPL-3.0`) and a few follow‑up questions, then tells you whether it is compatible.

### Gradio Web Interface

Launch the web UI with the `--gui` flag:

```bash
python main.py --gui
```

A local web server will start (usually at `http://127.0.0.1:7860`). The interface has two tabs:

- **License Recommendation** – all the questions from the CLI presented as radio buttons.
- **License Analysis** – enter a license ID and answer five key questions.

The interface is styled with a custom CSS file (`interface/style.css`).

---

## How It Works

### Forward Chaining (Recommendation)

1. **Facts** are gathered from the user (e.g., `closed_source = True`, `want_copyleft = True`, `project_type = "library"`).
2. The `Rules/rules.py` file defines **rules** – each rule has a **condition** (checks facts and/or license data) and an **action** (adds a license to `recommended`, `eliminated`, or appends a `warning`).
3. The engine iterates through all rules, evaluates conditions, and applies actions.
4. Finally, eliminated licenses are removed from the recommended set, and a report is generated using `explanation_engine.py`.

### Backward Chaining (Compatibility Check)

Given a license ID and a subset of facts (distribution, SaaS, commercial use, patent need, desire to relicense), the engine:

1. Looks up the license in the knowledge base.
2. Checks each critical condition of the license against the facts:
   - `disclose_source` vs `closed_source`
   - `same_license` vs `wants_relicense`
   - `net_copyleft` vs `saas` + `closed_source`
   - `commercial_use` permission vs `commercial_use` fact
3. Returns a verdict (`compatible` / `not compatible`), a list of violations, and a step‑by‑step explanation.

### Explanation Engine

- `explain_question(fact_name)` provides human‑readable explanations for why a particular question matters.
- `format_trace(trace)` and `generate_final_report(...)` produce detailed logs of which rules fired and why.

---

## License Data

All license information is stored in the `Licenses/` directory. The folder contains:

- `Families/` – one JSON file per license family (e.g., `GPL.json`, `BSD.json`, `creative_commons.json`). Each file lists licenses belonging to that family, including fields like:
  - `id`, `spdx_id`, `name`
  - `conditions`: `disclose_source`, `same_license`, `net_copyleft`, …
  - `permissions`: `commercial_use`
  - `limitations`: `patent_use`
  - `metadata`: `popularity_rank`, `description`, `url`
- `families_merger.py` – merges all family files into a single in‑memory structure for use by the inference engine.
- `families_deduplicate.py` – a utility to check for duplicate license entries.

> **Note:** The system does **not** require a single monolithic `licenses.json`. The merger is called dynamically by the CLI/Gradio at startup.

---

## Project Structure

```
.
├── Inference/                # Inference engine modules
│   ├── forward_chain.py
│   ├── backward_chain.py
│   └── explanation_engine.py
├── interface/                # User interfaces
│   ├── cli.py
│   ├── gradio_app.py
│   └── style.css
├── Licenses/                 # License knowledge base
│   ├── Families/             # JSON files grouped by family
│   ├── families_merger.py
│   └── families_deduplicate.py
├── Rules/
│   └── rules.py              # Forward‑chaining rule definitions
├── Tests/                    # (optional) test files
├── Docs/                     # Documentation and case studies
├── main.py                   # Main entry point (CLI + --gui)
├── requirements.txt          # Python dependencies (gradio)
├── shell.nix                 # Nix development environment
└── README.md                 # This file
```

---

## Adding or Modifying Licenses

1. Place a new JSON file in `Licenses/Families/` or edit an existing one.
   Use the same schema as the existing files (see `licenses_template.jsonl`).
2. The merger script (`families_merger.py`) will automatically combine all families when the CLI/Gradio loads.
3. If you introduce a new condition or permission, update the backward chaining logic in `backward_chain.py` and the relevant rules in `rules.py`.

---

## Extending the Rule Base

Add new rules to `Rules/rules.py`. Each rule is a dictionary with:

- `id` – unique identifier
- `name` – human‑readable name
- `condition` – function `(facts, licenses_data) -> bool`
- `action` – function `(working_memory) -> None` that modifies `recommended`, `eliminated`, or `warnings`
- `explanation` – string shown in the trace
- `action_type` – one of `"RECOMMEND"`, `"ELIMINATE"`, `"WARN"`

Example rule:

```python
{
    "id": "A01",
    "name": "recommend_MIT_if_closed_source",
    "condition": lambda f, _: f.get("closed_source") is True,
    "action": lambda wm: wm["recommended"].add("MIT"),
    "explanation": "MIT does not require source disclosure.",
    "action_type": "RECOMMEND"
}
```

---

## Disclaimer

**This tool is for educational and informational purposes only.**
It does **not** constitute legal advice. License selection involves legal consequences; always consult a qualified lawyer for your specific use case.

---

## Requirements

- Python 3.12+
- `gradio` (only for the web interface)
- (Optional) `uv` for fast environment management

All required packages are listed in `requirements.txt`.

## Sources

**Data Sources:**

- [SPDX License List](https://spdx.org/licenses/)
- [Open Source Initiative](https://opensource.org/licenses)
- [GNU License Summaries](https://www.gnu.org/licenses/license-list.html)
- [Choose a License](https://choosealicense.com/)

---

## 📄 License

This project itself is licensed under [MIT License](LICENSE).