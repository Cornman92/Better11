"""Code signing verification for Windows executables.

This module provides Authenticode signature verification for PE files
(EXE, DLL, MSI) to ensure software integrity and authenticity.
"""
from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# Import logging
import logging

_LOGGER = logging.getLogger(__name__)


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
        
        Raises
        ------
        RuntimeError
            If verification fails due to system errors
        """
        if platform.system() != "Windows":
            _LOGGER.warning("Code signing verification only available on Windows")
            return SignatureInfo(
                status=SignatureStatus.UNSIGNED,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message="Code signing verification only available on Windows"
            )
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Use PowerShell Get-AuthenticodeSignature
            # Convert to JSON for easier parsing
            ps_command = f"""
            $sig = Get-AuthenticodeSignature -FilePath '{file_path}'
            $result = @{{
                Status = $sig.Status.ToString()
                StatusMessage = $sig.StatusMessage
                Path = $sig.Path
                HashAlgorithm = $sig.HashAlgorithm.ToString()
            }}
            if ($sig.SignerCertificate) {{
                $result.Certificate = @{{
                    Subject = $sig.SignerCertificate.Subject
                    Issuer = $sig.SignerCertificate.Issuer
                    SerialNumber = $sig.SignerCertificate.SerialNumber
                    Thumbprint = $sig.SignerCertificate.Thumbprint
                    NotBefore = $sig.SignerCertificate.NotBefore.ToString('o')
                    NotAfter = $sig.SignerCertificate.NotAfter.ToString('o')
                }}
            }}
            if ($sig.TimeStamperCertificate) {{
                $result.Timestamp = $sig.TimeStamperCertificate.NotBefore.ToString('o')
            }}
            $result | ConvertTo-Json -Depth 10
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            data = json.loads(result.stdout)
            
            # Map PowerShell status to our enum
            ps_status = data.get("Status", "Unknown").upper()
            status_map = {
                "VALID": SignatureStatus.VALID,
                "NOTSIGNED": SignatureStatus.UNSIGNED,
                "HASHMISMATCH": SignatureStatus.INVALID,
                "NOTTRUSTED": SignatureStatus.UNTRUSTED,
                "REVOKED": SignatureStatus.REVOKED,
                "EXPIRED": SignatureStatus.EXPIRED,
                "UNKNOWN": SignatureStatus.INVALID,
            }
            status = status_map.get(ps_status, SignatureStatus.INVALID)
            
            # Extract certificate info if present
            cert_info = None
            if "Certificate" in data and data["Certificate"]:
                cert_data = data["Certificate"]
                cert_info = CertificateInfo(
                    subject=cert_data.get("Subject", ""),
                    issuer=cert_data.get("Issuer", ""),
                    serial_number=cert_data.get("SerialNumber", ""),
                    thumbprint=cert_data.get("Thumbprint", ""),
                    valid_from=datetime.fromisoformat(cert_data.get("NotBefore", "")),
                    valid_to=datetime.fromisoformat(cert_data.get("NotAfter", ""))
                )
                
                # Check if expired
                if cert_info.is_expired():
                    status = SignatureStatus.EXPIRED
            
            # Extract timestamp if present
            timestamp = None
            if "Timestamp" in data and data["Timestamp"]:
                timestamp = datetime.fromisoformat(data["Timestamp"])
            
            return SignatureInfo(
                status=status,
                certificate=cert_info,
                timestamp=timestamp,
                hash_algorithm=data.get("HashAlgorithm"),
                error_message=data.get("StatusMessage") if status != SignatureStatus.VALID else None
            )
            
        except subprocess.TimeoutExpired:
            _LOGGER.error("Code signing verification timed out for %s", file_path)
            return SignatureInfo(
                status=SignatureStatus.INVALID,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message="Verification timed out"
            )
        except subprocess.CalledProcessError as e:
            _LOGGER.error("PowerShell command failed: %s", e.stderr)
            return SignatureInfo(
                status=SignatureStatus.INVALID,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message=f"PowerShell error: {e.stderr}"
            )
        except json.JSONDecodeError as e:
            _LOGGER.error("Failed to parse PowerShell output: %s", e)
            return SignatureInfo(
                status=SignatureStatus.INVALID,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message=f"Failed to parse verification output: {e}"
            )
        except Exception as e:
            _LOGGER.error("Unexpected error during signature verification: %s", e)
            return SignatureInfo(
                status=SignatureStatus.INVALID,
                certificate=None,
                timestamp=None,
                hash_algorithm=None,
                error_message=f"Unexpected error: {str(e)}"
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
        # Use verify_signature and extract certificate from result
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
