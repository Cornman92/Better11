"""
Better11 Main Entry Point

Command-line entry point for Better11 with all features.
"""

import sys
import argparse


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Better11 - Comprehensive Windows Management Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch TUI
  python -m better11 tui

  # Launch GUI
  python -m better11 gui

  # Image management
  python -m better11 image mount image.wim --index 1

  # USB creation
  python -m better11 usb create --iso windows.iso --drive E

  # Updates
  python -m better11 updates check
  python -m better11 updates install

  # Drivers
  python -m better11 drivers list
  python -m better11 drivers backup

  # Packages
  python -m better11 packages search chrome
  python -m better11 packages install winget chrome

  # Optimization
  python -m better11 optimize gaming
  python -m better11 optimize clean

For full documentation, visit: https://github.com/yourusername/better11
        """
    )

    parser.add_argument(
        'mode',
        choices=['tui', 'gui', 'image', 'usb', 'updates', 'drivers', 'packages', 'optimize', 'files'],
        help='Operation mode'
    )

    parser.add_argument(
        'action',
        nargs='?',
        help='Action to perform'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    args, remaining = parser.parse_known_args()

    if args.mode == 'tui':
        from better11.tui import main as tui_main
        tui_main()

    elif args.mode == 'gui':
        from better11.enhanced_gui import main as gui_main
        gui_main()

    elif args.mode == 'image':
        print("Image management CLI (to be implemented)")
        print(f"Action: {args.action}")

    elif args.mode == 'usb':
        print("USB creator CLI (to be implemented)")
        print(f"Action: {args.action}")

    elif args.mode == 'updates':
        print("Updates CLI (to be implemented)")
        print(f"Action: {args.action}")

    elif args.mode == 'drivers':
        print("Drivers CLI (to be implemented)")
        print(f"Action: {args.action}")

    elif args.mode == 'packages':
        print("Packages CLI (to be implemented)")
        print(f"Action: {args.action}")

    elif args.mode == 'optimize':
        print("Optimization CLI (to be implemented)")
        print(f"Action: {args.action}")

    elif args.mode == 'files':
        print("File management CLI (to be implemented)")
        print(f"Action: {args.action}")

    else:
        parser.print_help()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
