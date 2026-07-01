"""
Prolog-based inference engine using pyswip.

Bridges Python interface to SWI-Prolog knowledge base.
All rules live in Rules/license_rules.pl.
"""

from typing import Any, Dict, List, Optional, Set
from pathlib import Path

from pyswip import Prolog


# Metadata condition checks shared between _metadata_fallback and backward_chain.
# Each entry: (condition_field, fact_key, message, how_template)
METADATA_CONDITIONS = [
    (
        "disclose_source",
        "closed_source",
        "License requires source disclosure, but you want closed-source",
        "{license_id} requires disclose_source=true, but you answered closed_source=true",
    ),
    (
        "same_license",
        "wants_relicense",
        "License requires derivatives to use the same license, but you want to relicense",
        "{license_id} requires same_license=true, but you answered wants_relicense=true",
    ),
    # net_copyleft is a special compound check (needs saas AND closed_source)
]


def _check_metadata_conditions(
    license_id: str,
    facts: Dict[str, Any],
    conds: Dict[str, Any],
    perms: Dict[str, Any],
) -> tuple:
    """
    Check license metadata conditions against user facts.
    Returns (violations, how_steps) as parallel lists.
    """
    violations = []
    how_steps = []

    for cond_field, fact_key, message, how_template in METADATA_CONDITIONS:
        if conds.get(cond_field) and facts.get(fact_key):
            violations.append(message)
            how_steps.append(how_template.format(license_id=license_id))

    # Compound check: net_copyleft + saas + closed_source
    if conds.get("net_copyleft") and facts.get("saas") and facts.get("closed_source"):
        violations.append(
            "License has network copyleft, incompatible with closed-source SaaS"
        )
        how_steps.append(
            f"{license_id} has net_copyleft=true, but you want SaaS + closed-source"
        )

    # Permission check: commercial_use
    if not perms.get("commercial_use") and facts.get("commercial_use"):
        violations.append("License prohibits commercial use, but you need it")
        how_steps.append(
            f"{license_id} has commercial_use=false, but you answered commercial_use=true"
        )

    return violations, how_steps


