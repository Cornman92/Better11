from __future__ import annotations

import base64
import hashlib
import hmac
from pathlib import Path

from .models import AppMetadata


class VerificationError(RuntimeError):
    pass


class DownloadVerifier:
    """Performs integrity and signature validation for downloaded installers."""

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
        self.verify_hash(file_path, metadata.sha256)
        if metadata.requires_signature_verification():
            try:
                self.verify_signature(file_path, metadata.signature, metadata.signature_key)
            except Exception as exc:
                raise VerificationError(f"Signature check failed for {metadata.app_id}") from exc
