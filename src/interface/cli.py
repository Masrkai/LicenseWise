import os
import sys
from pathlib import Path

# Add project root for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Inference.backward_chain import backward_chain
from Inference.forward_chain import forward_chain
from Inference.explanation_engine import explain_question, generate_final_report, generate_summary
from Rules.rules import RULES
from interface.common import get_licenses_data, yes_no_to_bool, distribute_to_closed_source


# ----------------------------------------------------------------------
# Helper to ask questions
# ----------------------------------------------------------------------
def ask_yes_no(question: str, fact_name: str, facts: dict) -> None:
    """Ask a yes/no question, store answer, and show explanation."""
    print(f"\n❓ {question}")
    print(f"   💡 Why we ask: {explain_question(fact_name)}")
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
    """Ask a multiple‑choice question."""
    print(f"\n❓ {question}")
    print(f"   💡 Why we ask: {explain_question(fact_name)}")
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
def run_recommendation(licenses_data: list) -> None:
    """Run the license recommendation wizard."""
    print("=" * 60)
    print("🔹 LicenseWise – License Recommendation Wizard")
    print("=" * 60)
    print("\nAnswer the following questions about your project.")
    print("Type 'skip' or press Enter to skip any question.\n")

    facts = {}

    # Distribution -> closed_source using shared utility
    ask_yes_no("Will you distribute your software to others?", "distribute", facts)
    facts["closed_source"] = distribute_to_closed_source(facts.get("distribute"))
    facts.pop("distribute", None)

    ask_yes_no("Will the software be used over a network (SaaS/web app)?", "saas", facts)
    ask_yes_no("Is commercial use intended?", "commercial_use", facts)
    ask_yes_no("Do you need patent protection?", "need_patent_protection", facts)
    ask_yes_no("Do you want derivatives to remain open source (copyleft)?", "want_copyleft", facts)

    if facts.get("want_copyleft"):
        ask_yes_no("Do you want copyleft only at the library level (weak copyleft)?", "want_weak_copyleft", facts)
        if not facts.get("want_weak_copyleft"):
            ask_yes_no("Do you want copyleft only at the file level?", "want_file_copyleft", facts)

    ask_yes_no("Do you want freedom to relicense derivatives?", "wants_relicense", facts)

    ask_choice("What type of project is this?", "project_type", ["Software", "Library", "Content"], facts)

    if facts.get("project_type") == "library":
        ask_choice("How will the library be linked?", "linking_type", ["Dynamic", "Static"], facts)
        ask_yes_no("Will you modify the library?", "modify_library", facts)

    ask_yes_no("Do you want to dedicate this to the public domain?", "want_public_domain", facts)

    if not facts.get("want_public_domain"):
        ask_yes_no("Do you prefer a simple permissive license (minimal requirements)?", "want_simple_permissive", facts)

    ask_yes_no("Is this an academic or research project?", "academic_project", facts)
    ask_yes_no("Will this be a mixed open/proprietary codebase?", "mixed_open_proprietary", facts)
    ask_yes_no("Are you concerned about legal recognition in all jurisdictions?", "concerned_about_legal_recognition", facts)

    print("\n" + "=" * 60)
    print("🧠 Analyzing your requirements...")
    print("=" * 60)

    trace = []
    wm = forward_chain(facts, RULES, licenses_data, trace)

    report = generate_final_report(wm, facts, trace)
    print(report)
    summary = generate_summary(wm, facts, trace)
    print(summary)


