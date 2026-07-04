"""Tests for interface.slint_app.QuestionNavigator."""

from src.interface.slint_app import QuestionNavigator


class TestQuestionNavigator:
    def setup_method(self):
        self.questions = [
            {"fact_name": "distribute", "question": "Will you distribute?", "type": "yes_no_skip"},
            {"fact_name": "saas", "question": "Will it be SaaS?", "type": "yes_no_skip"},
            {
                "fact_name": "want_copyleft",
                "question": "Want copyleft?",
                "type": "yes_no_skip",
                "requires": {"fact": "distribute", "value": "true"},
            },
        ]
        self.nav = QuestionNavigator(self.questions)

    def test_initial_state(self):
        assert self.nav.current_index == 0
        assert all(v == "skip" for v in self.nav.answers.values())

    def test_is_visible_no_requires(self):
        assert self.nav.is_visible(self.questions[0]) is True

    def test_is_visible_requires_not_met(self):
        assert self.nav.is_visible(self.questions[2]) is False

    def test_is_visible_requires_met(self):
        self.nav.answers["distribute"] = "true"
        assert self.nav.is_visible(self.questions[2]) is True

    def test_is_visible_unless(self):
        questions = [
            {
                "fact_name": "test",
                "question": "Test?",
                "type": "yes_no_skip",
                "requires": {"fact": "a", "value": "true", "unless": {"fact": "b", "value": "true"}},
            }
        ]
        nav = QuestionNavigator(questions)
        nav.answers["a"] = "true"
        assert nav.is_visible(questions[0]) is True

        nav.answers["b"] = "true"
        assert nav.is_visible(questions[0]) is False

    def test_on_answer_changed_advances(self):
        self.nav.on_answer_changed("distribute", "true")
        assert self.nav.answers["distribute"] == "true"
        assert self.nav.current_index == 1

    def test_go_to_previous(self):
        self.nav.current_index = 2
        self.nav.go_to_previous()
        assert self.nav.current_index == 1

    def test_go_to_previous_at_start(self):
        self.nav.current_index = 0
        self.nav.go_to_previous()
        assert self.nav.current_index == 0

    def test_go_to_next(self):
        self.nav.current_index = 0
        self.nav.go_to_next()
        assert self.nav.current_index == 1

    def test_go_to_next_at_end(self):
        visible = self.nav.get_visible_questions()
        self.nav.current_index = len(visible) - 1
        self.nav.go_to_next()
        assert self.nav.current_index == len(visible) - 1

    def test_get_visible_questions(self):
        visible = self.nav.get_visible_questions()
        assert len(visible) == 2
        assert visible[0]["fact_name"] == "distribute"
        assert visible[1]["fact_name"] == "saas"
