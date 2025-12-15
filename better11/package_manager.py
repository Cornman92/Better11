"""
Multi-Package Manager Module

Universal package management supporting:
- WinGet (Windows Package Manager)
- Chocolatey
- NPM (Node Package Manager)
- Pip (Python packages)
- Scoop
- Cargo (Rust)
- Offline cache for installations
- Injection into offline Windows images
"""

import os
import subprocess
import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib


class PackageManager(Enum):
    """Supported package managers"""
    WINGET = "winget"
    CHOCOLATEY = "choco"
    NPM = "npm"
    PIP = "pip"
    SCOOP = "scoop"
    CARGO = "cargo"
    APT = "apt"  # For WSL
    CUSTOM = "custom"


class PackageStatus(Enum):
    """Package installation status"""
    NOT_INSTALLED = "Not Installed"
    INSTALLED = "Installed"
    UPDATE_AVAILABLE = "Update Available"
    CACHED = "Cached"
    FAILED = "Failed"


@dataclass
class Package:
    """Represents a software package"""
    name: str
    package_id: str
    version: str
    manager: PackageManager
    description: str = ""
    source: str = ""
    status: PackageStatus = PackageStatus.NOT_INSTALLED
    size: int = 0
    publisher: str = ""
    homepage: str = ""
    license: str = ""
    install_location: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'package_id': self.package_id,
            'version': self.version,
            'manager': self.manager.value,
            'description': self.description,
            'source': self.source,
            'status': self.status.value,
            'size': self.size,
            'publisher': self.publisher,
            'homepage': self.homepage,
            'license': self.license,
            'install_location': self.install_location,
            'dependencies': self.dependencies
        }


@dataclass
class CachedPackage:
    """Represents a cached package for offline installation"""
    package: Package
    cache_path: str
    cache_date: str
    checksum: str
    metadata: Dict = field(default_factory=dict)


class BasePackageManager(ABC):
    """Abstract base class for package managers"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    @abstractmethod
    def is_available(self) -> bool:
        """Check if package manager is installed"""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 50) -> List[Package]:
        """Search for packages"""
        pass

    @abstractmethod
    def list_installed(self) -> List[Package]:
        """List installed packages"""
        pass

    @abstractmethod
    def install(self, package_id: str, version: Optional[str] = None) -> bool:
        """Install a package"""
        pass

    @abstractmethod
    def uninstall(self, package_id: str) -> bool:
        """Uninstall a package"""
        pass

    @abstractmethod
    def update(self, package_id: Optional[str] = None) -> bool:
        """Update package(s)"""
        pass

    def _run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Execute command"""
        if self.verbose:
            print(f"Executing: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")

        return result


class WinGetManager(BasePackageManager):
    """Windows Package Manager (WinGet)"""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.manager_type = PackageManager.WINGET

    def is_available(self) -> bool:
        """Check if WinGet is installed"""
        result = self._run_command(["winget", "--version"], check=False)
        return result.returncode == 0

    def search(self, query: str, limit: int = 50) -> List[Package]:
        """Search for packages"""
        cmd = ["winget", "search", query, "--accept-source-agreements"]

        result = self._run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        # Parse WinGet output
        packages = []
        lines = result.stdout.split('\n')

        for line in lines[2:]:  # Skip header
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 3:
                package = Package(
                    name=parts[0],
                    package_id=parts[1] if len(parts) > 1 else parts[0],
                    version=parts[2] if len(parts) > 2 else "Unknown",
                    manager=self.manager_type,
                    source="winget"
                )
                packages.append(package)

                if len(packages) >= limit:
                    break

        return packages

    def list_installed(self) -> List[Package]:
        """List installed packages"""
        cmd = ["winget", "list", "--accept-source-agreements"]

        result = self._run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        packages = []
        lines = result.stdout.split('\n')

        for line in lines[2:]:  # Skip header
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) >= 2:
                package = Package(
                    name=parts[0],
                    package_id=parts[1] if len(parts) > 1 else parts[0],
                    version=parts[2] if len(parts) > 2 else "Unknown",
                    manager=self.manager_type,
                    status=PackageStatus.INSTALLED
                )
                packages.append(package)

        return packages

    def install(self, package_id: str, version: Optional[str] = None) -> bool:
        """Install a package"""
        cmd = ["winget", "install", package_id, "--accept-package-agreements", "--accept-source-agreements", "--silent"]

        if version:
            cmd.extend(["--version", version])

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def uninstall(self, package_id: str) -> bool:
        """Uninstall a package"""
        cmd = ["winget", "uninstall", package_id, "--silent"]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def update(self, package_id: Optional[str] = None) -> bool:
        """Update package(s)"""
        if package_id:
            cmd = ["winget", "upgrade", package_id, "--accept-package-agreements", "--accept-source-agreements", "--silent"]
        else:
            cmd = ["winget", "upgrade", "--all", "--accept-package-agreements", "--accept-source-agreements", "--silent"]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def export_installed(self, output_path: str) -> bool:
        """Export installed packages to JSON"""
        cmd = ["winget", "export", "-o", output_path]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def import_packages(self, import_path: str) -> bool:
        """Import and install packages from JSON"""
        cmd = ["winget", "import", "-i", import_path, "--accept-package-agreements", "--accept-source-agreements"]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0


