import sys
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="LicenseWise - KBS License Advisor")
    parser.add_argument("--gui", action="store_true", help="Launch Slint GUI interface")
    parser.add_argument("--verbose", action="store_true", help="Show detailed reasoning trace")
    parser.add_argument(
        "-a", "--answers",
        type=str,
        help="Compact answer string for quick testing (skips interactive prompts)",
    )
    parser.add_argument(
        "--dump-merged-licenses",
        metavar="PATH",
        nargs="?",
        const="merged_licenses.json",
        default=None,
        help="Dump the merged license JSON to PATH for debugging (default: merged_licenses.json)",
    )
    args = parser.parse_args()

    if args.dump_merged_licenses:
        from src.Data.families_merger import dump_merged_json

        dump_merged_json(args.dump_merged_licenses)
        print(f"Merged license data written to {args.dump_merged_licenses}")
        return

    if args.gui:
        try:
            from src.interface.slint_app import launch_gui
            print("Starting Slint GUI interface...")
            launch_gui()
        except ImportError as e:
            print(e)
            sys.exit(1)
    else:
        from src.interface.cli import main_cli
        main_cli(verbose=args.verbose, answers=args.answers)


if __name__ == "__main__":
    main()
