# Better11 - Project Context for Claude

## Project Overview

Better11 is a fully-implemented Windows 11 system enhancement toolkit providing secure application management and system optimization tools.

## Current Implementation Status

✅ **Fully Implemented** - The project has complete working code with:
- Full application management system
- Comprehensive system tools
- CLI and GUI interfaces
- Test suite
- Complete documentation

## Core Features (Implemented)

### Application Manager
- **Secure Installation**: SHA-256 hash and HMAC signature verification
- **Dependency Management**: Automatic dependency resolution
- **Multi-Format Support**: MSI, EXE, and AppX installers
- **State Tracking**: Persistent installation state management
- **Catalog System**: JSON-based application catalog with domain vetting

### System Tools
- **Registry Management**: Apply tweaks with automatic backups
- **Bloatware Removal**: Remove unwanted AppX packages
- **Service Control**: Manage Windows services
- **Performance Presets**: Apply optimization profiles
- **Safety Features**: Restore points, backups, confirmations

### User Interfaces
- **CLI**: Full-featured command-line interface with argparse
- **GUI**: Tkinter-based graphical interface with async operations

## Architecture

```
better11/
├── better11/apps/          # Application management
│   ├── catalog.py          # Catalog management
│   ├── download.py         # Download with vetting
│   ├── manager.py          # Main orchestrator
│   ├── models.py           # Data models
│   ├── runner.py           # Installer execution
│   ├── state_store.py      # State persistence
│   └── verification.py     # Hash/signature verification
├── system_tools/           # System enhancement
│   ├── bloatware.py        # AppX package removal
│   ├── performance.py      # Performance presets
│   ├── registry.py         # Registry management
│   ├── safety.py           # Safety utilities
│   └── services.py         # Service management
└── tests/                  # Test suite
```

## Documentation

Complete documentation available:
- **README.md** - Project overview and quick start
- **INSTALL.md** - Installation instructions
- **USER_GUIDE.md** - Comprehensive usage guide
- **API_REFERENCE.md** - Complete API documentation
- **ARCHITECTURE.md** - System design documentation
- **CONTRIBUTING.md** - Development guidelines
- **SECURITY.md** - Security policies
- **CHANGELOG.md** - Version history
- **LICENSE** - MIT License

## Key Design Patterns

1. **Dependency Injection**: Components accept dependencies for testability
2. **Strategy Pattern**: Different installer types handled polymorphically
3. **Repository Pattern**: State store abstracts persistence
4. **Facade Pattern**: AppManager orchestrates multiple subsystems
5. **Template Method**: Consistent safety flow in system tools

## Security Architecture

**Multi-Layer Security**:
1. Domain vetting for downloads
2. SHA-256 hash verification (required)
3. HMAC-SHA256 signatures (optional)
4. Restore point creation
5. Registry backups
6. User confirmation prompts

## Development Guidelines

### Current Standards
- Python 3.8+ with type hints
- Black for code formatting
- pytest for testing
- Dataclasses for models
- Logging throughout

### Safety Practices (Already Implemented)
- All system tools validate Windows platform
- Automatic restore points before modifications
- Registry backups before changes
- User confirmation for destructive operations
- Comprehensive error handling and logging

### Testing
- Unit tests with mocking for platform-specific code
- Dry-run mode for cross-platform development
- Integration tests for workflows
- Test coverage for critical paths

## Common Development Tasks

### Adding New Applications
1. Add entry to `better11/apps/catalog.json`
2. Compute SHA-256 hash: `certutil -hashfile installer.msi SHA256`
3. Optional: Generate HMAC signature
4. Test installation: `python -m better11.cli install app-id`

### Adding System Tools
1. Create module in `system_tools/`
2. Follow safety pattern (see existing modules)
3. Add tests in `tests/test_system_tools.py`
4. Document in API_REFERENCE.md

### Extending Installer Support
1. Add enum to `InstallerType` in `models.py`
2. Implement in `InstallerRunner._install_command()`
3. Implement in `InstallerRunner._uninstall_command()`
4. Add tests in `tests/test_manager.py`

## Future Enhancements (Planned)

See CHANGELOG.md for detailed roadmap:
- v0.3.0: Authenticode verification, auto-updates
- v0.4.0: Improved GUI, backup/restore system
- v0.5.0: Plugin system, advanced features
- v1.0.0: Production-ready, stable API

## Notes for Claude

### Current State
- ✅ Fully functional implementation
- ✅ Comprehensive test coverage
- ✅ Complete documentation
- ✅ Security features implemented
- ✅ CLI and GUI working

### Working with Better11
- Code is production-quality with proper error handling
- All system modifications include safety features
- Tests can be run cross-platform with mocking
- Documentation is maintained and up-to-date

### Extension Points
- New installer types via `InstallerType` enum
- Custom verifiers via `DownloadVerifier` subclass
- Custom storage via `InstallationStateStore` subclass
- New system tools following established patterns

### Important Considerations
- System tools require Windows and admin privileges
- Application catalog requires SHA-256 hashes
- All operations are logged for troubleshooting
- Dry-run mode available for safe testing

## Quick Reference

```python
# Application installation
from better11.apps.manager import AppManager
manager = AppManager(catalog_path)
status, result = manager.install("app-id")

# Registry tweaks
from system_tools.registry import RegistryTweak, apply_tweaks
tweaks = [RegistryTweak(...)]
apply_tweaks(tweaks)

# Bloatware removal
from system_tools.bloatware import remove_bloatware
remove_bloatware(["Package.Name"])

# Service management
from system_tools.services import ServiceAction, apply_service_actions
actions = [ServiceAction("ServiceName", "disable")]
apply_service_actions(actions)
```

## Contact & Resources

- **Repository**: https://github.com/owner/better11
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **License**: MIT

---

**Last Updated**: December 9, 2025  
**Project Status**: Active Development (v0.2.0)  
**Code Quality**: Production-ready with comprehensive testing
