"""
Inference Engine for LicenseWise
Implements forward chaining for license recommendation and backward chaining for compliance analysis.
"""

from Knowledge.rules import Rules
from Inference.explanation_engine import ExplanationEngine


class InferenceEngine:
    """
    Hybrid inference engine supporting:
    - Forward chaining: Facts → Rules → Recommendations
    - Backward chaining: Goal → Required facts → Verification
    """

    def __init__(self):
        self.explanation = ExplanationEngine()
        self.working_memory = {
            "recommended": set(),
            "eliminated": set(),
            "warnings": [],
        }

    def reset(self):
        """Clear working memory for a new session."""
        self.working_memory = {
            "recommended": set(),
            "eliminated": set(),
            "warnings": [],
        }
        self.explanation.trace = []

    def forward_chain(self, facts):
        """
        Forward chaining: Given user facts, fire all matching rules.
        Returns the final working memory state.
        """
        self.reset()

        for rule in Rules:
            try:
                if rule.matches(facts):
                    # Determine action type from rule name
                    if rule.name.startswith("recommend_"):
                        action_type = "recommend"
                    elif rule.name.startswith("eliminate_"):
                        action_type = "eliminate"
                    elif rule.name.startswith("warn_"):
                        action_type = "warn"
                    else:
                        action_type = "other"

                    # Record in explanation trace
                    self.explanation.record(rule.name, facts, rule.explanation, action_type)

                    # Fire the rule
                    rule.fire(self.working_memory)
            except Exception as e:
                # Skip rules that fail due to missing facts
                continue

        return self.working_memory

    def backward_chain(self, license_id, intended_use, facts):
        """
        Backward chaining: Check if a specific license is compatible with intended use.
        Works backward from the license conditions to verify user facts.

        Args:
            license_id: SPDX ID of the license to check (e.g., "GPL-3.0")
            intended_use: Description of how the user wants to use the license
            facts: Current known facts about the user's project

        Returns:
            dict with 'compatible' (bool), 'violations' (list), and 'explanation' (str)
        """
        # Load license data
        import json
        with open('knowledge/licenses.json', 'r') as f:
            licenses_data = json.load(f)

        license_info = None
        for lic in licenses_data["licenses"]:
            if lic["id"] == license_id or lic["spdx_id"] == license_id:
                license_info = lic
                break

        if not license_info:
            return {
                "compatible": False,
                "violations": [f"License '{license_id}' not found in knowledge base."],
                "explanation": "Unknown license identifier."
            }

        violations = []
        explanations = []

        # Check each license condition against user facts
        conditions = license_info.get("conditions", {})
        permissions = license_info.get("permissions", {})

        # Source disclosure check
        if conditions.get("disclose_source") and facts.get("closed_source"):
            violations.append("Source disclosure required but user wants closed source")
            explanations.append(
                f"{license_id} requires disclosing source code (disclose_source=true), "
                f"but you indicated closed_source=true."
            )

        # Same license check
        if conditions.get("same_license") and facts.get("wants_relicense"):
            violations.append("Same license required but user wants to relicense")
            explanations.append(
                f"{license_id} requires derivatives use the same license (same_license=true), "
                f"but you want freedom to relicense."
            )

        # Network copyleft check
        if conditions.get("net_copyleft") and facts.get("saas") and facts.get("closed_source"):
            violations.append("Network copyleft conflicts with closed-source SaaS")
            explanations.append(
                f"{license_id} triggers copyleft on network use (net_copyleft=true). "
                f"Running this as a closed-source SaaS violates this condition."
            )

        # Commercial use check
        if not permissions.get("commercial_use") and facts.get("commercial_use"):
            violations.append("Commercial use prohibited")
            explanations.append(
                f"{license_id} does not permit commercial use (commercial_use=false)."
            )

        # Patent protection check
        if facts.get("need_patent_protection") and not license_info.get("limitations", {}).get("patent_use"):
            # This is a warning, not a violation
            explanations.append(
                f"⚠️ {license_id} does not include an explicit patent grant. "
                f"Consider Apache-2.0 if patent protection is critical."
            )

        compatible = len(violations) == 0

        return {
            "compatible": compatible,
            "violations": violations,
            "explanation": "\n".join(explanations) if explanations else f"{license_id} is compatible with your intended use.",
            "license_info": license_info
        }

    def get_explanation(self):
        """Get the explanation engine for formatting output."""
        return self.explanation
