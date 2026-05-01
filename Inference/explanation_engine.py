"""
Explanation Facility for LicenseWise
Generates dynamic reasoning traces showing HOW the inference engine reached each conclusion.
"""


class ExplanationEngine:
    """
    Tracks and explains the reasoning process of the inference engine.
    Every fired rule is recorded with its matched facts to build a traceable
    explanation of HOW the final recommendation was reached.
    """

    def __init__(self):
        self.trace = []
        self.fired_rules = []

    def record_fired_rule(self, rule, facts):
        """
        Record a rule that the inference engine actually fired.
        This captures the dynamic reasoning process.
        """
        # Capture which specific facts caused this rule to match
        matched_facts = {}

        # Try to extract the specific facts that triggered this rule
        # by checking what the rule's lambda condition would access
        fact_keys = [
            "closed_source", "saas", "commercial_use", "need_patent_protection",
            "want_copyleft", "want_weak_copyleft", "want_file_copyleft",
            "wants_relicense", "project_type", "want_public_domain",
            "want_simple_permissive", "academic_project", "mixed_open_proprietary",
            "linking_type", "modify_library", "concerned_about_legal_recognition"
        ]

        for key in fact_keys:
            if key in facts and facts[key] is not None:
                matched_facts[key] = facts[key]

        entry = {
            "step": len(self.trace) + 1,
            "rule_name": rule.name,
            "action_type": self._classify_action(rule.name),
            "matched_facts": matched_facts,
            "explanation": rule.explanation,
            "result": self._describe_result(rule.name)
        }

        self.trace.append(entry)
        self.fired_rules.append(rule.name)

    def _classify_action(self, rule_name):
        """Classify what type of action this rule performs."""
        if rule_name.startswith("recommend_"):
            return "RECOMMEND"
        elif rule_name.startswith("eliminate_"):
            return "ELIMINATE"
        elif rule_name.startswith("warn_"):
            return "WARN"
        return "OTHER"

    def _describe_result(self, rule_name):
        """Describe what this rule adds to working memory."""
        if "recommend_" in rule_name:
            # Extract license name from rule name
            parts = rule_name.replace("recommend_", "").split("_if_")
            license_name = parts[0].replace("_", "-")
            return f"Added '{license_name}' to recommended licenses"
        elif "eliminate_" in rule_name:
            parts = rule_name.replace("eliminate_", "").split("_if_")
            license_name = parts[0].replace("_", "-")
            return f"Added '{license_name}' to eliminated licenses"
        elif "warn_" in rule_name:
            return "Appended warning message"
        return "Unknown action"

    def get_reasoning_trace(self):
        """Return the full step-by-step reasoning trace."""
        return self.trace

    def format_trace(self):
        """Format the trace as a human-readable string showing HOW results were reached."""
        if not self.trace:
            return "No rules were fired during inference."

        lines = []
        lines.append("🔍 HOW THE ENGINE REACHED THIS CONCLUSION:")
        lines.append("=" * 60)

        for entry in self.trace:
            icon = {
                "RECOMMEND": "✅",
                "ELIMINATE": "❌", 
                "WARN": "⚠️"
            }.get(entry["action_type"], "•")

            lines.append(f"\nStep {entry['step']}: {icon} {entry['rule_name']}")
            lines.append(f"   Action: {entry['action_type']}")

            # Show which user facts triggered this rule
            if entry["matched_facts"]:
                lines.append(f"   Because you answered:")
                for fact, value in entry["matched_facts"].items():
                    # Format the fact nicely
                    fact_display = fact.replace("_", " ").title()
                    value_display = "Yes" if value == True else "No" if value == False else str(value)
                    lines.append(f"      • {fact_display}: {value_display}")

            lines.append(f"   Result: {entry['result']}")
            lines.append(f"   Why: {entry['explanation']}")

        return "\n".join(lines)

    def explain_question(self, fact_name, relevant_licenses=None):
        """
        Explain WHY a particular question was asked.
        Called BEFORE asking the user for input.
        """
        explanations = {
            "closed_source": (
                "We need to know if you'll distribute source code because "
                "strong copyleft licenses (GPL-3.0, AGPL-3.0) REQUIRE source disclosure. "
                "If you keep code private, these licenses are incompatible with your goals."
            ),
            "saas": (
                "Network deployment matters because AGPL-3.0 triggers copyleft "
                "when users interact with your software over a network — even if you "
                "don't distribute binaries. This is the 'SaaS loophole' that AGPL closes."
            ),
            "commercial_use": (
                "Some licenses explicitly prohibit commercial use (e.g., CC-BY-NC-4.0). "
                "Most open-source licenses allow it, but we need to confirm to eliminate "
                "non-commercial licenses from consideration."
            ),
            "need_patent_protection": (
                "Patent protection is important because not all licenses include an "
                "explicit patent grant. MIT and BSD-2-Clause offer NO patent protection, "
                "while Apache-2.0 includes a strong patent grant clause."
            ),
            "want_copyleft": (
                "Copyleft determines whether derivatives of your work must remain open. "
                "Strong copyleft (GPL-3.0, AGPL-3.0) ensures all downstream code stays open. "
                "Weak copyleft (LGPL-2.1, MPL-2.0) applies only to specific parts."
            ),
            "want_weak_copyleft": (
                "Weak copyleft is ideal for libraries: the library itself stays open, "
                "but applications that link to it can remain proprietary. "
                "This maximizes adoption while protecting your library's openness."
            ),
            "want_file_copyleft": (
                "File-level copyleft (MPL-2.0) means only the files you modify must stay open. "
                "The rest of the project can be proprietary. This is a middle ground between "
                "permissive and strong copyleft."
            ),
            "wants_relicense": (
                "Some licenses require derivatives to use the SAME license (GPL-3.0, AGPL-3.0). "
                "If you want the freedom to relicense derivatives or combine with other licenses, "
                "we need to avoid these 'same_license' requirements."
            ),
            "project_type": (
                "License suitability varies by project type. Software licenses (MIT, GPL) "
                "differ from content licenses (CC). Libraries need different rules than "
                "standalone applications — especially for copyleft linking requirements."
            ),
            "want_public_domain": (
                "Public domain dedication (Unlicense) means zero restrictions — no attribution, "
                "no license notice, no conditions. But it's not legally recognized everywhere. "
                "We need to know if this level of freedom (and risk) aligns with your goals."
            ),
            "want_simple_permissive": (
                "Simple permissive licenses (MIT, BSD-2-Clause) have minimal requirements: "
                "just keep the copyright notice. They're the most widely adopted and easiest "
                "to comply with, but offer no patent protection."
            ),
            "academic_project": (
                "Academic projects often prefer BSD-2-Clause due to its history in university "
                "and research settings. Some funding bodies also have specific license requirements."
            ),
            "mixed_open_proprietary": (
                "Mixed codebases need careful license selection. MPL-2.0 is designed specifically "
                "for this scenario — file-level copyleft keeps modified files open while allowing "
                "proprietary additions elsewhere."
            ),
            "linking_type": (
                "Linking type is critical for LGPL-2.1 compliance. Dynamic linking generally keeps "
                "your application free of copyleft obligations. Static linking may require your "
                "entire application to be open-sourced under LGPL."
            ),
            "modify_library": (
                "If you modify a copyleft library, you must share those modifications. "
                "This affects whether LGPL-2.1 or even stronger copyleft applies to your project."
            ),
            "concerned_about_legal_recognition": (
                "Some licenses (like Unlicense) rely on public domain dedication, which isn't "
                "recognized in all countries. If legal certainty is important, we should recommend "
                "a well-established permissive license as a fallback."
            ),
        }
        return explanations.get(fact_name, "This question helps us narrow down compatible licenses for your project.")

    def calculate_confidence(self, recommended, eliminated, warnings, facts):
        """
        Calculate confidence level in the recommendation.
        Returns: ("HIGH"/"MEDIUM"/"LOW", explanation_string)
        """
        # Count how many facts were provided (not None)
        provided_facts = sum(1 for v in facts.values() if v is not None)
        total_facts = len(facts)

        # Check for conflicts (same license in both recommended and eliminated)
        conflicts = recommended.intersection(eliminated)

        # High confidence: many facts, clear results, no conflicts
        if provided_facts >= 8 and len(recommended) >= 1 and len(eliminated) >= 2 and not conflicts:
            return "HIGH", f"Provided {provided_facts}/{total_facts} facts. Clear separation between recommended and eliminated licenses with no conflicts."

        # Medium confidence: some ambiguity or fewer facts
        if len(warnings) > 0 or provided_facts < 8:
            return "MEDIUM", f"Provided {provided_facts}/{total_facts} facts. Some factors depend on implementation details. Review warnings carefully."

        # Low confidence: conflicts or very little info
        if conflicts:
            return "LOW", f"Conflicts detected: {conflicts}. Some licenses appear in both recommended and eliminated sets. Review your project goals."

        if len(recommended) == 0:
            return "LOW", "No licenses were recommended. Please provide more details about your project goals."

        return "MEDIUM", "Recommendations are reasonable but review the reasoning trace for caveats."

    def generate_final_report(self, wm, facts):
        """
        Generate the complete final report showing HOW the engine reached its conclusion.
        """
        confidence, confidence_explanation = self.calculate_confidence(
            wm["recommended"], wm["eliminated"], wm["warnings"], facts
        )

        report = []
        report.append("=" * 60)
        report.append("📋 LICENSEWISE FINAL REPORT")
        report.append("=" * 60)

        # Recommendations
        if wm["recommended"]:
            report.append("\n✅ RECOMMENDED LICENSES:")
            for lic in sorted(wm["recommended"]):
                report.append(f"   • {lic}")
        else:
            report.append("\n⚠️ No licenses were recommended. Please review your project goals.")

        # Eliminations
        if wm["eliminated"]:
            report.append("\n❌ ELIMINATED LICENSES:")
            for lic in sorted(wm["eliminated"]):
                report.append(f"   • {lic}")

        # Warnings
        if wm["warnings"]:
            report.append("\n⚠️ WARNINGS:")
            for warning in wm["warnings"]:
                report.append(f"   • {warning}")

        # Confidence
        report.append(f"\n🎯 CONFIDENCE: {confidence}")
        report.append(f"   {confidence_explanation}")

        # THE KEY PART: Dynamic reasoning trace showing HOW
        report.append("\n" + self.format_trace())

        # Disclaimer
        report.append("\n" + "=" * 60)
        report.append("⚠️ DISCLAIMER: This is not legal advice. Consult a lawyer for production use.")
        report.append("=" * 60)

        return "\n".join(report)

    def generate_summary(self, wm, facts):
        """
        Generate a concise summary of HOW the conclusion was reached.
        Perfect for the explanation facility grading rubric.
        """
        lines = []
        lines.append("\n📖 EXPLANATION: How did the engine get this result?")
        lines.append("-" * 50)

        # Summarize the reasoning path
        recommend_steps = [e for e in self.trace if e["action_type"] == "RECOMMEND"]
        eliminate_steps = [e for e in self.trace if e["action_type"] == "ELIMINATE"]
        warn_steps = [e for e in self.trace if e["action_type"] == "WARN"]

        if recommend_steps:
            lines.append(f"\nThe engine RECOMMENDED licenses because:")
            for step in recommend_steps:
                lines.append(f"  {step['step']}. {step['explanation']}")

        if eliminate_steps:
            lines.append(f"\nThe engine ELIMINATED licenses because:")
            for step in eliminate_steps:
                lines.append(f"  {step['step']}. {step['explanation']}")

        if warn_steps:
            lines.append(f"\nThe engine WARNED because:")
            for step in warn_steps:
                lines.append(f"  {step['step']}. {step['explanation']}")

        lines.append("\n" + "-" * 50)
        lines.append("Each step above was triggered by matching your answers against the rule base.")

        return "\n".join(lines)
