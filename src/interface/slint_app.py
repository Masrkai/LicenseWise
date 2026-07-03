"""Slint GUI interface for LicenseWise."""

import os
import sys
import json
from pathlib import Path

from Inference.backward_chain import backward_chain
from Inference.forward_chain import forward_chain
from Inference.explanation_engine import (
    generate_final_report,
    generate_summary,
)
from interface.common import (
    get_licenses_data,
    yes_no_to_bool,
    distribute_to_closed_source,
    suggest_alternatives,
    build_analysis_facts,
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

# Load questions
def _load_questions():
    questions_path = Path(__file__).parent.parent / "Licenses" / "questions.json"
    with open(questions_path, 'r') as f:
        return json.load(f)

QUESTIONS = _load_questions()


def _build_recommendation_output_dict(answers) -> str:
    """Handle license recommendation request using a dictionary of answers."""
    if LOAD_ERROR:
        return f"Error: Cannot load license data.\n\n{LOAD_ERROR}\n\nPlease ensure licenses.json exists in your project root or Licenses/ directory."

    try:
        facts = {
            "saas": yes_no_to_bool(answers.get("saas", "skip")),
            "commercial_use": yes_no_to_bool(answers.get("commercial_use", "skip")),
            "need_patent_protection": yes_no_to_bool(answers.get("need_patent_protection", "skip")),
            "want_copyleft": yes_no_to_bool(answers.get("want_copyleft", "skip")),
            "want_weak_copyleft": yes_no_to_bool(answers.get("want_weak_copyleft", "skip")),
            "want_file_copyleft": yes_no_to_bool(answers.get("want_file_copyleft", "skip")),
            "wants_relicense": yes_no_to_bool(answers.get("wants_relicense", "skip")),
            "project_type": answers.get("project_type").lower() if answers.get("project_type", "skip") != "skip" else None,
            "linking_type": answers.get("linking_type").lower() if answers.get("linking_type", "skip") != "skip" else None,
            "modify_library": yes_no_to_bool(answers.get("modify_library", "skip")),
            "want_public_domain": yes_no_to_bool(answers.get("want_public_domain", "skip")),
            "want_simple_permissive": yes_no_to_bool(answers.get("want_simple_permissive", "skip")),
            "academic_project": yes_no_to_bool(answers.get("academic_project", "skip")),
            "mixed_open_proprietary": yes_no_to_bool(answers.get("mixed_open_proprietary", "skip")),
            "concerned_about_legal_recognition": yes_no_to_bool(answers.get("concerned_about_legal_recognition", "skip")),
        }
        dist_bool = yes_no_to_bool(answers.get("distribute", "skip"))
        facts["closed_source"] = distribute_to_closed_source(dist_bool)

        trace = []
        wm = forward_chain(facts, [], LICENSES_DATA, trace)
        report = generate_final_report(wm, facts, trace)
        summary = generate_summary(wm, facts, trace)
        return report + "\n\n" + summary
    except Exception as e:
        return f"Error: An unexpected error occurred.\n\n{str(e)}"


def _build_analysis_output(license_id, distribute, saas, commercial_use, need_patent, wants_relicense) -> str:
    """Handle license compatibility analysis with enhanced output."""
    if LOAD_ERROR:
        return f"Error: Cannot load license data.\n\n{LOAD_ERROR}\n\nPlease ensure licenses.json exists in your project root or Licenses/ directory."

    if not license_id or not license_id.strip():
        return "Please enter a license SPDX ID (e.g., MIT, GPL-3.0, Apache-2.0)"

    try:
        facts = build_analysis_facts(
            distribute=distribute,
            saas=saas,
            commercial_use=commercial_use,
            need_patent=need_patent,
            wants_relicense=wants_relicense,
        )
        result = backward_chain(license_id.strip(), facts, LICENSES_DATA)

        output = f"Compatibility Check: {license_id}\n\n"

        if result["compatible"] is True:
            output += f"COMPATIBLE\n\n{license_id} is compatible with your intended use.\n\n"
        elif result["compatible"] is False:
            output += f"NOT COMPATIBLE\n\n{license_id} is not compatible with your intended use.\n\n"
        else:
            output += f"UNCLEAR\n\nCompatibility could not be determined for {license_id}.\n\n"

        if result.get("violations"):
            output += "Violations Found\n\n"
            for v in result["violations"]:
                output += f"  - {v}\n"
            output += "\n"

        if result.get("explanation"):
            output += f"Analysis\n\n{result['explanation']}\n\n"

        if result.get("how"):
            output += "Reasoning\n\n"
            for line in result["how"].split("\n"):
                if line.strip():
                    output += f"  {line}\n"
            output += "\n"

        if result.get("warnings"):
            output += "Warnings\n\n"
            for w in result["warnings"]:
                output += f"  - {w}\n"
            output += "\n"

        if result.get("license_info"):
            lic = result["license_info"]
            output += "License Information\n\n"
            output += f"  Name: {lic.get('name', 'unknown')}\n"
            output += f"  Type: {lic.get('type', 'unknown').title()}\n"
            if lic.get("description"):
                output += f"  Description: {lic['description']}\n"

            if lic.get("permissions"):
                perms = lic["permissions"]
                output += "\n  Permissions:\n"
                for key, label in [
                    ("commercial_use", "Commercial use"),
                    ("modification", "Modification"),
                    ("distribution", "Distribution"),
                    ("private_use", "Private use"),
                ]:
                    if perms.get(key):
                        output += f"    + {label}\n"

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
                    output += "\n  Conditions:\n"
                    for cond in conditions_list:
                        output += f"    - {cond}\n"

            if lic.get("limitations"):
                lims = lic["limitations"]
                output += "\n  Limitations:\n"
                for key, label in [
                    ("liability", "No liability warranty"),
                    ("warranty", "No warranty"),
                ]:
                    if lims.get(key):
                        output += f"    ! {label}\n"
                if not lims.get("patent_use"):
                    output += "    ! No patent grant\n"
                if not lims.get("trademark_use"):
                    output += "    ! No trademark rights\n"

            output += "\n"

        if not result["compatible"] and result.get("violations"):
            all_text = (
                " ".join(result["violations"]).lower()
                + " "
                + result.get("explanation", "").lower()
            )
            suggestions = suggest_alternatives(all_text, format="plain")
            if suggestions:
                output += "Alternative Licenses to Consider\n\n"
                for sugg in suggestions:
                    output += f"  - {sugg}\n"
                output += "\n"

        output += "---\n\n"
        output += "Disclaimer: This analysis is for educational purposes only and does not constitute legal advice. "
        output += "Consult a qualified intellectual property lawyer for production use.\n"

        return output
    except Exception as e:
        return f"Error: An unexpected error occurred during analysis.\n\n{str(e)}"


def launch_gui():
    """Launch the Slint GUI interface."""
    import slint

    ui_dir = Path(__file__).parent / "ui"
    main_slint = ui_dir / "main.slint"

    if not main_slint.exists():
        print(f"Error: UI file not found at {main_slint}")
        sys.exit(1)

    try:
        ui = slint.load_file(
            str(main_slint),
            include_paths=[str(ui_dir)],
        )
    except Exception as e:
        print(f"Error loading Slint UI: {e}")
        sys.exit(1)
    # ...


    window = ui.LicenseWiseApp()

    if LOAD_ERROR:
        window.status_text = f"Warning: Could not load license database. {LICENSES_LOADED} licenses loaded.\n{LOAD_ERROR}"
    else:
        window.status_text = f"Successfully loaded {LICENSES_LOADED} licenses from database."

    window.license_count = str(LICENSES_LOADED)

    # State for dynamic questions
    current_answers = {q['fact_name']: "skip" for q in QUESTIONS['recommendation']}
    current_question_index = 0
    
    def get_visible_questions():
        """Get all questions whose requires conditions are met."""
        visible = []
        for q in QUESTIONS['recommendation']:
            if is_visible(q, current_answers):
                visible.append(q)
        return visible
    
    def is_visible(q, answers):
        if "requires" not in q:
            return True
        req = q["requires"]
        fact = req["fact"]
        val = req["value"]
        
        # Check 'unless'
        if "unless" in req:
            un = req["unless"]
            if answers.get(un["fact"]) == str(un["value"]):
                return False
                
        return answers.get(fact) == str(val)

    def update_visible_questions(ui_window):
        nonlocal current_question_index
        visible_qs = get_visible_questions()
        
        # Clamp index to valid range
        if current_question_index >= len(visible_qs):
            current_question_index = max(0, len(visible_qs) - 1)
        
        # Update total count on the UI
        ui_window.total_visible_questions = len(visible_qs)
        ui_window.current_question_index = current_question_index
        
        # Only show the current question
        visible = []
        if visible_qs and current_question_index < len(visible_qs):
            q = visible_qs[current_question_index]
            q_struct = ui.Question()
            q_struct.fact_name = str(q.get('fact_name', ''))
            q_struct.question = str(q.get('question', ''))
            q_struct.type = str(q.get('type', ''))
            q_struct.info = str(q.get('info', ''))
            q_struct.current_answer = str(current_answers.get(q.get('fact_name', ''), 'skip'))
            choices = q.get('choices', [])
            if choices:
                q_struct.choices = slint.ListModel([str(c) for c in choices])
            visible.append(q_struct)
        
        ui_window.visible_questions = slint.ListModel(visible)

    def on_answer_changed(fact_name, value):
        nonlocal current_question_index
        current_answers[fact_name] = value
        # Advance to next question
        visible_qs = get_visible_questions()
        if current_question_index < len(visible_qs) - 1:
            current_question_index += 1
        update_visible_questions(window)

    def go_to_previous():
        nonlocal current_question_index
        if current_question_index > 0:
            current_question_index -= 1
            update_visible_questions(window)

    def go_to_next():
        nonlocal current_question_index
        visible_qs = get_visible_questions()
        if current_question_index < len(visible_qs) - 1:
            current_question_index += 1
            update_visible_questions(window)

    window.on_answer_changed = on_answer_changed
    window.on_go_to_previous = go_to_previous
    window.on_go_to_next = go_to_next
    update_visible_questions(window)

    def on_get_recommendation():
        try:
            # Pass the current answers dictionary directly
            output = _build_recommendation_output_dict(current_answers)
            window.recommend_output = output
        except Exception as e:
            window.recommend_output = f"Error: {str(e)}"

    def on_check_compatibility():
        try:
            output = _build_analysis_output(
                window.license_id_input,
                window.distribute_an,
                window.saas_an,
                window.commercial_an,
                window.patent_an,
                window.relicense_an,
            )
            window.analyze_output = output
        except Exception as e:
            window.analyze_output = f"Error: {str(e)}"

    window.get_recommendation = on_get_recommendation
    window.check_compatibility = on_check_compatibility

    window.show()
    slint.run_event_loop()


if __name__ == "__main__":
    launch_gui()