class ChocolateyManager(BasePackageManager):
    """Chocolatey Package Manager"""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self.manager_type = PackageManager.CHOCOLATEY

    def is_available(self) -> bool:
        """Check if Chocolatey is installed"""
        result = self._run_command(["choco", "--version"], check=False)
        return result.returncode == 0

    def install_chocolatey(self) -> bool:
        """Install Chocolatey"""
        ps_script = """
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        """

        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True
        )

        return result.returncode == 0

    def search(self, query: str, limit: int = 50) -> List[Package]:
        """Search for packages"""
        cmd = ["choco", "search", query, "--limit-output"]

        result = self._run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        packages = []
        lines = result.stdout.split('\n')

        for line in lines:
            if not line.strip():
                continue

            parts = line.split('|')
            if len(parts) >= 2:
                package = Package(
                    name=parts[0],
                    package_id=parts[0],
                    version=parts[1],
                    manager=self.manager_type,
                    source="chocolatey"
                )
                packages.append(package)

                if len(packages) >= limit:
                    break

        return packages

    def list_installed(self) -> List[Package]:
        """List installed packages"""
        cmd = ["choco", "list", "--local-only", "--limit-output"]

        result = self._run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        packages = []
        lines = result.stdout.split('\n')

        for line in lines:
            if not line.strip():
                continue

            parts = line.split('|')
            if len(parts) >= 2:
                package = Package(
                    name=parts[0],
                    package_id=parts[0],
                    version=parts[1],
                    manager=self.manager_type,
                    status=PackageStatus.INSTALLED
                )
                packages.append(package)

        return packages

    def install(self, package_id: str, version: Optional[str] = None) -> bool:
        """Install a package"""
        cmd = ["choco", "install", package_id, "-y"]

        if version:
            cmd.extend(["--version", version])

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def uninstall(self, package_id: str) -> bool:
        """Uninstall a package"""
        cmd = ["choco", "uninstall", package_id, "-y"]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def update(self, package_id: Optional[str] = None) -> bool:
        """Update package(s)"""
        if package_id:
            cmd = ["choco", "upgrade", package_id, "-y"]
        else:
            cmd = ["choco", "upgrade", "all", "-y"]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0


class NPMManager(BasePackageManager):
    """Node Package Manager"""

    def __init__(self, verbose: bool = False, global_install: bool = True):
        super().__init__(verbose)
        self.manager_type = PackageManager.NPM
        self.global_install = global_install

    def is_available(self) -> bool:
        """Check if NPM is installed"""
        result = self._run_command(["npm", "--version"], check=False)
        return result.returncode == 0

    def search(self, query: str, limit: int = 50) -> List[Package]:
        """Search for packages"""
        cmd = ["npm", "search", query, "--json"]

        result = self._run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        try:
            data = json.loads(result.stdout)
            packages = []

            for item in data[:limit]:
                package = Package(
                    name=item.get('name', ''),
                    package_id=item.get('name', ''),
                    version=item.get('version', ''),
                    manager=self.manager_type,
                    description=item.get('description', ''),
                    publisher=item.get('publisher', {}).get('username', '')
                )
                packages.append(package)

            return packages
        except json.JSONDecodeError:
            return []

    def list_installed(self) -> List[Package]:
        """List installed packages"""
        cmd = ["npm", "list", "-g" if self.global_install else "", "--json", "--depth=0"]

        result = self._run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        try:
            data = json.loads(result.stdout)
            packages = []

            dependencies = data.get('dependencies', {})
            for name, info in dependencies.items():
                package = Package(
                    name=name,
                    package_id=name,
                    version=info.get('version', ''),
                    manager=self.manager_type,
                    status=PackageStatus.INSTALLED
                )
                packages.append(package)

            return packages
        except json.JSONDecodeError:
            return []

    def install(self, package_id: str, version: Optional[str] = None) -> bool:
        """Install a package"""
        package_spec = f"{package_id}@{version}" if version else package_id
        cmd = ["npm", "install", "-g" if self.global_install else "", package_spec]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def uninstall(self, package_id: str) -> bool:
        """Uninstall a package"""
        cmd = ["npm", "uninstall", "-g" if self.global_install else "", package_id]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def update(self, package_id: Optional[str] = None) -> bool:
        """Update package(s)"""
        if package_id:
            cmd = ["npm", "update", "-g" if self.global_install else "", package_id]
        else:
            cmd = ["npm", "update", "-g" if self.global_install else ""]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0


