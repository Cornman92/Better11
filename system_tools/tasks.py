"""Windows Scheduled Tasks management.

This module provides management of Windows Task Scheduler tasks including
listing, enabling, disabling, and analyzing scheduled tasks.
"""
from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

_LOGGER = get_logger(__name__)


class TaskState(Enum):
    """Scheduled task state."""
    
    READY = "Ready"
    RUNNING = "Running"
    DISABLED = "Disabled"
    QUEUED = "Queued"
    UNKNOWN = "Unknown"


class TaskTriggerType(Enum):
    """Types of task triggers."""
    
    BOOT = "Boot"
    LOGON = "Logon"
    IDLE = "Idle"
    TIME = "Time"
    EVENT = "Event"
    REGISTRATION = "Registration"
    SESSION = "Session"
    CUSTOM = "Custom"


@dataclass
class ScheduledTask:
    """Information about a scheduled task."""
    
    name: str
    path: str
    state: TaskState
    description: str
    author: str
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    last_result: int
    triggers: List[str]
    run_as_user: str
    run_level: str  # "Limited" or "Highest"

    @property
    def full_path(self) -> str:
        """Get full task path."""
        return f"{self.path}\\{self.name}" if self.path else self.name

    @property
    def is_system_task(self) -> bool:
        """Check if this is a system task."""
        system_prefixes = [
            "\\Microsoft\\",
            "\\MicrosoftEdge",
            "\\Adobe",
            "\\Intel",
            "\\NVIDIA",
            "\\AMD",
        ]
        for prefix in system_prefixes:
            if self.path.startswith(prefix) or prefix in self.path:
                return True
        return False

    @property
    def is_healthy(self) -> bool:
        """Check if task is running without errors."""
        return self.last_result == 0 or self.last_result == 267009

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "state": self.state.value,
            "description": self.description,
            "author": self.author,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "last_result": self.last_result,
            "triggers": self.triggers,
            "is_system_task": self.is_system_task,
            "is_healthy": self.is_healthy
        }


@dataclass
class TaskFolder:
    """A folder in Task Scheduler."""
    
    name: str
    path: str
    task_count: int
    subfolder_count: int


