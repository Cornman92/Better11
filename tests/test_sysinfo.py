"""Tests for System Information gathering."""
import platform
from datetime import datetime
from unittest.mock import patch

import pytest

from system_tools.sysinfo import (
    CPUInfo,
    MemoryInfo,
    GPUInfo,
    StorageInfo,
    NetworkAdapterInfo,
    WindowsInfo,
    BIOSInfo,
    SystemSummary,
    SystemInfoManager,
)


class TestCPUInfo:
    """Test CPUInfo dataclass."""

    def test_cpu_info_creation(self):
        """Test creating a CPUInfo."""
        cpu = CPUInfo(
            name="Intel Core i7-12700K",
            manufacturer="Intel",
            cores=12,
            logical_processors=20,
            max_clock_mhz=5000,
            architecture="AMD64",
            current_usage=25.5
        )

        assert cpu.name == "Intel Core i7-12700K"
        assert cpu.cores == 12
        assert cpu.logical_processors == 20
        assert cpu.current_usage == 25.5

    def test_to_dict(self):
        """Test to_dict method."""
        cpu = CPUInfo(
            name="Test CPU",
            manufacturer="Test",
            cores=4,
            logical_processors=8,
            max_clock_mhz=3500,
            architecture="x64",
            current_usage=10.0
        )

        d = cpu.to_dict()
        assert d["name"] == "Test CPU"
        assert d["cores"] == 4


class TestMemoryInfo:
    """Test MemoryInfo dataclass."""

    def test_memory_info_creation(self):
        """Test creating a MemoryInfo."""
        mem = MemoryInfo(
            total_bytes=32 * 1024 ** 3,  # 32 GB
            available_bytes=16 * 1024 ** 3,  # 16 GB
            used_bytes=16 * 1024 ** 3,
            usage_percent=50.0,
            slots_used=2,
            slots_total=4,
            speed_mhz=3200,
            type_name="DDR4"
        )

        assert mem.total_gb == 32.0
        assert mem.available_gb == 16.0
        assert mem.usage_percent == 50.0

    def test_to_dict(self):
        """Test to_dict method."""
        mem = MemoryInfo(
            total_bytes=16 * 1024 ** 3,
            available_bytes=8 * 1024 ** 3,
            used_bytes=8 * 1024 ** 3,
            usage_percent=50.0,
            slots_used=2,
            slots_total=4,
            speed_mhz=3200,
            type_name="DDR4"
        )

        d = mem.to_dict()
        assert d["total_gb"] == 16.0
        assert d["type"] == "DDR4"


class TestGPUInfo:
    """Test GPUInfo dataclass."""

    def test_gpu_info_creation(self):
        """Test creating a GPUInfo."""
        gpu = GPUInfo(
            name="NVIDIA GeForce RTX 4090",
            manufacturer="NVIDIA",
            driver_version="545.84",
            driver_date=datetime(2023, 11, 15),
            video_memory_mb=24576,
            current_resolution="2560x1440"
        )

        assert gpu.name == "NVIDIA GeForce RTX 4090"
        assert gpu.video_memory_mb == 24576

    def test_to_dict(self):
        """Test to_dict method."""
        gpu = GPUInfo(
            name="Test GPU",
            manufacturer="Test",
            driver_version="1.0",
            driver_date=None,
            video_memory_mb=8192,
            current_resolution="1920x1080"
        )

        d = gpu.to_dict()
        assert d["name"] == "Test GPU"
        assert d["video_memory_mb"] == 8192


class TestStorageInfo:
    """Test StorageInfo dataclass."""

    def test_storage_info_creation(self):
        """Test creating a StorageInfo."""
        storage = StorageInfo(
            name="\\\\.\\PHYSICALDRIVE0",
            model="Samsung 980 Pro",
            media_type="NVMe",
            size_bytes=1000 * 1024 ** 3,  # 1 TB
            interface_type="NVMe",
            status="OK",
            partitions=3
        )

        assert storage.model == "Samsung 980 Pro"
        assert storage.media_type == "NVMe"
        assert round(storage.size_gb, 0) == 1000

    def test_to_dict(self):
        """Test to_dict method."""
        storage = StorageInfo(
            name="Drive0",
            model="Test Drive",
            media_type="SSD",
            size_bytes=500 * 1024 ** 3,
            interface_type="SATA",
            status="OK",
            partitions=2
        )

        d = storage.to_dict()
        assert d["model"] == "Test Drive"
        assert d["media_type"] == "SSD"


