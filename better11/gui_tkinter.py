"""
Better11 - Tkinter GUI Prototype

A modern, user-friendly GUI for Windows 11 system optimization.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path
from typing import Optional, List
import threading

# Import Better11 modules
try:
    from system_tools.startup import StartupManager, StartupItem, StartupLocation, StartupImpact
    from system_tools.safety import SafetyError
except ImportError:
    # For development, add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from system_tools.startup import StartupManager, StartupItem, StartupLocation, StartupImpact
    from system_tools.safety import SafetyError


class Better11GUI:
    """Main GUI application for Better11."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI.
        
        Parameters
        ----------
        root : tk.Tk
            The root Tkinter window
        """
        self.root = root
        self.root.title("Better11 - Windows 11 Optimization Toolkit")
        self.root.geometry("1000x700")
        
        # Configure styling
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Modern theme
        
        # Configure colors
        self.bg_color = "#f0f0f0"
        self.accent_color = "#0078d4"  # Windows blue
        self.root.configure(bg=self.bg_color)
        
        # Initialize managers
        self.startup_manager = StartupManager()
        self.startup_items: List[StartupItem] = []
        
        # Create UI
        self.create_menu()
        self.create_widgets()
        
        # Load initial data
        self.refresh_startup_items()
    
    def create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh", command=self.refresh_startup_items)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Startup Manager", command=self.show_startup_tab)
        tools_menu.add_command(label="Privacy Settings", command=self.show_coming_soon)
        tools_menu.add_command(label="Performance", command=self.show_coming_soon)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_widgets(self):
        """Create the main UI widgets."""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_startup_tab()
        self.create_log_tab()
    
    def create_startup_tab(self):
        """Create the Startup Manager tab."""
        startup_frame = ttk.Frame(self.notebook)
        self.notebook.add(startup_frame, text="Startup Manager")
        
        # Top controls frame
        controls_frame = ttk.Frame(startup_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Refresh button
        ttk.Button(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_startup_items
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter dropdown
        ttk.Label(controls_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.filter_var,
            values=["All", "Enabled", "Disabled", "Registry", "Folders", "Tasks"],
            state="readonly",
            width=15
        )
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())
        
        # Stats label
        self.stats_label = ttk.Label(
            controls_frame,
            text="Total: 0 items (0 enabled)",
            font=("Arial", 10)
        )
        self.stats_label.pack(side=tk.RIGHT, padx=10)
        
        # Treeview frame with scrollbar
        tree_frame = ttk.Frame(startup_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Name", "Location", "Impact", "Enabled", "Command"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse"
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("Name", text="Name")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Impact", text="Impact")
        self.tree.heading("Enabled", text="Status")
        self.tree.heading("Command", text="Command")
        
        self.tree.column("Name", width=200)
        self.tree.column("Location", width=150)
        self.tree.column("Impact", width=80)
        self.tree.column("Enabled", width=80)
        self.tree.column("Command", width=400)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to show details
        self.tree.bind("<Double-Button-1>", self.show_item_details)
        
        # Action buttons frame
        action_frame = ttk.Frame(startup_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(
            action_frame,
            text="✓ Enable",
            command=self.enable_selected_item
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="✗ Disable",
            command=self.disable_selected_item
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="🗑 Remove",
            command=self.remove_selected_item
        ).pack(side=tk.LEFT, padx=5)
        
        # Info label
        info_text = (
            "💡 Tip: Disable unused startup programs to improve boot time. "
            "Double-click an item for details."
        )
        ttk.Label(
            action_frame,
            text=info_text,
            font=("Arial", 9),
            foreground="gray"
        ).pack(side=tk.RIGHT, padx=10)
    
    def create_log_tab(self):
        """Create the Log Viewer tab."""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="Activity Log")
        
        # Controls
        controls_frame = ttk.Frame(log_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            controls_frame,
            text="Clear Log",
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=5)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=100,
            height=30,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Add initial log message
        self.log("Better11 GUI Started")
        self.log("Ready to optimize your Windows 11 system!")
    
    def refresh_startup_items(self):
        """Refresh the startup items list."""
        self.log("Refreshing startup items...")
        
        # Run in background thread to avoid UI freeze
        thread = threading.Thread(target=self._load_startup_items)
        thread.daemon = True
        thread.start()
    
    def _load_startup_items(self):
        """Load startup items (runs in background thread)."""
        try:
            items = self.startup_manager.list_startup_items()
            
            # Update UI in main thread
            self.root.after(0, self._update_tree, items)
            self.root.after(0, self.log, f"Loaded {len(items)} startup items")
        except Exception as e:
            self.root.after(0, self.log, f"Error loading items: {e}")
            self.root.after(
                0,
                messagebox.showerror,
                "Error",
                f"Failed to load startup items:\n{e}"
            )
    
    def _update_tree(self, items: List[StartupItem]):
        """Update the treeview with items (runs in main thread)."""
        self.startup_items = items
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for item in items:
            status = "✓ Enabled" if item.enabled else "✗ Disabled"
            impact_emoji = {
                StartupImpact.HIGH: "🔴 HIGH",
                StartupImpact.MEDIUM: "🟡 MEDIUM",
                StartupImpact.LOW: "🟢 LOW",
                StartupImpact.UNKNOWN: "⚪ UNKNOWN"
            }.get(item.impact, "⚪ UNKNOWN")
            
            self.tree.insert(
                "",
                tk.END,
                values=(
                    item.name,
                    item.location.value,
                    impact_emoji,
                    status,
                    item.command[:100]  # Truncate long commands
                )
            )
        
        # Update stats
        enabled_count = sum(1 for item in items if item.enabled)
        self.stats_label.config(
            text=f"Total: {len(items)} items ({enabled_count} enabled)"
        )
        
        self.apply_filter()
    
    def apply_filter(self):
        """Apply the selected filter to the treeview."""
        filter_value = self.filter_var.get()
        
        # Show all items first
        for item in self.tree.get_children():
            self.tree.reattach(item, "", tk.END)
        
        if filter_value == "All":
            return
        
        # Hide items that don't match filter
        for idx, item_id in enumerate(self.tree.get_children()):
            item = self.startup_items[idx] if idx < len(self.startup_items) else None
            if not item:
                continue
            
            hide = False
            
            if filter_value == "Enabled" and not item.enabled:
                hide = True
            elif filter_value == "Disabled" and item.enabled:
                hide = True
            elif filter_value == "Registry" and "REGISTRY" not in item.location.value:
                hide = True
            elif filter_value == "Folders" and "FOLDER" not in item.location.value:
                hide = True
            elif filter_value == "Tasks" and item.location != StartupLocation.TASK_SCHEDULER:
                hide = True
            
            if hide:
                self.tree.detach(item_id)
    
    def get_selected_item(self) -> Optional[StartupItem]:
        """Get the currently selected startup item."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item first.")
            return None
        
        # Get the index of the selected item
        item_id = selection[0]
        index = self.tree.index(item_id)
        
        if index < len(self.startup_items):
            return self.startup_items[index]
        return None
    
    def enable_selected_item(self):
        """Enable the selected startup item."""
        item = self.get_selected_item()
        if not item:
            return
        
        if item.enabled:
            messagebox.showinfo("Already Enabled", f"{item.name} is already enabled.")
            return
        
        # Confirm action
        if not messagebox.askyesno(
            "Enable Startup Item",
            f"Enable startup item:\n\n{item.name}\n\nThis will allow it to run at startup."
        ):
            return
        
        try:
            self.startup_manager.enable_startup_item(item)
            self.log(f"✓ Enabled: {item.name}")
            messagebox.showinfo("Success", f"Enabled {item.name}")
            self.refresh_startup_items()
        except (SafetyError, NotImplementedError) as e:
            self.log(f"✗ Failed to enable {item.name}: {e}")
            messagebox.showerror("Error", f"Failed to enable item:\n{e}")
    
    def disable_selected_item(self):
        """Disable the selected startup item."""
        item = self.get_selected_item()
        if not item:
            return
        
        if not item.enabled:
            messagebox.showinfo("Already Disabled", f"{item.name} is already disabled.")
            return
        
        # Confirm action
        if not messagebox.askyesno(
            "Disable Startup Item",
            f"Disable startup item:\n\n{item.name}\n\n"
            f"This will prevent it from running at startup.\n"
            f"You can re-enable it later if needed."
        ):
            return
        
        try:
            self.startup_manager.disable_startup_item(item)
            self.log(f"✓ Disabled: {item.name}")
            messagebox.showinfo("Success", f"Disabled {item.name}")
            self.refresh_startup_items()
        except (SafetyError, NotImplementedError) as e:
            self.log(f"✗ Failed to disable {item.name}: {e}")
            messagebox.showerror("Error", f"Failed to disable item:\n{e}")
    
    def remove_selected_item(self):
        """Remove the selected startup item permanently."""
        item = self.get_selected_item()
        if not item:
            return
        
        # Confirm action (with warning)
        if not messagebox.askyesno(
            "Remove Startup Item",
            f"⚠️ WARNING: Permanently remove startup item:\n\n{item.name}\n\n"
            f"This action CANNOT be undone!\n"
            f"The item will be deleted from your system.\n\n"
            f"Are you sure you want to continue?",
            icon=messagebox.WARNING
        ):
            return
        
        try:
            self.startup_manager.remove_startup_item(item)
            self.log(f"✓ Removed: {item.name}")
            messagebox.showinfo("Success", f"Removed {item.name}")
            self.refresh_startup_items()
        except (SafetyError, NotImplementedError) as e:
            self.log(f"✗ Failed to remove {item.name}: {e}")
            messagebox.showerror("Error", f"Failed to remove item:\n{e}")
    
    def show_item_details(self, event):
        """Show detailed information about the selected item."""
        item = self.get_selected_item()
        if not item:
            return
        
        details = f"""
Startup Item Details
{'=' * 50}

Name:        {item.name}
Status:      {'Enabled' if item.enabled else 'Disabled'}
Location:    {item.location.value}
Impact:      {item.impact.value}
Publisher:   {item.publisher or 'Unknown'}
Command:     {item.command}

{'=' * 50}
        """
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Details: {item.name}")
        details_window.geometry("600x400")
        
        text_widget = scrolledtext.ScrolledText(
            details_window,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, details)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(
            details_window,
            text="Close",
            command=details_window.destroy
        ).pack(pady=10)
    
    def log(self, message: str):
        """Add a message to the log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Auto-scroll to bottom
    
    def clear_log(self):
        """Clear the log."""
        self.log_text.delete(1.0, tk.END)
        self.log("Log cleared")
    
    def show_startup_tab(self):
        """Show the Startup Manager tab."""
        self.notebook.select(0)
    
    def show_coming_soon(self):
        """Show 'coming soon' message."""
        messagebox.showinfo(
            "Coming Soon",
            "This feature is coming soon!\n\n"
            "Stay tuned for future updates."
        )
    
    def show_about(self):
        """Show the About dialog."""
        about_text = """
Better11 - Windows 11 Optimization Toolkit
Version 0.3.0 (Development)

A comprehensive, Python-based system optimization
toolkit for Windows 11, focused on improving
performance, privacy, and user experience.

Features:
• Startup program management
• Privacy settings control
• Performance optimization
• Bloatware removal
• And much more!

© 2025 Better11 Project
        """
        messagebox.showinfo("About Better11", about_text.strip())


def main():
    """Main entry point for the GUI."""
    root = tk.Tk()
    app = Better11GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
