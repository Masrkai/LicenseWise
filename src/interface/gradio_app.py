"""Gradio web interface for LicenseWise."""

import gradio as gr
from pathlib import Path

from Inference.backward_chain import backward_chain
from Inference.forward_chain import forward_chain
from Inference.explanation_engine import (
    explain_question,
    generate_final_report,
    generate_summary,
)
from interface.common import (
    get_licenses_data,
    yes_no_to_bool,
    distribute_to_closed_source,
    suggest_alternatives,
    build_analysis_facts,
    load_questions,
    YES_NO_SKIP_CHOICES,
    SKIP_VALUE,
)

# Load licenses with proper error handling
try:
    LICENSES_DATA = get_licenses_data()
    LICENSES_LOADED = len(LICENSES_DATA)
    LOAD_ERROR = None
except FileNotFoundError as e:
    LICENSES_DATA = []
    LICENSES_LOADED = 0
    LOAD_ERROR = str(e)

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
    """Convert Gradio string inputs to boolean/None facts dict."""
    facts = {
        "saas": yes_no_to_bool(saas),
        "commercial_use": yes_no_to_bool(commercial_use),
        "need_patent_protection": yes_no_to_bool(need_patent),
        "want_copyleft": yes_no_to_bool(want_copyleft),
        "want_weak_copyleft": yes_no_to_bool(want_weak_copyleft),
        "want_file_copyleft": yes_no_to_bool(want_file_copyleft),
        "wants_relicense": yes_no_to_bool(wants_relicense),
        "project_type": project_type.lower() if project_type != SKIP_VALUE else None,
        "linking_type": linking_type.lower() if linking_type != SKIP_VALUE else None,
        "modify_library": yes_no_to_bool(modify_library),
        "want_public_domain": yes_no_to_bool(want_public_domain),
        "want_simple_permissive": yes_no_to_bool(want_simple_permissive),
        "academic_project": yes_no_to_bool(academic),
        "mixed_open_proprietary": yes_no_to_bool(mixed_codebase),
        "concerned_about_legal_recognition": yes_no_to_bool(legal_recognition),
    }
    dist_bool = yes_no_to_bool(distribute)
    facts["closed_source"] = distribute_to_closed_source(dist_bool)
    return facts


# ----------------------------------------------------------------------
# Recommendation handler
# ----------------------------------------------------------------------
def recommend_handler(
    distribute,
    saas,
    commercial_use,
    need_patent,
    want_copyleft,
    want_weak_copyleft,
    want_file_copyleft,
    wants_relicense,
    project_type,
    linking_type,
    modify_library,
    want_public_domain,
    want_simple_permissive,
    academic,
    mixed_codebase,
    legal_recognition,
):
    """Handle license recommendation request."""
    if LOAD_ERROR:
        return f"\u274c **Error**: Cannot load license data.\n\n{LOAD_ERROR}\n\nPlease ensure licenses.json exists in your project root or Licenses/ directory."

    try:
        facts = gather_facts_from_form(
            distribute,
            saas,
            commercial_use,
            need_patent,
            want_copyleft,
            want_weak_copyleft,
            want_file_copyleft,
            wants_relicense,
            project_type,
            linking_type,
            modify_library,
            want_public_domain,
            want_simple_permissive,
            academic,
            mixed_codebase,
            legal_recognition,
        )
        trace = []
        wm = forward_chain(facts, [], LICENSES_DATA, trace)
        report = generate_final_report(wm, facts, trace)
        summary = generate_summary(wm, facts, trace)
        return report + "\n\n" + summary
    except Exception as e:
        return f"\u274c **Error**: An unexpected error occurred.\n\n```\n{str(e)}\n```"


# ----------------------------------------------------------------------
# Analysis output builders
# ----------------------------------------------------------------------
def _build_compatibility_status(license_id: str, result: dict) -> str:
    """Build the compatibility status section."""
    if result["compatible"] is True:
        return f"## \u2705 **COMPATIBLE**\n\n**{license_id}** is compatible with your intended use.\n\n"
    elif result["compatible"] is False:
        return f"## \u274c **NOT COMPATIBLE**\n\n**{license_id}** is not compatible with your intended use.\n\n"
    return f"## \u2753 **UNCLEAR**\n\nCompatibility could not be determined for **{license_id}**.\n\n"


def _build_violations_section(result: dict) -> str:
    """Build the violations section."""
    if not result.get("violations"):
        return ""
    output = "### \u26a0\ufe0f Violations Found\n\n"
    for v in result["violations"]:
        output += f"- {v}\n"
    return output + "\n"


