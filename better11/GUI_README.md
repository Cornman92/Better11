# Better11 - Tkinter GUI

## Overview

The Better11 Tkinter GUI (`gui_tkinter.py`) provides a modern, user-friendly graphical interface for Windows 11 system optimization. It offers an intuitive way to manage startup programs, view system logs, and access various optimization tools.

## Features

### Current Implementation ✅

#### Startup Manager Tab
- **List View**: Display all startup items in a sortable table
- **Filtering**: Filter by status (All, Enabled, Disabled) and location (Registry, Folders, Tasks)
- **Enable/Disable**: Safely enable or disable startup items
- **Remove**: Permanently remove startup items (with confirmation)
- **Details View**: Double-click items to see full details
- **Real-time Stats**: View count of total and enabled items
- **Background Loading**: Non-blocking refresh with threading

#### Activity Log Tab
- **Real-time Logging**: View all actions and operations
- **Timestamps**: Each entry includes date and time
- **Clear Function**: Clear log history
- **Auto-scroll**: Automatically scrolls to latest entries

#### User Experience
- **Modern Styling**: Clean, Windows 11-inspired design
- **Color-coded Status**: Visual indicators for enabled/disabled items
- **Impact Indicators**: 🔴 High, 🟡 Medium, 🟢 Low impact ratings
- **Confirmation Dialogs**: Prevent accidental changes
- **Warning Prompts**: Extra warnings for destructive operations
- **Tooltips & Tips**: Helpful information throughout

### Coming Soon 🔜

- Privacy Settings Manager
- Performance Optimization Tools
- Bloatware Removal Interface
- Registry Tweaks Manager
- Services Manager
- System Reports & Analytics

## Screenshots

### Main Window - Startup Manager
```
┌─────────────────────────────────────────────────────────────────┐
│ Better11 - Windows 11 Optimization Toolkit                      │
├─────────────────────────────────────────────────────────────────┤
│ File  Tools  Help                                               │
├─────────────────────────────────────────────────────────────────┤
│ ┌─ Startup Manager ────────────┬─ Activity Log ───────────────┐ │
│ │                              │                               │ │
│ │ [🔄 Refresh]  Filter: [All ▼]     Total: 18 items (15 enabled)│ │
│ │                                                               │ │
│ │ Name             Location        Impact   Status   Command   │ │
│ │ ───────────────────────────────────────────────────────────  │ │
│ │ OneDrive         REGISTRY_HKCU  🟡 MEDIUM ✓ Enabled  C:\...  │ │
│ │ Discord          REGISTRY_HKCU  🟢 LOW    ✓ Enabled  C:\...  │ │
│ │ Spotify.lnk      STARTUP_FOLDER 🟢 LOW    ✗ Disabled C:\...  │ │
│ │ Adobe Update     TASK_SCHEDULER 🟡 MEDIUM ✓ Enabled  Task:...│ │
│ │ ...                                                           │ │
│ │                                                               │ │
│ │ [✓ Enable] [✗ Disable] [🗑 Remove]                           │ │
│ │ 💡 Tip: Disable unused startup programs to improve boot time │ │
│ └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Usage

### Running the GUI

```bash
# From workspace root
python3 -m better11.gui_tkinter

# Or directly
python3 better11/gui_tkinter.py
```

### Basic Operations

#### View Startup Items
1. Launch the GUI
2. The startup items load automatically
3. Use the Filter dropdown to narrow results
4. Double-click any item to view details

#### Disable a Startup Item
1. Select the item in the list
2. Click **[✗ Disable]** button
3. Confirm the action
4. Item will be disabled and list refreshes

#### Enable a Startup Item
1. Filter by "Disabled" to see disabled items
2. Select the item to re-enable
3. Click **[✓ Enable]** button
4. Confirm the action

#### Remove a Startup Item
1. Select the item to remove
2. Click **[🗑 Remove]** button
3. Read the warning carefully
4. Confirm to permanently remove
5. **Warning**: This action cannot be undone!

### Menu Options

#### File Menu
- **Refresh**: Reload all startup items
- **Exit**: Close the application

#### Tools Menu
- **Startup Manager**: Jump to Startup Manager tab
- **Privacy Settings**: (Coming soon)
- **Performance**: (Coming soon)

#### Help Menu
- **About**: View version and information

## Technical Details

### Architecture

```python
Better11GUI
├── __init__()              # Initialize app, create UI
├── create_menu()           # Build menu bar
├── create_widgets()        # Create main UI components
├── create_startup_tab()    # Startup Manager interface
├── create_log_tab()        # Activity log interface
└── Methods
    ├── refresh_startup_items()      # Reload data
    ├── enable_selected_item()       # Enable item
    ├── disable_selected_item()      # Disable item
    ├── remove_selected_item()       # Remove item
    ├── show_item_details()          # Show details dialog
    ├── apply_filter()               # Filter treeview
    └── log()                        # Add log entry