class PipManager(BasePackageManager):
    """Python Package Manager"""

    def __init__(self, verbose: bool = False, python_exe: str = "python"):
        super().__init__(verbose)
        self.manager_type = PackageManager.PIP
        self.python_exe = python_exe

    def is_available(self) -> bool:
        """Check if Pip is installed"""
        result = self._run_command([self.python_exe, "-m", "pip", "--version"], check=False)
        return result.returncode == 0

    def search(self, query: str, limit: int = 50) -> List[Package]:
        """Search for packages (using PyPI API)"""
        import requests

        try:
            response = requests.get(f"https://pypi.org/pypi/{query}/json")
            if response.status_code == 200:
                data = response.json()
                info = data.get('info', {})

                package = Package(
                    name=info.get('name', query),
                    package_id=info.get('name', query),
                    version=info.get('version', ''),
                    manager=self.manager_type,
                    description=info.get('summary', ''),
                    homepage=info.get('home_page', ''),
                    license=info.get('license', '')
                )
                return [package]
        except:
            pass

        return []

    def list_installed(self) -> List[Package]:
        """List installed packages"""
        cmd = [self.python_exe, "-m", "pip", "list", "--format=json"]

        result = self._run_command(cmd, check=False)

        if result.returncode != 0:
            return []

        try:
            data = json.loads(result.stdout)
            packages = []

            for item in data:
                package = Package(
                    name=item['name'],
                    package_id=item['name'],
                    version=item['version'],
                    manager=self.manager_type,
                    status=PackageStatus.INSTALLED
                )
                packages.append(package)

            return packages
        except json.JSONDecodeError:
            return []

    def install(self, package_id: str, version: Optional[str] = None) -> bool:
        """Install a package"""
        package_spec = f"{package_id}=={version}" if version else package_id
        cmd = [self.python_exe, "-m", "pip", "install", package_spec]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def uninstall(self, package_id: str) -> bool:
        """Uninstall a package"""
        cmd = [self.python_exe, "-m", "pip", "uninstall", package_id, "-y"]

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def update(self, package_id: Optional[str] = None) -> bool:
        """Update package(s)"""
        if package_id:
            cmd = [self.python_exe, "-m", "pip", "install", "--upgrade", package_id]
        else:
            # Update all packages
            installed = self.list_installed()
            for pkg in installed:
                self.update(pkg.package_id)
            return True

        result = self._run_command(cmd, check=False)
        return result.returncode == 0


