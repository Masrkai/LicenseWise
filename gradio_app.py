"""
LicenseWise – Gradio GUI
interface/gradio_app.py

Two modes exposed as tabs:
  1. License Recommender  – forward-chaining wizard that narrows down licenses
                            based on project goals and outputs a ranked result
                            with step-by-step reasoning trace.
  2. Compliance Checker   – backward-chaining mode: user picks a license and
                            a use-case; system verifies compatibility and
                            explains every condition checked.
  3. License Browser      – searchable, filterable view of the full knowledge base
                            loaded from _Licenses/licenses.json (or family files).

Run:
    pip install gradio>=4.0
    python interface/gradio_app.py

The file is designed to work whether or not the inference/ modules exist yet.
If they are missing it falls back to a built-in lightweight engine so the GUI
is always runnable during development.
"""

import json
import os
import sys
import importlib.util
from pathlib import Path
from typing import Any

import gradio as gr
from interface.graphs import build_graphs_tab

# ---------------------------------------------------------------------------
# Path setup – works when launched from repo root OR from interface/ directly
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
LICENSES_PATH = REPO_ROOT / "_Licenses" / "licenses.json"
FAMILIES_DIR  = REPO_ROOT / "_Licenses" / "Families"

sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Load knowledge base
# ---------------------------------------------------------------------------

