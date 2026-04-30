"""
CLI Interface for LicenseWise
Interactive command-line interface for license recommendation and analysis.
"""

import sys
from Inference.inference_engine import InferenceEngine
from Inference.explanation_engine import ExplanationEngine


class LicenseWiseCLI:
    """Interactive CLI for LicenseWise."""

    def __init__(self):
        self.engine = InferenceEngine()
        self.explanation = ExplanationEngine()
        self.facts = {}

    def ask_yes_no(self, question, fact_name):
        """Ask a yes/no question and store the fact."""
        print(f"\n❓ {question}")

        # Show why this question matters
        why = self.explanation.explain_question(fact_name, [])
        print(f"   💡 Why we ask: {why}")

        while True:
            answer = input("   Answer (yes/no/skip): ").strip().lower()
            if answer in ["yes", "y"]:
                self.facts[fact_name] = True
                return True
            elif answer in ["no", "n"]:
                self.facts[fact_name] = False
                return False
            elif answer in ["skip", "s", ""]:
                self.facts[fact_name] = None
                return None
            else:
                print("   Please answer 'yes', 'no', or 'skip'.")

    def ask_choice(self, question, fact_name, choices):
        """Ask a multiple-choice question."""
        print(f"\n❓ {question}")
        why = self.explanation.explain_question(fact_name, [])
        print(f"   💡 Why we ask: {why}")

        for i, choice in enumerate(choices, 1):
            print(f"   [{i}] {choice}")

        while True:
            answer = input("   Choice (number): ").strip()
            try:
                idx = int(answer) - 1
                if 0 <= idx < len(choices):
                    self.facts[fact_name] = choices[idx].lower()
                    return choices[idx].lower()
                else:
                    print("   Invalid choice.")
            except ValueError:
                if answer == "":
                    self.facts[fact_name] = None
                    return None
                print("   Please enter a number.")

    def run_recommendation(self):
        """Run the license recommendation wizard."""
        print("=" * 60)
        print("🔹 LicenseWise – License Recommendation Wizard")
        print("=" * 60)
        print("\nAnswer the following questions about your project.")
        print("Type 'skip' or press Enter to skip any question.\n")

        # Core questions
        self.ask_yes_no("Will you distribute your software to others?", "closed_source")
        # Invert: if they distribute, closed_source is False
        if self.facts.get("closed_source") is not None:
            self.facts["closed_source"] = not self.facts["closed_source"]

        self.ask_yes_no("Will the software be used over a network (SaaS/web app)?", "saas")
        self.ask_yes_no("Is commercial use intended?", "commercial_use")
        self.ask_yes_no("Do you need patent protection?", "need_patent_protection")
        self.ask_yes_no("Do you want derivatives to remain open source (copyleft)?", "want_copyleft")

        if self.facts.get("want_copyleft"):
            self.ask_yes_no("Do you want copyleft only at the library level (weak copyleft)?", "want_weak_copyleft")
            if not self.facts.get("want_weak_copyleft"):
                self.ask_yes_no("Do you want copyleft only at the file level?", "want_file_copyleft")

        self.ask_yes_no("Do you want freedom to relicense derivatives?", "wants_relicense")

        self.ask_choice(
            "What type of project is this?",
            "project_type",
            ["Software", "Library", "Content"]
        )

        if self.facts.get("project_type") == "library":
            self.ask_choice(
                "How will the library be linked?",
                "linking_type",
                ["Dynamic", "Static"]
            )
            self.ask_yes_no("Will you modify the library?", "modify_library")

        self.ask_yes_no("Do you want to dedicate this to the public domain?", "want_public_domain")

        if not self.facts.get("want_public_domain"):
            self.ask_yes_no("Do you prefer a simple permissive license (minimal requirements)?", "want_simple_permissive")

        self.ask_yes_no("Is this an academic or research project?", "academic_project")
        self.ask_yes_no("Will this be a mixed open/proprietary codebase?", "mixed_open_proprietary")
        self.ask_yes_no("Are you concerned about legal recognition in all jurisdictions?", "concerned_about_legal_recognition")

        # Run inference
        print("\n" + "=" * 60)
        print("🧠 Analyzing your requirements...")
        print("=" * 60)

        wm = self.engine.forward_chain(self.facts)

        # Generate and print report
        report = self.explanation.generate_final_report(wm, self.facts)
        print(report)

    def run_analysis(self):
        """Run the license analysis mode."""
        print("=" * 60)
        print("🔹 LicenseWise – License Analysis")
        print("=" * 60)

        license_id = input("\nEnter license name or SPDX ID (e.g., GPL-3.0): ").strip()

        print("\nWhat is your intended use?")
        print("[1] Use in commercial closed-source application")
        print("[2] Use in open-source project with different license")
        print("[3] Modify and distribute without sharing source")
        print("[4] Use in SaaS without sharing source")
        print("[5] Other (describe below)")

        choice = input("\nChoice: ").strip()

        # Collect minimal facts for analysis
        print("\nPlease answer a few quick questions:")
        self.facts = {}

        self.ask_yes_no("Will you distribute the software?", "closed_source")
        if self.facts.get("closed_source") is not None:
            self.facts["closed_source"] = not self.facts["closed_source"]

        self.ask_yes_no("Will it be used over a network (SaaS)?", "saas")
        self.ask_yes_no("Is commercial use intended?", "commercial_use")
        self.ask_yes_no("Do you need patent protection?", "need_patent_protection")
        self.ask_yes_no("Do you want to relicense derivatives?", "wants_relicense")

        # Run backward chaining
        result = self.engine.backward_chain(license_id, choice, self.facts)

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

        # Suggest alternatives if incompatible
        if not result["compatible"]:
            print("\n📋 Alternative licenses to consider:")
            if any("closed source" in v for v in result["violations"]):
                print("   • MIT – No source disclosure required")
                print("   • Apache-2.0 – No source disclosure + patent grant")
                print("   • BSD-2-Clause – Simple permissive")
            if any("same license" in v for v in result["violations"]):
                print("   • MIT – No same-license requirement")
                print("   • Apache-2.0 – No same-license requirement")
            if any("commercial" in v for v in result["violations"]):
                print("   • Any OSI-approved license (MIT, Apache-2.0, GPL, etc.)")

        print("\n" + "=" * 60)
        print("⚠️ DISCLAIMER: This is not legal advice. Consult a lawyer.")
        print("=" * 60)

    def run(self):
        """Main entry point."""
        print("\n")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                                                              ║")
        print("║           📘 LICENSEWISE – Knowledge-Based System            ║")
        print("║         Intelligent Software License Selection               ║")
        print("║                                                              ║")
        print("╚══════════════════════════════════════════════════════════════╝")

        print("\nSelect mode:")
        print("[1] License Recommendation – Find the best license for your project")
        print("[2] License Analysis – Check if a specific license fits your needs")
        print("[3] Exit")

        while True:
            choice = input("\nChoice: ").strip()

            if choice == "1":
                self.run_recommendation()
                break
            elif choice == "2":
                self.run_analysis()
                break
            elif choice == "3":
                print("\nGoodbye! 👋")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    cli = LicenseWiseCLI()
    cli.run()
