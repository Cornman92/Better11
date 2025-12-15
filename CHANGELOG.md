# Changelog

All notable changes to Better11 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-12-10

### Added - Security & Automation Features

#### Code Signing Verification ✅
- **Authenticode Signature Verification**: Full PowerShell-based signature verification
- **Certificate Extraction**: Extract and validate certificate information
- **Publisher Management**: Trusted publisher list management
- **Integration**: Automatic signature verification in installer pipeline
- **Status Detection**: VALID, INVALID, UNSIGNED, REVOKED, EXPIRED, UNTRUSTED

#### Auto-Update System ✅
- **Application Updates**: Check for and install application updates
- **Version Comparison**: Semantic versioning support via `packaging` library
- **Better11 Self-Update**: Check for and download Better11 updates
- **Update Manifest**: Support for update metadata in catalog
- **Remote Catalog**: Fetch latest catalog from URL
- **Batch Updates**: Install all available updates at once

#### Windows Update Management ✅
- **Update Checking**: Check for available Windows updates (PowerShell + COM API)
- **Update Installation**: Install specific or all available updates
- **Pause/Resume**: Pause updates for up to 35 days
- **Active Hours**: Configure active hours to prevent restart interruptions
- **Update History**: View installation history (last N days)
- **Update Uninstall**: Uninstall updates by KB article number

#### Privacy & Telemetry Control ✅
- **Telemetry Levels**: Set Windows telemetry level (Security/Basic/Enhanced/Full)
- **App Permissions**: Manage 20+ app permission settings
- **Advertising ID**: Disable Windows advertising ID
- **Cortana Control**: Disable Cortana via group policy
- **Privacy Presets**: Maximum Privacy and Balanced presets
- **Preset Application**: Apply privacy presets with one command

#### Startup Manager ✅
- **Startup Listing**: List all startup items from registry and folders
- **Enable/Disable**: Enable or disable startup items
- **Remove Items**: Permanently remove startup items
- **Locations**: Support for registry keys and startup folders
- **Recommendations**: Get optimization recommendations based on startup items

#### Windows Features Manager ✅
- **Feature Listing**: List all Windows optional features via DISM
- **Enable Features**: Enable Windows features (WSL, Hyper-V, etc.)
- **Disable Features**: Disable unnecessary features
- **Dependencies**: Get feature dependencies
- **Feature Presets**: Developer and Minimal presets
- **Preset Application**: Apply feature presets

#### Configuration System ✅
- **TOML/YAML Support**: Load and save configuration in TOML or YAML
- **Environment Overrides**: Override config with environment variables
- **Configuration Validation**: Validate configuration values
- **Default Configuration**: Built-in defaults with user overrides

### Infrastructure
- **Base Classes**: SystemTool base class for all system tools
- **Interfaces**: Updatable, Configurable, Monitorable, Backupable interfaces
- **Enhanced Logging**: Structured logging with context
- **Test Suite**: 87+ comprehensive tests for all new features

### Documentation
- **API Reference**: Complete API documentation for all new modules
- **Implementation Guides**: Detailed implementation documentation
- **Test Documentation**: Test suite documentation
- **Status Tracking**: Implementation and testing status documents

### Changed
- **Verification Pipeline**: Enhanced with code signing verification
- **Download Verifier**: Added code signing verification option
- **Error Handling**: Improved error messages and handling

### Technical Details
- **PowerShell Integration**: Extensive use of PowerShell for Windows operations
- **DISM Integration**: Windows Features management via DISM
- **Registry Operations**: Comprehensive registry manipulation
- **COM API**: Windows Update COM API integration
- **Mocking Support**: Extensive test mocking for Windows APIs

#### Changed
- **Platform Safety Controls**: `ensure_windows` now supports an
  `allow_non_windows` flag with logging so CI and dry-run scenarios can proceed
  without raising errors while keeping production enforcement available via
  configuration or environment variables.
- **Configuration Paths**: `Config.get_system_path` accepts explicit platform
  and environment overrides to remove the need for global platform monkeypatching
  during tests.

### Planned for Future Releases
- Plugin system for extensibility (v0.5.0)
- Web-based GUI alternative (v0.4.0)
- Backup and restore system state (v0.4.0)
- Performance profiling tools (v0.5.0)
- Docker/container support for testing (v0.5.0)
- Driver management (v0.4.0)
- Network optimization (v0.4.0)
- Firewall management (v0.4.0)
- Power management (v0.4.0)
- Remote management (v1.0.0)

## [0.2.0] - 2025-12-09

### Added
- **Documentation Suite**: Comprehensive documentation added
  - Complete README.md with features and quick start
  - INSTALL.md with detailed installation instructions
  - USER_GUIDE.md with extensive usage examples
  - API_REFERENCE.md with full API documentation
  - ARCHITECTURE.md explaining system design
  - CONTRIBUTING.md with development guidelines
  - SECURITY.md with security policies
  - LICENSE file (MIT License)
