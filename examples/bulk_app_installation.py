"""
Example: Bulk Application Installation

This script demonstrates how to install multiple applications
using different package managers.

Usage:
    python examples/bulk_app_installation.py --profile gaming
    python examples/bulk_app_installation.py --profile development
    python examples/bulk_app_installation.py --custom apps.txt

Requirements:
    - Administrator privileges (recommended)
    - WinGet, Chocolatey, or other package managers installed
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from better11.package_manager import UnifiedPackageManager, PackageManager


# Predefined app profiles
PROFILES = {
    "gaming": [
        ("Steam", "Valve.Steam", PackageManager.WINGET),
        ("Discord", "Discord.Discord", PackageManager.WINGET),
        ("OBS Studio", "OBSProject.OBSStudio", PackageManager.WINGET),
        ("MSI Afterburner", "Guru3D.Afterburner", PackageManager.WINGET),
    ],
    "development": [
        ("Git", "Git.Git", PackageManager.WINGET),
        ("VSCode", "Microsoft.VisualStudioCode", PackageManager.WINGET),
        ("Python", "Python.Python.3.12", PackageManager.WINGET),
        ("Node.js", "OpenJS.NodeJS", PackageManager.WINGET),
        ("Docker Desktop", "Docker.DockerDesktop", PackageManager.WINGET),
    ],
    "productivity": [
        ("7-Zip", "7zip.7zip", PackageManager.WINGET),
        ("Notepad++", "Notepad++.Notepad++", PackageManager.WINGET),
        ("Chrome", "Google.Chrome", PackageManager.WINGET),
        ("VLC", "VideoLAN.VLC", PackageManager.WINGET),
        ("Zoom", "Zoom.Zoom", PackageManager.WINGET),
    ],
    "media": [
        ("VLC", "VideoLAN.VLC", PackageManager.WINGET),
        ("Spotify", "Spotify.Spotify", PackageManager.WINGET),
        ("Audacity", "Audacity.Audacity", PackageManager.WINGET),
        ("HandBrake", "HandBrake.HandBrake", PackageManager.WINGET),
    ]
}


def load_custom_apps(file_path):
    """Load apps from custom file"""
    apps = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    pkg_id = parts[1].strip()
                    manager = parts[2].strip() if len(parts) > 2 else "winget"

                    # Convert manager string to enum
                    manager_map = {
                        "winget": PackageManager.WINGET,
                        "choco": PackageManager.CHOCOLATEY,
                        "chocolatey": PackageManager.CHOCOLATEY,
                        "npm": PackageManager.NPM,
                        "pip": PackageManager.PIP,
                    }

                    apps.append((name, pkg_id, manager_map.get(manager.lower(), PackageManager.WINGET)))

    return apps


def main():
    parser = argparse.ArgumentParser(description="Bulk application installation")
    parser.add_argument("--profile", choices=list(PROFILES.keys()), help="App profile to install")
    parser.add_argument("--custom", help="Custom app list file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed without installing")

    args = parser.parse_args()

    if not args.profile and not args.custom:
        print("Error: Specify either --profile or --custom")
        print("\nAvailable profiles:")
        for profile in PROFILES.keys():
            print(f"  - {profile}")
        return 1

    print("=" * 60)
    print("Bulk Application Installation")
    print("=" * 60)
    print()

    # Get app list
    if args.profile:
        apps = PROFILES[args.profile]
        print(f"Profile: {args.profile}")
    else:
        print(f"Custom list: {args.custom}")
        try:
            apps = load_custom_apps(args.custom)
        except Exception as e:
            print(f"Error loading custom apps: {e}")
            return 1

    print(f"Total applications: {len(apps)}")
    print()

    # Display app list
    print("Applications to install:")
    for name, pkg_id, manager in apps:
        print(f"  [{manager.value}] {name}")

    print()

    if args.dry_run:
        print("Dry run - no installations will be performed")
        return 0

    response = input("Proceed with installation? (y/n): ")
    if response.lower() != 'y':
        print("Installation cancelled")
        return 0

    print()

    # Initialize package manager
    print("Initializing package manager...")
    pm = UnifiedPackageManager(verbose=True)

    # Check available managers
    available = pm.get_available_managers()
    print(f"Available package managers: {[m.value for m in available]}")
    print()

    # Install apps
    success_count = 0
    fail_count = 0

    for i, (name, pkg_id, manager) in enumerate(apps, 1):
        print(f"[{i}/{len(apps)}] Installing {name}...")

        if manager not in available:
            print(f"  ⚠ Package manager '{manager.value}' not available, skipping")
            fail_count += 1
            continue

        try:
            success = pm.install(manager, pkg_id)

            if success:
                print(f"  ✓ {name} installed successfully")
                success_count += 1
            else:
                print(f"  ✗ {name} installation failed")
                fail_count += 1

        except Exception as e:
            print(f"  ✗ Error installing {name}: {e}")
            fail_count += 1

        print()

    # Summary
    print("=" * 60)
    print("Installation Complete!")
    print("=" * 60)
    print(f"  Successfully installed: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"  Total: {len(apps)}")
    print()

    if fail_count > 0:
        print("⚠ Some installations failed. Check the output above for details.")

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
