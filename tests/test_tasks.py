"""Tests for Scheduled Tasks management."""
import platform
from datetime import datetime
from unittest.mock import patch

import pytest

from system_tools.tasks import (
    TaskState,
    TaskTriggerType,
    ScheduledTask,
    TaskFolder,
    TaskSchedulerManager,
)


class TestTaskState:
    """Test TaskState enum."""

    def test_task_state_values(self):
        """Test task state enum values."""
        assert TaskState.READY.value == "Ready"
        assert TaskState.RUNNING.value == "Running"
        assert TaskState.DISABLED.value == "Disabled"
        assert TaskState.QUEUED.value == "Queued"
        assert TaskState.UNKNOWN.value == "Unknown"


class TestTaskTriggerType:
    """Test TaskTriggerType enum."""

    def test_trigger_type_values(self):
        """Test trigger type enum values."""
        assert TaskTriggerType.BOOT.value == "Boot"
        assert TaskTriggerType.LOGON.value == "Logon"
        assert TaskTriggerType.TIME.value == "Time"


class TestScheduledTask:
    """Test ScheduledTask dataclass."""

    def test_scheduled_task_creation(self):
        """Test creating a ScheduledTask."""
        task = ScheduledTask(
            name="TestTask",
            path="\\Test",
            state=TaskState.READY,
            description="Test description",
            author="Test Author",
            last_run=datetime.now(),
            next_run=datetime.now(),
            last_result=0,
            triggers=["LogonTrigger"],
            run_as_user="SYSTEM",
            run_level="Highest"
        )

        assert task.name == "TestTask"
        assert task.path == "\\Test"
        assert task.state == TaskState.READY

    def test_full_path(self):
        """Test full_path property."""
        task = ScheduledTask(
            name="TestTask",
            path="\\Microsoft\\Windows",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )

        assert task.full_path == "\\Microsoft\\Windows\\TestTask"

    def test_is_system_task(self):
        """Test is_system_task property."""
        system_task = ScheduledTask(
            name="Test",
            path="\\Microsoft\\Windows",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )
        user_task = ScheduledTask(
            name="Test",
            path="\\MyTasks",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )

        assert system_task.is_system_task is True
        assert user_task.is_system_task is False

    def test_is_healthy(self):
        """Test is_healthy property."""
        healthy_task = ScheduledTask(
            name="Test",
            path="\\",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )
        unhealthy_task = ScheduledTask(
            name="Test",
            path="\\",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=1,
            triggers=[],
            run_as_user="",
            run_level=""
        )

        assert healthy_task.is_healthy is True
        assert unhealthy_task.is_healthy is False

    def test_to_dict(self):
        """Test to_dict method."""
        task = ScheduledTask(
            name="Test",
            path="\\Microsoft\\Windows",
            state=TaskState.READY,
            description="Test",
            author="Author",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=["BootTrigger"],
            run_as_user="SYSTEM",
            run_level="Highest"
        )

        d = task.to_dict()
        assert d["name"] == "Test"
        assert d["state"] == "Ready"
        assert d["is_system_task"] is True
        assert d["is_healthy"] is True


