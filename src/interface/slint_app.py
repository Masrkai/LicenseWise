"""Slint GUI interface for LicenseWise."""

import sys

from Inference.backward_chain import backward_chain
from Inference.forward_chain import forward_chain
from Inference.explanation_engine import (
    generate_final_report,
    generate_summary,
)
from config import UI_DIR
from interface.common import (
    get_licenses_data,
    load_questions,
    yes_no_to_bool,
    apply_closed_source_derivation,
    build_analysis_facts,
)
from interface.formatting import format_compatibility_result

# Load licenses with proper error handling
try:
    LICENSES_DATA = get_licenses_data()
    LICENSES_LOADED = len(LICENSES_DATA)
    LOAD_ERROR = None
except FileNotFoundError as e:
    LICENSES_DATA = []
    LICENSES_LOADED = 0
    LOAD_ERROR = str(e)

QUESTIONS = load_questions()

LICENSES_ERROR_TEMPLATE = (
    "Error: Cannot load license data.\n\n{error}\n\n"
    "Please ensure licenses.json exists in your project root or Licenses/ directory."
)


class QuestionNavigator:
    """Manages question visibility, navigation, and answer state for the GUI."""

    def __init__(self, questions):
        self.questions = questions
        self.answers = {q["fact_name"]: "skip" for q in questions}
        self.current_index = 0

    def is_visible(self, q):
        """Check if a question should be displayed given current answers."""
        if "requires" not in q:
            return True
        req = q["requires"]
        if "unless" in req:
            un = req["unless"]
            if self.answers.get(un["fact"]) == str(un["value"]):
                return False
        return self.answers.get(req["fact"]) == str(req["value"])

    def get_visible_questions(self):
        """Get all questions whose requires conditions are met."""
        return [q for q in self.questions if self.is_visible(q)]

    def on_answer_changed(self, fact_name, value):
        """Handle an answer change and advance to next question."""
        self.answers[fact_name] = value
        visible = self.get_visible_questions()
        if self.current_index < len(visible) - 1:
            self.current_index += 1

    def go_to_previous(self):
        """Move to previous question if possible."""
        if self.current_index > 0:
            self.current_index -= 1

    def go_to_next(self):
        """Move to next question if possible."""
        visible = self.get_visible_questions()
        if self.current_index < len(visible) - 1:
            self.current_index += 1


def _build_recommendation_output_dict(answers) -> str:
    """Handle license recommendation request using a dictionary of answers."""
    if LOAD_ERROR:
        return LICENSES_ERROR_TEMPLATE.format(error=LOAD_ERROR)

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
        facts["distribute"] = yes_no_to_bool(answers.get("distribute", "skip"))
        apply_closed_source_derivation(facts)

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
        return LICENSES_ERROR_TEMPLATE.format(error=LOAD_ERROR)

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
        return f"Compatibility Check: {license_id}\n\n{format_compatibility_result(result, license_id)}"
    except Exception as e:
        return f"Error: An unexpected error occurred during analysis.\n\n{str(e)}"


def launch_gui():
    """Launch the Slint GUI interface."""
    import slint

    main_slint = UI_DIR / "main.slint"

    if not main_slint.exists():
        print(f"Error: UI file not found at {main_slint}")
        sys.exit(1)

    try:
        ui = slint.load_file(
            str(main_slint),
            include_paths=[str(UI_DIR)],
        )
    except Exception as e:
        print(f"Error loading Slint UI: {e}")
        sys.exit(1)

    window = ui.LicenseWiseApp()

    if LOAD_ERROR:
        window.status_text = f"Warning: Could not load license database. {LICENSES_LOADED} licenses loaded.\n{LOAD_ERROR}"
    else:
        window.status_text = f"Successfully loaded {LICENSES_LOADED} licenses from database."

    window.license_count = str(LICENSES_LOADED)

    # Initialize question navigator
    navigator = QuestionNavigator(QUESTIONS["recommendation"])

    def update_ui():
        """Update the UI to reflect current navigator state."""
        visible_qs = navigator.get_visible_questions()
        if navigator.current_index >= len(visible_qs):
            navigator.current_index = max(0, len(visible_qs) - 1)

        window.total_visible_questions = len(visible_qs)
        window.current_question_index = navigator.current_index

        visible = []
        if visible_qs and navigator.current_index < len(visible_qs):
            q = visible_qs[navigator.current_index]
            q_struct = ui.Question()
            q_struct.fact_name = str(q.get("fact_name", ""))
            q_struct.question = str(q.get("question", ""))
            q_struct.type = str(q.get("type", ""))
            q_struct.info = str(q.get("info", ""))
            q_struct.current_answer = str(navigator.answers.get(q.get("fact_name", ""), "skip"))
            choices = q.get("choices", [])
            if choices:
                q_struct.choices = slint.ListModel([str(c) for c in choices])
            visible.append(q_struct)

        window.visible_questions = slint.ListModel(visible)

    def on_answer_changed(fact_name, value):
        navigator.on_answer_changed(fact_name, value)
        update_ui()

    def on_go_to_previous():
        navigator.go_to_previous()
        update_ui()

    def on_go_to_next():
        navigator.go_to_next()
        update_ui()

    window.on_answer_changed = on_answer_changed
    window.on_go_to_previous = on_go_to_previous
    window.on_go_to_next = on_go_to_next
    update_ui()

    def on_get_recommendation():
        try:
            output = _build_recommendation_output_dict(navigator.answers)
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
