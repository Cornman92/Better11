"""Code signing verification for Windows executables.

This module provides Authenticode signature verification for PE files
(EXE, DLL, MSI) to ensure software integrity and authenticity.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# Placeholder - will be implemented in Phase 2


class SignatureStatus(Enum):
    """Status of a digital signature."""
    
    VALID = "valid"
    INVALID = "invalid"
    UNSIGNED = "unsigned"
    REVOKED = "revoked"
    EXPIRED = "expired"
    UNTRUSTED = "untrusted"


@dataclass
class CertificateInfo:
    """Certificate information extracted from signed file."""
    
    subject: str
    issuer: str
    serial_number: str
    thumbprint: str
    valid_from: datetime
    valid_to: datetime
    
    def is_expired(self) -> bool:
        """Check if certificate has expired."""
        return datetime.now() > self.valid_to


@dataclass
class SignatureInfo:
    """Complete signature information for a file."""
    
    status: SignatureStatus
    certificate: Optional[CertificateInfo]
    timestamp: Optional[datetime]
    hash_algorithm: Optional[str]
    error_message: Optional[str] = None
    
    def is_trusted(self) -> bool:
        """Check if signature is valid and trusted."""
        return self.status == SignatureStatus.VALID


class CodeSigningVerifier:
    """Verify Authenticode signatures on Windows executables.
    
    This class provides methods to verify digital signatures, extract
    certificate information, and manage trusted publishers.
    
    Parameters
    ----------
    check_revocation : bool
        Whether to check certificate revocation status (CRL/OCSP)
    """
    
    def __init__(self, check_revocation: bool = False):
        self.check_revocation = check_revocation
        self._trusted_publishers: set[str] = set()
    
    def verify_signature(self, file_path: Path) -> SignatureInfo:
        """Verify the digital signature of a file.

        Parameters
        ----------
        file_path : Path
            Path to file to verify

        Returns
        -------
        SignatureInfo
            Signature verification results
        """
        if not file_path.exists():
            return SignatureInfo(
                status=SignatureStatus.INVALID,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message=f"File not found: {file_path}"
            )

        try:
            # Use PowerShell Get-AuthenticodeSignature
            script = f'''
            $sig = Get-AuthenticodeSignature -FilePath "{file_path}"
            $result = @{{
                Status = $sig.Status.ToString()
                StatusMessage = $sig.StatusMessage
                SignerCertificate = @{{}}
                TimeStamperCertificate = @{{}}
                HashAlgorithm = ""
            }}

            if ($sig.SignerCertificate) {{
                $result.SignerCertificate = @{{
                    Subject = $sig.SignerCertificate.Subject
                    Issuer = $sig.SignerCertificate.Issuer
                    SerialNumber = $sig.SignerCertificate.SerialNumber
                    Thumbprint = $sig.SignerCertificate.Thumbprint
                    NotBefore = $sig.SignerCertificate.NotBefore.ToString("o")
                    NotAfter = $sig.SignerCertificate.NotAfter.ToString("o")
                }}
                $result.HashAlgorithm = $sig.SignerCertificate.SignatureAlgorithm.FriendlyName
            }}

            if ($sig.TimeStamperCertificate) {{
                $result.TimeStamperCertificate = @{{
                    NotBefore = $sig.TimeStamperCertificate.NotBefore.ToString("o")
                }}
            }}

            $result | ConvertTo-Json -Depth 10
            '''

            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            if result.returncode != 0:
                return SignatureInfo(
                    status=SignatureStatus.INVALID,
                    certificate=None,
                    timestamp=None,
                    hash_algorithm=None,
                    error_message=f"PowerShell error: {result.stderr}"
                )

            return self._parse_powershell_result(result.stdout)

        except subprocess.TimeoutExpired:
            return SignatureInfo(
                status=SignatureStatus.INVALID,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message="Signature verification timed out"
            )
        except Exception as e:
            return SignatureInfo(
                status=SignatureStatus.INVALID,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message=f"Verification error: {str(e)}"
            )

    def _parse_powershell_result(self, json_output: str) -> SignatureInfo:
        """Parse PowerShell Get-AuthenticodeSignature JSON output.

        Parameters
        ----------
        json_output : str
            JSON output from PowerShell

        Returns
        -------
        SignatureInfo
            Parsed signature information
        """
        import json

        try:
            data = json.loads(json_output)

            # Map PowerShell status to our enum
            status_str = data.get("Status", "").lower()
            status_map = {
                "valid": SignatureStatus.VALID,
                "invalidsignature": SignatureStatus.INVALID,
                "notsigned": SignatureStatus.UNSIGNED,
                "hashesmismatch": SignatureStatus.INVALID,
                "notrusted": SignatureStatus.UNTRUSTED,
                "unknownerror": SignatureStatus.INVALID,
            }
            status = status_map.get(status_str, SignatureStatus.INVALID)

            # Extract certificate info if available
            cert_info = None
            cert_data = data.get("SignerCertificate", {})
            if cert_data and cert_data.get("Subject"):
                try:
                    cert_info = CertificateInfo(
                        subject=cert_data.get("Subject", ""),
                        issuer=cert_data.get("Issuer", ""),
                        serial_number=cert_data.get("SerialNumber", ""),
                        thumbprint=cert_data.get("Thumbprint", ""),
                        valid_from=datetime.fromisoformat(cert_data.get("NotBefore", "")),
                        valid_to=datetime.fromisoformat(cert_data.get("NotAfter", ""))
                    )
                except (ValueError, KeyError):
                    pass

            # Extract timestamp if available
            timestamp = None
            ts_data = data.get("TimeStamperCertificate", {})
            if ts_data and ts_data.get("NotBefore"):
                try:
                    timestamp = datetime.fromisoformat(ts_data.get("NotBefore", ""))
                except ValueError:
                    pass

            hash_algorithm = data.get("HashAlgorithm")
            error_message = data.get("StatusMessage") if status != SignatureStatus.VALID else None

            return SignatureInfo(
                status=status,
                certificate=cert_info,
                timestamp=timestamp,
                hash_algorithm=hash_algorithm,
                error_message=error_message
            )

        except json.JSONDecodeError as e:
            return SignatureInfo(
                status=SignatureStatus.INVALID,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message=f"Failed to parse PowerShell output: {str(e)}"
            )
    
    def extract_certificate(self, file_path: Path) -> Optional[CertificateInfo]:
        """Extract certificate information from signed file.

        Parameters
        ----------
        file_path : Path
            Path to signed file

        Returns
        -------
        Optional[CertificateInfo]
            Certificate information if file is signed, None otherwise
        """
        sig_info = self.verify_signature(file_path)
        return sig_info.certificate
    
    def is_trusted_publisher(self, cert_info: CertificateInfo) -> bool:
        """Check if certificate publisher is in trusted list.
        
        Parameters
        ----------
        cert_info : CertificateInfo
            Certificate to check
        
        Returns
        -------
        bool
            True if publisher is trusted
        """
        return cert_info.subject in self._trusted_publishers
    
    def add_trusted_publisher(self, cert_info: CertificateInfo) -> None:
        """Add publisher to trusted list.
        
        Parameters
        ----------
        cert_info : CertificateInfo
            Certificate to trust
        """
        self._trusted_publishers.add(cert_info.subject)
    
    def remove_trusted_publisher(self, subject: str) -> None:
        """Remove publisher from trusted list.
        
        Parameters
        ----------
        subject : str
            Certificate subject to remove
        """
        self._trusted_publishers.discard(subject)


__all__ = [
    "SignatureStatus",
    "CertificateInfo",
    "SignatureInfo",
    "CodeSigningVerifier",
]