class TestWindowsInfo:
    """Test WindowsInfo dataclass."""

    def test_windows_info_creation(self):
        """Test creating a WindowsInfo."""
        win = WindowsInfo(
            version="10.0.22631",
            build="22631",
            edition="Windows 11 Pro",
            product_id="00000-00000-00000-00000",
            install_date=datetime(2023, 1, 15),
            last_boot=datetime(2024, 1, 10),
            uptime_hours=24.5,
            registered_owner="User",
            system_root="C:\\Windows",
            windows_directory="C:\\Windows"
        )

        assert win.edition == "Windows 11 Pro"
        assert win.uptime_hours == 24.5

    def test_to_dict(self):
        """Test to_dict method."""
        win = WindowsInfo(
            version="10.0.22631",
            build="22631",
            edition="Windows 11 Pro",
            product_id="",
            install_date=None,
            last_boot=None,
            uptime_hours=10.0,
            registered_owner="",
            system_root="C:\\Windows",
            windows_directory="C:\\Windows"
        )

        d = win.to_dict()
        assert d["edition"] == "Windows 11 Pro"
        assert d["uptime_hours"] == 10.0


class TestBIOSInfo:
    """Test BIOSInfo dataclass."""

    def test_bios_info_creation(self):
        """Test creating a BIOSInfo."""
        bios = BIOSInfo(
            manufacturer="American Megatrends",
            version="F15",
            release_date=datetime(2023, 6, 1),
            serial_number="ABC123",
            is_uefi=True
        )

        assert bios.manufacturer == "American Megatrends"
        assert bios.is_uefi is True

    def test_to_dict(self):
        """Test to_dict method."""
        bios = BIOSInfo(
            manufacturer="Test",
            version="1.0",
            release_date=None,
            serial_number="",
            is_uefi=True
        )

        d = bios.to_dict()
        assert d["manufacturer"] == "Test"
        assert d["is_uefi"] is True


class TestSystemInfoManager:
    """Test SystemInfoManager class."""

    def test_manager_creation(self):
        """Test creating a system info manager."""
        manager = SystemInfoManager()
        metadata = manager.get_metadata()

        assert metadata.name == "System Information"
        assert metadata.version == "0.3.0"
        assert metadata.requires_admin is False
        assert metadata.category == "information"

    def test_manager_dry_run(self):
        """Test manager with dry-run mode."""
        manager = SystemInfoManager(dry_run=True)
        assert manager.dry_run is True

    def test_get_windows_info(self):
        """Test getting Windows info."""
        manager = SystemInfoManager()
        win_info = manager.get_windows_info()

        assert isinstance(win_info, WindowsInfo)
        assert win_info.version is not None

    def test_get_cpu_info(self):
        """Test getting CPU info."""
        manager = SystemInfoManager()
        cpu_info = manager.get_cpu_info()

        assert isinstance(cpu_info, CPUInfo)
        assert cpu_info.cores >= 1

    def test_get_memory_info(self):
        """Test getting memory info."""
        manager = SystemInfoManager()
        mem_info = manager.get_memory_info()

        assert isinstance(mem_info, MemoryInfo)

    def test_get_gpu_info(self):
        """Test getting GPU info."""
        manager = SystemInfoManager()
        gpus = manager.get_gpu_info()

        assert isinstance(gpus, list)

    def test_get_storage_info(self):
        """Test getting storage info."""
        manager = SystemInfoManager()
        storage = manager.get_storage_info()

        assert isinstance(storage, list)

    def test_get_network_info(self):
        """Test getting network info."""
        manager = SystemInfoManager()
        network = manager.get_network_info()

        assert isinstance(network, list)

    def test_get_bios_info(self):
        """Test getting BIOS info."""
        manager = SystemInfoManager()
        bios = manager.get_bios_info()

        assert isinstance(bios, BIOSInfo)

    def test_get_quick_summary(self):
        """Test getting quick summary."""
        manager = SystemInfoManager()
        
        with patch.object(manager, 'get_system_summary', return_value=None):
            summary = manager.get_quick_summary()
        
        assert summary == {}

    def test_validate_environment(self):
        """Test environment validation."""
        manager = SystemInfoManager()
        # Should not raise
        manager.validate_environment()


# Windows-specific tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestSystemInfoManagerWindows:
    """Tests that require Windows platform."""

    def test_get_system_summary_on_windows(self):
        """Test getting system summary on Windows."""
        manager = SystemInfoManager()
        summary = manager.get_system_summary()

        if summary:
            assert isinstance(summary, SystemSummary)
            assert summary.computer_name is not None

    def test_get_quick_summary_on_windows(self):
        """Test getting quick summary on Windows."""
        manager = SystemInfoManager()
        summary = manager.get_quick_summary()

        if summary:
            assert "Computer" in summary or "CPU" in summary

    def test_get_gpu_info_on_windows(self):
        """Test getting GPU info on Windows."""
        manager = SystemInfoManager()
        gpus = manager.get_gpu_info()

        # Most Windows systems have at least one GPU
        # But don't fail if there's none (headless servers)
        assert isinstance(gpus, list)
