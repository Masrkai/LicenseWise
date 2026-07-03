import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="LicenseWise - KBS License Advisor")
    parser.add_argument("--gui", action="store_true", help="Launch Slint GUI interface")
    parser.add_argument("--verbose", action="store_true", help="Show detailed reasoning trace")
    args = parser.parse_args()

    if args.gui:
        try:
            from interface.slint_app import launch_gui
            print("Starting Slint GUI interface...")
            launch_gui()
        except ImportError as e:
            print(e)
            sys.exit(1)
    else:
        from interface.cli import main_cli
        main_cli(verbose=args.verbose)


if __name__ == "__main__":
    main()
