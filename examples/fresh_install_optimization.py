"""
Example: Fresh Windows Installation Optimization

This script demonstrates how to optimize a fresh Windows 11 installation
for gaming and general performance.

Usage:
    python examples/fresh_install_optimization.py

Requirements:
    - Administrator privileges
    - Fresh Windows 11 installation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from better11.system_optimizer import SystemOptimizer, OptimizationLevel
from better11.update_manager import WindowsUpdateManager
from better11.package_manager import UnifiedPackageManager, PackageManager
from better11.driver_manager import DriverManager


def main():
    print("=" * 60)
    print("Fresh Windows 11 Installation Optimization")
    print("=" * 60)
    print()

    # Step 1: System Metrics Before
    print("[1/6] Checking system metrics...")
    optimizer = SystemOptimizer(verbose=True)
    metrics_before = optimizer.get_system_metrics()

    print(f"  CPU Usage: {metrics_before.cpu_percent}%")
    print(f"  Memory Usage: {metrics_before.memory_percent}%")
    print(f"  Running Processes: {metrics_before.running_processes}")
    print(f"  Running Services: {metrics_before.running_services}")
    print()

    # Step 2: Windows Updates
    print("[2/6] Checking for Windows updates...")
    update_manager = WindowsUpdateManager(verbose=True)

    try:
        updates = update_manager.check_for_updates()
        if updates:
            print(f"  Found {len(updates)} updates")
            response = input("  Install all updates? (y/n): ")

            if response.lower() == 'y':
                print("  Installing updates...")
                success, reboot_required = update_manager.install_updates()

                if success:
                    print("  ✓ Updates installed successfully")
                    if reboot_required:
                        print("  ⚠ Reboot required to complete installation")
                else:
                    print("  ✗ Update installation failed")
        else:
            print("  ✓ System is up to date")
    except Exception as e:
        print(f"  ⚠ Update check failed: {e}")

    print()

    # Step 3: Driver Updates
    print("[3/6] Checking drivers...")
    driver_manager = DriverManager(verbose=True)

    try:
        missing_drivers = driver_manager.get_missing_drivers()
        if missing_drivers:
            print(f"  Found {len(missing_drivers)} devices with missing drivers:")
            for device in missing_drivers[:5]:  # Show first 5
                print(f"    - {device.get('Name', 'Unknown')}")

            response = input("  Create driver backup? (y/n): ")
            if response.lower() == 'y':
                print("  Backing up drivers...")
                count, backup_path = driver_manager.backup_all_drivers()
                print(f"  ✓ Backed up {count} drivers to: {backup_path}")
        else:
            print("  ✓ All drivers installed")
    except Exception as e:
        print(f"  ⚠ Driver check failed: {e}")

    print()

    # Step 4: Install Essential Apps
    print("[4/6] Installing essential applications...")
    package_manager = UnifiedPackageManager(verbose=True)

    essential_apps = [
        ("7zip.7zip", PackageManager.WINGET, "7-Zip"),
        ("Google.Chrome", PackageManager.WINGET, "Chrome"),
        ("VideoLAN.VLC", PackageManager.WINGET, "VLC Media Player"),
    ]

    print(f"  Essential apps to install:")
    for pkg_id, manager, name in essential_apps:
        print(f"    - {name}")

    response = input("  Install essential apps? (y/n): ")
    if response.lower() == 'y':
        for pkg_id, manager, name in essential_apps:
            print(f"  Installing {name}...")
            try:
                success = package_manager.install(manager, pkg_id)
                if success:
                    print(f"    ✓ {name} installed")
                else:
                    print(f"    ✗ {name} installation failed")
            except Exception as e:
                print(f"    ✗ {name} installation error: {e}")

    print()

    # Step 5: System Optimization
    print("[5/6] Applying gaming optimizations...")
    response = input("  Apply gaming mode optimizations? (y/n): ")

    if response.lower() == 'y':
        print("  Optimizing system...")
        results = optimizer.optimize_for_gaming()

        success_count = sum(1 for r in results if r.success)
        print(f"  ✓ Applied {success_count}/{len(results)} optimizations")

        # Show some results
        print("\n  Optimization details:")
        for result in results[:10]:  # Show first 10
            status = "✓" if result.success else "✗"
            print(f"    {status} {result.category}: {result.operation}")

    print()

    # Step 6: System Cleanup
    print("[6/6] Cleaning up system...")
    response = input("  Clean temporary files and optimize disk? (y/n): ")

    if response.lower() == 'y':
        print("  Cleaning system...")
        cleanup_results = optimizer.clean_system()

        temp_cleaned = cleanup_results.get('temp_files_cleaned', 0)
        temp_cleaned_mb = temp_cleaned / (1024 * 1024)

        print(f"  ✓ Cleaned {temp_cleaned_mb:.2f} MB of temporary files")

    print()

    # Final metrics
    print("=" * 60)
    print("Optimization Complete!")
    print("=" * 60)

    metrics_after = optimizer.get_system_metrics()
    print("\nSystem Metrics After Optimization:")
    print(f"  CPU Usage: {metrics_after.cpu_percent}%")
    print(f"  Memory Usage: {metrics_after.memory_percent}%")
    print(f"  Running Processes: {metrics_after.running_processes}")
    print(f"  Running Services: {metrics_after.running_services}")

    print("\n⚠ Recommendations:")
    print("  - Restart your computer to apply all changes")
    print("  - Run Windows Update again after restart")
    print("  - Check for graphics driver updates from manufacturer")
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