class TaskSchedulerManager(SystemTool):
    """Manage Windows Task Scheduler.
    
    This class provides methods to list, enable, disable, and analyze
    scheduled tasks in Windows Task Scheduler.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    # Common tasks that are usually safe to disable
    SAFE_TO_DISABLE = [
        "Adobe Acrobat Update Task",
        "CCleaner Update",
        "OneDrive Standalone Update Task",
        "GoogleUpdateTaskMachine",
        "Opera scheduled",
        "Brave Update",
    ]
    
    # Critical tasks that should not be disabled
    CRITICAL_TASKS = [
        "SynchronizeTime",
        "Windows Defender",
        "Antimalware",
        "WindowsUpdate",
        "Backup",
    ]
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Task Scheduler Manager",
            description="Manage Windows scheduled tasks",
            version="0.3.0",
            requires_admin=True,  # Many tasks require admin to modify
            requires_restart=False,
            category="system"
        )
    
    def validate_environment(self) -> None:
        """Validate Task Scheduler prerequisites."""
        if platform.system() != "Windows":
            return
        
        try:
            subprocess.run(
                ["schtasks", "/?"],
                capture_output=True,
                timeout=10
            )
        except FileNotFoundError:
            _LOGGER.warning("schtasks not found")
    
    def execute(self) -> bool:
        """Execute default task listing operation."""
        tasks = self.list_tasks()
        _LOGGER.info("Found %d scheduled tasks", len(tasks))
        return True
    
    def list_tasks(self, folder: str = "\\", include_disabled: bool = True) -> List[ScheduledTask]:
        """List scheduled tasks.
        
        Parameters
        ----------
        folder : str
            Task folder path (default: root)
        include_disabled : bool
            Whether to include disabled tasks
        
        Returns
        -------
        List[ScheduledTask]
            List of scheduled tasks
        """
        _LOGGER.info("Listing scheduled tasks from %s", folder)
        
        if platform.system() != "Windows":
            _LOGGER.warning("Task Scheduler only available on Windows")
            return []
        
        try:
            # Use PowerShell for better data extraction
            ps_script = f'''
            Get-ScheduledTask -TaskPath "{folder}*" | ForEach-Object {{
                $Info = Get-ScheduledTaskInfo -TaskName $_.TaskName -TaskPath $_.TaskPath -ErrorAction SilentlyContinue
                @{{
                    Name = $_.TaskName
                    Path = $_.TaskPath
                    State = $_.State.ToString()
                    Description = $_.Description
                    Author = $_.Author
                    LastRunTime = if ($Info) {{ $Info.LastRunTime.ToString("o") }} else {{ $null }}
                    NextRunTime = if ($Info) {{ $Info.NextRunTime.ToString("o") }} else {{ $null }}
                    LastTaskResult = if ($Info) {{ $Info.LastTaskResult }} else {{ 0 }}
                    Principal = $_.Principal.UserId
                    RunLevel = $_.Principal.RunLevel.ToString()
                    Triggers = @($_.Triggers | ForEach-Object {{ $_.GetType().Name }})
                }}
            }} | ConvertTo-Json -Depth 10
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to list tasks: %s", result.stderr)
                return []
            
            output = result.stdout.strip()
            if not output or output == "null":
                return []
            
            data = json.loads(output)
            if not isinstance(data, list):
                data = [data] if data else []
            
            tasks = []
            for item in data:
                state = TaskState.UNKNOWN
                try:
                    state = TaskState(item.get("State", "Unknown"))
                except ValueError:
                    pass
                
                if not include_disabled and state == TaskState.DISABLED:
                    continue
                
                last_run = None
                if item.get("LastRunTime") and item["LastRunTime"] != "":
                    try:
                        last_run = datetime.fromisoformat(item["LastRunTime"].replace("Z", "+00:00"))
                    except ValueError:
                        pass
                
                next_run = None
                if item.get("NextRunTime") and item["NextRunTime"] != "":
                    try:
                        next_run = datetime.fromisoformat(item["NextRunTime"].replace("Z", "+00:00"))
                    except ValueError:
                        pass
                
                task = ScheduledTask(
                    name=item.get("Name", ""),
                    path=item.get("Path", ""),
                    state=state,
                    description=item.get("Description", "") or "",
                    author=item.get("Author", "") or "",
                    last_run=last_run,
                    next_run=next_run,
                    last_result=item.get("LastTaskResult", 0),
                    triggers=item.get("Triggers", []),
                    run_as_user=item.get("Principal", "") or "",
                    run_level=item.get("RunLevel", "Limited")
                )
                tasks.append(task)
            
            _LOGGER.info("Found %d tasks", len(tasks))
            return tasks
        
        except subprocess.TimeoutExpired:
            _LOGGER.error("Task listing timed out")
            return []
        except Exception as exc:
            _LOGGER.error("Failed to list tasks: %s", exc)
            return []
    
    def get_task(self, task_path: str, task_name: str) -> Optional[ScheduledTask]:
        """Get a specific scheduled task.
        
        Parameters
        ----------
        task_path : str
            Task folder path
        task_name : str
            Task name
        
        Returns
        -------
        ScheduledTask, optional
            Task details or None if not found
        """
        tasks = self.list_tasks(task_path)
        for task in tasks:
            if task.name == task_name:
                return task
        return None
    
    def enable_task(self, task_path: str, task_name: str) -> bool:
        """Enable a scheduled task.
        
        Parameters
        ----------
        task_path : str
            Task folder path
        task_name : str
            Task name
        
        Returns
        -------
        bool
            True if successful
        """
        full_path = f"{task_path}\\{task_name}" if task_path else task_name
        _LOGGER.info("Enabling task: %s", full_path)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would enable task: %s", full_path)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Task Scheduler only available on Windows")
            return False
        
        try:
            result = subprocess.run(
                ["schtasks", "/Change", "/TN", full_path, "/Enable"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                _LOGGER.info("Task enabled successfully")
                return True
            else:
                _LOGGER.error("Failed to enable task: %s", result.stderr or result.stdout)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to enable task: %s", exc)
            return False
    
    def disable_task(self, task_path: str, task_name: str) -> bool:
        """Disable a scheduled task.
        
        Parameters
        ----------
        task_path : str
            Task folder path
        task_name : str
            Task name
        
        Returns
        -------
        bool
            True if successful
        """
        full_path = f"{task_path}\\{task_name}" if task_path else task_name
        _LOGGER.info("Disabling task: %s", full_path)
        
        # Check if this is a critical task
        for critical in self.CRITICAL_TASKS:
            if critical.lower() in task_name.lower():
                _LOGGER.warning("Refusing to disable critical task: %s", task_name)
                return False
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable task: %s", full_path)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Task Scheduler only available on Windows")
            return False
        
        try:
            result = subprocess.run(
                ["schtasks", "/Change", "/TN", full_path, "/Disable"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                _LOGGER.info("Task disabled successfully")
                return True
            else:
                _LOGGER.error("Failed to disable task: %s", result.stderr or result.stdout)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to disable task: %s", exc)
            return False
    
    def run_task(self, task_path: str, task_name: str) -> bool:
        """Run a scheduled task immediately.
        
        Parameters
        ----------
        task_path : str
            Task folder path
        task_name : str
            Task name
        
        Returns
        -------
        bool
            True if task was started
        """
        full_path = f"{task_path}\\{task_name}" if task_path else task_name
        _LOGGER.info("Running task: %s", full_path)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would run task: %s", full_path)
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            result = subprocess.run(
                ["schtasks", "/Run", "/TN", full_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                _LOGGER.info("Task started successfully")
                return True
            else:
                _LOGGER.error("Failed to run task: %s", result.stderr or result.stdout)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to run task: %s", exc)
            return False
    
    def end_task(self, task_path: str, task_name: str) -> bool:
        """Stop a running scheduled task.
        
        Parameters
        ----------
        task_path : str
            Task folder path
        task_name : str
            Task name
        
        Returns
        -------
        bool
            True if successful
        """
        full_path = f"{task_path}\\{task_name}" if task_path else task_name
        _LOGGER.info("Stopping task: %s", full_path)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would stop task: %s", full_path)
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            result = subprocess.run(
                ["schtasks", "/End", "/TN", full_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                _LOGGER.info("Task stopped successfully")
                return True
            else:
                _LOGGER.error("Failed to stop task: %s", result.stderr or result.stdout)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to stop task: %s", exc)
            return False
    
    def delete_task(self, task_path: str, task_name: str) -> bool:
        """Delete a scheduled task.
        
        Parameters
        ----------
        task_path : str
            Task folder path
        task_name : str
            Task name
        
        Returns
        -------
        bool
            True if successful
        """
        full_path = f"{task_path}\\{task_name}" if task_path else task_name
        _LOGGER.info("Deleting task: %s", full_path)
        
        # Check if this is a system task
        task = self.get_task(task_path, task_name)
        if task and task.is_system_task:
            _LOGGER.warning("Refusing to delete system task: %s", task_name)
            return False
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would delete task: %s", full_path)
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            result = subprocess.run(
                ["schtasks", "/Delete", "/TN", full_path, "/F"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                _LOGGER.info("Task deleted successfully")
                return True
            else:
                _LOGGER.error("Failed to delete task: %s", result.stderr or result.stdout)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to delete task: %s", exc)
            return False
    
    def get_failed_tasks(self) -> List[ScheduledTask]:
        """Get tasks that failed on last run.
        
        Returns
        -------
        List[ScheduledTask]
            List of failed tasks
        """
        all_tasks = self.list_tasks()
        failed = [t for t in all_tasks if not t.is_healthy and t.last_result != 0]
        _LOGGER.info("Found %d failed tasks", len(failed))
        return failed
    
    def get_running_tasks(self) -> List[ScheduledTask]:
        """Get currently running tasks.
        
        Returns
        -------
        List[ScheduledTask]
            List of running tasks
        """
        all_tasks = self.list_tasks()
        running = [t for t in all_tasks if t.state == TaskState.RUNNING]
        _LOGGER.info("Found %d running tasks", len(running))
        return running
    
    def get_boot_tasks(self) -> List[ScheduledTask]:
        """Get tasks triggered at boot/startup.
        
        Returns
        -------
        List[ScheduledTask]
            List of boot-triggered tasks
        """
        all_tasks = self.list_tasks()
        boot_tasks = []
        
        for task in all_tasks:
            for trigger in task.triggers:
                if "Boot" in trigger or "Logon" in trigger:
                    boot_tasks.append(task)
                    break
        
        _LOGGER.info("Found %d boot/logon tasks", len(boot_tasks))
        return boot_tasks
    
    def get_safe_to_disable(self) -> List[ScheduledTask]:
        """Get tasks that are typically safe to disable.
        
        Returns
        -------
        List[ScheduledTask]
            List of tasks safe to disable
        """
        all_tasks = self.list_tasks()
        safe = []
        
        for task in all_tasks:
            if task.state == TaskState.DISABLED:
                continue
            
            for pattern in self.SAFE_TO_DISABLE:
                if pattern.lower() in task.name.lower():
                    safe.append(task)
                    break
        
        _LOGGER.info("Found %d tasks safe to disable", len(safe))
        return safe
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of scheduled tasks.
        
        Returns
        -------
        Dict
            Summary information
        """
        tasks = self.list_tasks()
        
        by_state: Dict[str, int] = {}
        for task in tasks:
            state = task.state.value
            by_state[state] = by_state.get(state, 0) + 1
        
        return {
            "total_tasks": len(tasks),
            "by_state": by_state,
            "running": sum(1 for t in tasks if t.state == TaskState.RUNNING),
            "disabled": sum(1 for t in tasks if t.state == TaskState.DISABLED),
            "failed": sum(1 for t in tasks if not t.is_healthy),
            "system_tasks": sum(1 for t in tasks if t.is_system_task),
            "user_tasks": sum(1 for t in tasks if not t.is_system_task),
            "boot_tasks": len(self.get_boot_tasks()),
            "safe_to_disable": len(self.get_safe_to_disable())
        }
    
    def optimize_startup_tasks(self) -> Dict[str, bool]:
        """Disable non-essential startup tasks.
        
        Returns
        -------
        Dict[str, bool]
            Dictionary of task name -> disabled status
        """
        _LOGGER.info("Optimizing startup tasks...")
        
        results = {}
        safe_tasks = self.get_safe_to_disable()
        
        for task in safe_tasks:
            # Only disable boot/logon tasks
            is_boot_task = any("Boot" in t or "Logon" in t for t in task.triggers)
            if is_boot_task:
                results[task.name] = self.disable_task(task.path, task.name)
        
        disabled = sum(1 for v in results.values() if v)
        _LOGGER.info("Disabled %d startup tasks", disabled)
        
        return results


__all__ = [
    "TaskState",
    "TaskTriggerType",
    "ScheduledTask",
    "TaskFolder",
    "TaskSchedulerManager",
]
