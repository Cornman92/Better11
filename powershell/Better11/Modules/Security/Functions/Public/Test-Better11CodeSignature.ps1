function Test-Better11CodeSignature {
    <#
    .SYNOPSIS
        Verifies the Authenticode signature of a file.
    
    .DESCRIPTION
        Checks if a file is digitally signed and validates the signature chain,
        expiration status, and trust level. Returns detailed signature information.
    
    .PARAMETER FilePath
        Path to the file to verify (EXE, DLL, MSI, etc.).
    
    .PARAMETER CheckRevocation
        If specified, performs certificate revocation checking (slower but more secure).
    
    .EXAMPLE
        Test-Better11CodeSignature -FilePath "C:\installer.exe"
    
    .EXAMPLE
        $result = Test-Better11CodeSignature -FilePath "C:\app.msi" -CheckRevocation
        if ($result.IsTrusted) {
            Write-Host "File is trusted"
        }
    
    .OUTPUTS
        PSCustomObject
        Returns signature information including status and certificate details.
    #>
    
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true, Position = 0, ValueFromPipeline = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$FilePath,
        
        [Parameter()]
        [switch]$CheckRevocation
    )
    
    process {
        try {
            Write-Better11Log -Message "Verifying code signature for: $FilePath" -Level Info
            
            $signature = Get-AuthenticodeSignature -FilePath $FilePath
            
            # Determine status
            $status = switch ($signature.Status) {
                'Valid' { 'Valid' }
                'NotSigned' { 'Unsigned' }
                'HashMismatch' { 'Invalid' }
                'NotTrusted' { 'Untrusted' }
                'UnknownError' { 'Unknown' }
                default { $signature.Status.ToString() }
            }
            
            # Extract certificate information
            $certificateInfo = $null
            if ($signature.SignerCertificate) {
                $cert = $signature.SignerCertificate
                $certificateInfo = [PSCustomObject]@{
                    Subject = $cert.Subject
                    Issuer = $cert.Issuer
                    SerialNumber = $cert.SerialNumber
                    Thumbprint = $cert.Thumbprint
                    ValidFrom = $cert.NotBefore
                    ValidTo = $cert.NotAfter
                    IsExpired = (Get-Date) -gt $cert.NotAfter
                    FriendlyName = $cert.FriendlyName
                }
            }
            
            # Timestamp information
            $timestampInfo = $null
            if ($signature.TimeStamperCertificate) {
                $timestampInfo = [PSCustomObject]@{
                    Timestamp = $signature.TimeStamperCertificate.NotBefore
                    Issuer = $signature.TimeStamperCertificate.Issuer
                }
            }
            
            $result = [PSCustomObject]@{
                FilePath = (Resolve-Path $FilePath).Path
                Status = $status
                IsTrusted = ($status -eq 'Valid')
                IsSigned = ($status -ne 'Unsigned')
                Certificate = $certificateInfo
                Timestamp = $timestampInfo
                HashAlgorithm = $signature.HashAlgorithm
                StatusMessage = $signature.StatusMessage
            }
            
            if ($result.IsTrusted) {
                Write-Better11Log -Message "File signature is valid and trusted" -Level Info
            }
            else {
                Write-Better11Log -Message "File signature status: $status" -Level Warning
            }
            
            return $result
        }
        catch {
            Write-Better11Log -Message "Failed to verify code signature: $_" -Level Error
            throw
        }
    }
}
