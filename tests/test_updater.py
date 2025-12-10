"""Tests for application update system."""
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from better11.apps.updater import (
    UpdateInfo,
    ApplicationUpdater,
    Better11Updater,
)
from better11.apps.manager import AppManager
from better11.apps.state_store import InstallationStateStore
from better11.interfaces import Version


class TestUpdateInfo:
    """Test UpdateInfo dataclass."""
    
    def test_update_info_creation(self):
        """Test creating update info."""
        current = Version(1, 0, 0)
        available = Version(1, 1, 0)
        
        update = UpdateInfo(
            app_id="test-app",
            current_version=current,
            available_version=available,
            download_url="https://example.com/app.exe",
            release_notes="Bug fixes",
            is_security_update=False
        )
        
        assert update.app_id == "test-app"
        assert update.current_version == current
        assert update.available_version == available
        assert update.available_version > update.current_version
    
    def test_update_info_string(self):
        """Test UpdateInfo string representation."""
        update = UpdateInfo(
            app_id="test-app",
            current_version=Version(1, 0, 0),
            available_version=Version(1, 1, 0),
            download_url="https://example.com/app.exe"
        )
        
        assert "test-app" in str(update)
        assert "1.0.0" in str(update)
        assert "1.1.0" in str(update)


class TestApplicationUpdater:
    """Test ApplicationUpdater class."""
    
    @pytest.fixture
    def mock_app_manager(self, tmp_path, default_catalog_path):
        """Create a mock AppManager."""
        manager = MagicMock(spec=AppManager)
        manager.catalog = MagicMock()
        manager.state_store = InstallationStateStore(tmp_path / "state.json")
        return manager
    
    @pytest.fixture
    def updater(self, mock_app_manager):
        """Create ApplicationUpdater instance."""
        return ApplicationUpdater(mock_app_manager)
    
    def test_updater_creation(self, updater, mock_app_manager):
        """Test creating an updater."""
        assert updater.app_manager == mock_app_manager
        assert updater.catalog_url is None
    
    def test_check_for_updates_no_installed(self, updater):
        """Test checking updates when no apps are installed."""
        updates = updater.check_for_updates()
        assert updates == []
    
    def test_check_for_updates_no_updates(self, updater, mock_app_manager):
        """Test checking updates when apps are up to date."""
        # Mark an app as installed
        mock_app_manager.state_store.mark_installed(
            "demo-app",
            "1.0.0",
            Path("/fake/path"),
            dependencies=[]
        )
        
        # Mock catalog to return same version
        mock_metadata = MagicMock()
        mock_metadata.version = "1.0.0"
        mock_metadata.uri = "https://example.com/app.exe"
        mock_app_manager.catalog.get.return_value = mock_metadata
        
        updates = updater.check_for_updates()
        assert len(updates) == 0
    
    def test_check_for_updates_available(self, updater, mock_app_manager):
        """Test checking updates when updates are available."""
        # Mark an app as installed with old version
        mock_app_manager.state_store.mark_installed(
            "demo-app",
            "1.0.0",
            Path("/fake/path"),
            dependencies=[]
        )
        
        # Mock catalog to return newer version
        mock_metadata = MagicMock()
        mock_metadata.version = "1.1.0"
        mock_metadata.uri = "https://example.com/app.exe"
        mock_metadata.release_notes = "Bug fixes"
        mock_metadata.release_date = None
        mock_metadata.is_security_update = False
        mock_metadata.is_mandatory = False
        mock_metadata.size_mb = 10.0
        mock_app_manager.catalog.get.return_value = mock_metadata
        
        updates = updater.check_for_updates()
        assert len(updates) == 1
        assert updates[0].app_id == "demo-app"
        assert updates[0].current_version == Version(1, 0, 0)
        assert updates[0].available_version == Version(1, 1, 0)
    
    def test_install_update(self, updater, mock_app_manager):
        """Test installing an update."""
        update = UpdateInfo(
            app_id="demo-app",
            current_version=Version(1, 0, 0),
            available_version=Version(1, 1, 0),
            download_url="https://example.com/app.exe"
        )
        
        # Mock successful installation
        mock_status = MagicMock()
        mock_status.installed = True
        mock_status.version = "1.1.0"
        mock_result = MagicMock()
        mock_app_manager.install.return_value = (mock_status, mock_result)
        
        success = updater.install_update(update)
        assert success is True
        mock_app_manager.install.assert_called_once_with("demo-app")
    
    def test_install_update_failure(self, updater, mock_app_manager):
        """Test update installation failure."""
        update = UpdateInfo(
            app_id="demo-app",
            current_version=Version(1, 0, 0),
            available_version=Version(1, 1, 0),
            download_url="https://example.com/app.exe"
        )
        
        # Mock failed installation
        mock_app_manager.install.side_effect = Exception("Install failed")
        
        success = updater.install_update(update)
        assert success is False
    
    def test_install_all_updates(self, updater, mock_app_manager):
        """Test installing all available updates."""
        updates = [
            UpdateInfo(
                app_id="app1",
                current_version=Version(1, 0, 0),
                available_version=Version(1, 1, 0),
                download_url="https://example.com/app1.exe"
            ),
            UpdateInfo(
                app_id="app2",
                current_version=Version(2, 0, 0),
                available_version=Version(2, 1, 0),
                download_url="https://example.com/app2.exe"
            ),
        ]
        
        # Mock successful installations
        mock_status = MagicMock()
        mock_status.installed = True
        mock_status.version = "1.1.0"
        mock_app_manager.install.return_value = (mock_status, MagicMock())
        
        results = updater.install_all_updates(updates)
        assert len(results) == 2
        assert all(results)
        assert mock_app_manager.install.call_count == 2


