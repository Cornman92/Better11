"""Tests for code signing verification."""
import sys
import pytest

from better11.apps.code_signing import (
    SignatureStatus,
    CertificateInfo,
    SignatureInfo,
    CodeSigningVerifier,
)
from datetime import datetime, timedelta


class TestSignatureStatus:
    """Test SignatureStatus enum."""
    
    def test_signature_status_values(self):
        """Test signature status enum values."""
        assert SignatureStatus.VALID.value == "valid"
        assert SignatureStatus.INVALID.value == "invalid"
        assert SignatureStatus.UNSIGNED.value == "unsigned"
        assert SignatureStatus.REVOKED.value == "revoked"
        assert SignatureStatus.EXPIRED.value == "expired"
        assert SignatureStatus.UNTRUSTED.value == "untrusted"


class TestCertificateInfo:
    """Test CertificateInfo dataclass."""
    
    def test_certificate_info_creation(self):
        """Test creating certificate info."""
        now = datetime.now()
        future = now + timedelta(days=365)
        
        cert = CertificateInfo(
            subject="CN=Test Publisher",
            issuer="CN=Test CA",
            serial_number="123456",
            thumbprint="ABCDEF",
            valid_from=now,
            valid_to=future
        )
        
        assert cert.subject == "CN=Test Publisher"
        assert cert.issuer == "CN=Test CA"
        assert not cert.is_expired()
    
    def test_certificate_expired(self):
        """Test expired certificate detection."""
        past = datetime.now() - timedelta(days=365)
        yesterday = datetime.now() - timedelta(days=1)
        
        cert = CertificateInfo(
            subject="CN=Test",
            issuer="CN=Test",
            serial_number="123",
            thumbprint="ABC",
            valid_from=past,
            valid_to=yesterday
        )
        
        assert cert.is_expired()


class TestSignatureInfo:
    """Test SignatureInfo dataclass."""
    
    def test_signature_info_valid(self):
        """Test valid signature info."""
        now = datetime.now()
        cert = CertificateInfo(
            subject="CN=Test",
            issuer="CN=Test",
            serial_number="123",
            thumbprint="ABC",
            valid_from=now,
            valid_to=now + timedelta(days=365)
        )
        
        sig_info = SignatureInfo(
            status=SignatureStatus.VALID,
            certificate=cert,
            timestamp=now,
            hash_algorithm="SHA256"
        )
        
        assert sig_info.is_trusted()
    
    def test_signature_info_invalid(self):
        """Test invalid signature info."""
        sig_info = SignatureInfo(
            status=SignatureStatus.INVALID,
            certificate=None,
            timestamp=None,
            hash_algorithm=None,
            error_message="Invalid signature"
        )
        
        assert not sig_info.is_trusted()


class TestCodeSigningVerifier:
    """Test CodeSigningVerifier class."""
    
    def test_verifier_creation(self):
        """Test creating a code signing verifier."""
        verifier = CodeSigningVerifier()
        assert verifier.check_revocation is False
    
    def test_verifier_with_revocation_check(self):
        """Test verifier with revocation checking enabled."""
        verifier = CodeSigningVerifier(check_revocation=True)
        assert verifier.check_revocation is True
    
    def test_trusted_publisher_management(self):
        """Test adding and checking trusted publishers."""
        verifier = CodeSigningVerifier()
        
        now = datetime.now()
        cert = CertificateInfo(
            subject="CN=Trusted Publisher",
            issuer="CN=Test CA",
            serial_number="123",
            thumbprint="ABC",
            valid_from=now,
            valid_to=now + timedelta(days=365)
        )
        
        # Not trusted initially
        assert not verifier.is_trusted_publisher(cert)
        
        # Add to trusted list
        verifier.add_trusted_publisher(cert)
        assert verifier.is_trusted_publisher(cert)
        
        # Remove from trusted list
        verifier.remove_trusted_publisher(cert.subject)
        assert not verifier.is_trusted_publisher(cert)


    @pytest.mark.skipif(
        sys.platform != "win32",
        reason="Code signing verification only works on Windows"
    )
    def test_verify_signature_signed_file(self, tmp_path):
        """Test verifying a signed file."""
        # Create a test file (in real scenario, would use actual signed file)
        test_file = tmp_path / "test.exe"
        test_file.write_bytes(b"test content")
        
        verifier = CodeSigningVerifier()
        sig_info = verifier.verify_signature(test_file)
        
        # Should return a SignatureInfo object
        assert isinstance(sig_info, SignatureInfo)
        assert isinstance(sig_info.status, SignatureStatus)
    
    @pytest.mark.skipif(
        sys.platform != "win32",
        reason="Code signing verification only works on Windows"
    )
    def test_verify_signature_nonexistent_file(self, tmp_path):
        """Test verifying a non-existent file."""
        verifier = CodeSigningVerifier()
        nonexistent = tmp_path / "nonexistent.exe"
        
        with pytest.raises(FileNotFoundError):
            verifier.verify_signature(nonexistent)
    
    def test_verify_signature_non_windows(self, tmp_path):
        """Test verification on non-Windows returns unsigned status."""
        if sys.platform == "win32":
            pytest.skip("This test is for non-Windows platforms")
        
        test_file = tmp_path / "test.exe"
        test_file.write_bytes(b"test")
        
        verifier = CodeSigningVerifier()
        sig_info = verifier.verify_signature(test_file)
        
        assert sig_info.status == SignatureStatus.UNSIGNED
        assert "Windows" in sig_info.error_message
    
    def test_extract_certificate(self, tmp_path, mocker):
        """Test certificate extraction."""
        verifier = CodeSigningVerifier()
        test_file = tmp_path / "test.exe"
        test_file.write_bytes(b"test")
        
        # Mock verify_signature to return a signature with certificate
        mock_cert = CertificateInfo(
            subject="CN=Test",
            issuer="CN=Test CA",
            serial_number="123",
            thumbprint="ABC",
            valid_from=datetime.now(),
            valid_to=datetime.now() + timedelta(days=365)
        )
        mock_sig_info = SignatureInfo(
            status=SignatureStatus.VALID,
            certificate=mock_cert,
            timestamp=datetime.now(),
            hash_algorithm="SHA256"
        )
        
        mocker.patch.object(verifier, 'verify_signature', return_value=mock_sig_info)
        
        cert = verifier.extract_certificate(test_file)
        assert cert == mock_cert
    
    def test_extract_certificate_unsigned(self, tmp_path, mocker):
        """Test certificate extraction from unsigned file."""
        verifier = CodeSigningVerifier()
        test_file = tmp_path / "test.exe"
        test_file.write_bytes(b"test")
        
        mock_sig_info = SignatureInfo(
            status=SignatureStatus.UNSIGNED,
            certificate=None,
            timestamp=None,
            hash_algorithm=None
        )
        
        mocker.patch.object(verifier, 'verify_signature', return_value=mock_sig_info)
        
        cert = verifier.extract_certificate(test_file)
        assert cert is None
