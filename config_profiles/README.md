# Better11 Configuration Profiles

This directory contains predefined configuration profiles for different use cases.

## Available Profiles

### `gaming.json`
Optimized for gaming performance:
- Aggressive system optimization
- Updates paused for 7 days
- Telemetry disabled
- High-performance settings
- Verbose output for monitoring

### `developer.json`
Optimized for development workflows:
- Balanced system optimization
- Auto-update enabled
- Package manager integration
- Fast file operations
- Less restrictive confirmations

### `productivity.json` (coming soon)
Optimized for office/productivity:
- Balanced optimization
- Auto-updates enabled
- Standard settings

### `server.json` (coming soon)
Optimized for server deployments:
- Maximum optimization
- Minimal UI
- Automated operations
- Enhanced security

## Using Profiles

### Method 1: Load via Config Manager

```python
from better11.config_manager import ConfigManager

# Load profile
config = ConfigManager()
config.apply_profile("gaming")

# Save as default
config.save()
```

### Method 2: Copy Profile

```bash
# Copy profile to config location
cp config_profiles/gaming.json ~/.better11/config.json
```

### Method 3: Command Line (future)

```bash
better11 config load --profile gaming
better11 config export --output my_config.json
```

## Configuration Structure

```json
{
  "version": "0.3.0",
  "image": {
    "work_dir": "",              // Work directory for image operations
    "mount_dir": "",             // Mount directory
    "default_index": 1,          // Default image index
    "auto_optimize": false,      // Auto-optimize images
    "compression": "max"         // Compression level: none, fast, max
  },
  "updates": {
    "auto_check": true,          // Auto-check for updates
    "auto_download": false,      // Auto-download updates
    "auto_install": false,       // Auto-install updates
    "pause_days": 0,             // Days to pause updates (0-35)
    "include_drivers": true      // Include driver updates
  },
  "drivers": {
    "backup_dir": "",            // Driver backup directory
    "auto_backup": true,         // Auto-backup before operations
    "include_inbox": false,      // Include inbox drivers in backup
    "force_unsigned": false      // Force unsigned driver installation
  },
  "packages": {
    "cache_dir": "",             // Package cache directory
    "preferred_manager": "winget", // Preferred package manager
    "auto_update": false,        // Auto-update packages
    "verify_signatures": true    // Verify package signatures
  },
  "optimizer": {
    "default_level": "balanced", // Optimization level
    "auto_backup_registry": true, // Auto-backup registry
    "create_restore_point": true, // Create restore points
    "disable_telemetry": false   // Disable Windows telemetry
  },
  "files": {
    "buffer_size": 1048576,      // File operation buffer (bytes)
    "use_robocopy": true,        // Use robocopy for fast operations
    "secure_delete": false       // Secure file deletion
  },
  "ui": {
    "theme": "default",          // UI theme
    "verbose": false,            // Verbose output
    "show_progress": true,       // Show progress bars
    "confirm_destructive": true  // Confirm destructive operations
  }
}
```

## Creating Custom Profiles

1. Copy an existing profile
2. Modify settings as needed
3. Save with descriptive name
4. Load using ConfigManager

Example:
```bash
cp config_profiles/gaming.json config_profiles/my_profile.json
# Edit my_profile.json
```

Then in Python:
```python
from better11.config_manager import load_config

config = load_config("config_profiles/my_profile.json")
```

## Optimization Levels

- `conservative`: Minimal changes, maximum safety
- `balanced`: Moderate optimizations (default)
- `aggressive`: Maximum performance
- `gaming`: Gaming-focused optimizations
- `productivity`: Work-focused optimizations
- `battery_saver`: Battery life optimization (laptops)

## Package Managers

- `winget`: Windows Package Manager (default)
- `chocolatey`: Chocolatey
- `npm`: Node Package Manager
- `pip`: Python Package Manager
- `scoop`: Scoop (coming soon)

## File Buffer Sizes

- `524288` (512 KB): Small files
- `1048576` (1 MB): Default
- `2097152` (2 MB): Large files
- `4194304` (4 MB): Very large files

## Tips

1. **Gaming**: Use `gaming.json` and pause updates
2. **Development**: Use `developer.json` with auto-updates
3. **Production**: Create custom profile with strict settings
4. **Testing**: Use developer profile with confirmations enabled

## Validation

Validate your custom configuration:

```python
from better11.config_manager import ConfigManager

config = ConfigManager("my_config.json")
if config.load():
    print("Configuration valid!")
else:
    print("Configuration invalid!")
```

## Export Current Configuration

```python
from better11.config_manager import get_config

config = get_config()
config.export_current("my_current_config.json")
```

---

**Version:** 0.3.0
**Last Updated:** 2024-12-19
