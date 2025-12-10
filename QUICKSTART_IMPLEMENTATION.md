# Better11 v0.3.0 - Quick Start Implementation Guide

**Version**: 0.3.0-dev  
**Date**: December 10, 2025  
**Purpose**: Get started implementing v0.3.0 features TODAY

---

## 🚀 TL;DR - Start in 5 Minutes

```bash
# 1. Verify setup
cd /workspace
python -m pytest tests/test_config.py -v

# 2. Choose your path:
# Path A - Week 1 Start (Configuration testing)
code tests/test_config.py

# Path B - Quick Win (Startup Manager)
touch system_tools/startup.py
code system_tools/startup.py

# 3. Start coding!
```

---

## 📊 What You Need to Know

### Current Status
✅ **Infrastructure Complete**: Config, interfaces, base classes all done  
✅ **Planning Complete**: 12-week roadmap ready  
✅ **Tests Ready**: Framework in place, 31 tests passing  
⏳ **Implementation**: Ready to begin NOW

### The Hybrid Approach (Recommended)
**12 weeks**, **3 major phases**, **early wins**:
1. **Weeks 1-2**: Startup Manager (FIRST WIN ⭐)
2. **Weeks 3-6**: Code Signing (CRITICAL SECURITY)
3. **Weeks 7-9**: Privacy + Updates (USER POWER)
4. **Weeks 10-12**: Integration + Release

### Why Hybrid?
- ✅ Delivers value in Week 2 (Startup Manager)
- ✅ Builds critical security (Code Signing)
- ✅ Comprehensive v0.3.0 by Week 12

---

## 🎯 Week 1 Implementation Guide

### Day 1-2: Configuration System Testing

**Goal**: Complete configuration system test coverage

**File**: `tests/test_config.py`

**Tasks**:
```python
# Add these tests:

def test_load_yaml_configuration():
    """Test loading YAML format config."""
    # Create temp YAML file
    # Load with Config.load()
    # Assert values loaded correctly

def test_environment_variable_overrides():
    """Test env var overrides."""
    # Set BETTER11_AUTO_UPDATE=false
    # Load config
    # Assert auto_update is False

def test_configuration_validation():
    """Test invalid config values rejected."""
    # Create config with invalid safety_level
    # Assert validate() raises ValueError

def test_save_and_reload():
    """Test config persistence."""
    # Create config with custom values
    # Save to temp file
    # Load from temp file
    # Assert values match
```

**Expected Time**: 8-12 hours  
**Deliverable**: All config tests passing

---

### Day 3-5: Startup Manager (Read-Only)

**Goal**: List all startup items from all sources

**File**: `system_tools/startup.py`

