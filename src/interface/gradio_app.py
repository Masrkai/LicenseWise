"""Gradio web interface for LicenseWise."""

import sys
from pathlib import Path
import gradio as gr

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
    """Convert Gradio string inputs ("yes"/"no"/"skip") to boolean/None facts dict."""
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

    # Handle distribution -> closed_source using shared utility
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
        return f"❌ **Error**: Cannot load license data.\n\n{LOAD_ERROR}\n\nPlease ensure licenses.json exists in your project root or Licenses/ directory."

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
        return f"❌ **Error**: An unexpected error occurred.\n\n```\n{str(e)}\n```"


# ----------------------------------------------------------------------
# Analysis handler (backward chaining) - ENHANCED VERSION
# ----------------------------------------------------------------------
def analysis_handler(
    license_id, distribute, saas, commercial_use, need_patent, wants_relicense
):
    """Handle license compatibility analysis with enhanced output."""
    if LOAD_ERROR:
        return f"❌ **Error**: Cannot load license data.\n\n{LOAD_ERROR}\n\nPlease ensure licenses.json exists in your project root or Licenses/ directory."

    if not license_id or not license_id.strip():
        return "⚠️ **Please enter a license SPDX ID** (e.g., MIT, GPL-3.0, Apache-2.0)"

    license_id = license_id.strip()

    try:
        # Gather facts
        facts = {}
        dist_bool = yes_no_to_bool(distribute)
        facts["closed_source"] = distribute_to_closed_source(dist_bool)
        facts["saas"] = yes_no_to_bool(saas)
        facts["commercial_use"] = yes_no_to_bool(commercial_use)
        facts["need_patent_protection"] = yes_no_to_bool(need_patent)
        facts["wants_relicense"] = yes_no_to_bool(wants_relicense)

        # Run backward chain
        result = backward_chain(license_id, facts, LICENSES_DATA)

        # Build enhanced output
        output = f"# Compatibility Check: {license_id}\n\n"

        # Compatibility status
        if result["compatible"] is True:
            output += f"## ✅ **COMPATIBLE**\n\n**{license_id}** is compatible with your intended use.\n\n"
        elif result["compatible"] is False:
            output += f"## ❌ **NOT COMPATIBLE**\n\n**{license_id}** is not compatible with your intended use.\n\n"
        else:
            output += f"## ❓ **UNCLEAR**\n\nCompatibility could not be determined for **{license_id}**.\n\n"

        # Violations section
        if result.get("violations"):
            output += "### ⚠️ Violations Found\n\n"
            for v in result["violations"]:
                output += f"- {v}\n"
            output += "\n"

        # Analysis/Explanation
        if result.get("explanation"):
            output += "### 💡 Analysis\n\n"
            output += f"{result['explanation']}\n\n"

        # Reasoning chain
        if result.get("how"):
            output += "### 🔍 Reasoning\n\n"
            # Format the reasoning with better structure
            reasoning_lines = result["how"].split("\n")
            for line in reasoning_lines:
                if line.strip():
                    output += f"{line}\n"
            output += "\n"

        # Warnings
        if result.get("warnings"):
            output += "### ⚠️ Warnings\n\n"
            for w in result["warnings"]:
                output += f"- {w}\n"
            output += "\n"

        # License information
        if result.get("license_info"):
            lic = result["license_info"]
            output += "### 📄 License Information\n\n"
            output += f"**Name:** {lic.get('name', license_id)}  \n"
            output += f"**Type:** {lic.get('type', 'unknown').title()}  \n"
            if lic.get("description"):
                output += f"**Description:** {lic['description']}  \n"

            # Add permissions, conditions, limitations if available
            if lic.get("permissions"):
                perms = lic["permissions"]
                output += f"\n**Permissions:**\n"
                if perms.get("commercial_use"):
                    output += "- ✅ Commercial use\n"
                if perms.get("modification"):
                    output += "- ✅ Modification\n"
                if perms.get("distribution"):
                    output += "- ✅ Distribution\n"
                if perms.get("private_use"):
                    output += "- ✅ Private use\n"

            if lic.get("conditions"):
                conds = lic["conditions"]
                conditions_list = []
                if conds.get("include_copyright"):
                    conditions_list.append("Include copyright notice")
                if conds.get("include_license"):
                    conditions_list.append("Include license text")
                if conds.get("disclose_source"):
                    conditions_list.append("Disclose source code")
                if conds.get("same_license"):
                    conditions_list.append("Use same license for derivatives")
                if conds.get("document_changes"):
                    conditions_list.append("Document changes")
                if conds.get("net_copyleft"):
                    conditions_list.append("Network copyleft (AGPL-style)")

                if conditions_list:
                    output += f"\n**Conditions:**\n"
                    for cond in conditions_list:
                        output += f"- {cond}\n"

            if lic.get("limitations"):
                lims = lic["limitations"]
                output += f"\n**Limitations:**\n"
                if lims.get("liability"):
                    output += "- ⚠️ No liability warranty\n"
                if lims.get("warranty"):
                    output += "- ⚠️ No warranty\n"
                if not lims.get("patent_use"):
                    output += "- ⚠️ No patent grant\n"
                if not lims.get("trademark_use"):
                    output += "- ⚠️ No trademark rights\n"

            output += "\n"

        # Alternative suggestions if incompatible
        if not result["compatible"] and result.get("violations"):
            output += "### 💡 Alternative Licenses to Consider\n\n"
            all_text = (
                " ".join(result["violations"]).lower()
                + " "
                + result.get("explanation", "").lower()
            )

            suggestions = []
            if (
                "source disclosure" in all_text
                or "disclose_source" in all_text
                or "closed" in all_text
            ):
                suggestions.extend(
                    [
                        "**MIT** – No source disclosure required",
                        "**Apache-2.0** – No source disclosure + patent grant",
                        "**BSD-2-Clause** – Simple permissive, no source disclosure",
                    ]
                )
            if (
                "same license" in all_text
                or "same_license" in all_text
                or "relicense" in all_text
            ):
                suggestions.extend(
                    [
                        "**MIT** – No same-license requirement",
                        "**Apache-2.0** – No same-license requirement",
                    ]
                )
            if "commercial" in all_text:
                suggestions.extend(
                    [
                        "**MIT** – Allows commercial use",
                        "**Apache-2.0** – Allows commercial use with patent grant",
                    ]
                )
            if "network" in all_text or "saas" in all_text:
                suggestions.extend(
                    [
                        "**MIT** – No network copyleft",
                        "**Apache-2.0** – No network copyleft",
                    ]
                )

            # Remove duplicates while preserving order
            seen = set()
            for sugg in suggestions:
                if sugg not in seen:
                    output += f"- {sugg}\n"
                    seen.add(sugg)

            if suggestions:
                output += "\n"

        # Disclaimer
        output += "---\n\n"
        output += "⚠️ **Disclaimer**: This analysis is for educational purposes only and does not constitute legal advice. "
        output += (
            "Consult a qualified intellectual property lawyer for production use.\n"
        )

        return output

    except Exception as e:
        return f"❌ **Error**: An unexpected error occurred during analysis.\n\n```\n{str(e)}\n```"