def _build_explanation_section(result: dict) -> str:
    """Build the analysis/explanation section."""
    if not result.get("explanation"):
        return ""
    return f"### \U0001f4a1 Analysis\n\n{result['explanation']}\n\n"


def _build_reasoning_section(result: dict) -> str:
    """Build the reasoning chain section."""
    if not result.get("how"):
        return ""
    output = "### \U0001f50d Reasoning\n\n"
    for line in result["how"].split("\n"):
        if line.strip():
            output += f"{line}\n"
    return output + "\n"


def _build_warnings_section(result: dict) -> str:
    """Build the warnings section."""
    if not result.get("warnings"):
        return ""
    output = "### \u26a0\ufe0f Warnings\n\n"
    for w in result["warnings"]:
        output += f"- {w}\n"
    return output + "\n"


def _build_license_info_section(result: dict) -> str:
    """Build the license information section."""
    if not result.get("license_info"):
        return ""
    lic = result["license_info"]
    output = "### \U0001f4c4 License Information\n\n"
    output += f"**Name:** {lic.get('name', 'unknown')}  \n"
    output += f"**Type:** {lic.get('type', 'unknown').title()}  \n"
    if lic.get("description"):
        output += f"**Description:** {lic['description']}  \n"

    if lic.get("permissions"):
        perms = lic["permissions"]
        output += "\n**Permissions:**\n"
        for key, label in [
            ("commercial_use", "Commercial use"),
            ("modification", "Modification"),
            ("distribution", "Distribution"),
            ("private_use", "Private use"),
        ]:
            if perms.get(key):
                output += f"- \u2705 {label}\n"

    if lic.get("conditions"):
        conds = lic["conditions"]
        condition_map = [
            ("include_copyright", "Include copyright notice"),
            ("include_license", "Include license text"),
            ("disclose_source", "Disclose source code"),
            ("same_license", "Use same license for derivatives"),
            ("document_changes", "Document changes"),
            ("net_copyleft", "Network copyleft (AGPL-style)"),
        ]
        conditions_list = [label for key, label in condition_map if conds.get(key)]
        if conditions_list:
            output += "\n**Conditions:**\n"
            for cond in conditions_list:
                output += f"- {cond}\n"

    if lic.get("limitations"):
        lims = lic["limitations"]
        output += "\n**Limitations:**\n"
        for key, label in [
            ("liability", "No liability warranty"),
            ("warranty", "No warranty"),
        ]:
            if lims.get(key):
                output += f"- \u26a0\ufe0f {label}\n"
        if not lims.get("patent_use"):
            output += "- \u26a0\ufe0f No patent grant\n"
        if not lims.get("trademark_use"):
            output += "- \u26a0\ufe0f No trademark rights\n"

    return output + "\n"


def _build_suggestions_section(result: dict) -> str:
    """Build the alternative license suggestions section."""
    if result["compatible"] or not result.get("violations"):
        return ""
    all_text = (
        " ".join(result["violations"]).lower()
        + " "
        + result.get("explanation", "").lower()
    )
    suggestions = suggest_alternatives(all_text, format="markdown")
    if not suggestions:
        return ""
    output = "### \U0001f4a1 Alternative Licenses to Consider\n\n"
    for sugg in suggestions:
        output += f"- {sugg}\n"
    return output + "\n"


def _build_disclaimer() -> str:
    """Build the disclaimer footer."""
    return (
        "---\n\n"
        "\u26a0\ufe0f **Disclaimer**: This analysis is for educational purposes only and does not constitute legal advice. "
        "Consult a qualified intellectual property lawyer for production use.\n"
    )


def _build_analysis_output(license_id: str, result: dict) -> str:
    """Build the complete analysis output from a result dict."""
    output = f"# Compatibility Check: {license_id}\n\n"
    output += _build_compatibility_status(license_id, result)
    output += _build_violations_section(result)
    output += _build_explanation_section(result)
    output += _build_reasoning_section(result)
    output += _build_warnings_section(result)
    output += _build_license_info_section(result)
    output += _build_suggestions_section(result)
    output += _build_disclaimer()
    return output


