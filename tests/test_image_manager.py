"""
Tests for image_manager module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestDismWrapper:
    """Tests for DismWrapper class"""

    @patch('subprocess.run')
    def test_find_dism(self, mock_run):
        """Test finding DISM executable"""
        from better11.image_manager import DismWrapper

        with patch('os.path.exists', return_value=True):
            wrapper = DismWrapper()
            assert wrapper.dism_path.endswith('dism.exe')

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    def test_mount_image(self, mock_exists, mock_run, tmp_path):
        """Test mounting an image"""
        from better11.image_manager import DismWrapper

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        wrapper = DismWrapper()
        mount_path = str(tmp_path / "mount")

        result = wrapper.mount_image("test.wim", mount_path, index=1)

        assert result.path == mount_path
        assert result.image_path == "test.wim"
        assert result.index == 1
        assert mock_run.called

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    def test_unmount_image(self, mock_exists, mock_run):
        """Test unmounting an image"""
        from better11.image_manager import DismWrapper

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        wrapper = DismWrapper()
        result = wrapper.unmount_image("/mount", commit=True)

        assert result is True
        assert mock_run.called

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    def test_add_driver(self, mock_exists, mock_run, tmp_path):
        """Test adding driver to image"""
        from better11.image_manager import DismWrapper

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        wrapper = DismWrapper()
        result = wrapper.add_driver(str(tmp_path), "C:\\Drivers", recurse=True)

        assert result is True
        assert mock_run.called

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    def test_add_package(self, mock_exists, mock_run, tmp_path):
        """Test adding package to image"""
        from better11.image_manager import DismWrapper

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        wrapper = DismWrapper()
        result = wrapper.add_package(str(tmp_path), "update.msu")

        assert result is True
        assert mock_run.called

    @patch('subprocess.run')
    @patch('os.path.exists', return_value=True)
    def test_enable_feature(self, mock_exists, mock_run, tmp_path):
        """Test enabling Windows feature"""
        from better11.image_manager import DismWrapper

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        wrapper = DismWrapper()
        result = wrapper.enable_feature(str(tmp_path), "NetFx3", all_features=True)

        assert result is True
        assert mock_run.called


class TestImageManager:
    """Tests for ImageManager class"""

    @patch('better11.image_manager.DismWrapper')
    def test_initialization(self, mock_dism, tmp_path):
        """Test ImageManager initialization"""
        from better11.image_manager import ImageManager

        manager = ImageManager(work_dir=str(tmp_path))

        assert manager.work_dir == str(tmp_path)
        assert manager.mount_dir == str(tmp_path / "mounts")

    @patch('better11.image_manager.DismWrapper')
    def test_get_available_mount_path(self, mock_dism, tmp_path):
        """Test getting available mount path"""
        from better11.image_manager import ImageManager

        manager = ImageManager(work_dir=str(tmp_path))
        mount_path = manager.get_available_mount_path()

        assert mount_path.startswith(str(tmp_path))
        assert "mount_" in mount_path

    @patch('better11.image_manager.DismWrapper')
    def test_mount_wim(self, mock_dism_class, tmp_path, mock_wim_file):
        """Test mounting WIM file"""
        from better11.image_manager import ImageManager, MountPoint

        # Mock DISM wrapper
        mock_dism = Mock()
        mock_mount_point = MountPoint(
            path=str(tmp_path / "mount"),
            image_path=mock_wim_file,
            index=1,
            read_only=False,
            mount_status="OK"
        )
        mock_dism.mount_image.return_value = mock_mount_point
        mock_dism_class.return_value = mock_dism

        manager = ImageManager(work_dir=str(tmp_path))
        result = manager.mount_wim(mock_wim_file, index=1)

        assert result.image_path == mock_wim_file
        assert result.index == 1
        mock_dism.mount_image.assert_called_once()

    @patch('better11.image_manager.DismWrapper')
    def test_inject_drivers_to_image(self, mock_dism_class, tmp_path, mock_wim_file, mock_driver_dir):
        """Test injecting drivers to image"""
        from better11.image_manager import ImageManager, MountPoint

        # Mock DISM wrapper
        mock_dism = Mock()
        mock_mount_point = MountPoint(
            path=str(tmp_path / "mount"),
            image_path=mock_wim_file,
            index=1,
            read_only=False,
            mount_status="OK"
        )
        mock_dism.mount_image.return_value = mock_mount_point
        mock_dism.add_driver.return_value = True
        mock_dism.unmount_image.return_value = True
        mock_dism_class.return_value = mock_dism

        manager = ImageManager(work_dir=str(tmp_path))
        result = manager.inject_drivers_to_image(mock_wim_file, mock_driver_dir)

        assert result is True
        mock_dism.add_driver.assert_called_once()
        mock_dism.unmount_image.assert_called_once()


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    @patch('better11.image_manager.ImageManager')
    def test_mount_image_convenience(self, mock_manager_class):
        """Test mount_image convenience function"""
        from better11.image_manager import mount_image, MountPoint

        mock_manager = Mock()
        mock_mount_point = MountPoint(
            path="/mount",
            image_path="test.wim",
            index=1,
            read_only=False,
            mount_status="OK"
        )
        mock_manager.mount_wim.return_value = mock_mount_point
        mock_manager_class.return_value = mock_manager

        result = mount_image("test.wim", index=1)

        assert result.image_path == "test.wim"
        mock_manager.mount_wim.assert_called_once()

    @patch('better11.image_manager.DismWrapper')
    def test_unmount_image_convenience(self, mock_dism_class):
        """Test unmount_image convenience function"""
        from better11.image_manager import unmount_image

        mock_dism = Mock()
        mock_dism.unmount_image.return_value = True
        mock_dism_class.return_value = mock_dism

        result = unmount_image("/mount", commit=True)

        assert result is True
        mock_dism.unmount_image.assert_called_once()


@pytest.mark.integration
class TestImageManagerIntegration:
    """Integration tests for ImageManager"""

    @pytest.mark.skipif(not Path("C:\\Windows\\System32\\dism.exe").exists(),
                       reason="DISM not available")
    @pytest.mark.windows_only
    def test_dism_available(self):
        """Test that DISM is available on Windows"""
        from better11.image_manager import DismWrapper

        wrapper = DismWrapper()
        assert wrapper.dism_path.endswith('dism.exe')
        assert Path(wrapper.dism_path).exists()