def _load_licenses() -> list[dict]:
    """Load licenses from licenses.json, or fall back to merging family files."""
    if LICENSES_PATH.exists():
        with open(LICENSES_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("licenses", data) if isinstance(data, dict) else data

    if FAMILIES_DIR.exists():
        seen, result = set(), []
        for path in sorted(FAMILIES_DIR.glob("*.json")):
            with open(path, encoding="utf-8") as f:
                family_data = json.load(f)
            for lic in family_data.get("licenses", []):
                key = lic.get("spdx_id") or lic.get("id")
                if key not in seen:
                    seen.add(key)
                    result.append(lic)
        return result

    return []

LICENSES: list[dict] = _load_licenses()
LICENSE_MAP: dict[str, dict] = {
    (l.get("spdx_id") or l.get("id")): l for l in LICENSES
}

# ---------------------------------------------------------------------------
# Try to import project inference modules; fall back to built-in engine
# ---------------------------------------------------------------------------

def _try_import(module_name: str):
    spec = importlib.util.find_spec(module_name)
    return importlib.import_module(module_name) if spec else None

forward_mod  = _try_import("inference.forward_chainer")
backward_mod = _try_import("inference.backward_chainer")
explain_mod  = _try_import("inference.explanation_engine")

# ---------------------------------------------------------------------------
# Built-in lightweight inference (used when project modules are absent)
# ---------------------------------------------------------------------------

class BuiltinForwardChainer:
    """
    Simple scoring engine.
    Each license starts at 0 and gains/loses points based on
    the user's project attributes. Returns a ranked list with
    a reasoning trace.
    """

    def recommend(self, answers: dict) -> list[dict]:
        results = []
        for lic in LICENSES:
            score = 0
            trace = []
            perms = lic.get("permissions", {})
            conds = lic.get("conditions", {})
            lims  = lic.get("limitations", {})
            meta  = lic.get("metadata", {})

            # Rule 1 – commercial use
            if answers.get("commercial"):
                if perms.get("commercial_use"):
                    score += 20
                    trace.append("✅ Allows commercial use (+20)")
                else:
                    score -= 40
                    trace.append("❌ Prohibits commercial use (–40)")

            # Rule 2 – distribution
            if answers.get("distribute"):
                if perms.get("distribution"):
                    score += 10
                    trace.append("✅ Distribution permitted (+10)")
                else:
                    score -= 30
                    trace.append("❌ Distribution not permitted (–30)")

            # Rule 3 – keep modifications private
            if answers.get("keep_private"):
                if conds.get("disclose_source"):
                    score -= 35
                    trace.append("❌ Requires source disclosure – conflicts with keeping changes private (–35)")
                else:
                    score += 15
                    trace.append("✅ Does not require source disclosure (+15)")

            # Rule 4 – want derivatives to stay open
            if answers.get("copyleft"):
                if conds.get("same_license"):
                    score += 20
                    trace.append("✅ Same-license (copyleft) requirement aligns with goal (+20)")
                else:
                    score += 0
                    trace.append("ℹ️  No copyleft clause (neutral for this goal)")
            else:
                if conds.get("same_license"):
                    score -= 15
                    trace.append("⚠️  Copyleft clause unwanted by user (–15)")
                else:
                    score += 10
                    trace.append("✅ No copyleft clause (+10)")

            # Rule 5 – patent protection needed
            if answers.get("patent"):
                if not lims.get("patent_use"):
                    score += 20
                    trace.append("✅ Grants explicit patent rights (+20)")
                else:
                    score -= 20
                    trace.append("❌ Restricts patent use (–20)")

            # Rule 6 – SaaS / network distribution
            if answers.get("saas"):
                if conds.get("net_copyleft"):
                    score -= 25
                    trace.append("⚠️  Network copyleft clause (AGPL-style) – forces source release for SaaS (–25)")
                else:
                    score += 5
                    trace.append("✅ No network copyleft clause (+5)")

            # Rule 7 – OSI approved preference
            if answers.get("osi_only") and not meta.get("osi_approved"):
                score -= 50
                trace.append("❌ Not OSI-approved – filtered out (–50)")

            # Rule 8 – minimal conditions preference
            if answers.get("minimal_conditions"):
                burden = sum([
                    conds.get("document_changes", False),
                    conds.get("disclose_source", False),
                    conds.get("same_license", False),
                    conds.get("net_copyleft", False),
                ])
                score -= burden * 5
                if burden:
                    trace.append(f"ℹ️  {burden} extra condition(s) reduce ranking (–{burden*5})")

            results.append({
                "id":    lic.get("spdx_id") or lic.get("id"),
                "name":  lic.get("name", ""),
                "type":  lic.get("type", ""),
                "score": score,
                "trace": trace,
                "hint":  lic.get("metadata", {}).get("explanation_hint", ""),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]


class BuiltinBackwardChainer:
    """
    Checks whether a given license permits a specific use-case
    by verifying each relevant condition.
    """

    USE_CASES = {
        "Commercial use in a product": ["commercial_use_ok"],
        "Distribute binary without source": ["distribute_binary_ok"],
        "Modify and keep changes private": ["keep_private_ok"],
        "Use in a SaaS / network service": ["saas_ok"],
        "Static-link into proprietary app": ["static_link_ok"],
        "Use as a dependency (dynamic link)": ["dynamic_link_ok"],
    }

    def check(self, license_id: str, use_case: str) -> dict:
        lic = LICENSE_MAP.get(license_id)
        if not lic:
            return {"compatible": False, "steps": [f"License '{license_id}' not found in knowledge base."]}

        perms = lic.get("permissions", {})
        conds = lic.get("conditions", {})
        steps = []
        compatible = True

        steps.append(f"🔍 Checking **{lic.get('name')}** for use-case: *{use_case}*\n")

        if use_case == "Commercial use in a product":
            if perms.get("commercial_use"):
                steps.append("✅ `commercial_use = true` → Commercial use is allowed.")
            else:
                steps.append("❌ `commercial_use = false` → Commercial use is **NOT** allowed.")
                compatible = False

        elif use_case == "Distribute binary without source":
            if perms.get("distribution"):
                steps.append("✅ `distribution = true` → Distribution is permitted.")
            else:
                steps.append("❌ `distribution = false` → Distribution is **NOT** permitted.")
                compatible = False
            if conds.get("disclose_source"):
                steps.append("❌ `disclose_source = true` → Must include source code when distributing.")
                compatible = False
            else:
                steps.append("✅ `disclose_source = false` → Binary-only distribution is fine.")

        elif use_case == "Modify and keep changes private":
            if conds.get("disclose_source"):
                steps.append("❌ `disclose_source = true` → Must publish modified source.")
                compatible = False
            else:
                steps.append("✅ `disclose_source = false` → Modifications can stay private.")
            if conds.get("same_license"):
                steps.append("⚠️  `same_license = true` → If you distribute, derivatives must use same license.")

        elif use_case == "Use in a SaaS / network service":
            if conds.get("net_copyleft"):
                steps.append("❌ `net_copyleft = true` → Network use triggers source-disclosure obligation (AGPL-style).")
                compatible = False
            else:
                steps.append("✅ `net_copyleft = false` → No network copyleft clause. SaaS use is permitted.")

        elif use_case == "Static-link into proprietary app":
            if conds.get("same_license"):
                steps.append("❌ `same_license = true` → Strong copyleft; static linking infects the whole app.")
                compatible = False
            elif conds.get("disclose_source"):
                steps.append("⚠️  `disclose_source = true` → Weak copyleft; static linking may require source disclosure. Confirm with legal counsel.")
                compatible = None  # uncertain
            else:
                steps.append("✅ No copyleft – static linking into proprietary code is permitted.")

        elif use_case == "Use as a dependency (dynamic link)":
            if conds.get("same_license") and lic.get("type") != "weak_copyleft":
                steps.append("❌ Strong copyleft – dynamic linking may still trigger copyleft.")
                compatible = False
            else:
                steps.append("✅ Dynamic linking is generally safe with this license.")

        else:
            steps.append("ℹ️  Use-case not in the built-in rule set. Manual review required.")
            compatible = None

        hint = lic.get("metadata", {}).get("explanation_hint", "")
        if hint:
            steps.append(f"\n💡 **Tip:** {hint}")

        return {
            "compatible": compatible,
            "steps": steps,
            "license": lic,
        }


# Instantiate engines (project modules take priority)
_fc = forward_mod.ForwardChainer()  if forward_mod  and hasattr(forward_mod,  "ForwardChainer")  else BuiltinForwardChainer()
_bc = backward_mod.BackwardChainer() if backward_mod and hasattr(backward_mod, "BackwardChainer") else BuiltinBackwardChainer()

# ---------------------------------------------------------------------------
# Helper formatters
# ---------------------------------------------------------------------------

TYPE_EMOJI = {
    "permissive":    "🟢",
    "weak_copyleft": "🟡",
    "copyleft":      "🟠",
    "other":         "🔵",
    "proprietary":   "🔴",
}


def _fmt_recommendation(results: list[dict]) -> tuple[str, str]:
    """Returns (summary_markdown, reasoning_markdown)."""
    if not results:
        return "No licenses matched your criteria.", ""

    top = results[0]
    summary_lines = ["## Recommended Licenses\n"]
    for i, r in enumerate(results, 1):
        emoji = TYPE_EMOJI.get(r["type"], "⚪")
        bar_pct = max(0, min(100, r["score"]))
        bar = "█" * (bar_pct // 5) + "░" * (20 - bar_pct // 5)
        summary_lines.append(
            f"### {i}. {emoji} {r['id']}\n"
            f"**{r['name']}** · *{r['type']}*\n\n"
            f"`Score: {r['score']:+d}` `{bar}`\n\n"
            f"> {r['hint']}\n"
        )

    reasoning_lines = ["## Reasoning Trace\n"]
    for i, r in enumerate(results[:3], 1):
        reasoning_lines.append(f"### {i}. {r['id']}")
        reasoning_lines += r["trace"]
        reasoning_lines.append("")

    return "\n".join(summary_lines), "\n".join(reasoning_lines)


def _fmt_compliance(result: dict) -> str:
    compatible = result.get("compatible")
    steps = result.get("steps", [])

    if compatible is True:
        verdict = "## ✅ Compatible\nThis use-case is permitted under the selected license.\n"
    elif compatible is False:
        verdict = "## ❌ Not Compatible\nThis use-case is **not** permitted under the selected license.\n"
    else:
        verdict = "## ⚠️ Uncertain\nCompatibility depends on interpretation. Consult legal counsel.\n"

    return verdict + "\n---\n\n" + "\n\n".join(steps)


def _fmt_license_detail(lic: dict) -> str:
    if not lic:
        return ""
    perms = lic.get("permissions", {})
    conds = lic.get("conditions", {})
    lims  = lic.get("limitations", {})
    meta  = lic.get("metadata", {})

    def _bool(v): return "✅ Yes" if v else "❌ No"

    lines = [
        f"## {lic.get('name', lic.get('id'))}",
        f"**SPDX ID:** `{lic.get('spdx_id') or lic.get('id')}`  "
        f"**Type:** {TYPE_EMOJI.get(lic.get('type',''), '')} {lic.get('type','')}",
        f"\n{lic.get('description', '')}\n",
        "### Permissions",
        f"- Commercial use: {_bool(perms.get('commercial_use'))}",
        f"- Distribution: {_bool(perms.get('distribution'))}",
        f"- Modification: {_bool(perms.get('modification'))}",
        f"- Private use: {_bool(perms.get('private_use'))}",
        "### Conditions",
        f"- Include copyright: {_bool(conds.get('include_copyright'))}",
        f"- Document changes: {_bool(conds.get('document_changes'))}",
        f"- Disclose source: {_bool(conds.get('disclose_source'))}",
        f"- Same license (copyleft): {_bool(conds.get('same_license'))}",
        f"- Network copyleft: {_bool(conds.get('net_copyleft'))}",
        "### Limitations",
        f"- No liability: {_bool(lims.get('liability'))}",
        f"- No warranty: {_bool(lims.get('warranty'))}",
        f"- Trademark restricted: {_bool(lims.get('trademark_use'))}",
        f"- Patent restricted: {_bool(lims.get('patent_use'))}",
        "### Metadata",
        f"- OSI approved: {_bool(meta.get('osi_approved'))}",
        f"- FSF free: {_bool(meta.get('fsf_free'))}",
    ]
    hint = meta.get("explanation_hint")
    if hint:
        lines += ["### When to use", f"> {hint}"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tab 1 – License Recommender
# ---------------------------------------------------------------------------

def run_recommender(
    commercial, distribute, keep_private, copyleft,
    patent, saas, osi_only, minimal_conditions
) -> tuple[str, str]:
    answers = {
        "commercial":         commercial,
        "distribute":         distribute,
        "keep_private":       keep_private,
        "copyleft":           copyleft,
        "patent":             patent,
        "saas":               saas,
        "osi_only":           osi_only,
        "minimal_conditions": minimal_conditions,
    }
    results = _fc.recommend(answers)
    return _fmt_recommendation(results)


def build_recommender_tab():
    with gr.Tab("🔍 License Recommender"):
        gr.Markdown(
            "## Find the right license for your project\n"
            "Answer the questions below and the inference engine will rank licenses "
            "by how well they match your goals, with a full reasoning trace."
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Project attributes")
                commercial   = gr.Checkbox(label="Commercial use intended",           value=True)
                distribute   = gr.Checkbox(label="Will distribute the software",      value=True)
                keep_private = gr.Checkbox(label="Want to keep modifications private", value=False)
                copyleft     = gr.Checkbox(label="Want derivatives to stay open-source", value=False)
                patent       = gr.Checkbox(label="Patent protection is important",    value=False)
                saas         = gr.Checkbox(label="Deploying as a SaaS / web service", value=False)
                gr.Markdown("### Preferences")
                osi_only     = gr.Checkbox(label="OSI-approved licenses only",        value=True)
                minimal_cond = gr.Checkbox(label="Prefer licenses with minimal conditions", value=False)

                run_btn = gr.Button("Recommend licenses ↗", variant="primary")

            with gr.Column(scale=2):
                summary_out   = gr.Markdown(label="Recommendations")
                reasoning_out = gr.Markdown(label="Reasoning trace")

        run_btn.click(
            fn=run_recommender,
            inputs=[commercial, distribute, keep_private, copyleft,
                    patent, saas, osi_only, minimal_cond],
            outputs=[summary_out, reasoning_out],
        )


# ---------------------------------------------------------------------------
# Tab 2 – Compliance Checker
# ---------------------------------------------------------------------------

def run_compliance(license_id: str, use_case: str) -> str:
    if not license_id:
        return "Please select a license."
    result = _bc.check(license_id, use_case)
    return _fmt_compliance(result)


def build_compliance_tab():
    all_ids = sorted(LICENSE_MAP.keys())
    use_cases = list(BuiltinBackwardChainer.USE_CASES.keys())

    with gr.Tab("⚖️ Compliance Checker"):
        gr.Markdown(
            "## Can I use this license for my use-case?\n"
            "Select a license and an intended use. The system works backward "
            "from your goal to verify each condition."
        )

        with gr.Row():
            with gr.Column(scale=1):
                lic_dropdown  = gr.Dropdown(choices=all_ids, label="License (SPDX ID)", value=all_ids[0] if all_ids else None)
                use_dropdown  = gr.Dropdown(choices=use_cases, label="Intended use-case", value=use_cases[0])
                check_btn     = gr.Button("Check compliance ↗", variant="primary")

            with gr.Column(scale=2):
                compliance_out = gr.Markdown(label="Compliance result")

        check_btn.click(
            fn=run_compliance,
            inputs=[lic_dropdown, use_dropdown],
            outputs=[compliance_out],
        )


# ---------------------------------------------------------------------------
# Tab 3 – License Browser
# ---------------------------------------------------------------------------

TYPE_FILTER_OPTIONS = ["All"] + sorted({l.get("type", "") for l in LICENSES if l.get("type")})
OSI_FILTER_OPTIONS  = ["All", "OSI Approved", "Not OSI Approved"]


def filter_licenses(search: str, type_filter: str, osi_filter: str) -> tuple[list[list], str]:
    results = []
    for lic in LICENSES:
        # Search filter
        q = search.strip().lower()
        if q and q not in (lic.get("id") or "").lower() \
               and q not in (lic.get("spdx_id") or "").lower() \
               and q not in (lic.get("name") or "").lower() \
               and q not in (lic.get("description") or "").lower():
            continue

        # Type filter
        if type_filter != "All" and lic.get("type") != type_filter:
            continue

        # OSI filter
        osi = lic.get("metadata", {}).get("osi_approved", False)
        if osi_filter == "OSI Approved" and not osi:
            continue
        if osi_filter == "Not OSI Approved" and osi:
            continue

        emoji = TYPE_EMOJI.get(lic.get("type", ""), "⚪")
        results.append([
            lic.get("spdx_id") or lic.get("id"),
            lic.get("name"),
            f"{emoji} {lic.get('type','')}",
            "✅" if osi else "❌",
            "✅" if lic.get("metadata", {}).get("fsf_free") else "❌",
        ])

    count_md = f"**{len(results)} license(s) found**"
    return results, count_md


def show_license_detail(evt: gr.SelectData, data: list[list]) -> str:
    try:
        row_idx = evt.index[0]
        lic_id  = data[row_idx][0]
        lic     = LICENSE_MAP.get(lic_id)
        return _fmt_license_detail(lic) if lic else f"License `{lic_id}` not found."
    except Exception as e:
        return f"Error loading license: {e}"


def build_browser_tab():
    with gr.Tab("📚 License Browser"):
        gr.Markdown(
            "## Browse the knowledge base\n"
            "Search and filter all licenses. Click a row to see full details."
        )

        with gr.Row():
            search_box   = gr.Textbox(placeholder="Search by ID, name, or keyword…", label="Search", scale=3)
            type_filter  = gr.Dropdown(choices=TYPE_FILTER_OPTIONS, value="All", label="Type", scale=1)
            osi_filter   = gr.Dropdown(choices=OSI_FILTER_OPTIONS,  value="All", label="OSI status", scale=1)

        count_label = gr.Markdown()

        table = gr.Dataframe(
            headers=["SPDX ID", "Name", "Type", "OSI", "FSF Free"],
            datatype=["str", "str", "str", "str", "str"],
            interactive=False,
            wrap=True,
        )

        detail_out = gr.Markdown(label="License details")

        # Initial population
        initial_rows, initial_count = filter_licenses("", "All", "All")
        table.value      = initial_rows
        count_label.value = initial_count

        def _filter(s, t, o):
            rows, count = filter_licenses(s, t, o)
            return rows, count

        for inp in [search_box, type_filter, osi_filter]:
            inp.change(fn=_filter, inputs=[search_box, type_filter, osi_filter],
                       outputs=[table, count_label])

        table.select(fn=show_license_detail, inputs=[table], outputs=[detail_out])


# ---------------------------------------------------------------------------
# Tab 4 – About / Disclaimer
# ---------------------------------------------------------------------------

def build_about_tab():
    with gr.Tab("ℹ️ About"):
        gr.Markdown("""
## LicenseWise

**Intelligent Software License Selection & Compliance Analyzer**

A knowledge-based expert system built as a CS academic project.

### Architecture

```
LicenseWise/
├── _Licenses/
│   ├── licenses.json          ← merged knowledge base
│   └── Families/              ← per-family JSON files
├── inference/
│   ├── forward_chainer.py     ← license recommendation
│   ├── backward_chainer.py    ← compliance checking
│   └── explanation_engine.py  ← reasoning trace
├── interface/
│   └── gradio_app.py          ← this file
└── main.py
```

### Inference modes

| Tab | Strategy | Description |
|-----|----------|-------------|
| Recommender | Forward chaining | User attributes → rules fire → ranked license list |
| Compliance | Backward chaining | Goal → system works backward → verifies conditions |

### Disclaimer

> This tool is built by CS students and is **not legal advice**.
> Results are based on a rule-based knowledge system and should not
> be treated as definitive legal guidance. Always consult a qualified
> lawyer before making license decisions that affect your product.

### Sources
- [SPDX License List](https://spdx.org/licenses/)
- [OSI Approved Licenses](https://opensource.org/licenses/)
- [FSF License List](https://www.gnu.org/licenses/license-list.html)
- [Creative Commons](https://creativecommons.org/licenses/)
        """)


# ---------------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------------

def build_app() -> gr.Blocks:
    with gr.Blocks(
        title="LicenseWise",
        theme=gr.themes.Default(
            primary_hue="indigo",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
        css="""
        .gradio-container { max-width: 1100px !important; margin: auto; }
        .tab-nav button { font-size: 15px; }
        """
    ) as app:
        gr.Markdown(
            "# ⚖️ LicenseWise\n"
            "*Intelligent Software License Selection & Compliance Analyzer*  \n"
            f"Knowledge base: **{len(LICENSES)} licenses** loaded"
        )

        build_recommender_tab()
        build_compliance_tab()
        build_browser_tab()
        build_graphs_tab(LICENSES)
        build_about_tab()

    return app


if __name__ == "__main__":
    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=False,
        show_error=True,
    )
