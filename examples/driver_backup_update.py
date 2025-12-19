"""
Example: Automated Driver Backup and Update

This script demonstrates how to backup all drivers and check for updates.

Usage:
    python examples/driver_backup_update.py

Requirements:
    - Administrator privileges
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from better11.driver_manager import DriverManager


def main():
    print("=" * 60)
    print("Driver Backup and Update Tool")
    print("=" * 60)
    print()

    # Initialize manager
    print("[1/4] Initializing driver manager...")
    driver_manager = DriverManager(verbose=True)
    print("  ✓ Driver manager ready")
    print()

    # Step 1: List current drivers
    print("[2/4] Scanning installed drivers...")
    try:
        drivers = driver_manager.get_all_drivers()
        print(f"  Found {len(drivers)} installed drivers")
        print()

        # Show summary by class
        driver_classes = {}
        for driver in drivers:
            cls = driver.class_name
            if cls not in driver_classes:
                driver_classes[cls] = 0
            driver_classes[cls] += 1

        print("  Driver breakdown by class:")
        for cls, count in sorted(driver_classes.items()):
            print(f"    {cls}: {count}")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 1

    print()

    # Step 2: Backup drivers
    print("[3/4] Backing up drivers...")
    response = input("  Create driver backup? (y/n): ")

    if response.lower() == 'y':
        try:
            count, backup_path = driver_manager.backup_all_drivers()
            print(f"  ✓ Backed up {count} drivers")
            print(f"  Location: {backup_path}")

            # Save backup info to log
            log_file = Path(backup_path) / "backup_info.txt"
            with open(log_file, 'w') as f:
                f.write(f"Driver Backup - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Drivers: {count}\n")
                f.write(f"Backup Path: {backup_path}\n\n")
                f.write("Driver Classes:\n")
                for cls, cnt in sorted(driver_classes.items()):
                    f.write(f"  {cls}: {cnt}\n")

            print(f"  ✓ Backup info saved to: {log_file}")

        except Exception as e:
            print(f"  ✗ Backup failed: {e}")

    print()

    # Step 3: Check for missing drivers
    print("[4/4] Checking for missing drivers...")
    try:
        missing = driver_manager.get_missing_drivers()

        if missing:
            print(f"  ⚠ Found {len(missing)} devices with issues:")
            for device in missing[:10]:  # Show first 10
                name = device.get('Name', 'Unknown')
                status = device.get('Status', 'Unknown')
                print(f"    - {name} (Status: {status})")

            if len(missing) > 10:
                print(f"    ... and {len(missing) - 10} more")

            print()
            print("  Recommendations:")
            print("    1. Visit manufacturer website for latest drivers")
            print("    2. Use Windows Update for basic drivers")
            print("    3. Check Device Manager for details")
        else:
            print("  ✓ All devices have drivers installed")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    print()
    print("=" * 60)
    print("Driver backup complete!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
