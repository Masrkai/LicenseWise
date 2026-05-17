"""Gradio web interface for LicenseWise."""

import sys
from pathlib import Path
import gradio as gr

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Inference.backward_chain import backward_chain
from Inference.forward_chain import forward_chain
from Inference.explanation_engine import explain_question, generate_final_report, generate_summary
from Rules.rules import RULES
from interface.cli import load_all_licenses


# Load licenses once at module load
LICENSES_DIR = Path(__file__).parent.parent / "Licenses"
LICENSES_DATA = load_all_licenses(LICENSES_DIR)

# Load custom CSS
CSS_PATH = Path(__file__).parent / "style.css"
CUSTOM_CSS = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""

# ----------------------------------------------------------------------
# Helper to convert facts dict from Gradio inputs
# ----------------------------------------------------------------------
def gather_facts_from_form(
    distribute: str,
    saas: str,
    commercial_use: str,
    need_patent: str,
    want_copyleft: str,
    want_weak_copyleft: str,
    want_file_copyleft: str,
    wants_relicense: str,
    project_type: str,
    linking_type: str,
    modify_library: str,
    want_public_domain: str,
    want_simple_permissive: str,
    academic: str,
    mixed_codebase: str,
    legal_recognition: str,
) -> dict:
    """Convert Gradio string inputs ("yes"/"no"/"skip") to boolean/None facts dict."""
    def to_bool_or_none(val: str):
        if val == "yes":
            return True
        elif val == "no":
            return False
        else:
            return None

    facts = {
        "closed_source": None,
        "saas": to_bool_or_none(saas),
        "commercial_use": to_bool_or_none(commercial_use),
        "need_patent_protection": to_bool_or_none(need_patent),
        "want_copyleft": to_bool_or_none(want_copyleft),
        "want_weak_copyleft": to_bool_or_none(want_weak_copyleft),
        "want_file_copyleft": to_bool_or_none(want_file_copyleft),
        "wants_relicense": to_bool_or_none(wants_relicense),
        "project_type": project_type if project_type != "skip" else None,
        "linking_type": linking_type if linking_type != "skip" else None,
        "modify_library": to_bool_or_none(modify_library),
        "want_public_domain": to_bool_or_none(want_public_domain),
        "want_simple_permissive": to_bool_or_none(want_simple_permissive),
        "academic_project": to_bool_or_none(academic),
        "mixed_open_proprietary": to_bool_or_none(mixed_codebase),
        "concerned_about_legal_recognition": to_bool_or_none(legal_recognition),
    }

    # Handle distribution -> closed_source
    dist_bool = to_bool_or_none(distribute)
    if dist_bool is not None:
        facts["closed_source"] = not dist_bool
    return facts

# ----------------------------------------------------------------------
# Recommendation handler
# ----------------------------------------------------------------------
def recommend_handler(
    distribute, saas, commercial_use, need_patent, want_copyleft,
    want_weak_copyleft, want_file_copyleft, wants_relicense,
    project_type, linking_type, modify_library, want_public_domain,
    want_simple_permissive, academic, mixed_codebase, legal_recognition
):
    facts = gather_facts_from_form(
        distribute, saas, commercial_use, need_patent, want_copyleft,
        want_weak_copyleft, want_file_copyleft, wants_relicense,
        project_type, linking_type, modify_library, want_public_domain,
        want_simple_permissive, academic, mixed_codebase, legal_recognition
    )
    trace = []
    wm = forward_chain(facts, RULES, LICENSES_DATA, trace)
    report = generate_final_report(wm, facts, trace)
    summary = generate_summary(wm, facts, trace)
    return report + "\n\n" + summary

# ----------------------------------------------------------------------
# Analysis handler (backward chaining)
# ----------------------------------------------------------------------
def analysis_handler(license_id, distribute, saas, commercial_use, need_patent, wants_relicense):
    facts = {}
    dist_bool = to_bool_or_none(distribute)
    facts["closed_source"] = not dist_bool if dist_bool is not None else None
    facts["saas"] = to_bool_or_none(saas)
    facts["commercial_use"] = to_bool_or_none(commercial_use)
    facts["need_patent_protection"] = to_bool_or_none(need_patent)
    facts["wants_relicense"] = to_bool_or_none(wants_relicense)

    result = backward_chain(license_id, facts, LICENSES_DATA)
    output = f"## Compatibility Check for {license_id}\n\n"
    if result["compatible"]:
        output += f"✅ **{license_id}** is COMPATIBLE with your intended use.\n\n"
    else:
        output += f"❌ **{license_id}** is NOT COMPATIBLE.\n\n"
    if result["violations"]:
        output += "### Violations\n" + "\n".join(f"- {v}" for v in result["violations"]) + "\n\n"
    output += f"### Analysis\n{result['explanation']}\n\n"
    output += f"### How the engine decided\n{result['how']}"
    return output

