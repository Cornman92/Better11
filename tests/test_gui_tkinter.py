"""
Tests for the Tkinter GUI module.

Note: These are basic tests to verify imports and initialization.
Full GUI testing would require a headless display (Xvfb) or mocking.
Tkinter may not be available on headless Linux systems.
"""

import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import, skip all tests if tkinter not available
pytest.importorskip("tkinter", reason="Tkinter not available")

from better11.gui_tkinter import Better11GUI


class TestGUIImports:
    """Test that GUI module imports correctly."""
    
    def test_imports(self):
        """Test that all required modules can be imported."""
        import tkinter as tk
        from tkinter import ttk, messagebox, scrolledtext
        
        assert tk is not None
        assert ttk is not None
        assert messagebox is not None
        assert scrolledtext is not None
    
    def test_gui_class_exists(self):
        """Test that Better11GUI class is defined."""
        assert Better11GUI is not None
        assert callable(Better11GUI)


class TestGUIStructure:
    """Test GUI class structure (without actually creating a window)."""
    
    def test_gui_has_required_methods(self):
        """Test that GUI class has required methods."""
        required_methods = [
            'create_menu',
            'create_widgets',
            'create_startup_tab',
            'create_log_tab',
            'refresh_startup_items',
            'enable_selected_item',
            'disable_selected_item',
            'remove_selected_item',
            'log',
            'show_about'
        ]
        
        for method in required_methods:
            assert hasattr(Better11GUI, method)
            assert callable(getattr(Better11GUI, method))


# Skip actual GUI tests if tkinter cannot create a display
@pytest.mark.skipif(
    sys.platform.startswith('linux') and not Path('/tmp/.X11-unix').exists(),
    reason="No display available for GUI testing"
)
class TestGUIBasicFunctionality:
    """Test basic GUI functionality (requires display)."""
    
    def test_gui_creation(self):
        """Test that GUI can be created."""
        import tkinter as tk
        
        root = tk.Tk()
        try:
            app = Better11GUI(root)
            
            # Verify basic attributes
            assert hasattr(app, 'root')
            assert hasattr(app, 'startup_manager')
            assert hasattr(app, 'tree')
            assert hasattr(app, 'log_text')
            
        finally:
            # Always clean up
            root.destroy()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