# ----------------------------------------------------------------------
# Build Gradio interface
# ----------------------------------------------------------------------
def create_interface():
    """Create the Gradio interface with enhanced layout and error handling."""
    with gr.Blocks(css=CUSTOM_CSS, title="LicenseWise – KBS License Advisor") as demo:
        # Header
        gr.Markdown("# 📘 LicenseWise – Knowledge-Based License Recommendation System")

        # Show license loading status
        if LOAD_ERROR:
            gr.Markdown(
                f"⚠️ **Warning**: Could not load license database. {LICENSES_LOADED} licenses loaded.\n\n{LOAD_ERROR}"
            )
        else:
            gr.Markdown(
                f"✅ Successfully loaded **{LICENSES_LOADED} licenses** from database."
            )

        gr.Markdown(
            "Answer the questions below to get a license recommendation or check a specific license's compatibility."
        )

        # Recommendation Tab
        with gr.Tab("📋 License Recommendation"):
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
                "🔍 Get Recommendation", variant="primary", size="lg"
            )
            recommend_output = gr.Markdown(
                "### Results will appear here after clicking the button above"
            )

            recommend_btn.click(
                fn=recommend_handler,
                inputs=[
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
                ],
                outputs=recommend_output,
            )

        # Analysis Tab
        with gr.Tab("🔍 License Analysis"):
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
                "✅ Check Compatibility", variant="primary", size="lg"
            )
            analyze_output = gr.Markdown(
                "### Compatibility results will appear here after clicking the button above"
            )

            analyze_btn.click(
                fn=analysis_handler,
                inputs=[
                    license_id,
                    distribute_an,
                    saas_an,
                    commercial_an,
                    patent_an,
                    relicense_an,
                ],
                outputs=analyze_output,
            )

        # Footer
        gr.Markdown("---")
        gr.Markdown(
            "⚠️ **Disclaimer**: This tool is for educational purposes only and does not constitute legal advice. "
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
