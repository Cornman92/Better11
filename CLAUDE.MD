# Better11 - Project Context for Claude

## Project Overview

Better11 is an all-around Windows 11 system enhancer that provides powerful tools for system customization and management.

## Core Features

- **Live Image Editing**: Modify Windows 11 installations while the system is running
- **Offline Image Editing**: Edit Windows installation images (WIM/ESD files) without booting
- **Application Management**: Download and install applications with ease
- **System Enhancement**: Various tools to improve and customize Windows 11 experience

## Project Goals

1. Provide a comprehensive toolkit for Windows 11 customization
2. Enable both live system modifications and offline image editing
3. Simplify application installation and management
4. Enhance user experience with Windows 11

## Technical Considerations

### Platform
- **Target OS**: Windows 11
- **Development**: Likely requires Windows-specific APIs and tools
- **Permissions**: May require administrator/elevated privileges for system modifications

### Key Components

1. **Image Editor**
   - Works with Windows image formats (WIM, ESD, ISO)
   - Can mount and modify offline images
   - Supports live system modifications

2. **Application Manager**
   - Application download functionality
   - Installation automation
   - Package management

3. **System Enhancer**
   - Windows 11 customization features
   - System optimization tools
   - UI/UX improvements

## Development Guidelines

### Safety First
- Always validate user inputs when working with system files
- Implement proper error handling for file operations
- Create backups before making system modifications
- Warn users about potentially destructive operations

### Code Quality
- Keep code modular and maintainable
- Document complex system interactions
- Use clear naming conventions
- Add error messages that help users understand what went wrong

### Windows Integration
- Respect Windows security boundaries
- Check for required permissions before operations
- Handle UAC (User Account Control) appropriately
- Test compatibility with different Windows 11 versions

## Common Tasks

### Working with Windows Images
- Mounting/unmounting WIM files
- Modifying registry in offline images
- Adding/removing features and packages
- Injecting drivers or updates

### Application Management
- Safe download from trusted sources
- Verify file integrity before installation
- Handle different installer types (MSI, EXE, AppX)
- Manage dependencies

### System Modifications
- Registry editing (both live and offline)
- Service management
- File system operations
- Permission handling

## Security Considerations

- Always validate file paths to prevent directory traversal
- Verify downloaded files with checksums/signatures
- Don't execute arbitrary code without user confirmation
- Implement proper input sanitization
- Use least-privilege principle where possible

## Future Enhancements

Consider these areas for future development:
- GUI interface for better user experience
- Preset profiles for common customizations
- Backup and restore functionality
- Update management
- Driver integration tools
- Windows feature customization
- Telemetry and bloatware removal options

## Notes for Claude

- This project deals with system-level Windows operations
- Many features require administrator privileges
- Focus on reliability and safety when implementing new features
- Always consider the impact of modifications on system stability
- Provide clear documentation for potentially risky operations