# ----------------------------------------------------------------------
# Analysis handler (backward chaining)
# ----------------------------------------------------------------------
def analysis_handler(
    license_id, distribute, saas, commercial_use, need_patent, wants_relicense
):
    """Handle license compatibility analysis with enhanced output."""
    if LOAD_ERROR:
        return f"\u274c **Error**: Cannot load license data.\n\n{LOAD_ERROR}\n\nPlease ensure licenses.json exists in your project root or Licenses/ directory."

    if not license_id or not license_id.strip():
        return "\u26a0\ufe0f **Please enter a license SPDX ID** (e.g., MIT, GPL-3.0, Apache-2.0)"

    try:
        facts = build_analysis_facts(
            distribute=distribute,
            saas=saas,
            commercial_use=commercial_use,
            need_patent=need_patent,
            wants_relicense=wants_relicense,
        )
        result = backward_chain(license_id.strip(), facts, LICENSES_DATA)
        return _build_analysis_output(license_id.strip(), result)
    except Exception as e:
        return f"\u274c **Error**: An unexpected error occurred during analysis.\n\n```\n{str(e)}\n```"


# ----------------------------------------------------------------------
# Build Gradio interface
# ----------------------------------------------------------------------
def _create_recommendation_tab():
    """Build the License Recommendation tab."""
    with gr.Tab("\U0001f4cb License Recommendation"):
        gr.Markdown("### Project Requirements")
        gr.Markdown(
            "Fill out the form below to get personalized license recommendations based on your project's needs."
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown("**Distribution & Usage**")
                distribute = gr.Radio(
                    YES_NO_SKIP_CHOICES,
                    label="Will you distribute your software to others?",
                    value=SKIP_VALUE,
                    info="Distribution means giving copies to other people/organizations",
                )
                saas = gr.Radio(
                    YES_NO_SKIP_CHOICES,
                    label="Will the software be used over a network (SaaS)?",
                    value=SKIP_VALUE,
                    info="Network use = users access it via web/API without downloading",
                )
                commercial_use = gr.Radio(
                    YES_NO_SKIP_CHOICES,
                    label="Is commercial use intended?",
                    value=SKIP_VALUE,
                    info="Will this be used to make money or in a commercial product?",
                )
                need_patent = gr.Radio(
                    YES_NO_SKIP_CHOICES,
                    label="Do you need patent protection?",
                    value=SKIP_VALUE,
                    info="Patent grants protect you from patent claims",
                )
                want_copyleft = gr.Radio(
                    YES_NO_SKIP_CHOICES,
                    label="Do you want derivatives to remain open source (copyleft)?",
                    value=SKIP_VALUE,
                    info="Copyleft ensures modifications stay open source",
                )

            with gr.Column():
                gr.Markdown("**License Preferences**")
                want_weak_copyleft = gr.Radio(
                    YES_NO_SKIP_CHOICES,
                    label="Want weak copyleft (library level)?",
                    value=SKIP_VALUE,
                    info="Library can be used in proprietary software",
                )
                want_file_copyleft = gr.Radio(
                    YES_NO_SKIP_CHOICES,
                    label="Want file-level copyleft?",
                    value=SKIP_VALUE,
                    info="Only modified files must remain open",
                )
                wants_relicense = gr.Radio(
                    YES_NO_SKIP_CHOICES,
                    label="Freedom to relicense derivatives?",
                    value=SKIP_VALUE,
                    info="Can derivatives use different licenses?",
                )
                project_type = gr.Radio(
                    ["Software", "Library", "Content", SKIP_VALUE],
                    label="Project type",
                    value=SKIP_VALUE,
                )
                linking_type = gr.Radio(
                    ["Dynamic", "Static", SKIP_VALUE],
                    label="Linking type (if library)",
                    value=SKIP_VALUE,
                )

        with gr.Row():
            modify_library = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Will you modify the library?",
                value=SKIP_VALUE,
            )
            want_public_domain = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Dedicate to public domain?",
                value=SKIP_VALUE,
            )
            want_simple_permissive = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Prefer simple permissive license?",
                value=SKIP_VALUE,
            )

        with gr.Row():
            academic = gr.Radio(
                YES_NO_SKIP_CHOICES, label="Academic project?", value=SKIP_VALUE
            )
            mixed_codebase = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Mixed open/proprietary codebase?",
                value=SKIP_VALUE,
            )
            legal_recognition = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Concerned about legal recognition?",
                value=SKIP_VALUE,
            )

        recommend_btn = gr.Button(
            "\U0001f50d Get Recommendation", variant="primary", size="lg"
        )
        recommend_output = gr.Markdown(
            "### Results will appear here after clicking the button above"
        )

    return {
        "distribute": distribute,
        "saas": saas,
        "commercial_use": commercial_use,
        "need_patent": need_patent,
        "want_copyleft": want_copyleft,
        "want_weak_copyleft": want_weak_copyleft,
        "want_file_copyleft": want_file_copyleft,
        "wants_relicense": wants_relicense,
        "project_type": project_type,
        "linking_type": linking_type,
        "modify_library": modify_library,
        "want_public_domain": want_public_domain,
        "want_simple_permissive": want_simple_permissive,
        "academic": academic,
        "mixed_codebase": mixed_codebase,
        "legal_recognition": legal_recognition,
        "recommend_btn": recommend_btn,
        "recommend_output": recommend_output,
    }


