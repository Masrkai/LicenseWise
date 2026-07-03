"""
Prolog-based inference engine using pyswip.

Bridges Python interface to SWI-Prolog knowledge base.
All rules live in Rules/license_rules.pl.
"""

from typing import Any, Dict, List

from pyswip import Prolog

from config import PROLOG_RULES_PATH
from Inference.fact_manager import FactManager
from Inference.trace_builder import TraceBuilder
from Inference.license_lookup import find_license, get_possible_ids


class PrologEngine:
    """SWI-Prolog inference engine via pyswip."""

    def __init__(self):
        self.prolog = Prolog()
        if not PROLOG_RULES_PATH.exists():
            raise FileNotFoundError(f"Prolog knowledge base not found: {PROLOG_RULES_PATH}")
        self.prolog.consult(str(PROLOG_RULES_PATH))
        self.fact_manager = FactManager(self.prolog)
        self.trace_builder = TraceBuilder(self.prolog)

    def get_question_explanation(self, fact_name: str) -> str:
        """Query Prolog for why a particular question is asked."""
        for sol in self.prolog.query(
            f"get_question_explanation({fact_name}, E)"
        ):
            return sol["E"]
        return "This question helps narrow down compatible licenses."

    def forward_chain(
        self,
        facts: Dict[str, Any],
        licenses_data: List[Dict],
    ) -> Dict[str, Any]:
        """
        Run all Prolog rules against user facts.
        Returns working memory: {recommended, eliminated, warnings}.
        """
        self.fact_manager.load_facts(facts)

        recommended = {str(sol["L"]) for sol in self.prolog.query("recommend(L)")}
        eliminated = {str(sol["L"]) for sol in self.prolog.query("eliminate(L)")}
        warnings = [
            f"{str(sol['L'])}: {str(sol['Msg'])}" for sol in self.prolog.query("warning(L, Msg)")
        ]

        # Elimination wins
        recommended -= eliminated

        return {
            "recommended": recommended,
            "eliminated": eliminated,
            "warnings": warnings,
        }

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
        3. Return result (unknown only if license not in database).
        """
        self.fact_manager.load_facts(facts)

        # Find the license metadata and assert it for Prolog
        lic = find_license(license_id, licenses_data)
        possible_ids = get_possible_ids(license_id, lic)

        if lic:
            for pid in possible_ids:
                self.fact_manager.assert_license_metadata(pid, lic)

        # Query Prolog for this license
        prolog_status = {}
        for pid in possible_ids:
            for sol in self.prolog.query(f"compatible('{pid}', R)"):
                prolog_status[pid] = sol["R"]

        trace = self.trace_builder.build_trace()

        # Determine status
        is_eliminated = any(
            prolog_status.get(pid) == "incompatible" for pid in possible_ids
        )
        is_recommended = any(
            prolog_status.get(pid) == "compatible" for pid in possible_ids
        )

        if is_eliminated:
            compatible = False
            violation_steps = [
                s for s in trace
                if s["action"] == "ELIMINATE"
                and any(pid in s.get("licenses_affected", []) for pid in possible_ids)
            ]
            violations = [s["explanation"] for s in violation_steps]
            how = "\n".join(f"Step {s['step']}: {s['explanation']}" for s in violation_steps)
            explanation = "\n".join(violations) if violations else f"{license_id} was eliminated by the rules."

        elif is_recommended:
            compatible = True
            rec_steps = [
                s for s in trace
                if s["action"] == "RECOMMEND"
                and any(pid in s.get("licenses_affected", []) for pid in possible_ids)
            ]
            explanation = f"{license_id} is recommended based on your answers."
            how = (
                "\n".join(f"Step {s['step']}: {s['explanation']}" for s in rec_steps)
                if rec_steps
                else "Forward rules did not explicitly recommend this licence."
            )
            violations = []

        else:
            if lic is None:
                return {
                    "compatible": False,
                    "violations": [f"License '{license_id}' not found in the database."],
                    "explanation": f"Unknown licence: {license_id}",
                    "how": "This license is not in our database. Please check the spelling or use a valid SPDX ID.",
                    "license_info": None,
                    "warnings": [],
                    "trace": trace,
                }
            compatible = None
            explanation = f"{license_id} could not be definitively classified."
            how = "No rules matched for this license."
            violations = []

        relevant_warnings = [
            s["explanation"] for s in trace
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
