from __future__ import annotations

import base64
import hashlib
import hmac
import logging
from pathlib import Path

from .code_signing import CodeSigningVerifier, SignatureStatus
from .models import AppMetadata
from .code_signing import CodeSigningVerifier, SignatureStatus

_LOGGER = logging.getLogger(__name__)

_LOGGER = logging.getLogger(__name__)


class VerificationError(RuntimeError):
    pass


class DownloadVerifier:
    """Performs integrity and signature validation for downloaded installers.
    
    Parameters
    ----------
    verify_code_signatures : bool
        Whether to verify Authenticode signatures (default: True)
    require_code_signing : bool
        Whether to reject unsigned files (default: False)
    check_revocation : bool
        Whether to check certificate revocation (default: False)
    """
    
    def __init__(
        self,
        verify_code_signatures: bool = True,
        require_code_signing: bool = False,
        check_revocation: bool = False
    ):
        self.verify_code_signatures = verify_code_signatures
        self.require_code_signing = require_code_signing
        self.code_signing_verifier = CodeSigningVerifier(check_revocation=check_revocation) if verify_code_signatures else None

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
        """Verify installer integrity and authenticity.
        
        Performs the following checks:
        1. SHA-256 hash verification (always)
        2. HMAC signature verification (if provided)
        3. Authenticode signature verification (if enabled)
        
        Parameters
        ----------
        metadata : AppMetadata
            Application metadata with verification information
        file_path : Path
            Path to downloaded installer
        
        Raises
        ------
        VerificationError
            If any verification check fails
        """
        # Always verify hash first
        self.verify_hash(file_path, metadata.sha256)
        
        # Verify HMAC signature if provided
        if metadata.requires_signature_verification():
            try:
                self.verify_signature(file_path, metadata.signature, metadata.signature_key)
            except Exception as exc:
                raise VerificationError(f"HMAC signature check failed for {metadata.app_id}") from exc
        
        # Verify Authenticode signature if enabled
        if self.verify_code_signatures and self.code_signing_verifier:
            try:
                sig_info = self.code_signing_verifier.verify_signature(file_path)
                
                if sig_info.status == SignatureStatus.UNSIGNED:
                    if self.require_code_signing:
                        raise VerificationError(
                            f"File is not digitally signed: {file_path.name}. "
                            "Code signing is required."
                        )
                    else:
                        _LOGGER.warning(
                            "File is not digitally signed: %s. Continuing with installation.",
                            file_path.name
                        )
                elif not sig_info.is_trusted():
                    error_msg = sig_info.error_message or f"Invalid signature status: {sig_info.status.value}"
                    raise VerificationError(
                        f"Code signature verification failed for {file_path.name}: {error_msg}"
                    )
                else:
                    _LOGGER.info(
                        "Code signature verified successfully for %s (Publisher: %s)",
                        file_path.name,
                        sig_info.certificate.subject if sig_info.certificate else "Unknown"
                    )
            except VerificationError:
                # Re-raise verification errors
                raise
            except Exception as exc:
                # Log other errors but don't fail if code signing is not required
                if self.require_code_signing:
                    raise VerificationError(
                        f"Code signature verification error for {file_path.name}: {exc}"
                    ) from exc
                else:
                    _LOGGER.warning(
                        "Code signature verification error (non-fatal): %s",
                        exc
                    )
