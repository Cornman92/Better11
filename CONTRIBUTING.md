# Contributing to Better11

Thank you for your interest in contributing to Better11! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Security](#security)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Windows 11 (for testing system tools)
- Git for version control
- A code editor (VS Code, PyCharm, etc.)

### First-Time Contributors

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/better11.git`
3. Add upstream remote: `git remote add upstream https://github.com/original-owner/better11.git`
4. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/your-username/better11.git
cd better11
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements-dev.txt  # If available
pip install pytest pytest-cov black flake8 mypy
```

### 4. Verify Setup

```bash
# Run tests
python -m pytest tests/

# List available apps (should work)
python -m better11.cli list
```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical fixes for production

### Making Changes

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/add-awesome-feature
   ```

3. **Make your changes**:
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**:
   ```bash
   # Run all tests
   python -m pytest tests/
   
   # Run specific test file
   python -m pytest tests/test_manager.py
   
   # Run with coverage
   python -m pytest --cov=better11 --cov=system_tools tests/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add awesome new feature"
   ```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: Maximum 120 characters (instead of 79)
- **Imports**: Group imports (standard library, third-party, local)
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Use Google-style docstrings

### Code Formatting

We use `black` for automatic code formatting:

```bash
# Format all files
black better11/ system_tools/ tests/

# Check formatting without making changes
black --check better11/ system_tools/ tests/
```

### Linting

Use `flake8` for linting:

```bash
flake8 better11/ system_tools/ tests/ --max-line-length=120
```

### Type Checking

Use `mypy` for type checking:

```bash
mypy better11/ system_tools/ --ignore-missing-imports
```

### Example Code Style

```python
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

def download_application(
    app_id: str,
    destination: Path,
    verify_signature: bool = True
) -> Path:
    """
    Download an application installer to the specified destination.

    Args:
        app_id: Unique identifier for the application
        destination: Path where the installer will be saved
        verify_signature: Whether to verify HMAC signature

    Returns:
        Path to the downloaded installer

    Raises:
        DownloadError: If download fails
        VerificationError: If signature verification fails

    Example:
        >>> path = download_application("demo-app", Path("~/downloads"))
        >>> print(f"Downloaded to {path}")
    """
    # Implementation here
    pass
```

## Testing

### Test Organization

```
tests/
├── test_application_manager.py    # Application manager tests
├── test_manager.py                # Main manager tests
├── test_system_tools.py           # System tools tests
└── fixtures/                       # Test fixtures and data
```

### Writing Tests

Use `pytest` for testing:

```python
import pytest
from pathlib import Path
from better11.apps.manager import AppManager

def test_list_available_apps():
    """Test listing available applications."""
    catalog_path = Path("better11/apps/catalog.json")
    manager = AppManager(catalog_path)
    apps = manager.list_available()
    assert len(apps) > 0
    assert all(hasattr(app, 'app_id') for app in apps)

def test_download_invalid_app():
    """Test downloading non-existent application."""
    catalog_path = Path("better11/apps/catalog.json")
    manager = AppManager(catalog_path)
    with pytest.raises(KeyError):
        manager.download("non-existent-app")
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_manager.py

# Run specific test
pytest tests/test_manager.py::test_list_available_apps

# Run with coverage report
pytest --cov=better11 --cov=system_tools --cov-report=html

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"
```

### Test Coverage

Aim for at least 80% code coverage for new features:

```bash
pytest --cov=better11 --cov=system_tools --cov-report=term-missing
```

## Documentation

### Docstrings

All public functions, classes, and modules must have docstrings:

```python
def verify_signature(file_path: Path, signature: str, key: str) -> None:
    """
    Verify HMAC-SHA256 signature of a file.

    This function computes the HMAC-SHA256 of the file contents and
    compares it with the provided signature using constant-time comparison.

    Args:
        file_path: Path to the file to verify
        signature: Base64-encoded HMAC signature
        key: Base64-encoded HMAC key

    Raises:
        VerificationError: If signature verification fails

    Example:
        >>> verify_signature(
        ...     Path("installer.msi"),
        ...     "base64_signature",
        ...     "base64_key"
        ... )
    """
    pass
```

### Updating Documentation

When adding or modifying features, update:

1. **README.md** - If adding major features
2. **USER_GUIDE.md** - For user-facing changes
3. **API_REFERENCE.md** - For API changes
4. **CHANGELOG.md** - For all changes

## Submitting Changes

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(apps): add support for MSIX installers

Implement MSIX installer support with signature verification
and dependency resolution.

Closes #123
```

```
fix(system_tools): correct registry backup path on Windows 11

The backup path was incorrectly using forward slashes on Windows.
Changed to use os.path.join for cross-platform compatibility.

Fixes #456
```

### Pull Request Process

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**:
   - Go to the repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template

4. **PR Checklist**:
   - [ ] Code follows style guidelines
   - [ ] All tests pass
   - [ ] New tests added for new features
   - [ ] Documentation updated
   - [ ] Commit messages follow conventions
   - [ ] No merge conflicts

5. **Review Process**:
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Once approved, maintainers will merge

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code formatted with black
- [ ] Type hints added
- [ ] Changelog updated
```

## Security

### Reporting Security Issues

**Do not report security vulnerabilities through public GitHub issues.**

Please report security vulnerabilities to: security@better11.example.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

When contributing:

1. **Input Validation**: Always validate user input
2. **Path Traversal**: Use `Path.resolve()` to prevent directory traversal
3. **Command Injection**: Use `subprocess` with lists, not shell=True
4. **Sensitive Data**: Never commit secrets, keys, or credentials
5. **Dependencies**: Keep dependencies updated and secure

## Development Tips

### Testing System Tools

System tools require Windows and administrator privileges:

```python
# Use mocking for cross-platform development
from unittest.mock import patch, MagicMock

@patch('system_tools.safety.subprocess.run')
def test_create_restore_point(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    create_restore_point("Test")
    assert mock_run.called
```

### Virtual Machine Testing

For testing system modifications:

1. Use Windows 11 VM (VirtualBox, VMware, Hyper-V)
2. Create VM snapshots before testing
3. Test restore point creation
4. Verify rollback functionality

### Debugging

```python
# Add logging to your code
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting operation")
logger.info("Processing application: %s", app_id)
logger.warning("Missing optional field: %s", field_name)
logger.error("Operation failed: %s", error)
```

## Getting Help

- **Documentation**: Check [USER_GUIDE.md](USER_GUIDE.md) and [API_REFERENCE.md](API_REFERENCE.md)
- **Issues**: Search existing [issues](https://github.com/owner/better11/issues)
- **Discussions**: Ask in [GitHub Discussions](https://github.com/owner/better11/discussions)
- **Chat**: Join our community chat (if available)

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- CHANGELOG.md
- Release notes

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the `question` label
- Start a discussion
- Contact the maintainers

Thank you for contributing to Better11! 🚀
