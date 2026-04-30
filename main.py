#!/usr/bin/env python3
"""
LicenseWise – Main Entry Point
Intelligent Software License Selection & Compliance Analyzer

Usage:
    python main.py              # Interactive CLI
    python main.py --recommend  # Recommendation mode directly
    python main.py --analyze    # Analysis mode directly
"""

import sys
import argparse

# Add project root to path
sys.path.insert(0, '.')

from interface.cli import LicenseWiseCLI


def main():
    parser = argparse.ArgumentParser(
        description="LicenseWise – Intelligent Software License Selection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Interactive mode
  python main.py --recommend  # Start recommendation wizard
  python main.py --analyze    # Start license analysis
        """
    )

    parser.add_argument(
        "--recommend",
        action="store_true",
        help="Start license recommendation wizard"
    )

    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Start license analysis mode"
    )

    args = parser.parse_args()

    cli = LicenseWiseCLI()

    if args.recommend:
        cli.run_recommendation()
    elif args.analyze:
        cli.run_analysis()
    else:
        cli.run()


if __name__ == "__main__":
    main()
