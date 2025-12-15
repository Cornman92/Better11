# API Reference

Complete API documentation for Better11 modules and functions.

## Table of Contents

- [Application Manager](#application-manager)
  - [better11.apps.manager](#better11appsmanager)
  - [better11.apps.catalog](#better11appscatalog)
  - [better11.apps.models](#better11appsmodels)
  - [better11.apps.download](#better11appsdownload)
  - [better11.apps.verification](#better11appsverification)
  - [better11.apps.code_signing](#better11appscode_signing)
  - [better11.apps.updater](#better11appsupdater)
  - [better11.apps.runner](#better11appsrunner)
  - [better11.apps.state_store](#better11appsstate_store)
- [System Tools](#system-tools)
  - [system_tools.registry](#system_toolsregistry)
  - [system_tools.bloatware](#system_toolsbloatware)
  - [system_tools.services](#system_toolsservices)
  - [system_tools.performance](#system_toolsperformance)
  - [system_tools.updates](#system_toolsupdates)
  - [system_tools.privacy](#system_toolsprivacy)
  - [system_tools.startup](#system_toolsstartup)
  - [system_tools.features](#system_toolsfeatures)
  - [system_tools.safety](#system_toolssafety)
  - [system_tools.base](#system_toolsbase)
- [Configuration](#configuration)
  - [better11.config](#better11config)
- [Interfaces](#interfaces)
  - [better11.interfaces](#better11interfaces)
- [User Interfaces](#user-interfaces)
  - [better11.cli](#better11cli)
  - [better11.gui](#better11gui)

---

## Application Manager

### better11.apps.manager

Main orchestrator for application management.

#### Class: `AppManager`

Coordinates catalog lookup, downloading, verification, and installation.

**Constructor:**

```python
AppManager(
    catalog_path: Path,
    download_dir: Optional[Path] = None,
    state_file: Optional[Path] = None,
    downloader: Optional[AppDownloader] = None,
    verifier: Optional[DownloadVerifier] = None,
    runner: Optional[InstallerRunner] = None
)
```

**Parameters:**
- `catalog_path` (Path): Path to the application catalog JSON file
- `download_dir` (Path, optional): Directory for downloaded installers. Defaults to `~/.better11/downloads`
- `state_file` (Path, optional): Path to installation state file. Defaults to `~/.better11/installed.json`
- `downloader` (AppDownloader, optional): Custom downloader instance
- `verifier` (DownloadVerifier, optional): Custom verifier instance
- `runner` (InstallerRunner, optional): Custom installer runner instance

**Methods:**

##### `list_available() -> List[AppMetadata]`

List all available applications from catalog.

**Returns:** List of AppMetadata objects

**Example:**
```python
manager = AppManager(Path("catalog.json"))
apps = manager.list_available()
for app in apps:
    print(f"{app.app_id}: {app.name} v{app.version}")
```

##### `download(app_id: str) -> Path`

Download an application installer.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** Path to downloaded installer

**Raises:**
- `KeyError`: If app_id not found in catalog
- `DownloadError`: If download fails

**Example:**
```python
path = manager.download("demo-app")
print(f"Downloaded to {path}")
```

##### `install(app_id: str) -> Tuple[AppStatus, InstallerResult]`

Download, verify, and install an application with dependencies.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** Tuple of (AppStatus, InstallerResult)

**Raises:**
- `KeyError`: If app_id not found
- `DownloadError`: If download fails
- `VerificationError`: If verification fails
- `DependencyError`: If circular dependency detected

**Example:**
```python
status, result = manager.install("demo-app")
print(f"Installed {status.app_id} v{status.version}")
print(f"Command: {' '.join(result.command)}")
```

##### `uninstall(app_id: str) -> InstallerResult`

Uninstall an installed application.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** InstallerResult with uninstall details

**Raises:**
- `DependencyError`: If application is required by other installed apps

**Example:**
```python
result = manager.uninstall("demo-app")
print(f"Uninstalled via: {' '.join(result.command)}")
```

##### `status(app_id: Optional[str] = None) -> List[AppStatus]`

Get installation status.

**Parameters:**
- `app_id` (str, optional): Specific application ID, or None for all

**Returns:** List of AppStatus objects

**Example:**
```python
# All applications
all_status = manager.status()

# Specific application
app_status = manager.status("demo-app")
```

##### `summarized_status(app_id: Optional[str] = None) -> List[str]`

Get human-readable status messages.

**Parameters:**
- `app_id` (str, optional): Specific application ID

**Returns:** List of status strings

**Example:**
```python
messages = manager.summarized_status()
for msg in messages:
    print(msg)
```

#### Exception: `DependencyError`

Raised when dependency-related issues occur.

---

### better11.apps.catalog

Application catalog management.

#### Class: `AppCatalog`

Loads and manages application metadata from catalog file.

**Constructor:**

```python
AppCatalog(applications: Iterable[AppMetadata])
```

**Class Methods:**

##### `from_file(path: Path) -> AppCatalog`

Load catalog from JSON file.

**Parameters:**
- `path` (Path): Path to catalog JSON file

**Returns:** AppCatalog instance

**Example:**
```python
catalog = AppCatalog.from_file(Path("catalog.json"))
```

**Methods:**

##### `list_all() -> List[AppMetadata]`

List all applications in catalog.

**Returns:** List of AppMetadata objects

##### `get(app_id: str) -> AppMetadata`

Get metadata for specific application.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** AppMetadata object

**Raises:**
- `KeyError`: If app_id not found

##### `__contains__(app_id: str) -> bool`

Check if application exists in catalog.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** True if exists, False otherwise

**Example:**
```python
if "demo-app" in catalog:
    metadata = catalog.get("demo-app")
```

---

### better11.apps.models

Data models for application management.

#### Enum: `InstallerType`

Supported installer types.

**Values:**
- `MSI` - Microsoft Installer (.msi)
- `EXE` - Executable installer (.exe)
- `APPX` - Windows Store App (.appx)

**Class Methods:**

##### `from_filename(filename: str) -> InstallerType`

Determine installer type from filename.

**Parameters:**
- `filename` (str): Installer filename

**Returns:** InstallerType

**Raises:**
- `ValueError`: If unsupported file type

**Example:**
```python
installer_type = InstallerType.from_filename("installer.msi")
# Returns InstallerType.MSI
```

#### Dataclass: `AppMetadata`

Application metadata with verification details.

**Attributes:**
- `app_id` (str): Unique application identifier
- `name` (str): Human-readable application name
- `version` (str): Application version
- `uri` (str): Download URI (HTTP/HTTPS or file://)
- `sha256` (str): SHA-256 hash for verification
- `installer_type` (InstallerType): Type of installer
- `vetted_domains` (List[str]): Approved download domains
- `signature` (str, optional): HMAC-SHA256 signature (base64)
- `signature_key` (str, optional): HMAC key (base64)
- `dependencies` (List[str]): Required application IDs
- `silent_args` (List[str]): Silent installation arguments
- `uninstall_command` (str, optional): Uninstall command

**Methods:**

##### `domain_is_vetted(hostname: str) -> bool`

Check if domain is vetted for downloads.

**Parameters:**
- `hostname` (str): Domain hostname

**Returns:** True if vetted, False otherwise

##### `requires_signature_verification() -> bool`

Check if HMAC signature verification is required.

**Returns:** True if signature and key are present

**Example:**
```python
app = AppMetadata(
    app_id="demo",
    name="Demo App",
    version="1.0",
    uri="https://example.com/demo.msi",
    sha256="abc123...",
    installer_type=InstallerType.MSI,
    vetted_domains=["example.com"]
)

if app.domain_is_vetted("example.com"):
    print("Domain is vetted")
```

#### Dataclass: `AppStatus`

Installation status tracking.

**Attributes:**
- `app_id` (str): Application identifier
- `version` (str): Installed version
- `installer_path` (str): Path to installer file
- `installed` (bool): Installation status
- `dependencies_installed` (List[str]): Installed dependency IDs

---

### better11.apps.download

Application download functionality.

#### Class: `AppDownloader`

Downloads application installers with domain vetting.

**Constructor:**

```python
AppDownloader(
    download_dir: Path,
    catalog_base_dir: Path
)
```

**Parameters:**
- `download_dir` (Path): Directory for downloaded files
- `catalog_base_dir` (Path): Base directory for resolving relative file:// URIs

**Methods:**

##### `download(app: AppMetadata) -> Path`

Download application installer.

**Parameters:**
- `app` (AppMetadata): Application metadata

**Returns:** Path to downloaded installer

**Raises:**
- `DownloadError`: If download fails or domain not vetted

**Example:**
```python
downloader = AppDownloader(
    Path.home() / ".better11" / "downloads",
    Path(".")
)
path = downloader.download(app_metadata)
```

#### Exception: `DownloadError`

Raised when download operations fail.

---

### better11.apps.verification

Download integrity and signature verification.

#### Class: `DownloadVerifier`

Verifies download integrity and HMAC signatures.

**Methods:**

##### `verify_hash(file_path: Path, expected_sha256: str) -> str`

Verify SHA-256 hash of file.

**Parameters:**
- `file_path` (Path): Path to file
- `expected_sha256` (str): Expected hash (hex string)

**Returns:** Actual hash (hex string)

**Raises:**
- `VerificationError`: If hash mismatch

**Example:**
```python
verifier = DownloadVerifier()
actual_hash = verifier.verify_hash(
    Path("installer.msi"),
    "abc123..."
)
```

##### `verify_signature(file_path: Path, signature_b64: str, key_b64: str) -> None`

Verify HMAC-SHA256 signature.

**Parameters:**
- `file_path` (Path): Path to file
- `signature_b64` (str): Base64-encoded HMAC signature
- `key_b64` (str): Base64-encoded HMAC key

**Raises:**
- `VerificationError`: If signature verification fails

##### `verify(metadata: AppMetadata, file_path: Path) -> None`

Verify hash and signature (if required).

**Parameters:**
- `metadata` (AppMetadata): Application metadata
- `file_path` (Path): Path to downloaded file

**Raises:**
- `VerificationError`: If verification fails

**Example:**
```python
verifier = DownloadVerifier()
verifier.verify(app_metadata, Path("installer.msi"))
```

#### Exception: `VerificationError`

Raised when verification fails.

---

### better11.apps.runner

Installer execution with dry-run support.

#### Class: `InstallerRunner`

Executes Windows installers.

**Constructor:**

```python
InstallerRunner(dry_run: bool | None = None)
```

**Parameters:**
- `dry_run` (bool, optional): Enable dry-run mode. Defaults to True on non-Windows

**Methods:**

##### `install(app: AppMetadata, installer_path: Path) -> InstallerResult`

Execute installer.

**Parameters:**
- `app` (AppMetadata): Application metadata
- `installer_path` (Path): Path to installer file

**Returns:** InstallerResult with execution details

**Raises:**
- `InstallerError`: If installation fails

**Example:**
```python
runner = InstallerRunner(dry_run=False)
result = runner.install(app_metadata, Path("installer.msi"))
print(f"Exit code: {result.returncode}")
```

##### `uninstall(app: AppMetadata, installer_path: Path | None) -> InstallerResult`

Execute uninstaller.

**Parameters:**
- `app` (AppMetadata): Application metadata
- `installer_path` (Path, optional): Path to installer (for MSI)

**Returns:** InstallerResult

**Raises:**
- `InstallerError`: If uninstall fails or command not configured

#### Dataclass: `InstallerResult`

Result of installer execution.

**Attributes:**
- `command` (List[str]): Command executed
- `returncode` (int): Exit code
- `stdout` (str): Standard output
- `stderr` (str): Standard error

#### Exception: `InstallerError`

Raised when installer execution fails.

---

### better11.apps.state_store

Installation state persistence.

#### Class: `InstallationStateStore`

Manages persistent installation state.

**Constructor:**

```python
InstallationStateStore(state_file: Path)
```

**Parameters:**
- `state_file` (Path): Path to JSON state file

**Methods:**

##### `mark_installed(app_id: str, version: str, installer_path: Path, dependencies: List[str] = []) -> AppStatus`

Mark application as installed.

**Parameters:**
- `app_id` (str): Application identifier
- `version` (str): Version installed
- `installer_path` (Path): Path to installer
- `dependencies` (List[str]): Installed dependencies

**Returns:** AppStatus object

**Example:**
```python
store = InstallationStateStore(Path("installed.json"))
status = store.mark_installed(
    "demo-app",
    "1.0.0",
    Path("installer.msi"),
    dependencies=["dep-app"]
)
```

##### `mark_uninstalled(app_id: str) -> None`

Mark application as uninstalled.

**Parameters:**
- `app_id` (str): Application identifier

##### `get(app_id: str) -> Optional[AppStatus]`

Get installation status for application.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** AppStatus or None if not found

##### `list() -> List[AppStatus]`

List all tracked applications.

**Returns:** List of AppStatus objects

---

## System Tools

### system_tools.registry

Windows Registry management.

#### Dataclass: `RegistryTweak`

Represents a registry modification.

**Attributes:**
- `hive` (str): Registry hive (e.g., "HKEY_CURRENT_USER")
- `path` (str): Registry key path
- `name` (str): Value name
- `value` (object): Value data
- `value_type` (int): Registry value type (winreg constants)

**Properties:**

##### `full_path -> str`

Get full registry path.

**Example:**
```python
import winreg

tweak = RegistryTweak(
    hive="HKEY_CURRENT_USER",
    path=r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
    name="HideFileExt",
    value=0,
    value_type=winreg.REG_DWORD
)

print(tweak.full_path)
# Output: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced
```

#### Function: `apply_tweak`

```python
apply_tweak(tweak: RegistryTweak) -> None
```

Apply a single registry tweak.

**Parameters:**
- `tweak` (RegistryTweak): Registry modification to apply

**Raises:**
- `SafetyError`: If operation fails

#### Function: `apply_tweaks`

```python
apply_tweaks(
    tweaks: Iterable[RegistryTweak],
    *,
    confirm: bool = True,
    create_backup: bool = True,
    create_restore: bool = True,
    input_func = input
) -> None
```

Apply multiple registry tweaks with safeguards.

**Parameters:**
- `tweaks` (Iterable[RegistryTweak]): Registry modifications
- `confirm` (bool): Prompt for user confirmation
- `create_backup` (bool): Backup affected keys
- `create_restore` (bool): Create system restore point
- `input_func` (Callable): Input function for testing

**Raises:**
- `SafetyError`: If operation fails or user cancels

**Example:**
```python
from system_tools.registry import RegistryTweak, apply_tweaks
import winreg

tweaks = [
    RegistryTweak("HKEY_CURRENT_USER", r"Software\...", "Key", 0, winreg.REG_DWORD)
]

apply_tweaks(tweaks, confirm=True, create_backup=True)
```

---

### system_tools.bloatware

Windows bloatware removal.

#### Function: `remove_bloatware`

```python
remove_bloatware(
    packages: Iterable[str],
    *,
    confirm: bool = True,
    input_func = input
) -> None
```

Remove AppX packages.

**Parameters:**
- `packages` (Iterable[str]): Package names to remove
- `confirm` (bool): Prompt for user confirmation
- `input_func` (Callable): Input function for testing

**Raises:**
- `SafetyError`: If operation fails or user cancels

**Example:**
```python
from system_tools.bloatware import remove_bloatware

packages = [
    "Microsoft.BingWeather",
    "Microsoft.BingNews"
]

remove_bloatware(packages, confirm=True)
```

---

### system_tools.services

Windows service management.

#### Dataclass: `ServiceAction`

Windows service action definition.

**Attributes:**
- `name` (str): Service name
- `action` (str): Action to perform ("start", "stop", "enable", "disable")

**Methods:**

##### `command() -> list[str]`

Get command for executing the action.

**Returns:** Command as list of strings

**Example:**
```python
action = ServiceAction(name="WSearch", action="disable")
cmd = action.command()
# Returns: ["sc", "config", "WSearch", "start=", "disabled"]
```

#### Function: `apply_service_actions`

```python
apply_service_actions(
    actions: Iterable[ServiceAction],
    *,
    confirm: bool = True,
    create_restore: bool = True,
    input_func = input
) -> None
```

Apply service modifications.

**Parameters:**
- `actions` (Iterable[ServiceAction]): Service actions to apply
- `confirm` (bool): Prompt for user confirmation
- `create_restore` (bool): Create system restore point
- `input_func` (Callable): Input function for testing

**Raises:**
- `SafetyError`: If operation fails or user cancels

**Example:**
```python
from system_tools.services import ServiceAction, apply_service_actions

actions = [
    ServiceAction(name="WSearch", action="stop"),
    ServiceAction(name="WSearch", action="disable")
]

apply_service_actions(actions, confirm=True)
```

---

### system_tools.performance

Performance optimization presets.

#### Dataclass: `PerformancePreset`

Performance optimization configuration.

**Attributes:**
- `name` (str): Preset name
- `registry_tweaks` (List[RegistryTweak]): Registry modifications
- `service_actions` (List[ServiceAction]): Service changes
- `description` (str): Preset description

**Example:**
```python
preset = PerformancePreset(
    name="Gaming",
    description="Optimize for gaming performance",
    registry_tweaks=[...],
    service_actions=[...]
)
```

#### Function: `apply_performance_preset`

```python
apply_performance_preset(
    preset: PerformancePreset,
    *,
    confirm: bool = True,
    input_func = input
) -> None
```

Apply performance preset.

**Parameters:**
- `preset` (PerformancePreset): Preset to apply
- `confirm` (bool): Prompt for user confirmation
- `input_func` (Callable): Input function for testing

**Raises:**
- `SafetyError`: If operation fails or user cancels

**Example:**
```python
from system_tools.performance import PerformancePreset, apply_performance_preset
from system_tools.registry import RegistryTweak
import winreg

preset = PerformancePreset(
    name="Performance",
    registry_tweaks=[
        RegistryTweak("HKEY_CURRENT_USER", r"...", "Key", 0, winreg.REG_DWORD)
    ]
)

apply_performance_preset(preset, confirm=True)
```

---

### system_tools.safety

Safety utilities and checks.

#### Exception: `SafetyError`

Raised when safety precondition fails.

#### Function: `ensure_windows`

```python
ensure_windows(allow_non_windows: bool = False) -> bool
```

Ensure current platform is Windows. When ``allow_non_windows`` is True, the
function logs a warning and returns ``False`` instead of raising an error so
callers can explicitly permit cross-platform dry runs or CI environments.

**Returns:** ``True`` when Windows is detected, ``False`` when bypassing the
platform check.

**Raises:**
- `SafetyError`: If not running on Windows and ``allow_non_windows`` is False

#### Function: `confirm_action`

```python
confirm_action(
    prompt: str,
    input_func: Callable[[str], str] = input
) -> bool
```

Prompt user for action confirmation.

**Parameters:**
- `prompt` (str): Message to display
- `input_func` (Callable): Input function

**Returns:** True if confirmed, False if cancelled

**Example:**
```python
from system_tools.safety import confirm_action

if confirm_action("Apply these changes?"):
    # Proceed
    pass
```

#### Function: `create_restore_point`

```python
create_restore_point(description: str) -> None
```

Create Windows system restore point.

**Parameters:**
- `description` (str): Restore point description

**Raises:**
- `SafetyError`: If restore point creation fails

#### Function: `backup_registry_key`

```python
backup_registry_key(
    key_path: str,
    destination: Optional[Path] = None
) -> Path
```

Export registry key to file.

**Parameters:**
- `key_path` (str): Registry key path
- `destination` (Path, optional): Backup file path

**Returns:** Path to backup file

**Raises:**
- `SafetyError`: If backup fails

**Example:**
```python
from system_tools.safety import backup_registry_key
from pathlib import Path

backup_path = backup_registry_key(
    r"HKCU\Software\Microsoft\Windows",
    destination=Path("backup.reg")
)
```

---

## User Interfaces

### better11.cli

Command-line interface module.

#### Function: `main`

```python
main(argv: list[str] | None = None) -> int
```

Main CLI entry point.

**Parameters:**
- `argv` (list[str], optional): Command-line arguments

**Returns:** Exit code (0 for success, 1 for error)

**Commands:**
- `list` - List available applications
- `download <app_id>` - Download application
- `install <app_id>` - Install application
- `uninstall <app_id>` - Uninstall application
- `status [app_id]` - Show installation status

**Options:**
- `--catalog PATH` - Path to catalog JSON file

**Example:**
```bash
python -m better11.cli list
python -m better11.cli --catalog custom.json install app-id
```

---

### better11.gui

Graphical user interface module.

#### Class: `AppManagerGUI`

Tkinter-based GUI for application management.

**Constructor:**

```python
AppManagerGUI(manager: AppManager)
```

**Parameters:**
- `manager` (AppManager): AppManager instance

#### Function: `launch_gui`

```python
launch_gui(catalog_path: Path | None = None) -> None
```

Launch the GUI application.

**Parameters:**
- `catalog_path` (Path, optional): Path to catalog file

**Example:**
```python
from better11.gui import launch_gui
from pathlib import Path

launch_gui(Path("catalog.json"))
```

---

## Code Signing Verification

### better11.apps.code_signing

Authenticode signature verification for Windows executables.

#### Enum: `SignatureStatus`

Signature verification status.

**Values:**
- `VALID` - Signature is valid and trusted
- `INVALID` - Signature is invalid
- `UNSIGNED` - File is not signed
- `REVOKED` - Certificate has been revoked
- `EXPIRED` - Certificate has expired
- `UNTRUSTED` - Signature is not trusted

#### Class: `CertificateInfo`

Certificate information extracted from signed file.

**Attributes:**
- `subject` (str): Certificate subject
- `issuer` (str): Certificate issuer
- `serial_number` (str): Certificate serial number
- `thumbprint` (str): Certificate thumbprint
- `valid_from` (datetime): Certificate valid from date
- `valid_to` (datetime): Certificate valid to date

**Methods:**
- `is_expired() -> bool`: Check if certificate has expired

#### Class: `SignatureInfo`

Complete signature information for a file.

**Attributes:**
- `status` (SignatureStatus): Signature status
- `certificate` (Optional[CertificateInfo]): Certificate information
- `timestamp` (Optional[datetime]): Signature timestamp
- `hash_algorithm` (Optional[str]): Hash algorithm used
- `error_message` (Optional[str]): Error message if verification failed

**Methods:**
- `is_trusted() -> bool`: Check if signature is valid and trusted

#### Class: `CodeSigningVerifier`

Verify Authenticode signatures on Windows executables.

**Constructor:**
```python
CodeSigningVerifier(check_revocation: bool = False)
```

**Parameters:**
- `check_revocation` (bool): Whether to check certificate revocation (CRL/OCSP)

**Methods:**

##### `verify_signature(file_path: Path) -> SignatureInfo`

Verify the digital signature of a file.

**Parameters:**
- `file_path` (Path): Path to file to verify

**Returns:** SignatureInfo with verification results

**Example:**
```python
from better11.apps.code_signing import CodeSigningVerifier
from pathlib import Path

verifier = CodeSigningVerifier()
sig_info = verifier.verify_signature(Path("installer.exe"))

if sig_info.is_trusted():
    print(f"Signed by: {sig_info.certificate.subject}")
else:
    print(f"Verification failed: {sig_info.error_message}")
```

##### `extract_certificate(file_path: Path) -> Optional[CertificateInfo]`

Extract certificate information from signed file.

**Parameters:**
- `file_path` (Path): Path to signed file

**Returns:** CertificateInfo if file is signed, None otherwise

##### `is_trusted_publisher(cert_info: CertificateInfo) -> bool`

Check if certificate publisher is in trusted list.

##### `add_trusted_publisher(cert_info: CertificateInfo) -> None`

Add publisher to trusted list.

##### `remove_trusted_publisher(subject: str) -> None`

Remove publisher from trusted list.

---

## Auto-Update System

### better11.apps.updater

Application update management for Better11.

#### Class: `UpdateInfo`

Information about an available update.

**Attributes:**
- `app_id` (str): Application identifier
- `current_version` (Version): Currently installed version
- `available_version` (Version): Available version
- `download_url` (str): URL to download update
- `release_notes` (str): Release notes
- `release_date` (Optional[datetime]): Release date
- `is_security_update` (bool): Whether this is a security update
- `is_mandatory` (bool): Whether update is mandatory
- `size_mb` (float): Update size in MB

#### Class: `ApplicationUpdater`

Manage application updates.

**Constructor:**
```python
ApplicationUpdater(
    app_manager: AppManager,
    catalog_url: Optional[str] = None
)
```

**Parameters:**
- `app_manager` (AppManager): Application manager instance
- `catalog_url` (Optional[str]): URL to fetch latest catalog from

**Methods:**

##### `check_for_updates(app_id: Optional[str] = None) -> List[UpdateInfo]`

Check for updates for installed applications.

**Parameters:**
- `app_id` (Optional[str]): Specific app ID to check, or None for all

**Returns:** List of available updates

**Example:**
```python
from better11.apps.updater import ApplicationUpdater

updater = ApplicationUpdater(app_manager)
updates = updater.check_for_updates()

for update in updates:
    print(f"{update.app_id}: {update.current_version} -> {update.available_version}")
```

##### `install_update(update_info: UpdateInfo) -> bool`

Install an application update.

**Parameters:**
- `update_info` (UpdateInfo): Update information

**Returns:** True if installation successful

##### `install_all_updates(updates: Optional[List[UpdateInfo]] = None) -> List[bool]`

Install all available updates.

#### Class: `Better11Updater`

Self-update capability for Better11.

**Constructor:**
```python
Better11Updater(version_check_url: Optional[str] = None)
```

**Methods:**

##### `get_current_version() -> Version`

Get currently installed Better11 version.

##### `check_for_updates() -> Optional[UpdateInfo]`

Check if newer Better11 version is available.

##### `download_update(version: Version) -> Path`

Download Better11 update package.

##### `install_update(package_path: Path) -> bool`

Install Better11 update (requires restart).

---

## Windows Update Management

### system_tools.updates

Windows Update management and control.

#### Class: `WindowsUpdate`

Representation of a Windows update.

**Attributes:**
- `id` (str): Update identifier
- `title` (str): Update title
- `description` (str): Update description
- `update_type` (UpdateType): Type of update
- `size_mb` (float): Update size in MB
- `status` (UpdateStatus): Update status
- `kb_article` (Optional[str]): KB article number
- `is_mandatory` (bool): Whether update is mandatory
- `requires_restart` (bool): Whether restart is required

#### Class: `WindowsUpdateManager`

Manage Windows Update settings and operations.

**Constructor:**
```python
WindowsUpdateManager(config: Optional[dict] = None, dry_run: bool = False)
```

**Methods:**

##### `check_for_updates() -> List[WindowsUpdate]`

Check for available Windows updates.

**Returns:** List of available updates

**Example:**
```python
from system_tools.updates import WindowsUpdateManager

manager = WindowsUpdateManager()
updates = manager.check_for_updates()

for update in updates:
    print(f"{update.title} ({update.size_mb} MB)")
```

##### `install_updates(update_ids: Optional[List[str]] = None) -> bool`

Install specific updates or all available updates.

##### `pause_updates(days: int = 7) -> bool`

Pause Windows updates for specified number of days (max 35).

##### `resume_updates() -> bool`

Resume Windows updates if paused.

##### `set_active_hours(start_hour: int, end_hour: int) -> bool`

Set active hours to prevent restart interruptions.

##### `get_update_history(days: int = 30) -> List[WindowsUpdate]`

Get Windows update installation history.

##### `uninstall_update(kb_article: str) -> bool`

Uninstall a specific update by KB number.

---

## Privacy & Telemetry Control

### system_tools.privacy

Privacy and telemetry control for Windows.

#### Class: `PrivacyManager`

Manage Windows privacy and telemetry settings.

**Constructor:**
```python
PrivacyManager(config: Optional[dict] = None, dry_run: bool = False)
```

**Presets:**
- `MAXIMUM_PRIVACY`: Disable all telemetry and most app permissions
- `BALANCED`: Reasonable privacy with essential features enabled

**Methods:**

##### `set_telemetry_level(level: TelemetryLevel) -> bool`

Set Windows telemetry level.

**Parameters:**
- `level` (TelemetryLevel): Desired telemetry level (SECURITY/BASIC/ENHANCED/FULL)

**Example:**
```python
from system_tools.privacy import PrivacyManager, TelemetryLevel

manager = PrivacyManager()
manager.set_telemetry_level(TelemetryLevel.BASIC)
```

##### `get_telemetry_level() -> TelemetryLevel`

Get current Windows telemetry level.

##### `set_app_permission(setting: PrivacySetting, enabled: bool) -> bool`

Set an app permission.

##### `get_app_permission(setting: PrivacySetting) -> bool`

Get current state of an app permission.

##### `disable_advertising_id() -> bool`

Disable Windows advertising ID.

##### `disable_cortana() -> bool`

Disable Cortana.

##### `apply_preset(preset: PrivacyPreset) -> bool`

Apply a privacy preset.

---

## Startup Manager

### system_tools.startup

Startup program management.

#### Class: `StartupManager`

Manage Windows startup programs.

**Constructor:**
```python
StartupManager(config: Optional[dict] = None, dry_run: bool = False)
```

**Methods:**

##### `list_startup_items() -> List[StartupItem]`

List all startup programs from all locations.

**Returns:** List of StartupItem objects

**Example:**
```python
from system_tools.startup import StartupManager

manager = StartupManager()
items = manager.list_startup_items()

for item in items:
    print(f"{item.name}: {item.command} ({item.location.value})")
```

##### `enable_startup_item(item: StartupItem) -> bool`

Enable a startup item.

##### `disable_startup_item(item: StartupItem) -> bool`

Disable a startup item.

##### `remove_startup_item(item: StartupItem) -> bool`

Permanently remove a startup item.

##### `get_recommendations() -> List[str]`

Get startup optimization recommendations.

---

## Windows Features Manager

### system_tools.features

Windows optional features management.

#### Class: `WindowsFeaturesManager`

Manage Windows optional features.

**Constructor:**
```python
WindowsFeaturesManager(config: Optional[dict] = None, dry_run: bool = False)
```

**Presets:**
- `DEVELOPER_PRESET`: Enable features useful for developers (WSL, Hyper-V, etc.)
- `MINIMAL_PRESET`: Disable unnecessary features

**Methods:**

##### `list_features(state: Optional[FeatureState] = None) -> List[WindowsFeature]`

List available Windows features.

**Parameters:**
- `state` (Optional[FeatureState]): Filter by feature state

**Example:**
```python
from system_tools.features import WindowsFeaturesManager, FeatureState

manager = WindowsFeaturesManager()
features = manager.list_features(FeatureState.ENABLED)

for feature in features:
    print(f"{feature.display_name}: {feature.state.value}")
```

##### `enable_feature(feature_name: str) -> bool`

Enable a Windows feature.

##### `disable_feature(feature_name: str) -> bool`

Disable a Windows feature.

##### `get_feature_dependencies(feature_name: str) -> List[str]`

Get feature dependencies.

##### `get_feature_state(feature_name: str) -> FeatureState`

Get the state of a specific feature.

##### `apply_preset(preset: FeaturePreset) -> bool`

Apply a feature preset.

---

## Configuration

### better11.config

Configuration management for Better11.

#### Class: `Config`

Complete Better11 configuration.

**Constructor:**
```python
Config.load(path: Optional[Path] = None) -> Config
```

**Methods:**

##### `load(path: Optional[Path] = None) -> Config`

Load configuration from file with defaults.

**Parameters:**
- `path` (Optional[Path]): Path to config file. If None, uses default location.

**Returns:** Config instance

**Example:**
```python
from better11.config import Config

config = Config.load()
print(f"Auto-update: {config.better11.auto_update}")
```

##### `save(path: Optional[Path] = None) -> None`

Save configuration to file.

##### `validate() -> bool`

Validate configuration values.

---

## Interfaces

### better11.interfaces

Common interfaces for Better11 components.

#### Class: `Version`

Semantic version representation.

**Constructor:**
```python
Version(major: int, minor: int, patch: int)
```

**Methods:**
- `parse(version_str: str) -> Version`: Parse version string

**Example:**
```python
from better11.interfaces import Version

v1 = Version(1, 2, 3)
v2 = Version.parse("1.2.3")
assert v1 == v2
assert Version.parse("1.3.0") > v1
```

#### Interface: `Updatable`

Interface for components that can be updated.

**Methods:**
- `get_current_version() -> Version`
- `check_for_updates() -> Optional[Version]`
- `download_update(version: Version) -> Path`
- `install_update(package_path: Path) -> bool`
- `rollback_update() -> bool`

---

## Type Aliases and Constants

### Registry Value Types

From `winreg` module:
- `REG_SZ` - String value
- `REG_DWORD` - 32-bit integer
- `REG_QWORD` - 64-bit integer
- `REG_BINARY` - Binary data
- `REG_MULTI_SZ` - Multiple strings
- `REG_EXPAND_SZ` - Expandable string

### Registry Hives

Common hive names:
- `HKEY_CURRENT_USER` (HKCU)
- `HKEY_LOCAL_MACHINE` (HKLM)
- `HKEY_CLASSES_ROOT` (HKCR)
- `HKEY_USERS` (HKU)
- `HKEY_CURRENT_CONFIG` (HKCC)

---

## Usage Examples

### Complete Application Installation

```python
from pathlib import Path
from better11.apps.manager import AppManager

# Initialize manager
catalog_path = Path("better11/apps/catalog.json")
manager = AppManager(catalog_path)

# List applications
apps = manager.list_available()
print(f"Found {len(apps)} applications")

# Install application
app_id = "demo-app"
status, result = manager.install(app_id)
print(f"Installed: {status.app_id} v{status.version}")

# Check status
app_status = manager.status(app_id)
if app_status[0].installed:
    print("Installation confirmed")

# Uninstall
result = manager.uninstall(app_id)
print(f"Uninstalled successfully")
```

### Complete System Optimization

```python
from system_tools.registry import RegistryTweak, apply_tweaks
from system_tools.services import ServiceAction, apply_service_actions
from system_tools.bloatware import remove_bloatware
import winreg

# Registry tweaks
tweaks = [
    RegistryTweak("HKEY_CURRENT_USER", r"Software\...", "Key", 0, winreg.REG_DWORD)
]
apply_tweaks(tweaks)

# Service management
actions = [
    ServiceAction("WSearch", "disable")
]
apply_service_actions(actions)

# Bloatware removal
packages = ["Microsoft.BingWeather"]
remove_bloatware(packages)

print("System optimized!")
```

---

## Notes

- All system modification functions require Windows and administrator privileges
- File paths should use `pathlib.Path` objects when possible
- Functions that modify the system create automatic backups and restore points
- User confirmation prompts can be disabled for scripting (set `confirm=False`)
- Dry-run mode available for testing (see `InstallerRunner`)

## See Also

- [User Guide](USER_GUIDE.md) - Practical usage examples
- [Architecture](ARCHITECTURE.md) - System design documentation
- [Contributing](CONTRIBUTING.md) - Development guidelines

---

**Last Updated:** December 2025