def _create_analysis_tab():
    """Build the License Analysis tab."""
    with gr.Tab("\U0001f50d License Analysis"):
        gr.Markdown("### Check License Compatibility")
        gr.Markdown(
            "Enter a license ID and answer questions about your use case to check compatibility."
        )

        with gr.Row():
            license_id = gr.Textbox(
                label="License SPDX ID",
                placeholder="e.g., MIT, GPL-3.0, Apache-2.0, BSD-2-Clause",
                info="Enter the SPDX identifier for the license you want to analyze",
            )

        gr.Markdown("**Your Use Case**")
        with gr.Row():
            distribute_an = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Will you distribute?",
                value=SKIP_VALUE,
                info="Give copies to others?",
            )
            saas_an = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Used over network (SaaS)?",
                value=SKIP_VALUE,
                info="Web service / API?",
            )
            commercial_an = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Commercial use?",
                value=SKIP_VALUE,
                info="For profit?",
            )

        with gr.Row():
            patent_an = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Need patent protection?",
                value=SKIP_VALUE,
                info="Want patent grants?",
            )
            relicense_an = gr.Radio(
                YES_NO_SKIP_CHOICES,
                label="Want to relicense derivatives?",
                value=SKIP_VALUE,
                info="Use different license?",
            )

        analyze_btn = gr.Button(
            "\u2705 Check Compatibility", variant="primary", size="lg"
        )
        analyze_output = gr.Markdown(
            "### Compatibility results will appear here after clicking the button above"
        )

    return {
        "license_id": license_id,
        "distribute_an": distribute_an,
        "saas_an": saas_an,
        "commercial_an": commercial_an,
        "patent_an": patent_an,
        "relicense_an": relicense_an,
        "analyze_btn": analyze_btn,
        "analyze_output": analyze_output,
    }


def create_interface():
    """Create the Gradio interface with enhanced layout and error handling."""
    with gr.Blocks(css=CUSTOM_CSS, title="LicenseWise \u2013 KBS License Advisor") as demo:
        # Header
        gr.Markdown("# \U0001f4d8 LicenseWise \u2013 Knowledge-Based License Recommendation System")

        # Show license loading status
        if LOAD_ERROR:
            gr.Markdown(
                f"\u26a0\ufe0f **Warning**: Could not load license database. {LICENSES_LOADED} licenses loaded.\n\n{LOAD_ERROR}"
            )
        else:
            gr.Markdown(
                f"\u2705 Successfully loaded **{LICENSES_LOADED} licenses** from database."
            )

        gr.Markdown(
            "Answer the questions below to get a license recommendation or check a specific license's compatibility."
        )

        # Build tabs
        rec = _create_recommendation_tab()
        ana = _create_analysis_tab()

        # Wire recommendation tab
        rec["recommend_btn"].click(
            fn=recommend_handler,
            inputs=[
                rec["distribute"],
                rec["saas"],
                rec["commercial_use"],
                rec["need_patent"],
                rec["want_copyleft"],
                rec["want_weak_copyleft"],
                rec["want_file_copyleft"],
                rec["wants_relicense"],
                rec["project_type"],
                rec["linking_type"],
                rec["modify_library"],
                rec["want_public_domain"],
                rec["want_simple_permissive"],
                rec["academic"],
                rec["mixed_codebase"],
                rec["legal_recognition"],
            ],
            outputs=rec["recommend_output"],
        )

        # Wire analysis tab
        ana["analyze_btn"].click(
            fn=analysis_handler,
            inputs=[
                ana["license_id"],
                ana["distribute_an"],
                ana["saas_an"],
                ana["commercial_an"],
                ana["patent_an"],
                ana["relicense_an"],
            ],
            outputs=ana["analyze_output"],
        )

        # Footer
        gr.Markdown("---")
        gr.Markdown(
            "\u26a0\ufe0f **Disclaimer**: This tool is for educational purposes only and does not constitute legal advice. "
            "Always consult a qualified intellectual property lawyer for production use."
        )
        if not LOAD_ERROR:
            gr.Markdown(f"*Database: {LICENSES_LOADED} licenses loaded from JSON*")

    return demo


def launch_gui():
    """Launch the Gradio interface."""
    demo = create_interface()
    demo.launch(share=False)


if __name__ == "__main__":
    launch_gui()