- **Application Manager**
  - Full application installation pipeline with verification
  - Support for MSI, EXE, and AppX installers
  - Dependency resolution and installation
  - SHA-256 hash verification
  - HMAC-SHA256 signature verification (optional)
  - Domain vetting for downloads
  - Installation state tracking
  - Silent installation support
- **System Tools**
  - Registry tweak management with automatic backups
  - Bloatware removal for AppX packages
  - Windows service management (start/stop/enable/disable)
  - Performance preset system
  - Automatic system restore point creation
  - User confirmation prompts for safety
  - Comprehensive logging
- **User Interfaces**
  - CLI with argparse for all operations
  - Tkinter-based GUI with async operations
  - Status tracking and reporting
- **Testing**
  - Test suite for application manager
  - Test suite for system tools
  - Cross-platform test support with mocking
  - Dry-run mode for safe testing

### Changed
- Restructured project for better organization
- Improved error handling throughout
- Enhanced logging with contextual information

### Security
- Multi-layer download verification
- Registry backup before modifications
- System restore point creation
- User confirmation for destructive operations
- Domain vetting prevents untrusted downloads
- Constant-time comparison for signatures

## [0.1.0] - 2025-12-02

### Added
- Initial project structure
- Basic project documentation (CLAUDE.MD)
- Git repository initialization
- Project vision and goals defined

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

---

## Release Notes

### Version 0.2.0 - Major Feature Release

This release marks the first functional version of Better11 with complete implementation of core features.

**Highlights:**
- 🚀 Full application management system
- 🛠️ Comprehensive system tools
- 📚 Complete documentation suite
- 🔒 Strong security features
- ✅ Extensive test coverage

**What's New:**

The application manager now supports:
- Downloading applications from vetted sources
- Installing with automatic dependency resolution
- Verifying downloads with SHA-256 and optional HMAC
- Tracking installation state persistently
- Uninstalling with dependency checking

System tools provide:
- Safe registry modifications with automatic backups
- Bloatware removal for unwanted AppX packages
- Windows service management
- Performance optimization presets
- Automatic restore point creation

Documentation now includes:
- Complete installation guide
- Comprehensive user guide with examples
- Full API reference
- Architecture documentation
- Contributing guidelines
- Security policies

**Breaking Changes:**
- N/A (first functional release)

**Migration Guide:**
- N/A (first functional release)

**Known Issues:**
- No automatic updates yet (planned for 0.3.0)
- No code signing verification (planned for 0.3.0)
- GUI is basic Tkinter (improved UI planned)
- No undo/rollback for all operations yet

**Upgrade Instructions:**
- Clone or download the repository
- Follow INSTALL.md for setup
- Review USER_GUIDE.md for usage

### Version 0.1.0 - Initial Release

Initial project setup with vision and goals documented.

---

## Versioning Scheme

Better11 uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New features, backwards compatible
- **PATCH** version (0.0.X): Bug fixes, backwards compatible

### Pre-1.0 Releases

Versions before 1.0.0 are considered development releases. Breaking changes may occur between minor versions.

## Types of Changes

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security fixes and improvements

## Release Process

1. Update CHANGELOG.md with changes
2. Update version numbers in code
3. Create git tag: `git tag -a v0.X.0 -m "Version 0.X.0"`
4. Push tag: `git push origin v0.X.0`
5. Create GitHub release with release notes
6. Announce in discussions

## Future Releases

### v0.3.0 (Planned - Q1 2026)

**Focus**: Security and Updates

- Authenticode signature verification for installers
- Automatic application updates
- Update checking for Better11 itself
- Improved error messages
- Better progress reporting in GUI
- Configuration file support

### v0.4.0 (Planned - Q2 2026)

**Focus**: User Experience

- Improved GUI with better design
- Search and filter in application list
- Categories and tags for applications
- Application screenshots and descriptions
- Installation profiles (save common configurations)
- Backup and restore system state

### v0.5.0 (Planned - Q3 2026)

**Focus**: Advanced Features

- Plugin system for extensibility
- Custom performance preset editor
- Advanced logging and diagnostics
- Scheduled operations
- Rollback/undo system
- Multi-catalog support

### v1.0.0 (Planned - Q4 2026)

**Focus**: Production Ready

- Stable API
- Complete feature set
- Comprehensive testing
- Security audit completed
- Performance optimization
- Professional documentation
- Installer for Better11 itself

## Contributing

When contributing, please:
1. Update CHANGELOG.md under [Unreleased] section
2. Follow the format: `- Category: Description (#PR)`
3. Include issue/PR references
4. Use conventional commits

Example entry:
```markdown
### Added
- Application manager: Add support for MSIX installers (#123)
```

## Questions?

- Check [GitHub Issues](https://github.com/owner/better11/issues) for known issues
- Start a [Discussion](https://github.com/owner/better11/discussions) for questions
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines

---

**Note**: This changelog is maintained manually. Version dates reflect documentation dates, not necessarily code implementation dates.

**Last Updated**: December 9, 2025
