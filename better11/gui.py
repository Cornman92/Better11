from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from better11.apps.download import DownloadError
from better11.apps.manager import AppManager, DependencyError
from better11.apps.verification import VerificationError


class AppManagerGUI(tk.Tk):
    def __init__(self, manager: AppManager):
        super().__init__()
        self.title("Better11 App Manager")
        self.manager = manager
        self._build_widgets()
        self._populate_apps()

    def _build_widgets(self) -> None:
        self.app_list = tk.Listbox(self, height=10, width=60)
        self.app_list.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.download_button = tk.Button(self, text="Download", command=self._download_selected)
        self.download_button.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.install_button = tk.Button(self, text="Install", command=self._install_selected)
        self.install_button.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        self.uninstall_button = tk.Button(self, text="Uninstall", command=self._uninstall_selected)
        self.uninstall_button.grid(row=1, column=2, sticky="ew", padx=10, pady=5)

        self.status_label = tk.Label(self, text="Ready", anchor="w", justify="left")
        self.status_label.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

    def _populate_apps(self) -> None:
        self.app_list.delete(0, tk.END)
        for app in self.manager.list_available():
            self.app_list.insert(tk.END, f"{app.app_id} | {app.name} v{app.version} | {app.installer_type.value}")

    def _selected_app_id(self) -> str | None:
        selection = self.app_list.curselection()
        if not selection:
            return None
        return self.manager.list_available()[selection[0]].app_id

    def _report(self, message: str) -> None:
        self.status_label.config(text=message)

    def _run_async(self, func, *args) -> None:
        threading.Thread(target=self._wrap_action, args=(func, *args), daemon=True).start()

    def _wrap_action(self, func, *args) -> None:
        try:
            func(*args)
        except Exception as exc:  # GUI fallback
            message = str(exc)
            self.after(0, lambda msg=message: messagebox.showerror("Error", msg))

    def _download_selected(self) -> None:
        app_id = self._selected_app_id()
        if not app_id:
            messagebox.showinfo("Select", "Select an app to download")
            return
        self._run_async(self._download_app, app_id)

    def _download_app(self, app_id: str) -> None:
        try:
            destination, cache_hit = self.manager.download(app_id)
        except DownloadError as exc:
            message = str(exc)
            self.after(0, lambda msg=message: messagebox.showerror("Download failed", msg))
            return
        descriptor = "Cached" if cache_hit else "Downloaded"
        self.after(0, lambda: self._report(f"{descriptor} {app_id} to {destination}"))

    def _install_selected(self) -> None:
        app_id = self._selected_app_id()
        if not app_id:
            messagebox.showinfo("Select", "Select an app to install")
            return
        self._run_async(self._install_app, app_id)

    def _install_app(self, app_id: str) -> None:
        try:
            plan = self.manager.build_install_plan(app_id)
        except KeyError as exc:
            message = str(exc)
            self.after(0, lambda msg=message: messagebox.showerror("Planning failed", msg))
            return

        if any(step.action == "blocked" for step in plan.steps):
            warning = "\n".join(plan.warnings) if plan.warnings else "Installation blocked by dependency issues."
            self.after(0, lambda msg=warning: messagebox.showerror("Installation blocked", msg))
            return

        if plan.warnings:
            warning = "\n".join(plan.warnings)
            self.after(0, lambda msg=warning: messagebox.showwarning("Plan warnings", msg))

        try:
            status, result = self.manager.install(app_id)
        except (DownloadError, VerificationError, DependencyError) as exc:
            message = str(exc)
            self.after(0, lambda msg=message: messagebox.showerror("Installation failed", msg))
            return
        command = " ".join(result.command) if result.command else "already installed"
        dependency_chain = [step.app_id for step in plan.steps if step.app_id != app_id]
        chain_text = ", ".join(dependency_chain) if dependency_chain else "no dependencies"
        self.after(0, lambda: self._report(f"Installed {status.app_id} ({command}; plan: {chain_text})"))

    def _uninstall_selected(self) -> None:
        app_id = self._selected_app_id()
        if not app_id:
            messagebox.showinfo("Select", "Select an app to uninstall")
            return
        self._run_async(self._uninstall_app, app_id)

    def _uninstall_app(self, app_id: str) -> None:
        try:
            result = self.manager.uninstall(app_id)
        except DependencyError as exc:
            message = str(exc)
            self.after(0, lambda msg=message: messagebox.showerror("Uninstall failed", msg))
            return
        command = " ".join(result.command)
        self.after(0, lambda: self._report(f"Uninstalled {app_id} ({command})"))


def launch_gui(catalog_path: Path | None = None) -> None:
    manager = AppManager(catalog_path or Path(__file__).parent / "apps" / "catalog.json")
    gui = AppManagerGUI(manager)
    gui.mainloop()


if __name__ == "__main__":
    launch_gui()
