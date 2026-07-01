import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="LicenseWise \u2013 KBS License Advisor")
    parser.add_argument("--gui", action="store_true", help="Launch Gradio web interface")
    args = parser.parse_args()

    if args.gui:
        try:
            from interface.gradio_app import launch_gui
            print("Starting Gradio web interface...")
            launch_gui()
        except ImportError as e:
            print(e)
            sys.exit(1)
    else:
        from interface.cli import main_cli
        main_cli()


if __name__ == "__main__":
    main()
