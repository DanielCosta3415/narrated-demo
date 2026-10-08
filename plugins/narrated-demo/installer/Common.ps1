Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Get-SafeRoot([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { throw 'Empty installation path.' }
    $full = [IO.Path]::GetFullPath($Path)
    $resolved = $full.TrimEnd('\', '/')
    if ($resolved -eq [IO.Path]::GetPathRoot($full).TrimEnd('\', '/')) { throw 'Drive root rejected.' }
    if ($resolved.StartsWith('\\')) { throw 'Network/UNC installation roots are not supported.' }
    $forbidden = @($env:USERPROFILE, $env:LOCALAPPDATA, $env:ProgramFiles)
    foreach ($item in $forbidden) {
        if ($item -and $resolved -eq [IO.Path]::GetFullPath($item).TrimEnd('\', '/')) { throw 'Broad installation path rejected.' }
    }
    $cursor = $resolved
    while ($cursor) {
        if ((Test-Path -LiteralPath $cursor) -and ((Get-Item -LiteralPath $cursor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Reparse-point installation path rejected.' }
        $parent = Split-Path $cursor -Parent
        if ($parent -eq $cursor) { break }
        $cursor = $parent
    }
    return $resolved
}
function Assert-Owned([string]$Root) {
    $Root = Get-SafeRoot $Root
    $marker = Join-Path $Root '.narrated-demo-owner.json'
    if (-not (Test-Path -LiteralPath $marker)) { throw 'No ownership marker. Refusing to change this directory.' }
    $data = Get-Content -LiteralPath $marker -Raw -Encoding UTF8 | ConvertFrom-Json
    $storedRoot = Get-SafeRoot $data.root
    if ($data.app -ne 'narrated-demo' -or $storedRoot -ne $Root) { throw "Invalid ownership marker. Stored root: $storedRoot; resolved target: $Root" }
    return $Root
}
function Write-JsonAtomic($Path, $Value) {
    $temporary = "$Path.new"
    $Value | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}
function Expand-SafeArchive($Archive, $Destination) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $base = [IO.Path]::GetFullPath($Destination).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    $zip = [IO.Compression.ZipFile]::OpenRead($Archive)
    try {
        foreach ($entry in $zip.Entries) {
            $target = [IO.Path]::GetFullPath((Join-Path $Destination $entry.FullName))
            if (-not $target.StartsWith($base, [StringComparison]::OrdinalIgnoreCase) -or $entry.FullName.Contains(':')) { throw 'Unsafe ZIP entry.' }
        }
        # Avoid Expand-Archive's legacy MAX_PATH cleanup failure. Explicit
        # extended paths keep extraction inside the checked destination.
        foreach ($entry in $zip.Entries) {
            $target = [IO.Path]::GetFullPath((Join-Path $Destination $entry.FullName))
            $null = Get-SafeRoot $target
            $extended = '\\?\' + $target
            if ($entry.FullName.EndsWith('/')) { $null = [IO.Directory]::CreateDirectory($extended) }
            else {
                $null = [IO.Directory]::CreateDirectory('\\?\' + [IO.Path]::GetDirectoryName($target))
                [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $extended, $true)
            }
        }
    } finally { $zip.Dispose() }
}
