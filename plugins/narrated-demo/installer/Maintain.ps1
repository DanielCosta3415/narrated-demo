param([ValidateSet('Rollback','Uninstall')] [string]$Action, [string]$Destination = "$env:LOCALAPPDATA/NarratedDemo/runtime", [switch]$ConfirmAction)
. "$PSScriptRoot/Common.ps1"
if (-not $ConfirmAction) { throw 'Explicit -ConfirmAction is required.' }
$managedRoot = Assert-Owned $Destination
$lock = [IO.File]::Open("$managedRoot/install.lock", 'OpenOrCreate', 'ReadWrite', 'None')
try {
    if ($Action -eq 'Rollback') {
        $previousPath = "$managedRoot/previous-runtime.json"
        $previous = Get-Content -LiteralPath $previousPath -Raw | ConvertFrom-Json
        foreach ($key in @('python','node','model','voices','ffmpeg','ffprobe')) {
            $target = [IO.Path]::GetFullPath($previous.$key)
            if (-not $target.StartsWith($managedRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Previous configuration escapes the owned runtime.' }
        }
        & $previous.python "$PSScriptRoot/../app/runtime.py" doctor --runtime $previousPath
        if ($LASTEXITCODE -ne 0) { throw 'Previous runtime failed diagnostics. Active configuration was not changed.' }
        Write-JsonAtomic "$managedRoot/runtime.json" $previous
        Write-Host 'Previous verified runtime restored.'
    }
} finally { $lock.Dispose() }
if ($Action -eq 'Uninstall') {
    # Recoverable deactivation; no recursive deletion and no deletion of videos.
    $archive = "$managedRoot.archived-$([DateTime]::UtcNow.ToString('yyyyMMddHHmmssfff'))"
    $null = Get-SafeRoot $archive
    if (Test-Path -LiteralPath $archive) { throw 'Archive already exists.' }
    Move-Item -LiteralPath $managedRoot -Destination $archive
    Write-Host "Runtime deactivated and recoverable at: $archive"
    Write-Host 'Disable/remove the Codex plugin separately. All files, including any videos, were preserved.'
}
