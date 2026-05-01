"""
Inference Engine for LicenseWise
Implements forward chaining for license recommendation and backward chaining for compliance analysis.
Records every fired rule in the explanation engine to show HOW results were reached.
"""


class InferenceEngine:
    """
    Hybrid inference engine supporting:
    - Forward chaining: Facts → Rules → Recommendations
    - Backward chaining: Goal → Required facts → Verification

    Every fired rule is recorded in the explanation engine to build
    a traceable reasoning path showing HOW the conclusion was reached.
    """

    def __init__(self, rules_list, explanation_engine):
        self.rules = rules_list
        self.explanation = explanation_engine
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
        self.explanation.fired_rules = []

    def forward_chain(self, facts):
        """
        Forward chaining: Given user facts, fire all matching rules.
        Records each fired rule in the explanation engine to show HOW
        the final recommendation was reached.

        Returns the final working memory state.
        """
        self.reset()

        print("\n🧠 Running forward chaining inference...")
        print("   Matching your answers against the rule base...\n")

        for rule in self.rules:
            try:
                if rule.matches(facts):
                    # Record this fired rule in the explanation engine
                    # This captures HOW the engine reached its conclusion
                    self.explanation.record_fired_rule(rule, facts)

                    # Fire the rule
                    rule.fire(self.working_memory)
            except Exception as e:
                # Skip rules that fail due to missing facts
                continue

        print(f"   ✓ Evaluated {len(self.rules)} rules")
        print(f"   ✓ Fired {len(self.explanation.trace)} rules")
        print(f"   ✓ Found {len(self.working_memory['recommended'])} recommendations")
        print(f"   ✓ Eliminated {len(self.working_memory['eliminated'])} licenses")
        if self.working_memory['warnings']:
            print(f"   ✓ Generated {len(self.working_memory['warnings'])} warnings")

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
        import json
        import os

        # Find licenses.json relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        kb_dir = os.path.join(os.path.dirname(current_dir), 'knowledge')
        json_path = os.path.join(kb_dir, 'licenses.json')

        with open(json_path, 'r') as f:
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
                "explanation": "Unknown license identifier.",
                "how": "The engine could not find this license in the SPDX database."
            }

        violations = []
        explanations = []
        how_explanations = []

        conditions = license_info.get("conditions", {})
        permissions = license_info.get("permissions", {})

        # Source disclosure check
        if conditions.get("disclose_source") and facts.get("closed_source"):
            violations.append("Source disclosure required but user wants closed source")
            explanations.append(
                f"{license_id} requires disclosing source code (disclose_source=true), "
                f"but you indicated closed_source=true."
            )
            how_explanations.append(
                f"HOW: The engine checked {license_id}'s conditions and found disclose_source=true. "
                f"You answered closed_source=true, so this license was flagged as incompatible."
            )

        # Same license check
        if conditions.get("same_license") and facts.get("wants_relicense"):
            violations.append("Same license required but user wants to relicense")
            explanations.append(
                f"{license_id} requires derivatives use the same license (same_license=true), "
                f"but you want freedom to relicense."
            )
            how_explanations.append(
                f"HOW: The engine checked {license_id}'s conditions and found same_license=true. "
                f"You answered wants_relicense=true, so this license was flagged as incompatible."
            )

        # Network copyleft check
        if conditions.get("net_copyleft") and facts.get("saas") and facts.get("closed_source"):
            violations.append("Network copyleft conflicts with closed-source SaaS")
            explanations.append(
                f"{license_id} triggers copyleft on network use (net_copyleft=true). "
                f"Running this as a closed-source SaaS violates this condition."
            )
            how_explanations.append(
                f"HOW: The engine checked {license_id}'s conditions and found net_copyleft=true. "
                f"You answered saas=true AND closed_source=true, so this license was flagged."
            )

        # Commercial use check
        if not permissions.get("commercial_use") and facts.get("commercial_use"):
            violations.append("Commercial use prohibited")
            explanations.append(
                f"{license_id} does not permit commercial use (commercial_use=false)."
            )
            how_explanations.append(
                f"HOW: The engine checked {license_id}'s permissions and found commercial_use=false. "
                f"You answered commercial_use=true, so this license was flagged."
            )

        # Patent protection check (warning, not violation)
        if facts.get("need_patent_protection") and not license_info.get("limitations", {}).get("patent_use"):
            explanations.append(
                f"⚠️ {license_id} does not include an explicit patent grant. "
                f"Consider Apache-2.0 if patent protection is critical."
            )
            how_explanations.append(
                f"HOW: The engine checked {license_id}'s limitations and found patent_use=false. "
                f"You answered need_patent_protection=true, so a warning was generated."
            )

        compatible = len(violations) == 0

        # Build the HOW explanation
        how_result = "\n".join(how_explanations) if how_explanations else (
            f"HOW: The engine checked all conditions of {license_id} against your answers. "
            f"No conflicts were found, so the license is compatible with your intended use."
        )

        return {
            "compatible": compatible,
            "violations": violations,
            "explanation": "\n".join(explanations) if explanations else f"{license_id} is compatible with your intended use.",
            "how": how_result,
            "license_info": license_info
        }

    def get_explanation(self):
        """Get the explanation engine for formatting output."""
        return self.explanation
