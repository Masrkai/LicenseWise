import sys
from pathlib import Path

from Inference.backward_chain import backward_chain
from Inference.explanation_engine import (
    explain_question,
    generate_final_report,
    generate_summary,
    DISCLAIMER,
)
from Inference.forward_chain import forward_chain
from interface.common import (
    apply_closed_source_derivation,
    get_licenses_data,
    load_questions,
    suggest_alternatives,
    build_analysis_facts,
)


# ----------------------------------------------------------------------
# Helper to ask questions
# ----------------------------------------------------------------------
def ask_yes_no(question: str, fact_name: str, facts: dict) -> None:
    """Ask a yes/no question, store answer, and show explanation."""
    print(f"\n? {question}")
    print(f"   Why: {explain_question(fact_name)}")
    while True:
        ans = input("   Answer (yes/no/skip): ").strip().lower()
        if ans in ("yes", "y"):
            facts[fact_name] = True
            return
        elif ans in ("no", "n"):
            facts[fact_name] = False
            return
        elif ans in ("skip", "s", ""):
            facts[fact_name] = None
            return
        else:
            print("   Please answer 'yes', 'no', or 'skip'.")


def ask_choice(question: str, fact_name: str, choices: list, facts: dict) -> None:
    """Ask a multiple-choice question."""
    print(f"\n? {question}")
    print(f"   Why: {explain_question(fact_name)}")
    for i, choice in enumerate(choices, 1):
        print(f"   [{i}] {choice}")
    while True:
        ans = input("   Choice (number): ").strip()
        if not ans:
            facts[fact_name] = None
            return
        try:
            idx = int(ans) - 1
            if 0 <= idx < len(choices):
                facts[fact_name] = choices[idx].lower()
                return
            else:
                print("   Invalid number.")
        except ValueError:
            print("   Please enter a number.")


# ----------------------------------------------------------------------
# Recommendation mode
# ----------------------------------------------------------------------
def run_recommendation(licenses_data: list, verbose: bool = False) -> None:
    """Run the license recommendation wizard."""
    questions = load_questions()["recommendation"]

    print("=" * 60)
    print("LicenseWise - License Recommendation Wizard")
    print("=" * 60)
    print("\nAnswer the following questions about your project.")
    print("Type 'skip' or press Enter to skip any question.\n")

    facts = {}

    for q in questions:
        req = q.get("requires")
        if req:
            unless = req.get("unless")
            if (unless and facts.get(unless["fact"]) == unless["value"]) \
               or facts.get(req["fact"]) != req["value"]:
                continue

        fact_name = q["fact_name"]

        if q["type"] == "yes_no_skip":
            ask_yes_no(q["question"], fact_name, facts)
        elif q["type"] == "choice":
            ask_choice(q["question"], fact_name, q["choices"], facts)

        # Handle distribute -> closed_source conversion
        if fact_name == "distribute":
            apply_closed_source_derivation(facts)

    print("\n" + "=" * 60)
    print("Analyzing your requirements...")
    print("=" * 60)

    trace = []
    wm = forward_chain(facts, [], licenses_data, trace)

    report = generate_final_report(wm, facts, trace, include_trace=verbose)
    print(report)

    if verbose:
        summary = generate_summary(wm, facts, trace)
        print(summary)


# ----------------------------------------------------------------------
# Analysis mode
# ----------------------------------------------------------------------
def run_analysis(licenses_data: list) -> None:
    """Check compatibility of a specific license."""
    print("=" * 60)
    print("LicenseWise - License Analysis")
    print("=" * 60)

    license_id = input("\nEnter license name or SPDX ID (e.g., GPL-3.0, MIT): ").strip()
    if not license_id:
        print("No license entered.")
        return

    print("\nWhat is your intended use?")
    print("[1] Use in commercial closed-source application")
    print("[2] Use in open-source project with different license")
    print("[3] Modify and distribute without sharing source")
    print("[4] Use in SaaS without sharing source")
    print("[5] Other (describe below)")

    choice = input("\nChoice: ").strip()

    print("\nPlease answer a few quick questions:")
    facts = {}

    ask_yes_no("Will you distribute the software?", "distribute", facts)
    apply_closed_source_derivation(facts)

    ask_yes_no("Will it be used over a network (SaaS)?", "saas", facts)
    ask_yes_no("Is commercial use intended?", "commercial_use", facts)
    ask_yes_no("Do you need patent protection?", "need_patent_protection", facts)
    ask_yes_no("Do you want to relicense derivatives?", "wants_relicense", facts)

    # Run the backward chain
    result = backward_chain(license_id, facts, licenses_data)

    print("\n" + "=" * 60)
    if result["compatible"] is True:
        print(f"{license_id} is COMPATIBLE with your intended use.")
    elif result["compatible"] is False:
        print(f"{license_id} is NOT COMPATIBLE with your intended use.")
    else:
        print(f"{license_id} compatibility unclear. See explanation below.")

    # Show violations
    if result.get("violations"):
        print("\nViolations found:")
        for v in result["violations"]:
            print(f"   - {v}")

    # Show explanation
    print("\nAnalysis:")
    for line in result["explanation"].split("\n"):
        if line.strip():
            print(f"   {line}")

    # Show how the decision was made
    if result.get("how"):
        print("\nReasoning:")
        for line in result["how"].split("\n"):
            if line.strip():
                print(f"   {line}")

    # Show warnings
    if result.get("warnings"):
        print("\nWarnings:")
        for w in result["warnings"]:
            print(f"   - {w}")

    # Show license info if available
    if result.get("license_info"):
        lic = result["license_info"]
        print(f"\nLicense Info: {lic.get('name', license_id)}")
        print(f"   Type: {lic.get('type', 'unknown')}")
        if lic.get("description"):
            print(f"   Description: {lic['description']}")

    # Suggest alternatives if incompatible
    if not result["compatible"] and result["violations"]:
        print("\nAlternative licenses to consider:")
        all_text = (
            " ".join(result["violations"]).lower()
            + " "
            + result.get("explanation", "").lower()
        )
        for sugg in suggest_alternatives(all_text, format="plain"):
            print(f"   - {sugg}")

    print("\n" + "=" * 60)
    print(DISCLAIMER)
    print("=" * 60)


# ----------------------------------------------------------------------
# Main CLI entry
# ----------------------------------------------------------------------
def main_cli(verbose: bool = False) -> None:
    try:
        licenses_data = get_licenses_data()
        print(f"Loaded {len(licenses_data)} licenses from JSON files.")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("\nMake sure you have one of the following:", file=sys.stderr)
        print("   - licenses.json in your project root", file=sys.stderr)
        print("   - licenses.json in Licenses/ directory", file=sys.stderr)
        print("   - *.json files in Licenses/ directory", file=sys.stderr)
        sys.exit(1)

    print()
    print("============================================================")
    print("  LICENSEWISE - Knowledge-Based System")
    print("  Intelligent Software License Selection")
    print("============================================================")

    while True:
        print("\nSelect mode:")
        print("[1] License Recommendation - Find the best license for your project")
        print("[2] License Analysis - Check if a specific license fits your needs")
        print("[3] Exit")

        choice = input("\nChoice: ").strip()
        if choice == "1":
            run_recommendation(licenses_data, verbose=verbose)
        elif choice == "2":
            run_analysis(licenses_data)
        elif choice == "3":
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main_cli()