```

### Key Components

- **Notebook (Tabs)**: `ttk.Notebook` for multi-tab interface
- **Treeview**: `ttk.Treeview` for startup items table
- **ScrolledText**: Log viewer with scrolling
- **Threading**: Background loading to prevent UI freeze
- **Styling**: `ttk.Style` with 'clam' theme

### Integration

The GUI integrates seamlessly with Better11's core modules:

```python
from system_tools.startup import StartupManager, StartupItem
from system_tools.safety import SafetyError

# Create manager
startup_manager = StartupManager()

# Use manager methods
items = startup_manager.list_startup_items()
startup_manager.disable_startup_item(item)
startup_manager.enable_startup_item(item)
startup_manager.remove_startup_item(item)
```

## Requirements

### Python Packages
```
tkinter (usually included with Python)
```

### System Requirements
- **OS**: Windows 10/11 (primary target)
- **Python**: 3.8+ with tkinter
- **Display**: GUI environment (not headless)

### Linux/macOS
The GUI can run on Linux/macOS for development/testing, but startup management features require Windows APIs and will be limited.

## Development

### Testing

Tests are in `tests/test_gui_tkinter.py`:

```bash
# Run GUI tests (requires display)
pytest tests/test_gui_tkinter.py -v

# Tests will skip on headless systems
```

**Note**: Full GUI testing requires either:
- A display (X11, Wayland, Windows)
- Virtual display (Xvfb on Linux)
- Mocking of tkinter components

### Extending the GUI

To add new features:

1. **Add a new tab**:
```python
def create_newtool_tab(self):
    frame = ttk.Frame(self.notebook)
    self.notebook.add(frame, text="New Tool")
    # Add widgets...
```

2. **Add to Tools menu**:
```python
tools_menu.add_command(
    label="New Tool",
    command=self.show_newtool_tab
)
```

3. **Integrate with backend**:
```python
from system_tools.newtool import NewToolManager

self.newtool_manager = NewToolManager()
```

## Styling & Customization

### Current Theme
- **Base Theme**: 'clam' (modern, flat design)
- **Accent Color**: `#0078d4` (Windows blue)
- **Background**: `#f0f0f0` (light gray)
- **Font**: Arial (UI), Consolas (logs)

### Custom Colors
Edit in `__init__()`:
```python
self.bg_color = "#f0f0f0"      # Background
self.accent_color = "#0078d4"  # Accent
```

### Icons
Current emoji-based icons:
- 🔄 Refresh
- ✓ Enable
- ✗ Disable
- 🗑 Remove
- 💡 Tips
- 🔴🟡🟢⚪ Impact indicators

Can be replaced with actual icon files or icon fonts.

## Troubleshooting

### GUI Won't Start
```
Error: No module named 'tkinter'
```
**Solution**: Install tkinter:
- **Windows**: Usually included with Python
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **macOS**: Usually included, or use `brew install python-tk`

### "No Selection" Warning
```
Please select an item first.
```
**Solution**: Click an item in the list before using Enable/Disable/Remove buttons.

### Operations Fail
```
Failed to disable item: ...
```
**Possible Causes**:
1. **Permissions**: Run as Administrator on Windows
2. **Not on Windows**: Some features require Windows APIs
3. **Item Already Changed**: Refresh the list

### GUI Freezes
If the GUI becomes unresponsive:
1. Wait a few seconds (may be loading)
2. Close and restart
3. Check Activity Log for errors

## Future Enhancements

### Planned Features (v0.4.0+)
- [ ] **Dark Mode**: Theme switcher
- [ ] **System Tray**: Minimize to system tray
- [ ] **Notifications**: Toast notifications for operations
- [ ] **Search**: Search/filter startup items by name
- [ ] **Batch Operations**: Select multiple items
- [ ] **Profiles**: Save/load optimization profiles
- [ ] **Undo/Redo**: Revert recent changes
- [ ] **Export**: Export startup list to CSV/JSON
- [ ] **Recommendations**: AI-powered recommendations
- [ ] **Performance Graph**: Boot time tracking over time

### Alternative GUI Frameworks

For future versions, consider:
- **PyQt6/PySide6**: More powerful, professional look
- **wxPython**: Native look and feel
- **Kivy**: Cross-platform, modern
- **Electron + Python**: Web technologies
- **WinUI 3 (PowerShell)**: Native Windows 11 design

## Contributing

To contribute to the GUI:

1. Follow Python/tkinter best practices
2. Test on Windows (primary target)
3. Maintain accessibility features
4. Document new features in this README
5. Add tests when possible
6. Follow the existing code style

## License

Same as Better11 project (see root LICENSE file).

---

## Quick Reference

### Keyboard Shortcuts
- **F5**: Refresh startup items
- **Double-click**: Show item details
- **Delete**: Remove selected item (with confirmation)

### Color Codes
- **🔴 Red**: High impact on boot time
- **🟡 Yellow**: Medium impact on boot time
- **🟢 Green**: Low impact on boot time
- **⚪ White**: Unknown impact

### Safety Features
- ✅ Confirmation dialogs for all destructive actions
- ✅ Extra warnings for permanent removals
- ✅ Background thread for non-blocking operations
- ✅ Exception handling with user-friendly errors
- ✅ Activity logging for audit trail

---

**Better11 GUI - Modern Windows 11 Optimization Made Easy! 🚀**