class TestBetter11Updater:
    """Test Better11Updater class."""
    
    @pytest.fixture
    def updater(self):
        """Create Better11Updater instance."""
        return Better11Updater()
    
    def test_get_current_version(self, updater):
        """Test getting current Better11 version."""
        version = updater.get_current_version()
        assert isinstance(version, Version)
        assert version.major >= 0
    
    @patch('better11.apps.updater.requests.get')
    def test_check_for_updates_no_update(self, mock_get, updater):
        """Test checking for updates when up to date."""
        # Mock GitHub API response with same version
        current = updater.get_current_version()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'tag_name': f'v{current}',
            'assets': [],
            'body': 'Release notes',
            'published_at': '2025-01-01T00:00:00Z'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        update = updater.check_for_updates()
        assert update is None
    
    @patch('better11.apps.updater.requests.get')
    def test_check_for_updates_available(self, mock_get, updater):
        """Test checking for updates when update available."""
        current = updater.get_current_version()
        newer = Version(current.major, current.minor + 1, current.patch)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'tag_name': f'v{newer}',
            'assets': [{'browser_download_url': 'https://github.com/.../better11.zip'}],
            'body': 'New features',
            'published_at': '2025-12-10T00:00:00Z'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        update = updater.check_for_updates()
        assert update is not None
        assert update.app_id == "better11"
        assert update.available_version == newer
    
    @patch('better11.apps.updater.requests.get')
    def test_check_for_updates_error(self, mock_get, updater):
        """Test handling update check errors."""
        mock_get.side_effect = Exception("Network error")
        
        update = updater.check_for_updates()
        assert update is None
    
    @patch('better11.apps.updater.requests.get')
    def test_download_update(self, mock_get, updater, tmp_path):
        """Test downloading update."""
        # Mock update check
        current = updater.get_current_version()
        newer = Version(current.major, current.minor + 1, current.patch)
        
        mock_check_response = MagicMock()
        mock_check_response.json.return_value = {
            'tag_name': f'v{newer}',
            'assets': [{'browser_download_url': 'https://github.com/.../better11.zip'}],
            'body': 'Update',
            'published_at': '2025-12-10T00:00:00Z'
        }
        mock_check_response.raise_for_status.return_value = None
        
        # Mock download response
        mock_download_response = MagicMock()
        mock_download_response.iter_content.return_value = [b'zip', b'content']
        mock_download_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [mock_check_response, mock_download_response]
        
        download_path = updater.download_update(newer)
        assert download_path.exists()
        assert download_path.name.startswith("better11-")
    
    def test_install_update_not_implemented(self, updater, tmp_path):
        """Test that install_update is not fully implemented."""
        package_path = tmp_path / "update.zip"
        package_path.write_bytes(b"test")
        
        # Should return False (not fully implemented)
        result = updater.install_update(package_path)
        assert result is False
    
    def test_rollback_not_implemented(self, updater):
        """Test that rollback is not implemented."""
        result = updater.rollback_update()
        assert result is False
