from __future__ import annotations

import base64
import hashlib
import hmac

import pytest

from better11.apps.models import AppMetadata, InstallerType
from better11.apps.verification import DownloadVerifier, VerificationError


def _signed_metadata(file_bytes: bytes, key: bytes) -> tuple[AppMetadata, str, str]:
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    signature = hmac.new(key, hashlib.sha256(file_bytes).digest(), hashlib.sha256).digest()
    return (
        AppMetadata(
            app_id="demo",
            name="Demo",
            version="1.0",
            uri="file://payload",
            sha256=sha256,
            installer_type=InstallerType.EXE,
            signature=base64.b64encode(signature).decode("ascii"),
            signature_key=base64.b64encode(key).decode("ascii"),
        ),
        sha256,
        base64.b64encode(signature).decode("ascii"),
    )


def test_verify_accepts_matching_hash_and_signature(tmp_path):
    payload = b"payload"
    payload_path = tmp_path / "demo.bin"
    payload_path.write_bytes(payload)
    key = b"test-key"
    metadata, _, _ = _signed_metadata(payload, key)

    verifier = DownloadVerifier()
    verifier.verify(metadata, payload_path)


def test_verify_raises_on_signature_mismatch(tmp_path):
    payload = b"payload"
    payload_path = tmp_path / "demo.bin"
    payload_path.write_bytes(payload)
    key = b"test-key"
    metadata, _, _ = _signed_metadata(payload, key)

    broken_metadata = AppMetadata(
        app_id=metadata.app_id,
        name=metadata.name,
        version=metadata.version,
        uri=metadata.uri,
        sha256=metadata.sha256,
        installer_type=metadata.installer_type,
        signature=metadata.signature,
        signature_key=base64.b64encode(b"other-key").decode("ascii"),
    )

    verifier = DownloadVerifier()
    with pytest.raises(VerificationError):
        verifier.verify(broken_metadata, payload_path)