**Starter Code**:
```python
"""Windows startup program management.

This module provides functionality to list, enable, disable, and remove
startup programs from various locations in Windows.
"""
from __future__ import annotations

import os
import winreg
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata
from .safety import SafetyError

_LOGGER = get_logger(__name__)


class StartupLocation(Enum):
    """Location where startup item is registered."""
    REGISTRY_HKLM_RUN = "hklm_run"
    REGISTRY_HKCU_RUN = "hkcu_run"
    STARTUP_FOLDER_COMMON = "startup_common"
    STARTUP_FOLDER_USER = "startup_user"
    TASK_SCHEDULER = "task_scheduler"
    SERVICES = "services"


class StartupImpact(Enum):
    """Estimated impact on boot time."""
    HIGH = "high"      # >3s delay
    MEDIUM = "medium"  # 1-3s delay
    LOW = "low"        # <1s delay
    UNKNOWN = "unknown"


@dataclass
class StartupItem:
    """Represents a startup program."""
    name: str
    command: str
    location: StartupLocation
    enabled: bool
    impact: StartupImpact = StartupImpact.UNKNOWN
    publisher: Optional[str] = None


class StartupManager(SystemTool):
    """Manage Windows startup programs."""
    
    # Registry keys to check
    REGISTRY_KEYS = [
        (winreg.HKEY_LOCAL_MACHINE, 
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
         StartupLocation.REGISTRY_HKLM_RUN),
        (winreg.HKEY_CURRENT_USER,
         r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
         StartupLocation.REGISTRY_HKCU_RUN),
    ]
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Startup Manager",
            description="Manage Windows startup programs",
            version="0.3.0",
            requires_admin=False,  # Reading doesn't need admin
            requires_restart=False,
            category="performance"
        )
    
    def validate_environment(self) -> None:
        """Validate environment."""
        # Already checked by base class
        pass
    
    def execute(self, *args, **kwargs) -> bool:
        """Execute startup management.
        
        This is called by the base class run() method.
        """
        # For now, just list items
        items = self.list_startup_items()
        _LOGGER.info("Found %d startup items", len(items))
        return True
    
    def list_startup_items(self) -> List[StartupItem]:
        """List all startup programs from all locations.
        
        Returns
        -------
        List[StartupItem]
            All discovered startup items
        """
        items = []
        items.extend(self._get_registry_items())
        items.extend(self._get_startup_folder_items())
        # TODO: Add scheduled tasks
        # TODO: Add services
        return items
    
    def _get_registry_items(self) -> List[StartupItem]:
        """Get startup items from registry."""
        items = []
        
        for hive, subkey, location in self.REGISTRY_KEYS:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    i = 0
                    while True:
                        try:
                            name, command, _ = winreg.EnumValue(key, i)
                            items.append(StartupItem(
                                name=name,
                                command=command,
                                location=location,
                                enabled=True  # In registry = enabled
                            ))
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                _LOGGER.debug("Registry key not found: %s", subkey)
            except Exception as exc:
                _LOGGER.warning("Failed to read registry: %s", exc)
        
        return items
    
    def _get_startup_folder_items(self) -> List[StartupItem]:
        """Get startup items from startup folders."""
        items = []
        
        # User startup folder
        user_startup = Path(os.environ.get('APPDATA', '')) / \
            'Microsoft/Windows/Start Menu/Programs/Startup'
        
        # Common startup folder
        common_startup = Path(os.environ.get('PROGRAMDATA', '')) / \
            'Microsoft/Windows/Start Menu/Programs/Startup'
        
        for folder, location in [
            (user_startup, StartupLocation.STARTUP_FOLDER_USER),
            (common_startup, StartupLocation.STARTUP_FOLDER_COMMON)
        ]:
            if folder.exists():
                for item in folder.iterdir():
                    if item.is_file() and item.suffix in {'.lnk', '.exe', '.bat'}:
                        items.append(StartupItem(
                            name=item.stem,
                            command=str(item),
                            location=location,
                            enabled=True
                        ))
        
        return items


def list_startup_items() -> List[StartupItem]:
    """Convenience function to list startup items.
    
    Returns
    -------
    List[StartupItem]
        All discovered startup items
    """
    manager = StartupManager()
    return manager.list_startup_items()


__all__ = [
    "StartupLocation",
    "StartupImpact",
    "StartupItem",
    "StartupManager",
    "list_startup_items",
]
```

**Test File**: `tests/test_startup.py`
```python
"""Tests for startup manager."""
import pytest
from system_tools.startup import (
    StartupManager, 
    StartupLocation, 
    list_startup_items
)


def test_list_startup_items():
    """Test listing startup items."""
    items = list_startup_items()
    assert isinstance(items, list)
    # Note: May be empty on test systems
    

def test_startup_manager_creation():
    """Test creating StartupManager."""
    manager = StartupManager()
    assert manager is not None
    metadata = manager.get_metadata()
    assert metadata.name == "Startup Manager"


def test_get_registry_items():
    """Test getting registry startup items."""
    manager = StartupManager()
    items = manager._get_registry_items()
    assert isinstance(items, list)


def test_get_startup_folder_items():
    """Test getting startup folder items."""
    manager = StartupManager()
    items = manager._get_startup_folder_items()
    assert isinstance(items, list)


# Add more tests...
```

