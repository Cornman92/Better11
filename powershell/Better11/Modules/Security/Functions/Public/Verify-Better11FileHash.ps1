function Verify-Better11FileHash {
    <#
    .SYNOPSIS
        Verifies the hash of a file against an expected value.
    
    .DESCRIPTION
        Computes the hash of a file and compares it to an expected hash value.
        Supports multiple hash algorithms (SHA256, SHA1, MD5).
    
    .PARAMETER FilePath
        Path to the file to verify.
    
    .PARAMETER ExpectedHash
        The expected hash value to compare against.
    
    .PARAMETER Algorithm
        Hash algorithm to use. Default is SHA256.
    
    .EXAMPLE
        Verify-Better11FileHash -FilePath "installer.exe" -ExpectedHash "abc123..."
    
    .EXAMPLE
        $verified = Verify-Better11FileHash -FilePath "file.zip" -ExpectedHash "def456..." -Algorithm SHA1
    
    .OUTPUTS
        PSCustomObject
        Returns verification result with hash information.
    #>
    
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateScript({ Test-Path $_ })]
        [string]$FilePath,
        
        [Parameter(Mandatory = $true, Position = 1)]
        [string]$ExpectedHash,
        
        [Parameter()]
        [ValidateSet('SHA256', 'SHA1', 'MD5', 'SHA384', 'SHA512')]
        [string]$Algorithm = 'SHA256'
    )
    
    process {
        try {
            Write-Better11Log -Message "Verifying $Algorithm hash for: $FilePath" -Level Info
            
            # Compute file hash
            $fileHash = Get-FileHash -Path $FilePath -Algorithm $Algorithm
            $computedHash = $fileHash.Hash
            
            # Normalize hashes for comparison (remove spaces, convert to lowercase)
            $normalizedComputed = $computedHash.ToLower().Replace(' ', '').Replace('-', '')
            $normalizedExpected = $ExpectedHash.ToLower().Replace(' ', '').Replace('-', '')
            
            # Compare hashes
            $isMatch = $normalizedComputed -eq $normalizedExpected
            
            $result = [PSCustomObject]@{
                FilePath = (Resolve-Path $FilePath).Path
                Algorithm = $Algorithm
                ComputedHash = $computedHash
                ExpectedHash = $ExpectedHash
                IsMatch = $isMatch
                FileSize = (Get-Item $FilePath).Length
            }
            
            if ($isMatch) {
                Write-Better11Log -Message "Hash verification successful" -Level Info
            }
            else {
                Write-Better11Log -Message "Hash mismatch! File may be corrupted or tampered with" -Level Error
                Write-Better11Log -Message "Expected: $ExpectedHash" -Level Error
                Write-Better11Log -Message "Computed: $computedHash" -Level Error
            }
            
            return $result
        }
        catch {
            Write-Better11Log -Message "Failed to verify file hash: $_" -Level Error
            throw
        }
    }
}
