# Better11 Documentation Guide

Welcome to Better11! This guide helps you navigate the documentation and find what you need.

## 📚 Documentation Structure

### Getting Started

Start here if you're new to Better11:

1. **[README.md](README.md)** - Project overview, features, and quick start
   - What Better11 does
   - Key features summary
   - Quick installation and usage
   - Project structure overview

2. **[INSTALL.md](INSTALL.md)** - Complete installation guide
   - System requirements
   - Installation methods (Git, ZIP, Development)
   - Post-installation setup
   - Troubleshooting common issues
   - Uninstallation instructions

### Using Better11

Once installed, learn how to use it:

3. **[USER_GUIDE.md](USER_GUIDE.md)** - Comprehensive usage documentation
   - Application manager (CLI and GUI)
   - System tools (registry, bloatware, services)
   - Advanced usage and scripting
   - Best practices
   - FAQ and troubleshooting

### For Developers

If you want to contribute or understand the internals:

4. **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
   - All modules and classes
   - Function signatures and parameters
   - Return types and exceptions
   - Usage examples
   - Type information

5. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design documentation
   - High-level architecture
   - Component design
   - Data flow diagrams
   - Design patterns used
   - Extension points
   - Future roadmap

6. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines
   - How to contribute
   - Development setup
   - Coding standards
   - Testing requirements
   - Pull request process
   - Code review checklist

### Important Policies

Before using or contributing:

7. **[SECURITY.md](SECURITY.md)** - Security policies and practices
   - Security features
   - Reporting vulnerabilities
   - Best practices
   - Known limitations
   - Threat model

8. **[LICENSE](LICENSE)** - MIT License
   - Usage rights
   - Liability disclaimer

9. **[CHANGELOG.md](CHANGELOG.md)** - Version history
   - Release notes
   - Breaking changes
   - New features by version
   - Bug fixes
   - Future roadmap

### AI Assistant Context

For AI assistants (like Claude):

10. **[CLAUDE.MD](CLAUDE.MD)** - Project context for AI
    - Current implementation status
    - Architecture overview
    - Development guidelines
    - Quick reference
    - Extension points

## 🎯 Common Use Cases

### "I want to install Better11"
→ Start with [README.md](README.md), then [INSTALL.md](INSTALL.md)

### "I want to use Better11"
→ Read [USER_GUIDE.md](USER_GUIDE.md)

### "I want to understand how it works"
→ Check [ARCHITECTURE.md](ARCHITECTURE.md) and [API_REFERENCE.md](API_REFERENCE.md)

### "I want to contribute"
→ Read [CONTRIBUTING.md](CONTRIBUTING.md)

### "I found a security issue"
→ Follow [SECURITY.md](SECURITY.md) reporting guidelines

### "I want to see what's changed"
→ Check [CHANGELOG.md](CHANGELOG.md)

### "I have a question"
→ Check FAQ in [USER_GUIDE.md](USER_GUIDE.md), then GitHub Discussions

## 📖 Documentation by Role

### End Users
1. README.md - Overview
2. INSTALL.md - Installation
3. USER_GUIDE.md - How to use
4. SECURITY.md - Stay safe

### Developers
1. CONTRIBUTING.md - How to contribute
2. ARCHITECTURE.md - System design
3. API_REFERENCE.md - API details
4. CLAUDE.MD - Project context

### Maintainers
1. All of the above, plus:
2. CHANGELOG.md - Track changes
3. SECURITY.md - Handle reports

## 🔍 Quick Reference

### Application Management

```bash
# List applications
python -m better11.cli list

# Install application
python -m better11.cli install app-id

# Launch GUI
python -m better11.gui
```

**Documentation**: [USER_GUIDE.md](USER_GUIDE.md) → Application Manager section

### System Tools

```python
from system_tools.registry import RegistryTweak, apply_tweaks
from system_tools.bloatware import remove_bloatware
from system_tools.services import ServiceAction, apply_service_actions
```

**Documentation**: [USER_GUIDE.md](USER_GUIDE.md) → System Tools section

### API Usage

```python
from better11.apps.manager import AppManager
manager = AppManager(catalog_path)
status, result = manager.install("app-id")
```

**Documentation**: [API_REFERENCE.md](API_REFERENCE.md)

## 📝 Documentation Standards

All Better11 documentation follows these principles:

1. **Clear Structure**: Table of contents and sections
2. **Examples**: Code examples for all features
3. **Up-to-date**: Maintained with code changes
4. **Searchable**: Good headings and organization
5. **Accessible**: Clear language, no jargon

## 🔗 External Resources

- **GitHub Repository**: https://github.com/owner/better11
- **Issue Tracker**: GitHub Issues
- **Discussions**: GitHub Discussions
- **License**: MIT (see LICENSE file)

## 📊 Documentation Metrics

- **Total Documentation**: 10 files
- **Total Lines**: ~3,000+ lines
- **Coverage**: All features documented
- **Last Updated**: December 2025
- **Status**: Complete ✅

## 🆘 Getting Help

1. **Check Documentation**: Search existing docs first
2. **FAQ**: See USER_GUIDE.md FAQ section
3. **GitHub Issues**: Search existing issues
4. **GitHub Discussions**: Ask questions
5. **Security Issues**: Use SECURITY.md process

## 🎓 Learning Path

### Beginner
1. README.md (10 min)
2. INSTALL.md (20 min)
3. USER_GUIDE.md - Getting Started (30 min)
4. Try basic commands (30 min)

**Total**: ~1.5 hours to get started

### Intermediate
1. USER_GUIDE.md - Complete (2 hours)
2. Experiment with system tools (1 hour)
3. Create custom catalog (30 min)
4. SECURITY.md (30 min)

**Total**: ~4 hours to become proficient

### Advanced
1. API_REFERENCE.md (1 hour)
2. ARCHITECTURE.md (1 hour)
3. CONTRIBUTING.md (30 min)
4. Review source code (2+ hours)

**Total**: ~4.5+ hours to master

## 📌 Quick Links

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [README.md](README.md) | Overview | 10 min |
| [INSTALL.md](INSTALL.md) | Installation | 20 min |
| [USER_GUIDE.md](USER_GUIDE.md) | Usage | 60 min |
| [API_REFERENCE.md](API_REFERENCE.md) | API Details | 45 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Design | 45 min |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributing | 30 min |
| [SECURITY.md](SECURITY.md) | Security | 30 min |
| [CHANGELOG.md](CHANGELOG.md) | Changes | 15 min |
| [LICENSE](LICENSE) | License | 5 min |
| [CLAUDE.MD](CLAUDE.MD) | AI Context | 15 min |

## ✨ What's Next?

1. **Read README.md** to understand Better11
2. **Follow INSTALL.md** to set it up
3. **Use USER_GUIDE.md** to learn features
4. **Check CONTRIBUTING.md** if you want to help
5. **Join Discussions** to connect with community

## 🤝 Contributing to Documentation

Found a typo? Section unclear? Want to add examples?

1. Documentation is as important as code
2. Follow existing format and style
3. Add examples where helpful
4. Keep language clear and simple
5. Submit PR with documentation changes

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

**Documentation Version**: 1.0  
**Last Updated**: December 9, 2025  
**Status**: Complete and up-to-date ✅

Need help? Start with [README.md](README.md) or ask in GitHub Discussions!