class TestTaskSchedulerManager:
    """Test TaskSchedulerManager class."""

    def test_manager_creation(self):
        """Test creating a task scheduler manager."""
        manager = TaskSchedulerManager()
        metadata = manager.get_metadata()

        assert metadata.name == "Task Scheduler Manager"
        assert metadata.version == "0.3.0"
        assert metadata.requires_admin is True
        assert metadata.category == "system"

    def test_manager_dry_run(self):
        """Test manager with dry-run mode."""
        manager = TaskSchedulerManager(dry_run=True)
        assert manager.dry_run is True

    @patch('system_tools.tasks.platform.system')
    def test_list_tasks_non_windows(self, mock_system):
        """Test listing tasks on non-Windows."""
        mock_system.return_value = "Linux"

        manager = TaskSchedulerManager()
        tasks = manager.list_tasks()

        assert tasks == []

    def test_enable_task_dry_run(self):
        """Test enabling task in dry-run mode."""
        manager = TaskSchedulerManager(dry_run=True)
        result = manager.enable_task("\\Test", "TestTask")
        assert result is True

    def test_disable_task_dry_run(self):
        """Test disabling task in dry-run mode."""
        manager = TaskSchedulerManager(dry_run=True)
        result = manager.disable_task("\\Test", "TestTask")
        assert result is True

    def test_disable_critical_task_refused(self):
        """Test that critical tasks cannot be disabled."""
        manager = TaskSchedulerManager()
        result = manager.disable_task("\\Microsoft\\Windows", "Windows Defender Cache")
        assert result is False

    def test_run_task_dry_run(self):
        """Test running task in dry-run mode."""
        manager = TaskSchedulerManager(dry_run=True)
        result = manager.run_task("\\Test", "TestTask")
        assert result is True

    def test_end_task_dry_run(self):
        """Test ending task in dry-run mode."""
        manager = TaskSchedulerManager(dry_run=True)
        result = manager.end_task("\\Test", "TestTask")
        assert result is True

    def test_delete_task_dry_run(self):
        """Test deleting task in dry-run mode."""
        manager = TaskSchedulerManager(dry_run=True)
        
        with patch.object(manager, 'get_task', return_value=ScheduledTask(
            name="UserTask",
            path="\\MyTasks",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )):
            result = manager.delete_task("\\MyTasks", "UserTask")
        
        assert result is True

    def test_delete_system_task_refused(self):
        """Test that system tasks cannot be deleted."""
        manager = TaskSchedulerManager()
        
        with patch.object(manager, 'get_task', return_value=ScheduledTask(
            name="SystemTask",
            path="\\Microsoft\\Windows",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )):
            result = manager.delete_task("\\Microsoft\\Windows", "SystemTask")
        
        assert result is False

    def test_get_failed_tasks(self):
        """Test getting failed tasks."""
        healthy = ScheduledTask(
            name="Healthy",
            path="\\",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )
        failed = ScheduledTask(
            name="Failed",
            path="\\",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=1,
            triggers=[],
            run_as_user="",
            run_level=""
        )

        manager = TaskSchedulerManager()
        with patch.object(manager, 'list_tasks', return_value=[healthy, failed]):
            failed_tasks = manager.get_failed_tasks()

        assert len(failed_tasks) == 1
        assert failed_tasks[0].name == "Failed"

    def test_get_running_tasks(self):
        """Test getting running tasks."""
        ready = ScheduledTask(
            name="Ready",
            path="\\",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )
        running = ScheduledTask(
            name="Running",
            path="\\",
            state=TaskState.RUNNING,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=[],
            run_as_user="",
            run_level=""
        )

        manager = TaskSchedulerManager()
        with patch.object(manager, 'list_tasks', return_value=[ready, running]):
            running_tasks = manager.get_running_tasks()

        assert len(running_tasks) == 1
        assert running_tasks[0].name == "Running"

    def test_get_boot_tasks(self):
        """Test getting boot/logon tasks."""
        boot_task = ScheduledTask(
            name="BootTask",
            path="\\",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=["BootTrigger"],
            run_as_user="",
            run_level=""
        )
        time_task = ScheduledTask(
            name="TimeTask",
            path="\\",
            state=TaskState.READY,
            description="",
            author="",
            last_run=None,
            next_run=None,
            last_result=0,
            triggers=["TimeTrigger"],
            run_as_user="",
            run_level=""
        )

        manager = TaskSchedulerManager()
        with patch.object(manager, 'list_tasks', return_value=[boot_task, time_task]):
            boot_tasks = manager.get_boot_tasks()

        assert len(boot_tasks) == 1
        assert boot_tasks[0].name == "BootTask"

    def test_get_task_summary(self):
        """Test getting task summary."""
        manager = TaskSchedulerManager()
        
        with patch.object(manager, 'list_tasks', return_value=[]):
            with patch.object(manager, 'get_boot_tasks', return_value=[]):
                with patch.object(manager, 'get_safe_to_disable', return_value=[]):
                    summary = manager.get_task_summary()

        assert "total_tasks" in summary
        assert "by_state" in summary
        assert "running" in summary
        assert "failed" in summary

    def test_safe_to_disable_list(self):
        """Test SAFE_TO_DISABLE list."""
        assert "Adobe Acrobat Update Task" in TaskSchedulerManager.SAFE_TO_DISABLE
        assert "OneDrive Standalone Update Task" in TaskSchedulerManager.SAFE_TO_DISABLE

    def test_critical_tasks_list(self):
        """Test CRITICAL_TASKS list."""
        assert "Windows Defender" in TaskSchedulerManager.CRITICAL_TASKS
        assert "WindowsUpdate" in TaskSchedulerManager.CRITICAL_TASKS

    def test_validate_environment(self):
        """Test environment validation."""
        manager = TaskSchedulerManager()
        # Should not raise
        manager.validate_environment()


# Windows-specific tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestTaskSchedulerManagerWindows:
    """Tests that require Windows platform."""

    def test_list_tasks_on_windows(self):
        """Test listing tasks on Windows."""
        manager = TaskSchedulerManager()
        tasks = manager.list_tasks()

        # Should return a list
        assert isinstance(tasks, list)

    def test_get_task_summary_on_windows(self):
        """Test getting task summary on Windows."""
        manager = TaskSchedulerManager()
        summary = manager.get_task_summary()

        assert isinstance(summary, dict)
        assert summary["total_tasks"] >= 0
