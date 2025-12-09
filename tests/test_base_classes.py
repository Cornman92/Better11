"""Tests for system tool base classes."""
import pytest

from system_tools.base import SystemTool, RegistryTool, ToolMetadata
from system_tools.safety import SafetyError


class MockSystemTool(SystemTool):
    """Mock system tool for testing."""
    
    def get_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="Mock Tool",
            description="A mock tool for testing",
            version="1.0.0",
            requires_admin=False,
            requires_restart=False
        )
    
    def validate_environment(self) -> None:
        pass
    
    def execute(self, *args, **kwargs) -> bool:
        return True


class TestToolMetadata:
    """Test ToolMetadata dataclass."""
    
    def test_metadata_creation(self):
        """Test creating tool metadata."""
        metadata = ToolMetadata(
            name="Test Tool",
            description="A test tool",
            version="1.0.0"
        )
        assert metadata.name == "Test Tool"
        assert metadata.description == "A test tool"
        assert metadata.version == "1.0.0"
        assert metadata.requires_admin is True  # Default
        assert metadata.requires_restart is False  # Default
        assert metadata.category == "general"  # Default


class TestSystemTool:
    """Test SystemTool base class."""
    
    def test_tool_creation(self):
        """Test creating a system tool."""
        tool = MockSystemTool()
        assert tool.config == {}
        assert tool.dry_run is False
    
    def test_tool_with_config(self):
        """Test creating tool with configuration."""
        config = {'always_create_restore_point': False}
        tool = MockSystemTool(config=config)
        assert tool.config == config
    
    def test_tool_dry_run_mode(self):
        """Test tool in dry-run mode."""
        tool = MockSystemTool(dry_run=True)
        assert tool.dry_run is True
        result = tool.run(skip_confirmation=True)
        assert result is True  # Dry run should succeed
    
    def test_tool_run_success(self):
        """Test successful tool execution."""
        tool = MockSystemTool()
        result = tool.run(skip_confirmation=True)
        assert result is True
    
    def test_tool_get_metadata(self):
        """Test getting tool metadata."""
        tool = MockSystemTool()
        metadata = tool.get_metadata()
        assert metadata.name == "Mock Tool"
        assert metadata.version == "1.0.0"


class TestRegistryTool:
    """Test RegistryTool base class."""
    
    def test_registry_tool_is_system_tool(self):
        """Test that RegistryTool inherits from SystemTool."""
        assert issubclass(RegistryTool, SystemTool)


# TODO: Add tests for:
# - Pre-execution checks
# - User confirmation prompts
# - Restore point creation
# - Admin privilege checking
# - Error handling
# - Post-execution cleanup
# - Tool execution with arguments
