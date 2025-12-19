# Better11 Testing Guide

Complete guide for testing Better11 modules and features.

## Table of Contents

- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Test Fixtures](#test-fixtures)
- [Integration Testing](#integration-testing)
- [Manual Testing](#manual-testing)
- [CI/CD Integration](#cicd-integration)

---

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking support

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=better11 --cov-report=html

# Run specific test file
pytest tests/test_image_manager.py
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run tests in specific directory
pytest tests/

# Run specific test file
pytest tests/test_image_manager.py

# Run specific test class
pytest tests/test_image_manager.py::TestDismWrapper

# Run specific test method
pytest tests/test_image_manager.py::TestDismWrapper::test_mount_image

# Run tests matching pattern
pytest -k "test_mount"
```

### Test Markers

```bash
# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run Windows-only tests
pytest -m windows_only

# Run tests requiring admin
pytest -m requires_admin

# Combine markers
pytest -m "integration and not slow"
```

### Output Options

```bash
# Verbose output
pytest -v

# Very verbose (show test names)
pytest -vv

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Show slowest tests
pytest --durations=10
```

### Coverage Reporting

```bash
# Basic coverage
pytest --cov=better11

# HTML coverage report
pytest --cov=better11 --cov-report=html

# Terminal coverage report
pytest --cov=better11 --cov-report=term

# XML coverage (for CI)
pytest --cov=better11 --cov-report=xml

# Coverage for specific module
pytest --cov=better11.image_manager tests/test_image_manager.py
```

---

## Test Structure

### Directory Organization

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── test_image_manager.py       # Image management tests
├── test_iso_manager.py         # ISO/USB tests
├── test_update_manager.py      # Windows Update tests
├── test_driver_manager.py      # Driver management tests
├── test_package_manager.py     # Package manager tests
├── test_system_optimizer.py    # Optimizer tests
├── test_file_manager.py        # File management tests
├── test_tui.py                 # TUI tests
└── test_gui.py                 # GUI tests
```

### Test File Structure

```python
"""
Tests for module_name
"""

import pytest
from unittest.mock import Mock, patch


class TestClassName:
    """Tests for ClassName"""

    def test_method_name(self, fixture_name):
        """Test description"""
        # Arrange
        ...

        # Act
        ...

        # Assert
        ...


@pytest.mark.integration
class TestIntegration:
    """Integration tests"""
    ...
```

---

## Writing Tests

### Basic Test Template

```python
import pytest
from unittest.mock import Mock, patch


class TestYourClass:
    """Tests for YourClass"""

    def test_initialization(self):
        """Test object initialization"""
        from better11.your_module import YourClass

        obj = YourClass()

        assert obj is not None
        assert obj.attribute == expected_value

    def test_method_success(self, tmp_path):
        """Test method with successful outcome"""
        from better11.your_module import YourClass

        obj = YourClass()
        result = obj.method(param)

        assert result == expected
        assert obj.state == expected_state

    def test_method_failure(self):
        """Test method with failure case"""
        from better11.your_module import YourClass

        obj = YourClass()

        with pytest.raises(ExpectedException):
            obj.method(invalid_param)

    @patch('better11.your_module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependency"""
        mock_dependency.return_value = Mock(value=123)

        from better11.your_module import YourClass

        obj = YourClass()
        result = obj.method_using_dependency()

        assert result == 123
        mock_dependency.assert_called_once()
```

### Testing Async Code

```python
import pytest


@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    from better11.your_module import async_function

    result = await async_function()

    assert result == expected
```

### Parametrized Tests

```python
import pytest


@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    """Test doubling function with multiple inputs"""
    from better11.your_module import double

    result = double(input)

    assert result == expected
```

---

## Test Fixtures

### Available Fixtures

#### From `conftest.py`

```python
# Temporary directory
def test_with_temp_dir(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("data")
    assert file_path.read_text() == "data"


# Mock WIM file
def test_with_wim(mock_wim_file):
    assert Path(mock_wim_file).exists()


# Mock ISO file
def test_with_iso(mock_iso_file):
    assert Path(mock_iso_file).exists()


# Mock driver directory
def test_with_drivers(mock_driver_dir):
    drivers = list(Path(mock_driver_dir).glob("*.inf"))
    assert len(drivers) == 3


# Successful subprocess
def test_subprocess_success(mock_subprocess_success):
    result = subprocess.run(["cmd"])
    assert result.returncode == 0


# Sample data
def test_with_packages(sample_packages):
    assert len(sample_packages) == 2
    assert sample_packages[0]["name"] == "TestPackage1"


def test_with_drivers(sample_drivers):
    assert len(sample_drivers) == 2
    assert sample_drivers[0]["class_name"] == "Display"
```

### Creating Custom Fixtures

```python
# In conftest.py or test file

@pytest.fixture
def custom_fixture():
    """Custom test fixture"""
    # Setup
    resource = create_resource()

    yield resource

    # Teardown
    resource.cleanup()


@pytest.fixture(scope="module")
def module_fixture():
    """Fixture with module scope (created once per module)"""
    expensive_resource = create_expensive_resource()
    yield expensive_resource
    expensive_resource.cleanup()


@pytest.fixture(scope="session")
def session_fixture():
    """Fixture with session scope (created once per test session)"""
    global_resource = create_global_resource()
    yield global_resource
    global_resource.cleanup()
```

---

## Integration Testing

### Windows-Only Tests

```python
import pytest
import platform


@pytest.mark.windows_only
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
def test_windows_feature():
    """Test Windows-specific feature"""
    from better11.windows_module import WindowsFeature

    feature = WindowsFeature()
    result = feature.do_something()

    assert result is not None
```

### Admin-Required Tests

```python
import pytest
import os


@pytest.mark.requires_admin
@pytest.mark.skipif(not is_admin(), reason="Requires admin privileges")
def test_admin_operation():
    """Test operation requiring admin"""
    from better11.admin_module import AdminOperation

    op = AdminOperation()
    result = op.execute()

    assert result.success


def is_admin():
    """Check if running as admin"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
```

### Integration Test Example

```python
import pytest


@pytest.mark.integration
@pytest.mark.slow
class TestImageManagerIntegration:
    """Integration tests for ImageManager"""

    @pytest.mark.skipif(not has_dism(), reason="DISM not available")
    def test_full_workflow(self, tmp_path, mock_wim_file):
        """Test complete image management workflow"""
        from better11.image_manager import ImageManager

        manager = ImageManager(work_dir=str(tmp_path))

        # Mount
        mount_point = manager.mount_wim(mock_wim_file)
        assert mount_point.is_mounted()

        # Perform operations
        # ...

        # Unmount
        success = manager.dism.unmount_image(mount_point.path, commit=False)
        assert success


def has_dism():
    """Check if DISM is available"""
    import shutil
    return shutil.which("dism.exe") is not None
```

---

## Manual Testing

### TUI Testing

```bash
# Launch TUI
python -m better11 tui

# Test keyboard navigation
# Test all menu options
# Verify output formatting
# Test error handling
```

### GUI Testing

```bash
# Launch GUI
python -m better11 gui

# Test all tabs
# Test file dialogs
# Test button actions
# Test error dialogs
# Test progress bars
```

### Module Testing

```python
# Test image management
python -c "from better11.image_manager import ImageManager; m=ImageManager(); print('OK')"

# Test package manager
python -c "from better11.package_manager import UnifiedPackageManager; m=UnifiedPackageManager(); print(m.get_available_managers())"

# Test system optimizer
python -c "from better11.system_optimizer import SystemOptimizer; o=SystemOptimizer(); print(o.get_system_metrics())"
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest --cov=better11 --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

---

## Best Practices

### Test Guidelines

1. **One assertion per test** (when possible)
2. **Clear test names** describing what is tested
3. **Arrange-Act-Assert** pattern
4. **Mock external dependencies**
5. **Test both success and failure cases**
6. **Use fixtures** for common setup
7. **Clean up resources** in teardown
8. **Avoid test interdependencies**

### Coverage Goals

- **Overall**: 80%+ coverage
- **Critical modules**: 90%+ coverage
- **New code**: 100% coverage

### Performance

- **Unit tests**: < 100ms each
- **Integration tests**: < 5s each
- **Total test suite**: < 2 minutes

---

## Troubleshooting

### Common Issues

**Tests fail on non-Windows systems:**
```python
# Use markers to skip
@pytest.mark.windows_only
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
```

**Import errors:**
```bash
# Ensure Better11 is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# Or
python -m pytest
```

**Mock not working:**
```python
# Ensure correct import path
@patch('better11.module.function')  # Correct
@patch('module.function')  # Wrong
```

**Fixtures not found:**
```python
# Ensure conftest.py in correct location
# Use pytest --fixtures to list available fixtures
```

---

## Example Test Run

```bash
$ pytest -v --cov=better11

======================== test session starts ========================
collected 45 items

tests/test_image_manager.py::TestDismWrapper::test_find_dism PASSED
tests/test_image_manager.py::TestDismWrapper::test_mount_image PASSED
tests/test_image_manager.py::TestImageManager::test_initialization PASSED
tests/test_package_manager.py::TestWinGetManager::test_search PASSED
...

---------- coverage: platform win32, python 3.11.0 -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
better11/__init__.py                  5      0   100%
better11/image_manager.py           250     25    90%
better11/package_manager.py         180     20    89%
...
-----------------------------------------------------
TOTAL                              2150    180    92%

======================== 45 passed in 12.45s ========================
```

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)

---

**Version:** 0.3.0
**Last Updated:** 2024-12-19
