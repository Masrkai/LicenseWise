"""Slint GUI interface for LicenseWise."""

from __future__ import annotations

import sys
from typing import Any

from ..Inference.backward_chain import backward_chain
from ..Inference.forward_chain import forward_chain
from ..Inference.explanation_engine import (
    generate_final_report,
)
from ..config import UI_DIR
from .common import (
    get_licenses_data,
    load_questions,
    yes_no_to_bool,
    apply_closed_source_derivation,
    build_analysis_facts,
)
from .formatting import format_compatibility_result

# Load licenses with proper error handling
try:
    LICENSES_DATA: list[dict[str, Any]] = get_licenses_data()
    LICENSES_LOADED: int = len(LICENSES_DATA)
    LOAD_ERROR: str | None = None
except FileNotFoundError as e:
    LICENSES_DATA = []
    LICENSES_LOADED = 0
    LOAD_ERROR = str(e)

QUESTIONS: dict[str, list[dict[str, Any]]] = load_questions()

LICENSES_ERROR_TEMPLATE: str = (
    "Error: Cannot load license data.\n\n{error}\n\n"
    "Please ensure Licenses/Families/ exists and contains *.json files."
)


def _match_requires_value(answer: str, required_value: Any) -> bool:
    """Compare an answer string against a requires.value from JSON.

    JSON ``true``/``false`` become Python booleans after ``json.load()``.
    ComboBox answers are ``"yes"``/``"no"``/``"skip"`` for yes_no_skip, or
    lowercased choice strings for choice questions.
    """
    if isinstance(required_value, bool):
        return (answer.strip().lower() == "yes") == required_value
    return answer.strip().lower() == str(required_value).lower()


class QuestionNavigator:
    """Manages question visibility, navigation, and answer state for the GUI."""

    def __init__(self, questions: list[dict[str, Any]]) -> None:
        self.questions = questions
        self.answers: dict[str, str] = {q["fact_name"]: "skip" for q in questions}
        self.current_index: int = 0

    def is_visible(self, q: dict[str, Any]) -> bool:
        """Check if a question should be displayed given current answers."""
        if "requires" not in q:
            return True
        req = q["requires"]
        answer = self.answers.get(req["fact"], "skip")
        if "unless" in req:
            un = req["unless"]
            un_answer = self.answers.get(un["fact"], "skip")
            if _match_requires_value(un_answer, un["value"]):
                return False
        return _match_requires_value(answer, req["value"])

    def get_visible_questions(self) -> list[dict[str, Any]]:
        """Get all questions whose requires conditions are met."""
        return [q for q in self.questions if self.is_visible(q)]

    def on_answer_changed(self, fact_name: str, value: str) -> None:
        """Handle an answer change and advance to next question."""
        self.answers[fact_name] = value
        visible = self.get_visible_questions()
        if self.current_index < len(visible) - 1:
            self.current_index += 1

    def go_to_previous(self) -> None:
        """Move to previous question if possible."""
        if self.current_index > 0:
            self.current_index -= 1

    def go_to_next(self) -> None:
        """Move to next question if possible."""
        visible = self.get_visible_questions()
        if self.current_index < len(visible) - 1:
            self.current_index += 1


def _build_recommendation_output_dict(answers: dict[str, str]) -> str:
    """Handle license recommendation request using a dictionary of answers."""
    if LOAD_ERROR:
        return LICENSES_ERROR_TEMPLATE.format(error=LOAD_ERROR)

    try:
        facts: dict[str, Any] = {
            "saas": yes_no_to_bool(answers.get("saas", "skip")),
            "commercial_use": yes_no_to_bool(answers.get("commercial_use", "skip")),
            "need_patent_protection": yes_no_to_bool(answers.get("need_patent_protection", "skip")),
            "want_copyleft": yes_no_to_bool(answers.get("want_copyleft", "skip")),
            "want_weak_copyleft": yes_no_to_bool(answers.get("want_weak_copyleft", "skip")),
            "want_file_copyleft": yes_no_to_bool(answers.get("want_file_copyleft", "skip")),
            "wants_relicense": yes_no_to_bool(answers.get("wants_relicense", "skip")),
            "project_type": answers.get("project_type", "skip").lower() if answers.get("project_type", "skip") != "skip" else None,
            "linking_type": answers.get("linking_type", "skip").lower() if answers.get("linking_type", "skip") != "skip" else None,
            "modify_library": yes_no_to_bool(answers.get("modify_library", "skip")),
            "want_public_domain": yes_no_to_bool(answers.get("want_public_domain", "skip")),
            "want_simple_permissive": yes_no_to_bool(answers.get("want_simple_permissive", "skip")),
            "academic_project": yes_no_to_bool(answers.get("academic_project", "skip")),
            "mixed_open_proprietary": yes_no_to_bool(answers.get("mixed_open_proprietary", "skip")),
            "concerned_about_legal_recognition": yes_no_to_bool(answers.get("concerned_about_legal_recognition", "skip")),
            "dual_licensing": yes_no_to_bool(answers.get("dual_licensing", "skip")),
            "wants_attribution": yes_no_to_bool(answers.get("wants_attribution", "skip")),
            "wants_patent_retaliation": yes_no_to_bool(answers.get("wants_patent_retaliation", "skip")),
        }
        facts["distribute"] = yes_no_to_bool(answers.get("distribute", "skip"))
        apply_closed_source_derivation(facts)

        trace: list[dict[str, Any]] = []
        wm = forward_chain(facts, [], LICENSES_DATA, trace)
        return generate_final_report(wm, facts, trace, include_trace=False)
    except Exception as e:
        return f"Error: An unexpected error occurred.\n\n{str(e)}"


