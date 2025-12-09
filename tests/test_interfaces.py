"""Tests for common interfaces."""
import pytest

from better11.interfaces import Version, Updatable, Configurable


class TestVersion:
    """Test Version class."""
    
    def test_version_creation(self):
        """Test creating a version."""
        v = Version(1, 2, 3)
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
    
    def test_version_string(self):
        """Test version string representation."""
        v = Version(1, 2, 3)
        assert str(v) == "1.2.3"
    
    def test_version_repr(self):
        """Test version repr."""
        v = Version(1, 2, 3)
        assert repr(v) == "Version(1, 2, 3)"
    
    def test_version_parse(self):
        """Test parsing version string."""
        v = Version.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
    
    def test_version_parse_invalid(self):
        """Test parsing invalid version string."""
        with pytest.raises(ValueError):
            Version.parse("invalid")
        
        with pytest.raises(ValueError):
            Version.parse("1.2")  # Missing patch
    
    def test_version_comparison_eq(self):
        """Test version equality."""
        v1 = Version(1, 2, 3)
        v2 = Version(1, 2, 3)
        v3 = Version(1, 2, 4)
        
        assert v1 == v2
        assert v1 != v3
    
    def test_version_comparison_lt(self):
        """Test version less than."""
        v1 = Version(1, 2, 3)
        v2 = Version(1, 2, 4)
        v3 = Version(2, 0, 0)
        
        assert v1 < v2
        assert v1 < v3
        assert v2 < v3
        assert not (v2 < v1)
    
    def test_version_comparison_le(self):
        """Test version less than or equal."""
        v1 = Version(1, 2, 3)
        v2 = Version(1, 2, 3)
        v3 = Version(1, 2, 4)
        
        assert v1 <= v2
        assert v1 <= v3
        assert not (v3 <= v1)
    
    def test_version_comparison_gt(self):
        """Test version greater than."""
        v1 = Version(1, 2, 4)
        v2 = Version(1, 2, 3)
        
        assert v1 > v2
        assert not (v2 > v1)
    
    def test_version_comparison_ge(self):
        """Test version greater than or equal."""
        v1 = Version(1, 2, 3)
        v2 = Version(1, 2, 3)
        v3 = Version(1, 2, 2)
        
        assert v1 >= v2
        assert v1 >= v3
        assert not (v3 >= v1)


class TestUpdatableInterface:
    """Test Updatable interface."""
    
    def test_updatable_is_abstract(self):
        """Test that Updatable cannot be instantiated."""
        with pytest.raises(TypeError):
            Updatable()  # type: ignore


class TestConfigurableInterface:
    """Test Configurable interface."""
    
    def test_configurable_is_abstract(self):
        """Test that Configurable cannot be instantiated."""
        with pytest.raises(TypeError):
            Configurable()  # type: ignore


# TODO: Add tests for:
# - Monitorable interface
# - Backupable interface
# - Mock implementations of interfaces