**Expected Time**: 12-16 hours  
**Deliverable**: Startup Manager can list all items, basic tests passing

---

## 🎯 Week 2: Complete Startup Manager

### Day 1-3: Enable/Disable/Remove

**Add to `startup.py`**:
```python
def enable_startup_item(self, item: StartupItem) -> bool:
    """Enable a startup item."""
    # Implementation depends on location
    # Registry: Add value back
    # Folder: Restore file
    pass

def disable_startup_item(self, item: StartupItem) -> bool:
    """Disable a startup item."""
    # Implementation depends on location  
    # Registry: Delete value or rename to disable
    # Folder: Move file or rename
    pass

def remove_startup_item(self, item: StartupItem) -> bool:
    """Permanently remove a startup item."""
    # More aggressive than disable
    pass
```

### Day 4: CLI Integration

**Add to `better11/cli.py`**:
```python
def create_startup_parser(subparsers):
    """Create startup management parser."""
    startup_parser = subparsers.add_parser(
        'startup', 
        help='Manage startup programs'
    )
    startup_sub = startup_parser.add_subparsers(dest='startup_command')
    
    # List command
    list_parser = startup_sub.add_parser('list', help='List startup items')
    list_parser.add_argument(
        '--location',
        help='Filter by location',
        choices=['registry', 'folder', 'all'],
        default='all'
    )
    
    # Disable command
    disable_parser = startup_sub.add_parser('disable', help='Disable item')
    disable_parser.add_argument('name', help='Name of item to disable')
    
    # Enable command
    enable_parser = startup_sub.add_parser('enable', help='Enable item')
    enable_parser.add_argument('name', help='Name of item to enable')

def handle_startup(args):
    """Handle startup command."""
    from system_tools.startup import StartupManager
    
    manager = StartupManager()
    
    if args.startup_command == 'list':
        items = manager.list_startup_items()
        for item in items:
            status = "✓" if item.enabled else "✗"
            print(f"{status} {item.name:30s} [{item.location.value}]")
    
    elif args.startup_command == 'disable':
        # Find item by name
        items = manager.list_startup_items()
        item = next((i for i in items if i.name == args.name), None)
        if item:
            manager.disable_startup_item(item)
            print(f"Disabled: {item.name}")
        else:
            print(f"Not found: {args.name}")
    
    # ... other commands
```

### Day 5: GUI Integration

**Add to `better11/gui.py`**:
```python
def create_startup_tab(self):
    """Create startup management tab."""
    frame = ttk.Frame(self.notebook)
    self.notebook.add(frame, text="Startup")
    
    # List with checkboxes
    list_frame = ttk.Frame(frame)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Scrollable list
    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    self.startup_list = tk.Listbox(
        list_frame,
        yscrollcommand=scrollbar.set
    )
    self.startup_list.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=self.startup_list.yview)
    
    # Buttons
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Button(
        button_frame,
        text="Refresh",
        command=self.refresh_startup_items
    ).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(
        button_frame,
        text="Disable Selected",
        command=self.disable_startup_item
    ).pack(side=tk.LEFT, padx=5)

def refresh_startup_items(self):
    """Refresh startup items list."""
    from system_tools.startup import list_startup_items
    
    self.startup_list.delete(0, tk.END)
    items = list_startup_items()
    
    for item in items:
        status = "✓" if item.enabled else "✗"
        self.startup_list.insert(
            tk.END,
            f"{status} {item.name} [{item.location.value}]"
        )
```

---

## 📚 Key Files Reference

### Must Understand
1. `better11/config.py` - Configuration pattern
2. `better11/interfaces.py` - Interface design
3. `system_tools/base.py` - SystemTool base class
4. `system_tools/registry.py` - Existing implementation example

### Must Extend
1. `better11/cli.py` - Add new commands
2. `better11/gui.py` - Add new tabs
3. `tests/` - Add tests for new features

---

## 🧪 Testing Strategy

