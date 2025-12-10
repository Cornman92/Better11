"""Tests for Windows Update management."""
import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from system_tools.updates import (
    UpdateType,
    UpdateStatus,
    WindowsUpdate,
    WindowsUpdateManager,
)


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="Windows Update management only works on Windows"
)
class TestWindowsUpdateManager:
    """Test WindowsUpdateManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create WindowsUpdateManager instance."""
        return WindowsUpdateManager(dry_run=True)
    
    def test_manager_creation(self, manager):
        """Test creating update manager."""
        assert manager.dry_run is True
        metadata = manager.get_metadata()
        assert metadata.name == "Windows Update Manager"
        assert metadata.requires_admin is True
    
    @patch('system_tools.updates.subprocess.run')
    def test_check_for_updates(self, mock_run, manager):
        """Test checking for updates."""
        # Mock PowerShell output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([{
            "Id": "update-123",
            "Title": "Security Update",
            "Description": "Important security update",
            "UpdateType": "SECURITY",
            "Size": 50.0,
            "IsMandatory": True,
            "RequiresReboot": False,
            "KBArticle": "KB123456"
        }])
        mock_run.return_value = mock_result
        
        updates = manager.check_for_updates()
        assert len(updates) == 1
        assert updates[0].title == "Security Update"
        assert updates[0].update_type == UpdateType.SECURITY
    
    @patch('system_tools.updates.subprocess.run')
    def test_check_for_updates_no_updates(self, mock_run, manager):
        """Test checking when no updates available."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        updates = manager.check_for_updates()
        assert len(updates) == 0
    
    @patch('system_tools.updates.subprocess.run')
    def test_pause_updates(self, mock_run, manager):
        """Test pausing updates."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        success = manager.pause_updates(days=7)
        assert success is True
    
    def test_pause_updates_invalid_days(self, manager):
        """Test pausing updates with invalid days."""
        with pytest.raises(ValueError, match="Cannot pause updates for more than 35 days"):
            manager.pause_updates(days=40)
    
    @patch('system_tools.updates.subprocess.run')
    def test_resume_updates(self, mock_run, manager):
        """Test resuming updates."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        success = manager.resume_updates()
        assert success is True
    
    @patch('system_tools.updates.subprocess.run')
    def test_set_active_hours(self, mock_run, manager):
        """Test setting active hours."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        success = manager.set_active_hours(start_hour=9, end_hour=17)
        assert success is True
    
    def test_set_active_hours_invalid(self, manager):
        """Test setting invalid active hours."""
        with pytest.raises(ValueError, match="Hours must be between 0 and 23"):
            manager.set_active_hours(start_hour=25, end_hour=10)
    
    @patch('system_tools.updates.subprocess.run')
    def test_get_update_history(self, mock_run, manager):
        """Test getting update history."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps([{
            "Id": "update-123",
            "Title": "Installed Update",
            "Description": "Update description",
            "UpdateType": "OTHER",
            "Size": 0,
            "InstallDate": "2025-12-01T00:00:00Z",
            "ResultCode": 2,
            "KBArticle": "KB123456"
        }])
        mock_run.return_value = mock_result
        
        history = manager.get_update_history(days=30)
        assert len(history) == 1
        assert history[0].status == UpdateStatus.INSTALLED
    
    @patch('system_tools.updates.subprocess.run')
    def test_uninstall_update(self, mock_run, manager):
        """Test uninstalling an update."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        success = manager.uninstall_update("KB123456")
        assert success is True


class TestWindowsUpdate:
    """Test WindowsUpdate dataclass."""
    
    def test_update_creation(self):
        """Test creating a Windows update."""
        update = WindowsUpdate(
            id="update-123",
            title="Test Update",
            description="Test description",
            update_type=UpdateType.SECURITY,
            size_mb=50.0,
            status=UpdateStatus.AVAILABLE,
            kb_article="KB123456"
        )
        
        assert update.id == "update-123"
        assert update.title == "Test Update"
        assert update.update_type == UpdateType.SECURITY
        assert update.status == UpdateStatus.AVAILABLE
