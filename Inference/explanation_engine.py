"""
Explanation Facility for LicenseWise
Provides reasoning traces, confidence scoring, and natural language explanations.
"""


class ExplanationEngine:
    """
    Generates human-readable explanations for every recommendation,
    elimination, and warning produced by the rule engine.
    """

    def __init__(self):
        self.trace = []

    def record(self, rule_name, facts, explanation, action_type):
        """Record a fired rule in the reasoning trace."""
        self.trace.append({
            "rule": rule_name,
            "facts_matched": {k: v for k, v in facts.items() if v is not None},
            "explanation": explanation,
            "action": action_type  # "recommend", "eliminate", "warn"
        })

    def get_reasoning_trace(self):
        """Return the full step-by-step reasoning trace."""
        return self.trace

    def format_trace(self):
        """Format the trace as a human-readable string."""
        lines = ["🔍 Reasoning Trace:", "=" * 50]
        for i, step in enumerate(self.trace, 1):
            icon = {"recommend": "✅", "eliminate": "❌", "warn": "⚠️"}.get(step["action"], "•")
            lines.append(f"\nStep {i}: {icon} {step['rule']}")
            lines.append(f"   Action: {step['action'].upper()}")
            lines.append(f"   Facts matched: {step['facts_matched']}")
            lines.append(f"   Why: {step['explanation']}")
        return "\n".join(lines)

    def explain_question(self, fact_name, relevant_licenses):
        """
        Explain WHY a particular question was asked.
        Called before asking the user for input.
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
        return explanations.get(fact_name, f"This question helps us narrow down compatible licenses for your project.")

    def calculate_confidence(self, recommended, eliminated, warnings, facts):
        """
        Calculate confidence level in the recommendation.
        Returns: "HIGH", "MEDIUM", or "LOW" with explanation.
        """
        # High confidence: clear goals, no conflicts, well-understood scenario
        if len(recommended) >= 1 and len(eliminated) >= 3:
            # Check for ambiguous facts
            ambiguous = sum(1 for v in facts.values() if v is None or v == "unsure")
            if ambiguous == 0:
                return "HIGH", "All user goals are clearly defined and fully compatible with the recommended licenses."

        # Medium confidence: some ambiguity or edge cases
        if len(warnings) > 0 or any(facts.get(k) is None for k in ["linking_type", "modify_library"]):
            return "MEDIUM", "Some factors depend on implementation details (e.g., linking type). Review warnings carefully."

        # Low confidence: too little information or conflicting goals
        if len(recommended) == 0 or len(recommended) > 5:
            return "LOW", "Insufficient or conflicting information. Please provide more details about your project goals."

        return "MEDIUM", "Recommendations are reasonable but review the reasoning trace for caveats."

    def generate_final_report(self, wm, facts):
        """Generate the complete final report with all explanations."""
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
            report.append("\n⚠️ No licenses recommended. Please review your project goals.")

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

        # Reasoning trace
        report.append("\n" + self.format_trace())

        # Disclaimer
        report.append("\n" + "=" * 60)
        report.append("⚠️ DISCLAIMER: This is not legal advice. Consult a lawyer for production use.")
        report.append("=" * 60)

        return "\n".join(report)
