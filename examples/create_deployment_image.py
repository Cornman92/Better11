"""
Example: Create Custom Windows Deployment Image

This script demonstrates how to create a customized Windows installation image
with drivers, updates, and applications pre-installed.

Usage:
    python examples/create_deployment_image.py --source install.wim --output custom.wim

Requirements:
    - Administrator privileges
    - Windows ADK (for some operations)
    - Source Windows image (WIM/ESD)
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from better11.image_manager import ImageManager
from better11.driver_manager import DriverManager
from better11.package_manager import PackageCache


def main():
    parser = argparse.ArgumentParser(description="Create custom Windows deployment image")
    parser.add_argument("--source", required=True, help="Source WIM/ESD file")
    parser.add_argument("--output", required=True, help="Output WIM file")
    parser.add_argument("--drivers", help="Driver folder to inject")
    parser.add_argument("--updates", help="Updates folder to inject")
    parser.add_argument("--index", type=int, default=1, help="Image index (default: 1)")
    parser.add_argument("--optimize", action="store_true", help="Optimize image after customization")

    args = parser.parse_args()

    print("=" * 70)
    print("Windows Deployment Image Creator")
    print("=" * 70)
    print()

    # Verify source image exists
    if not Path(args.source).exists():
        print(f"Error: Source image not found: {args.source}")
        return 1

    # Initialize manager
    print("[1/6] Initializing image manager...")
    image_manager = ImageManager(verbose=True)
    print("  ✓ Image manager ready")
    print()

    # Step 1: Export/Copy source image
    print(f"[2/6] Preparing image from {args.source}...")
    print(f"  Index: {args.index}")

    try:
        # Export to new file
        success = image_manager.dism.export_image(
            args.source,
            args.output,
            args.index,
            compress="max"
        )

        if success:
            print(f"  ✓ Image exported to {args.output}")
        else:
            print("  ✗ Image export failed")
            return 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 1

    print()

    # Step 2: Inject Drivers
    if args.drivers:
        print(f"[3/6] Injecting drivers from {args.drivers}...")

        if not Path(args.drivers).exists():
            print(f"  ⚠ Driver folder not found: {args.drivers}")
        else:
            try:
                success = image_manager.inject_drivers_to_image(
                    args.output,
                    args.drivers,
                    index=args.index
                )

                if success:
                    print("  ✓ Drivers injected successfully")
                else:
                    print("  ✗ Driver injection failed")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    else:
        print("[3/6] Skipping driver injection (no driver folder specified)")

    print()

    # Step 3: Inject Updates
    if args.updates:
        print(f"[4/6] Injecting updates from {args.updates}...")

        if not Path(args.updates).exists():
            print(f"  ⚠ Updates folder not found: {args.updates}")
        else:
            try:
                success_count, fail_count = image_manager.inject_updates_to_image(
                    args.output,
                    args.updates,
                    index=args.index
                )

                print(f"  ✓ Successfully injected: {success_count}")
                if fail_count > 0:
                    print(f"  ⚠ Failed to inject: {fail_count}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    else:
        print("[4/6] Skipping update injection (no updates folder specified)")

    print()

    # Step 4: Optimize Image
    if args.optimize:
        print("[5/6] Optimizing image...")

        try:
            success = image_manager.optimize_image(args.output, index=args.index)

            if success:
                print("  ✓ Image optimized successfully")
            else:
                print("  ✗ Image optimization failed")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    else:
        print("[5/6] Skipping optimization")

    print()

    # Step 5: Summary
    print("[6/6] Image creation complete!")
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Output Image: {args.output}")
    print(f"  Drivers Injected: {'Yes' if args.drivers else 'No'}")
    print(f"  Updates Injected: {'Yes' if args.updates else 'No'}")
    print(f"  Optimized: {'Yes' if args.optimize else 'No'}")
    print()

    print("Next steps:")
    print("  1. Test the image in a VM")
    print("  2. Create bootable USB with ISO manager")
    print("  3. Deploy to target machines")
    print()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