class PrologEngine:
    """SWI-Prolog inference engine via pyswip."""

    def __init__(self):
        self.prolog = Prolog()
        rules_path = Path(__file__).parent.parent / "Rules" / "license_rules.pl"
        if not rules_path.exists():
            raise FileNotFoundError(f"Prolog knowledge base not found: {rules_path}")
        self.prolog.consult(str(rules_path))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_facts(self, facts: Dict[str, Any]) -> None:
        """Assert user facts into the Prolog knowledge base."""
        list(self.prolog.query("clear_facts, clear_trace"))
        for key, value in facts.items():
            if value is True:
                self.prolog.assertz(f"fact({key})")

    def get_question_explanation(self, fact_name: str) -> str:
        """Query Prolog for why a particular question is asked."""
        for sol in self.prolog.query(
            f"get_question_explanation({fact_name}, E)"
        ):
            return sol["E"]
        return "This question helps narrow down compatible licenses."

    def _find_license(
        self, license_id: str, licenses_data: List[Dict]
    ) -> Optional[Dict]:
        """Find a license dict by id or spdx_id."""
        for lic in licenses_data:
            if lic.get("id") == license_id or lic.get("spdx_id") == license_id:
                return lic
        return None

    def _get_possible_ids(
        self, license_id: str, lic: Optional[Dict]
    ) -> Set[str]:
        """Build set of possible IDs to check (original + spdx variants)."""
        ids = {license_id}
        if lic:
            if lic.get("id"):
                ids.add(lic["id"])
            if lic.get("spdx_id"):
                ids.add(lic["spdx_id"])
        ids.discard(None)
        return ids

    def build_trace(self) -> List[Dict]:
        """Query step/6 facts and build trace preserving original format."""
        trace = []
        for sol in self.prolog.query(
            "step(Id, Name, Type, Facts, Affected, Explanation)"
        ):
            trace.append({
                "step": len(trace) + 1,
                "rule_id": sol["Id"],
                "rule_name": sol["Name"],
                "matched_facts": {f: True for f in sol["Facts"]},
                "explanation": sol["Explanation"],
                "action": sol["Type"],
                "licenses_affected": sol["Affected"],
            })
        return trace

    # ------------------------------------------------------------------
    # Forward chain
    # ------------------------------------------------------------------

    def forward_chain(
        self,
        facts: Dict[str, Any],
        licenses_data: List[Dict],
    ) -> Dict[str, Any]:
        """
        Run all Prolog rules against user facts.
        Returns working memory: {recommended, eliminated, warnings}.
        """
        self._load_facts(facts)

        recommended = set()
        for sol in self.prolog.query("recommend(L)"):
            recommended.add(sol["L"])

        eliminated = set()
        for sol in self.prolog.query("eliminate(L)"):
            eliminated.add(sol["L"])

        warnings = []
        for sol in self.prolog.query("warning(L, Msg)"):
            warnings.append(f"{sol['L']}: {sol['Msg']}")

        # Elimination wins
        recommended -= eliminated

        return {
            "recommended": recommended,
            "eliminated": eliminated,
            "warnings": warnings,
        }

    # ------------------------------------------------------------------
    # Backward chain
    # ------------------------------------------------------------------

    def backward_chain(
        self,
        license_id: str,
        facts: Dict[str, Any],
        licenses_data: List[Dict],
    ) -> Dict[str, Any]:
        """
        Check compatibility of a specific license.
        1. Run forward rules via Prolog.
        2. Query compatible/2 for the license.
        3. Fall back to metadata check if unknown.
        """
        self._load_facts(facts)

        # Find the license metadata
        lic = self._find_license(license_id, licenses_data)
        possible_ids = self._get_possible_ids(license_id, lic)

        # Query Prolog for this license
        prolog_status = {}
        for pid in possible_ids:
            for sol in self.prolog.query(f"compatible('{pid}', R)"):
                prolog_status[pid] = sol["R"]

        # Collect trace
        trace = self.build_trace()

        # Determine status
        is_eliminated = any(
            prolog_status.get(pid) == "incompatible" for pid in possible_ids
        )
        is_recommended = any(
            prolog_status.get(pid) == "compatible" for pid in possible_ids
        )

        if is_eliminated:
            compatible = False
            # Collect violations from trace steps that eliminated this license
            violation_steps = [
                s
                for s in trace
                if s["action"] == "ELIMINATE"
                and any(
                    pid in s.get("licenses_affected", []) for pid in possible_ids
                )
            ]
            violations = [s["explanation"] for s in violation_steps]
            how_steps = [
                f"Step {s['step']}: {s['explanation']}" for s in violation_steps
            ]
            explanation = (
                "\n".join(violations)
                if violations
                else f"{license_id} was eliminated by the rules."
            )
            how = "\n".join(how_steps)

        elif is_recommended:
            compatible = True
            rec_steps = [
                s
                for s in trace
                if s["action"] == "RECOMMEND"
                and any(
                    pid in s.get("licenses_affected", []) for pid in possible_ids
                )
            ]
            explanation = f"{license_id} is recommended based on your answers."
            how = (
                "\n".join(
                    f"Step {s['step']}: {s['explanation']}" for s in rec_steps
                )
                if rec_steps
                else "Forward rules did not explicitly recommend this licence."
            )
            violations = []

        else:
            # Neither recommended nor eliminated — metadata fallback
            if lic is None:
                return {
                    "compatible": False,
                    "violations": [f"License '{license_id}' not found in the database."],
                    "explanation": f"Unknown licence: {license_id}",
                    "how": (
                        "This license is not in our database. "
                        "Please check the spelling or use a valid SPDX ID."
                    ),
                    "license_info": None,
                    "warnings": [],
                    "trace": trace,
                }

            conds = lic.get("conditions", {})
            perms = lic.get("permissions", {})
            violations, how_steps = _check_metadata_conditions(
                license_id, facts, conds, perms
            )

            # Patent warning
            if facts.get("need_patent_protection") and not lic.get(
                "limitations", {}
            ).get("patent_use"):
                how_steps.append(
                    f"{license_id} offers no patent protection "
                    f"(patent_use=false) - consider this carefully"
                )

            compatible = len(violations) == 0
            explanation = (
                "\n".join(violations)
                if violations
                else f"{license_id} appears compatible based on metadata."
            )
            how = (
                "\n".join(how_steps)
                if how_steps
                else "No conflicts found in direct metadata check."
            )

        # Collect warnings relevant to this license
        relevant_warnings = [
            s["explanation"]
            for s in trace
            if s["action"] == "WARN"
            and any(pid in s.get("licenses_affected", []) for pid in possible_ids)
        ]

        return {
            "compatible": compatible,
            "violations": violations,
            "explanation": explanation,
            "how": how,
            "license_info": lic,
            "warnings": relevant_warnings,
            "trace": trace,
        }
