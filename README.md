# LicenseWise – KBS License Advisor

<p align="center">
  <img src="./assets/licensewise_icon.svg" alt="licensewise icon" width="400">
</p>

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
  - **Slint GUI** – Native desktop interface (also supports WASM/web) with tabs for recommendation and analysis.

- **Rich License Knowledge Base**
  Licenses are stored as JSON files grouped by family (GPL, BSD, Creative Commons, etc.). The system includes metadata such as conditions, permissions, and limitations, as well as popularity rankings.

---

## Installation

### Using `uv` (recommended)

```bash
# Clone the repository
git clone https://github.com/Masrkai/LicenseWise.git
cd LicenseWise

# Create a virtual environment and install dependencies
uv venv .venv
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
python -m src.main
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

### Slint GUI Interface

Launch the GUI with the `--gui` flag:

```bash
python -m src.main --gui
```

A native desktop window will open. The interface has two tabs:

- **License Recommendation** – all the questions from the CLI presented as combo box selectors.
- **License Analysis** – enter a license ID and answer five key questions.

The UI is defined in `.slint` files under `interface/ui/`.

### Debug / Reasoning

there are extra flags to check

```bash
➜  python -m src.main -h
usage: main.py [-h] [--gui] [--verbose] [--dump-merged-licenses [PATH]]

LicenseWise - KBS License Advisor

options:
  -h, --help            show this help message and exit
  --gui                 Launch Slint GUI interface
  --verbose             Show detailed reasoning trace
  --dump-merged-licenses [PATH]
                        Dump the merged license JSON to PATH for debugging (default: merged_licenses.json)
```

---

## How It Works

### Forward Chaining (Recommendation)

1. **Facts** are gathered from the user (e.g., `closed_source = True`, `want_copyleft = True`, `project_type = "library"`).
2. The `src/Rules/license_rules.pl` file defines **rules** – each rule has a **condition** (checks facts) and an **action** (adds a license to `recommended`, `eliminated`, or appends a `warning`).
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

> **Note:** The system does **not** require a single monolithic `licenses.json`. The merger is called dynamically by the CLI/Slint at startup.

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
│   ├── slint_app.py
│   ├── common.py
│   └── ui/
│       ├── main.slint
│       ├── recommendation.slint
│       ├── analysis.slint
│       └── styles.slint
├── Licenses/                 # License knowledge base
│   ├── Families/             # JSON files grouped by family
│   ├── families_merger.py
│   └── families_deduplicate.py
├── Rules/
│   └── license_rules.pl      # Forward‑chaining rule definitions
├── Tests/                    # (optional) test files
├── Docs/                     # Documentation and case studies
├── main.py                   # Main entry point (CLI + --gui)
├── requirements.txt          # Python dependencies (slint)
├── shell.nix                 # Nix development environment
└── README.md                 # This file
```

---

## Adding or Modifying Licenses

1. Place a new JSON file in `Licenses/Families/` or edit an existing one.
   Use the same schema as the existing files (see `licenses_template.jsonl`).
2. The merger script (`families_merger.py`) will automatically combine all families when the CLI/Slint loads.
3. If you introduce a new condition or permission, update the backward chaining logic in `backward_chain.py` and the relevant rules in `src/Rules/license_rules.pl`.

---

## Extending the Rule Base

Add new rules to `src/Rules/license_rules.pl` using Prolog syntax.

Each rule should define:

- `recommend(License)`: Predicate to recommend a license based on facts.
- `eliminate(License)`: Predicate to eliminate a license based on facts.
- `warning(License, Message)`: Predicate to issue warnings.

The Prolog engine utilizes `assert_step` to log trace information for the explanation facility. For a detailed reference on rule structure, check the existing rules in `src/Rules/license_rules.pl`.

---

## Disclaimer

**This tool is for educational and informational purposes only.**
It does **not** constitute legal advice. License selection involves legal consequences; always consult a qualified lawyer for your specific use case.

---

## Requirements

- Python 3.12+
- `slint` (for the GUI interface)
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