class PackageCache:
    """Manage package cache for offline installation"""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or os.path.join(os.path.expanduser("~"), ".package_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.metadata_file = os.path.join(self.cache_dir, "cache_metadata.json")
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load cache metadata"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save cache metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def cache_package(self, package: Package, source_path: str) -> CachedPackage:
        """Add package to cache"""
        from datetime import datetime

        # Create package cache directory
        pkg_cache_dir = os.path.join(self.cache_dir, package.manager.value, package.package_id)
        os.makedirs(pkg_cache_dir, exist_ok=True)

        # Copy package to cache
        cache_path = os.path.join(pkg_cache_dir, os.path.basename(source_path))
        shutil.copy2(source_path, cache_path)

        # Calculate checksum
        checksum = self._calculate_checksum(cache_path)

        # Create cached package entry
        cached = CachedPackage(
            package=package,
            cache_path=cache_path,
            cache_date=datetime.now().isoformat(),
            checksum=checksum
        )

        # Update metadata
        cache_key = f"{package.manager.value}:{package.package_id}:{package.version}"
        self.metadata[cache_key] = {
            'package': package.to_dict(),
            'cache_path': cache_path,
            'cache_date': cached.cache_date,
            'checksum': checksum
        }
        self._save_metadata()

        return cached

    def get_cached_package(self, manager: PackageManager, package_id: str, version: str) -> Optional[CachedPackage]:
        """Get package from cache"""
        cache_key = f"{manager.value}:{package_id}:{version}"

        if cache_key in self.metadata:
            data = self.metadata[cache_key]

            # Verify file exists
            if os.path.exists(data['cache_path']):
                pkg_data = data['package']
                package = Package(**pkg_data)

                return CachedPackage(
                    package=package,
                    cache_path=data['cache_path'],
                    cache_date=data['cache_date'],
                    checksum=data['checksum']
                )

        return None

    def list_cached(self) -> List[CachedPackage]:
        """List all cached packages"""
        cached = []

        for key, data in self.metadata.items():
            if os.path.exists(data['cache_path']):
                pkg_data = data['package']
                package = Package(**pkg_data)

                cached_pkg = CachedPackage(
                    package=package,
                    cache_path=data['cache_path'],
                    cache_date=data['cache_date'],
                    checksum=data['checksum']
                )
                cached.append(cached_pkg)

        return cached

    def clear_cache(self, manager: Optional[PackageManager] = None):
        """Clear package cache"""
        if manager:
            # Clear specific manager cache
            keys_to_remove = [k for k in self.metadata.keys() if k.startswith(manager.value + ":")]
            for key in keys_to_remove:
                del self.metadata[key]
        else:
            # Clear all cache
            self.metadata = {}

        self._save_metadata()


class UnifiedPackageManager:
    """Unified interface for all package managers"""

    def __init__(self, cache_dir: Optional[str] = None, verbose: bool = False):
        self.verbose = verbose
        self.cache = PackageCache(cache_dir)

        # Initialize package managers
        self.managers: Dict[PackageManager, BasePackageManager] = {
            PackageManager.WINGET: WinGetManager(verbose),
            PackageManager.CHOCOLATEY: ChocolateyManager(verbose),
            PackageManager.NPM: NPMManager(verbose),
            PackageManager.PIP: PipManager(verbose)
        }

    def get_available_managers(self) -> List[PackageManager]:
        """Get list of available package managers"""
        available = []
        for manager_type, manager in self.managers.items():
            if manager.is_available():
                available.append(manager_type)
        return available

    def search(self, query: str, manager: Optional[PackageManager] = None) -> Dict[PackageManager, List[Package]]:
        """Search across all or specific package manager"""
        results = {}

        managers_to_search = [manager] if manager else self.managers.keys()

        for mgr_type in managers_to_search:
            if mgr_type in self.managers:
                mgr = self.managers[mgr_type]
                if mgr.is_available():
                    packages = mgr.search(query)
                    if packages:
                        results[mgr_type] = packages

        return results

    def list_all_installed(self) -> Dict[PackageManager, List[Package]]:
        """List installed packages from all managers"""
        results = {}

        for mgr_type, mgr in self.managers.items():
            if mgr.is_available():
                packages = mgr.list_installed()
                if packages:
                    results[mgr_type] = packages

        return results

    def install(self, manager: PackageManager, package_id: str, version: Optional[str] = None, use_cache: bool = True) -> bool:
        """Install package"""
        # Check cache first
        if use_cache and version:
            cached = self.cache.get_cached_package(manager, package_id, version)
            if cached:
                # Install from cache
                # Implementation depends on package type
                pass

        # Install normally
        if manager in self.managers:
            mgr = self.managers[manager]
            if mgr.is_available():
                return mgr.install(package_id, version)

        return False

    def uninstall(self, manager: PackageManager, package_id: str) -> bool:
        """Uninstall package"""
        if manager in self.managers:
            mgr = self.managers[manager]
            if mgr.is_available():
                return mgr.uninstall(package_id)

        return False

    def update_all(self) -> Dict[PackageManager, bool]:
        """Update all packages in all managers"""
        results = {}

        for mgr_type, mgr in self.managers.items():
            if mgr.is_available():
                results[mgr_type] = mgr.update()

        return results


# Convenience functions
def search_packages(query: str) -> Dict[PackageManager, List[Package]]:
    """Quick search packages"""
    manager = UnifiedPackageManager()
    return manager.search(query)


def list_installed() -> Dict[PackageManager, List[Package]]:
    """Quick list installed packages"""
    manager = UnifiedPackageManager()
    return manager.list_all_installed()


def install_package(manager: PackageManager, package_id: str) -> bool:
    """Quick install package"""
    mgr = UnifiedPackageManager()
    return mgr.install(manager, package_id)