# ----------------------------------------------------------------------
# Analysis mode (fixed version)
# ----------------------------------------------------------------------
def run_analysis(licenses_data: list) -> None:
    """Check compatibility of a specific license."""
    print("=" * 60)
    print("🔹 LicenseWise – License Analysis")
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
    facts["closed_source"] = distribute_to_closed_source(facts.get("distribute"))
    facts.pop("distribute", None)

    ask_yes_no("Will it be used over a network (SaaS)?", "saas", facts)
    ask_yes_no("Is commercial use intended?", "commercial_use", facts)
    ask_yes_no("Do you need patent protection?", "need_patent_protection", facts)
    ask_yes_no("Do you want to relicense derivatives?", "wants_relicense", facts)

    # Run the backward chain
    result = backward_chain(license_id, facts, licenses_data)

    print("\n" + "=" * 60)
    if result["compatible"] is True:
        print(f"✅ {license_id} is COMPATIBLE with your intended use.")
    elif result["compatible"] is False:
        print(f"❌ {license_id} is NOT COMPATIBLE with your intended use.")
    else:
        print(f"❓ {license_id} compatibility unclear. See explanation below.")

    # Show violations
    if result.get("violations"):
        print("\n⚠️  Violations found:")
        for v in result["violations"]:
            print(f"   • {v}")

    # Show explanation
    print(f"\n💡 Analysis:")
    for line in result['explanation'].split('\n'):
        if line.strip():
            print(f"   {line}")

    # Show how the decision was made
    if result.get("how"):
        print(f"\n🔍 Reasoning:")
        for line in result['how'].split('\n'):
            if line.strip():
                print(f"   {line}")

    # Show warnings
    if result.get("warnings"):
        print(f"\n⚠️  Warnings:")
        for w in result["warnings"]:
            print(f"   • {w}")

    # Show license info if available
    if result.get("license_info"):
        lic = result["license_info"]
        print(f"\n📄 License Info: {lic.get('name', license_id)}")
        print(f"   Type: {lic.get('type', 'unknown')}")
        if lic.get('description'):
            print(f"   Description: {lic['description']}")

    # Suggest alternatives if incompatible
    if not result["compatible"] and result["violations"]:
        print("\n💡 Alternative licenses to consider:")
        all_text = " ".join(result["violations"]).lower() + " " + result.get("explanation", "").lower()
        
        suggestions = []
        if "source disclosure" in all_text or "disclose_source" in all_text or "closed" in all_text:
            suggestions.extend([
                "MIT – No source disclosure required",
                "Apache-2.0 – No source disclosure + patent grant",
                "BSD-2-Clause – Simple permissive, no source disclosure"
            ])
        if "same license" in all_text or "same_license" in all_text or "relicense" in all_text:
            suggestions.extend([
                "MIT – No same-license requirement",
                "Apache-2.0 – No same-license requirement"
            ])
        if "commercial" in all_text:
            suggestions.extend([
                "MIT – Allows commercial use",
                "Apache-2.0 – Allows commercial use with patent grant"
            ])
        if "network" in all_text or "saas" in all_text:
            suggestions.extend([
                "MIT – No network copyleft",
                "Apache-2.0 – No network copyleft"
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        for sugg in suggestions:
            if sugg not in seen:
                print(f"   • {sugg}")
                seen.add(sugg)

    print("\n" + "=" * 60)
    print("⚠️  DISCLAIMER: This is not legal advice. Consult a lawyer.")
    print("=" * 60)


# ----------------------------------------------------------------------
# Main CLI entry
# ----------------------------------------------------------------------
def main_cli():
    try:
        licenses_data = get_licenses_data()
        print(f"✓ Loaded {len(licenses_data)} licenses from JSON files.")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("\n💡 Make sure you have one of the following:", file=sys.stderr)
        print("   • licenses.json in your project root", file=sys.stderr)
        print("   • licenses.json in Licenses/ directory", file=sys.stderr)
        print("   • *.json files in Licenses/ directory", file=sys.stderr)
        sys.exit(1)

    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           📘 LICENSEWISE – Knowledge-Based System            ║")
    print("║         Intelligent Software License Selection               ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    while True:
        print("\nSelect mode:")
        print("[1] License Recommendation – Find the best license for your project")
        print("[2] License Analysis – Check if a specific license fits your needs")
        print("[3] Exit")

        choice = input("\nChoice: ").strip()
        if choice == "1":
            run_recommendation(licenses_data)
        elif choice == "2":
            run_analysis(licenses_data)
        elif choice == "3":
            print("\nGoodbye! 👋")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main_cli()