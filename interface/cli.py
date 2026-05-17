import os
import sys
import json
from pathlib import Path

# Add project root for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Inference.backward_chain import backward_chain
from Inference.forward_chain import forward_chain
from Inference.explanation_engine import explain_question, generate_final_report, generate_summary
from Rules.rules import RULES

# ----------------------------------------------------------------------
# Load license data from JSON files (in memory, not combined to one file)
# ----------------------------------------------------------------------
def load_all_licenses(licenses_dir: Path) -> list:
    """Load all JSON files from Licenses/ directory and return list of license dicts."""
    all_licenses = []
    for json_file in licenses_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            licenses = data.get("licenses", [])
            all_licenses.extend(licenses)
    return all_licenses

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

    # Distribution -> closed_source
    ask_yes_no("Will you distribute your software to others?", "distribute", facts)
    if facts.get("distribute") is not None:
        facts["closed_source"] = not facts["distribute"]
    else:
        facts["closed_source"] = None
    # Remove distribute to avoid confusion
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
# Analysis mode (backward chaining)
# ----------------------------------------------------------------------
def run_analysis(licenses_data: list) -> None:
    """Check compatibility of a specific license."""
    print("=" * 60)
    print("🔹 LicenseWise – License Analysis")
    print("=" * 60)

    license_id = input("\nEnter license name or SPDX ID (e.g., GPL-3.0): ").strip()
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
    if facts.get("distribute") is not None:
        facts["closed_source"] = not facts["distribute"]
    else:
        facts["closed_source"] = None
    facts.pop("distribute", None)

    ask_yes_no("Will it be used over a network (SaaS)?", "saas", facts)
    ask_yes_no("Is commercial use intended?", "commercial_use", facts)
    ask_yes_no("Do you need patent protection?", "need_patent_protection", facts)
    ask_yes_no("Do you want to relicense derivatives?", "wants_relicense", facts)

    result = backward_chain(license_id, facts, licenses_data)

    print("\n" + "=" * 60)
    if result["compatible"]:
        print(f"✅ {license_id} is COMPATIBLE with your intended use.")
    else:
        print(f"❌ {license_id} is NOT COMPATIBLE with your intended use.")

    if result["violations"]:
        print("\nViolations:")
        for v in result["violations"]:
            print(f"   • {v}")

    print(f"\n💡 Analysis:\n   {result['explanation']}")
    print(f"\n🔍 HOW the engine reached this conclusion:\n   {result['how']}")

    if not result["compatible"]:
        print("\n📋 Alternative licenses to consider:")
        if any("source_disclosure" in v for v in result["violations"]):
            print("   • MIT – No source disclosure required")
            print("   • Apache-2.0 – No source disclosure + patent grant")
        if any("same_license" in v for v in result["violations"]):
            print("   • MIT – No same-license requirement")
            print("   • Apache-2.0 – No same-license requirement")
        if any("commercial" in v for v in result["violations"]):
            print("   • Any OSI-approved permissive license (MIT, Apache-2.0)")

    print("\n" + "=" * 60)
    print("⚠️ DISCLAIMER: This is not legal advice. Consult a lawyer.")
    print("=" * 60)

# ----------------------------------------------------------------------
# Main CLI entry
# ----------------------------------------------------------------------
def main_cli():
    """Main entry point for CLI."""
    # Locate Licenses directory
    base_dir = Path(__file__).parent.parent
    licenses_dir = base_dir / "Licenses"
    if not licenses_dir.exists():
        print("ERROR: Licenses directory not found.", file=sys.stderr)
        sys.exit(1)

    licenses_data = load_all_licenses(licenses_dir)
    print(f"Loaded {len(licenses_data)} licenses from JSON files.")

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