def _build_analysis_output_dict(license_id: str, answers: dict[str, str]) -> str:
    """Handle license compatibility analysis using a dictionary of answers."""
    if LOAD_ERROR:
        return LICENSES_ERROR_TEMPLATE.format(error=LOAD_ERROR)

    if not license_id or not license_id.strip():
        return "Please enter a license SPDX ID (e.g., MIT, GPL-3.0, Apache-2.0)"

    try:
        facts = build_analysis_facts(
            distribute=answers.get("distribute"),
            saas=answers.get("saas"),
            commercial_use=answers.get("commercial_use"),
            need_patent=answers.get("need_patent_protection"),
            wants_relicense=answers.get("wants_relicense"),
        )
        result = backward_chain(license_id.strip(), facts, LICENSES_DATA)
        return f"Compatibility Check: {license_id}\n\n{format_compatibility_result(result, license_id)}"
    except Exception as e:
        return f"Error: An unexpected error occurred during analysis.\n\n{str(e)}"


def launch_gui() -> None:
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

    # Initialize question navigators
    navigator = QuestionNavigator(QUESTIONS["recommendation"])
    analysis_navigator = QuestionNavigator(QUESTIONS["analysis"])

    def update_ui() -> None:
        """Update the UI to reflect current navigator state."""
        # Recommendation questions
        visible_qs = navigator.get_visible_questions()
        if navigator.current_index >= len(visible_qs):
            navigator.current_index = max(0, len(visible_qs) - 1)

        window.total_visible_questions = len(visible_qs)
        window.current_question_index = navigator.current_index

        visible: list[Any] = []
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

        # Analysis questions
        analysis_visible_qs = analysis_navigator.get_visible_questions()
        if analysis_navigator.current_index >= len(analysis_visible_qs):
            analysis_navigator.current_index = max(0, len(analysis_visible_qs) - 1)

        window.analysis_total_visible_questions = len(analysis_visible_qs)
        window.analysis_current_question_index = analysis_navigator.current_index

        analysis_visible: list[Any] = []
        if analysis_visible_qs and analysis_navigator.current_index < len(analysis_visible_qs):
            q = analysis_visible_qs[analysis_navigator.current_index]
            q_struct = ui.Question()
            q_struct.fact_name = str(q.get("fact_name", ""))
            q_struct.question = str(q.get("question", ""))
            q_struct.type = str(q.get("type", ""))
            q_struct.info = str(q.get("info", ""))
            q_struct.current_answer = str(analysis_navigator.answers.get(q.get("fact_name", ""), "skip"))
            choices = q.get("choices", [])
            if choices:
                q_struct.choices = slint.ListModel([str(c) for c in choices])
            analysis_visible.append(q_struct)

        window.analysis_visible_questions = slint.ListModel(analysis_visible)

    def on_answer_changed(fact_name: str, value: str) -> None:
        navigator.on_answer_changed(fact_name, value)
        update_ui()

    def on_go_to_previous() -> None:
        navigator.go_to_previous()
        update_ui()

    def on_go_to_next() -> None:
        navigator.go_to_next()
        update_ui()

    def on_analysis_answer_changed(fact_name: str, value: str) -> None:
        analysis_navigator.on_answer_changed(fact_name, value)
        update_ui()

    def on_analysis_go_to_previous() -> None:
        analysis_navigator.go_to_previous()
        update_ui()

    def on_analysis_go_to_next() -> None:
        analysis_navigator.go_to_next()
        update_ui()

    window.on_answer_changed = on_answer_changed
    window.on_go_to_previous = on_go_to_previous
    window.on_go_to_next = on_go_to_next
    window.on_analysis_answer_changed = on_analysis_answer_changed
    window.on_analysis_go_to_previous = on_analysis_go_to_previous
    window.on_analysis_go_to_next = on_analysis_go_to_next
    update_ui()

    def on_get_recommendation() -> None:
        try:
            output = _build_recommendation_output_dict(navigator.answers)
            window.recommend_output = output
        except Exception as e:
            window.recommend_output = f"Error: {str(e)}"

    def on_check_compatibility() -> None:
        try:
            output = _build_analysis_output_dict(
                window.license_id_input,
                analysis_navigator.answers,
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