### Test Each Feature Incrementally
```bash
# Test as you build
python -m pytest tests/test_startup.py -v

# Test specific function
python -m pytest tests/test_startup.py::test_list_startup_items -v

# Test with coverage
python -m pytest tests/test_startup.py --cov=system_tools.startup
```

### Write Tests First (TDD)
1. Write failing test
2. Implement feature
3. Test passes
4. Refactor
5. Repeat

---

## 🎯 Success Checklist - Week 1

By end of Week 1, you should have:
- [ ] Configuration tests 100% passing
- [ ] YAML configuration support tested
- [ ] Environment variable overrides tested
- [ ] Enhanced logging implemented
- [ ] `startup.py` created with list functionality
- [ ] Can list all startup items from registry
- [ ] Can list all startup items from folders
- [ ] Basic tests for startup module passing
- [ ] CLI command `better11-cli startup list` working
- [ ] Documentation started

---

## 🎯 Success Checklist - Week 2

By end of Week 2, you should have:
- [ ] `enable_startup_item()` working
- [ ] `disable_startup_item()` working
- [ ] `remove_startup_item()` working
- [ ] 15+ tests for startup module passing
- [ ] CLI commands complete (list/enable/disable)
- [ ] GUI startup tab functional
- [ ] Can actually enable/disable items from GUI
- [ ] Documentation complete for Startup Manager
- [ ] Ready to demo!

---

## 💡 Pro Tips

### Development Best Practices
1. **Test First**: Write tests before implementation
2. **Small Commits**: Commit after each small feature
3. **Document As You Go**: Don't defer documentation
4. **Use Dry Run**: Test destructive operations safely
5. **Log Everything**: Comprehensive logging helps debugging

### Common Pitfalls to Avoid
❌ Modifying registry without backup  
❌ Skipping user confirmation  
❌ Not testing on clean system  
❌ Forgetting error handling  
❌ Hardcoding paths  

✅ Always use `SafetyError` for failures  
✅ Always use `confirm_action()` for changes  
✅ Always use `create_restore_point()`  
✅ Always log operations  
✅ Always use Path objects  

### Code Style
```python
# Good: Descriptive, type hints, docstring
def list_startup_items() -> List[StartupItem]:
    """List all startup programs.
    
    Returns
    -------
    List[StartupItem]
        All discovered startup items
    """
    pass

# Bad: No types, no docs
def list_items():
    pass
```

---

## 🚨 When Things Go Wrong

### Tests Failing?
```bash
# Run with verbose output
python -m pytest tests/test_startup.py -vv

# Run with pdb on failure
python -m pytest tests/test_startup.py --pdb

# Check coverage
python -m pytest tests/test_startup.py --cov=system_tools.startup --cov-report=html
```

### Import Errors?
```bash
# Ensure you're in workspace directory
cd /workspace

# Reinstall in development mode
pip install -e .

# Or add to path
export PYTHONPATH=/workspace:$PYTHONPATH
```

### Registry Access Errors?
- Must run as Administrator for modifications
- Read-only operations don't need admin
- Use `try/except` around all registry operations

---

## 📞 Get Help

### Resources
- **Planning**: See FORWARD_PLAN.md (comprehensive)
- **Details**: See IMPLEMENTATION_PLAN_V0.3.0.md (technical specs)
- **Architecture**: See ARCHITECTURE.md (system design)
- **Questions**: Check WHATS_NEXT.md (context)

### Stuck?
1. Check existing code for patterns
2. Review test examples
3. Look at similar features (e.g., registry.py)
4. Check Python docs for Windows APIs
5. Ask for help with specific error messages

---

## 🎉 You're Ready!

You now have:
- ✅ Clear 12-week roadmap
- ✅ Week 1 & 2 detailed guide
- ✅ Code examples to copy
- ✅ Testing strategy
- ✅ Success criteria

**Stop reading. Start coding!** 🚀

```bash
# Create your feature branch
git checkout -b feature/startup-manager

# Open your editor
code system_tools/startup.py

# Make it happen!
```

---

**Good luck! You've got this!** 💪

---

*Last Updated: December 10, 2025*
