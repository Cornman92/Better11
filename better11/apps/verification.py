from __future__ import annotations

import base64
import hashlib
import hmac
import logging
from pathlib import Path

from .code_signing import CodeSigningVerifier, SignatureStatus
from .models import AppMetadata

_LOGGER = logging.getLogger(__name__)


class VerificationError(RuntimeError):
    pass


class DownloadVerifier:
    """Performs integrity and signature validation for downloaded installers."""
    
    def __init__(self, verify_code_signing: bool = True, require_signatures: bool = False):
        """Initialize verifier with code signing options.
        
        Parameters
        ----------
        verify_code_signing : bool
            Whether to verify Authenticode signatures
        require_signatures : bool
            Whether to reject unsigned files
        """
        self.verify_code_signing = verify_code_signing
        self.require_signatures = require_signatures
        self.code_signing_verifier = CodeSigningVerifier() if verify_code_signing else None

    def verify_hash(self, file_path: Path, expected_sha256: str) -> str:
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        actual = digest.hexdigest()
        if actual.lower() != expected_sha256.lower():
            raise VerificationError(
                f"Hash mismatch for {file_path.name}: expected {expected_sha256}, got {actual}"
            )
        return actual

    def verify_signature(self, file_path: Path, signature_b64: str, key_b64: str) -> None:
        key = base64.b64decode(key_b64)
        provided = base64.b64decode(signature_b64)
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        expected = hmac.new(key, digest.digest(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, provided):
            raise VerificationError("Signature validation failed")

    def verify(self, metadata: AppMetadata, file_path: Path) -> None:
        # 1. Verify SHA-256 hash (required)
        self.verify_hash(file_path, metadata.sha256)
        
        # 2. Verify HMAC signature if present
        if metadata.requires_signature_verification():
            try:
                self.verify_signature(file_path, metadata.signature, metadata.signature_key)
            except Exception as exc:
                raise VerificationError(f"Signature check failed for {metadata.app_id}") from exc
        
        # 3. Verify Authenticode code signing (NEW!)
        if self.verify_code_signing and self.code_signing_verifier:
            sig_info = self.code_signing_verifier.verify_signature(file_path)
            
            if sig_info.status == SignatureStatus.UNSIGNED:
                _LOGGER.warning("File is not digitally signed: %s", file_path)
                if self.require_signatures:
                    raise VerificationError("File is not digitally signed (required by policy)")
            
            elif sig_info.status != SignatureStatus.VALID:
                _LOGGER.error("File has invalid signature: %s - %s", 
                             sig_info.status.value, sig_info.error_message)
                raise VerificationError(f"Invalid code signature: {sig_info.status.value}")
            
            else:
                _LOGGER.info("✅ File signature is VALID: %s", file_path)
                if sig_info.certificate:
                    _LOGGER.info("📝 Signed by: %s", sig_info.certificate.subject)