# Helper for to_bool_or_none used in analysis
def to_bool_or_none(val):
    if val == "yes":
        return True
    elif val == "no":
        return False
    return None

# ----------------------------------------------------------------------
# Build Gradio interface
# ----------------------------------------------------------------------
def create_interface():
    with gr.Blocks(css=CUSTOM_CSS, title="LicenseWise – KBS License Advisor") as demo:
        gr.Markdown("# 📘 LicenseWise – Knowledge-Based License Recommendation System")
        gr.Markdown("Answer the questions below to get a license recommendation or check a specific license's compatibility.")

        with gr.Tab("License Recommendation"):
            with gr.Row():
                with gr.Column():
                    distribute = gr.Radio(["yes", "no", "skip"], label="Will you distribute your software to others?", value="skip")
                    saas = gr.Radio(["yes", "no", "skip"], label="Will the software be used over a network (SaaS)?", value="skip")
                    commercial_use = gr.Radio(["yes", "no", "skip"], label="Is commercial use intended?", value="skip")
                    need_patent = gr.Radio(["yes", "no", "skip"], label="Do you need patent protection?", value="skip")
                    want_copyleft = gr.Radio(["yes", "no", "skip"], label="Do you want derivatives to remain open source (copyleft)?", value="skip")
                with gr.Column():
                    want_weak_copyleft = gr.Radio(["yes", "no", "skip"], label="Want weak copyleft (library level)?", value="skip")
                    want_file_copyleft = gr.Radio(["yes", "no", "skip"], label="Want file-level copyleft?", value="skip")
                    wants_relicense = gr.Radio(["yes", "no", "skip"], label="Freedom to relicense derivatives?", value="skip")
                    project_type = gr.Radio(["Software", "Library", "Content", "skip"], label="Project type", value="skip")
                    linking_type = gr.Radio(["Dynamic", "Static", "skip"], label="Linking type (if library)", value="skip")
            with gr.Row():
                modify_library = gr.Radio(["yes", "no", "skip"], label="Will you modify the library?", value="skip")
                want_public_domain = gr.Radio(["yes", "no", "skip"], label="Dedicate to public domain?", value="skip")
                want_simple_permissive = gr.Radio(["yes", "no", "skip"], label="Prefer simple permissive license?", value="skip")
                academic = gr.Radio(["yes", "no", "skip"], label="Academic project?", value="skip")
                mixed_codebase = gr.Radio(["yes", "no", "skip"], label="Mixed open/proprietary codebase?", value="skip")
                legal_recognition = gr.Radio(["yes", "no", "skip"], label="Concerned about legal recognition in all jurisdictions?", value="skip")
            recommend_btn = gr.Button("Get Recommendation")
            recommend_output = gr.Markdown("### Results will appear here")

            recommend_btn.click(
                fn=recommend_handler,
                inputs=[
                    distribute, saas, commercial_use, need_patent, want_copyleft,
                    want_weak_copyleft, want_file_copyleft, wants_relicense,
                    project_type, linking_type, modify_library, want_public_domain,
                    want_simple_permissive, academic, mixed_codebase, legal_recognition
                ],
                outputs=recommend_output
            )

        with gr.Tab("License Analysis"):
            with gr.Row():
                license_id = gr.Textbox(label="License SPDX ID (e.g., GPL-3.0, MIT)", placeholder="Enter license identifier")
            with gr.Row():
                distribute_an = gr.Radio(["yes", "no", "skip"], label="Will you distribute?", value="skip")
                saas_an = gr.Radio(["yes", "no", "skip"], label="Used over network (SaaS)?", value="skip")
                commercial_an = gr.Radio(["yes", "no", "skip"], label="Commercial use?", value="skip")
                patent_an = gr.Radio(["yes", "no", "skip"], label="Need patent protection?", value="skip")
                relicense_an = gr.Radio(["yes", "no", "skip"], label="Want to relicense derivatives?", value="skip")
            analyze_btn = gr.Button("Check Compatibility")
            analyze_output = gr.Markdown("### Compatibility results will appear here")

            analyze_btn.click(
                fn=analysis_handler,
                inputs=[license_id, distribute_an, saas_an, commercial_an, patent_an, relicense_an],
                outputs=analyze_output
            )

        gr.Markdown("---\n⚠️ **Disclaimer**: This tool is for educational purposes only. Not legal advice. Consult a qualified lawyer for production use.")

    return demo

def launch_gui():
    demo = create_interface()
    demo.launch(share=False)

if __name__ == "__main__":
    launch_gui()