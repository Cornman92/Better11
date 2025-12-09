# Security Policy

## Security Overview

Better11 takes security seriously. This document outlines our security practices, how to report vulnerabilities, and security considerations for users.

## Table of Contents

- [Supported Versions](#supported-versions)
- [Security Features](#security-features)
- [Reporting Vulnerabilities](#reporting-vulnerabilities)
- [Security Considerations](#security-considerations)
- [Best Practices](#best-practices)
- [Known Limitations](#known-limitations)

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |
| < 0.1   | :x:                |

**Note**: Better11 is currently in active development (pre-1.0). Security patches will be applied to the latest development version.

## Security Features

### Application Installation Security

#### 1. Download Security

**Domain Vetting**
- Only downloads from pre-approved domains
- Domains must be explicitly listed in catalog's `vetted_domains`
- Prevents malicious URL injection

```json
{
  "app_id": "example",
  "uri": "https://example.com/installer.msi",
  "vetted_domains": ["example.com"]
}
```

**Protocol Enforcement**
- HTTPS required for remote downloads
- HTTP connections rejected for security
- Local file:// URIs supported for testing

#### 2. Integrity Verification

**SHA-256 Hash Verification** (Required)
- All downloads verified against expected SHA-256 hash
- Detects corruption and tampering
- Prevents partial or modified downloads

**HMAC-SHA256 Signature** (Optional)
- Additional cryptographic signature verification
- Authenticates catalog maintainer
- Prevents catalog tampering if keys compromised

```python
# Verification process
verifier.verify_hash(file, expected_sha256)  # Always
if app.requires_signature_verification():
    verifier.verify_signature(file, sig, key)  # Optional
```

#### 3. Execution Safety

**Silent Installation**
- No user interaction during installation
- Prevents social engineering attacks
- Standardized installation arguments

**Dry-Run Mode**
- Test operations without execution
- Enabled by default on non-Windows platforms
- Useful for testing and validation

**Command Validation**
- Installer arguments validated
- Subprocess calls use list format (not shell)
- Prevents command injection

### System Modification Security

#### 1. Platform Validation

```python
ensure_windows()  # Raises SafetyError if not Windows
```

- Prevents accidental execution on wrong platform
- Protects against cross-platform bugs

#### 2. User Confirmation

```python
if not confirm_action("Apply changes?"):
    raise SafetyError("Cancelled by user")
```

- Required for destructive operations
- Prevents unauthorized modifications
- Can be disabled for automation (use carefully)

#### 3. Automatic Backups

**System Restore Points**
- Created before system modifications
- Allows full system rollback
- Uses Windows built-in functionality

**Registry Backups**
- Exports registry keys before modification
- Stored as `.reg` files
- Can be imported to restore

#### 4. Error Handling

- All operations wrapped in try/except
- Errors logged with context
- Cleanup on failure

### Data Security

#### 1. Local Storage

**Installation State** (`~/.better11/installed.json`)
- Stores metadata only (no secrets)
- User directory with standard permissions
- JSON format for transparency

**Downloaded Installers** (`~/.better11/downloads/`)
- Temporary storage for installers
- Can be safely deleted after installation
- Standard file permissions

#### 2. No Network Communication

- Better11 does not "phone home"
- No telemetry or tracking
- Downloads only from user-specified sources
- No automatic updates (yet)

## Reporting Vulnerabilities

### How to Report

**DO NOT** report security vulnerabilities through public GitHub issues.

Instead, please report security vulnerabilities via:

**Email**: security@better11.example.com (replace with actual email)

**Include in your report:**
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Affected versions
5. Suggested fix (if any)
6. Your contact information

### What to Expect

1. **Acknowledgment**: Within 48 hours
2. **Assessment**: Within 1 week
3. **Fix Timeline**: Depends on severity
   - Critical: 1-7 days
   - High: 1-2 weeks
   - Medium: 2-4 weeks
   - Low: Next release
4. **Disclosure**: Coordinated disclosure after fix

### Responsible Disclosure

We follow responsible disclosure practices:

1. **Private Reporting**: Report privately first
2. **Reasonable Time**: Allow time for fix (typically 90 days)
3. **Coordinated Disclosure**: Agree on disclosure timing
4. **Credit**: Reporter credited (unless anonymous)

### Scope

**In Scope:**
- Better11 codebase
- Security of application installation
- System modification safety
- Catalog validation
- Verification mechanisms

**Out of Scope:**
- Third-party applications in catalog
- Windows OS vulnerabilities
- Python interpreter vulnerabilities
- Social engineering (unless related to Better11 UI)

## Security Considerations

### For Users

#### Before Using Better11

1. **Review Source Code**: Better11 is open source - review before running
2. **Test in VM**: Test system modifications in virtual machine first
3. **Create Backups**: Full system backup recommended
4. **Check Catalog**: Review applications in catalog.json
5. **Verify Hashes**: Independently verify critical application hashes

#### During Usage

1. **Run as Administrator**: Required for system modifications
2. **Review Prompts**: Read confirmation prompts carefully
3. **Check Logs**: Review logs for unexpected behavior
4. **One at a Time**: Apply changes incrementally
5. **Monitor System**: Watch for issues after modifications

#### After Modifications

1. **Test Functionality**: Verify system works correctly
2. **Check Restore Points**: Ensure restore points were created
3. **Keep Backups**: Maintain registry backups
4. **Document Changes**: Note what was modified

### For Catalog Maintainers

#### Creating Catalog Entries

1. **Verify Source**: Only include applications from trusted sources
2. **Compute Hashes**: Generate SHA-256 hashes accurately
3. **Test Installation**: Test silent installation arguments
4. **Vet Domains**: Only include domains you control or trust
5. **Sign Catalog**: Use HMAC signatures for additional security

#### Hash Computation

```bash
# Compute SHA-256 hash (Windows)
certutil -hashfile installer.msi SHA256

# Verify hash matches expected value
```

#### HMAC Signature (Optional)

```python
import base64
import hashlib
import hmac

# Generate HMAC key (once)
key = os.urandom(32)
key_b64 = base64.b64encode(key).decode()

# Compute HMAC signature
with open("installer.msi", "rb") as f:
    file_hash = hashlib.sha256(f.read()).digest()
signature = hmac.new(key, file_hash, hashlib.sha256).digest()
signature_b64 = base64.b64encode(signature).decode()

# Add to catalog
{
    "signature": signature_b64,
    "signature_key": key_b64
}
```

**Important**: Keep HMAC key secure! Anyone with the key can create valid signatures.

### For Developers

#### Secure Coding Practices

1. **Input Validation**: Validate all user input
2. **Path Sanitization**: Use `Path.resolve()` to prevent traversal
3. **Subprocess Safety**: Use list format, avoid `shell=True`
4. **Error Messages**: Don't leak sensitive information
5. **Logging**: Log operations but not secrets

#### Code Review Checklist

- [ ] Input validation present
- [ ] No SQL injection (if database added)
- [ ] No command injection
- [ ] No path traversal
- [ ] Secrets not hardcoded
- [ ] Error handling appropriate
- [ ] User confirmation for destructive ops
- [ ] Tests include security scenarios

#### Testing Security

```python
# Test domain vetting
def test_untrusted_domain_rejected():
    with pytest.raises(DownloadError):
        downloader.download(app_with_untrusted_domain)

# Test hash verification
def test_hash_mismatch_rejected():
    with pytest.raises(VerificationError):
        verifier.verify_hash(file, wrong_hash)

# Test confirmation requirement
def test_requires_confirmation():
    with pytest.raises(SafetyError):
        apply_tweaks(tweaks, confirm=True, input_func=lambda _: "n")
```

## Best Practices

### General Security

1. **Keep Updated**: Use latest version of Better11
2. **Review Changes**: Review what each operation does
3. **Minimize Privileges**: Don't run as admin unnecessarily (though required for many features)
4. **Use VM for Testing**: Test in virtual machine first
5. **Regular Backups**: Maintain system backups

### Catalog Security

1. **Verify Sources**: Only include trusted applications
2. **Check URLs**: Verify download URLs are correct
3. **Update Hashes**: Update hashes when applications update
4. **Sign Catalog**: Use HMAC signatures for distribution
5. **Version Control**: Track catalog changes in git

### System Modifications

1. **Understand Impact**: Research registry tweaks before applying
2. **Test Individually**: Apply one change at a time
3. **Document Changes**: Keep record of modifications
4. **Keep Backups**: Maintain registry backups
5. **Plan Rollback**: Know how to revert changes

## Known Limitations

### Current Limitations

1. **No Code Signing Verification**
   - Does not verify Authenticode signatures
   - Relies on hash/HMAC verification
   - Future enhancement planned

2. **No Sandbox Execution**
   - Installers run with admin privileges
   - No containerization or sandboxing
   - Trust the catalog maintainer

3. **No Automatic Updates**
   - No automatic security updates
   - User must manually update Better11
   - Future feature planned

4. **No Network Security**
   - Downloads use system proxy settings
   - No certificate pinning
   - Relies on OS certificate store

5. **No Audit Logging**
   - Basic logging only
   - No tamper-proof audit trail
   - Consider enabling Windows audit logging

### Risk Mitigation

**For Limitation #1 (Code Signing)**:
- Use HMAC signatures in catalog
- Verify hashes independently
- Only use trusted catalogs

**For Limitation #2 (Sandboxing)**:
- Test in VM first
- Review installer source code if possible
- Use only trusted applications

**For Limitation #3 (Auto-Updates)**:
- Check repository regularly
- Subscribe to release notifications
- Follow security advisories

**For Limitation #4 (Network Security)**:
- Use trusted networks only
- Consider VPN for downloads
- Verify hashes after download

**For Limitation #5 (Audit Logging)**:
- Enable Windows audit logging
- Review Better11 logs regularly
- Keep logs for forensics

## Threat Model

### Threats Considered

1. **Malicious Catalog**: Attacker modifies catalog
   - Mitigated by: HMAC signatures, hash verification
   
2. **Man-in-the-Middle**: Network attacker intercepts download
   - Mitigated by: HTTPS, hash verification
   
3. **Compromised Application**: Downloaded application is malicious
   - Mitigated by: Catalog vetting, hash verification
   
4. **Registry Corruption**: Incorrect registry modification
   - Mitigated by: Backups, restore points, testing
   
5. **Dependency Confusion**: Malicious dependency in catalog
   - Mitigated by: Catalog review, dependency tracking

### Threats NOT Considered

1. **Compromised Python Interpreter**: Python itself is malicious
2. **Compromised Windows**: Operating system is compromised
3. **Physical Access**: Attacker has physical machine access
4. **Insider Threat**: Catalog maintainer is malicious
5. **Zero-Day Exploits**: Unknown vulnerabilities in dependencies

## Compliance

### Privacy

Better11:
- ✅ Does not collect user data
- ✅ Does not transmit data to external servers
- ✅ Stores only necessary metadata locally
- ✅ No tracking or telemetry
- ✅ No cookies or persistent identifiers

### Licensing

- Better11 is MIT licensed
- No restrictions on use
- No warranty provided
- Use at your own risk

## Security Updates

Security updates will be:
1. Released promptly for critical issues
2. Announced in CHANGELOG.md
3. Tagged with security label in releases
4. Documented with CVE if applicable

## Contact

**Security Issues**: security@better11.example.com (replace with actual)  
**General Issues**: [GitHub Issues](https://github.com/owner/better11/issues)  
**Discussions**: [GitHub Discussions](https://github.com/owner/better11/discussions)

## Acknowledgments

We appreciate security researchers who responsibly disclose vulnerabilities. Contributors will be credited in:
- CHANGELOG.md
- Release notes
- Security advisories
- Hall of Fame (if established)

---

**Last Updated**: December 2025  
**Policy Version**: 1.0

**Remember**: Security is a shared responsibility. Users, developers, and catalog maintainers all play a role in keeping Better11 secure.
