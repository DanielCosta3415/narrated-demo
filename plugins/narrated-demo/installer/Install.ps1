param([string]$Destination = "$env:LOCALAPPDATA/NarratedDemo/runtime", [switch]$AcceptDownloads)
$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path $PSScriptRoot -Parent
$pluginRoot = if (Test-Path -LiteralPath "$sourceRoot/plugin.json") { $sourceRoot } else { "$sourceRoot/plugins/narrated-demo" }
. "$pluginRoot/installer/Common.ps1"
if ($env:OS -ne 'Windows_NT' -or -not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { throw 'Supported platform: Windows x64.' }
if (-not $AcceptDownloads -and (Read-Host 'Baixar Python, Node, Chromium, bibliotecas e modelos locais? Digite SIM') -ne 'SIM') { throw 'Instalação cancelada.' }
$managedRoot = Get-SafeRoot $Destination
if ((Test-Path -LiteralPath $managedRoot) -and @(Get-ChildItem -LiteralPath $managedRoot -Force).Count -gt 0) { $null = Assert-Owned $managedRoot }
New-Item -ItemType Directory -Force -Path $managedRoot | Out-Null
if (-not (Test-Path -LiteralPath "$managedRoot/.narrated-demo-owner.json")) { Write-JsonAtomic "$managedRoot/.narrated-demo-owner.json" @{app='narrated-demo';root=$managedRoot;schema_version=1} }
$version = (Get-Content -LiteralPath "$pluginRoot/plugin.json" -Raw | ConvertFrom-Json).version
$generation = [Guid]::NewGuid().ToString('N').Substring(0,8)
$installRoot = Get-SafeRoot (Join-Path $managedRoot "versions/$version-$generation")
New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
New-Item -ItemType Directory -Force -Path "$managedRoot/downloads" | Out-Null
$lock = [IO.File]::Open("$managedRoot/install.lock", 'OpenOrCreate', 'ReadWrite', 'None')
$savedEnv = @{}
foreach ($name in @('UV_PYTHON_INSTALL_DIR','UV_CACHE_DIR','UV_PYTHON_BIN_DIR','PLAYWRIGHT_BROWSERS_PATH')) { $savedEnv[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
try {
function Download-Verified($Url, $Name, $Hash) {
    $target = Join-Path $managedRoot "downloads/$Name"
    if ((Test-Path -LiteralPath $target) -and (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -eq $Hash) { return $target }
    & curl.exe --fail --location --silent --show-error --connect-timeout 30 --max-time 600 --retry 2 --output "$target.part" $Url
    if ($LASTEXITCODE -ne 0) { throw "Download falhou: $Name. Execute novamente para retomar a instalação." }
    if ((Get-FileHash -LiteralPath "$target.part" -Algorithm SHA256).Hash -ne $Hash) { throw "Checksum incorreto: $Name" }
    Move-Item -LiteralPath "$target.part" -Destination $target -Force
    return $target
}
function Run-Checked($Executable, $Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Falha ao executar $Executable (código $LASTEXITCODE). Execute novamente para retomar." }
}
$uvArchive = Download-Verified 'https://github.com/astral-sh/uv/releases/download/0.8.22/uv-x86_64-pc-windows-msvc.zip' 'uv.zip' '5049375aa2a5162f132b2c1cb992e25d42d47d934cab8c174dbe6f60973dcc12'
Expand-SafeArchive $uvArchive "$installRoot/uv"
$uv = (Get-ChildItem -LiteralPath "$installRoot/uv" -Filter uv.exe -Recurse | Select-Object -First 1).FullName
$env:UV_PYTHON_INSTALL_DIR = "$installRoot/python"
$env:UV_CACHE_DIR = "$managedRoot/cache"
$env:UV_PYTHON_BIN_DIR = "$installRoot/python-bin"
Run-Checked $uv @('python', 'install', '3.12.10')
Run-Checked $uv @('venv', '--python', '3.12.10', "$installRoot/venv", '--allow-existing')
$python = "$installRoot/venv/Scripts/python.exe"
Run-Checked $uv @('pip', 'sync', '--python', $python, '--require-hashes', "$pluginRoot/dependencies/requirements.lock")
$nodeArchive = Download-Verified 'https://nodejs.org/dist/v24.11.0/node-v24.11.0-win-x64.zip' 'node.zip' '1054540bce22b54ec7e50ebc078ec5d090700a77657607a58f6a64df21f49fdd'
Expand-SafeArchive $nodeArchive "$installRoot/node"
$nodeDir = "$installRoot/node/node-v24.11.0-win-x64"
$env:PLAYWRIGHT_BROWSERS_PATH = "$installRoot/browsers"
New-Item -ItemType Directory -Force -Path "$installRoot/node-deps" | Out-Null
Copy-Item -LiteralPath "$pluginRoot/dependencies/package.json" -Destination "$installRoot/node-deps/package.json" -Force
Copy-Item -LiteralPath "$pluginRoot/dependencies/package-lock.json" -Destination "$installRoot/node-deps/package-lock.json" -Force
Run-Checked "$nodeDir/node.exe" @("$nodeDir/node_modules/npm/bin/npm-cli.js", 'ci', '--prefix', "$installRoot/node-deps", '--no-audit', '--no-fund')
Run-Checked "$nodeDir/node.exe" @("$installRoot/node-deps/node_modules/playwright/cli.js", 'install', 'chromium')
$mediaArchive = Download-Verified 'https://github.com/GyanD/codexffmpeg/releases/download/9.0.2/ffmpeg-9.0.2-essentials_build.zip' 'ffmpeg-9.0.2.zip' '60f467265b1e312373dbcd92200c2618a74850f98d3d078e94296bb3fa2047ba'
Expand-SafeArchive $mediaArchive "$installRoot/media"
$mediaBin = "$installRoot/media/ffmpeg-9.0.2-essentials_build/bin"
$model = Download-Verified 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx' 'kokoro-v1.0.onnx' 'beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a'
$voices = Download-Verified 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin' 'voices-v1.0.bin' 'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d'
$config = @{schema_version=1; version=$version; python=$python; node="$nodeDir/node.exe"; node_deps="$installRoot/node-deps"; browsers=$env:PLAYWRIGHT_BROWSERS_PATH; model=$model; voices=$voices; ffmpeg="$mediaBin/ffmpeg.exe"; ffprobe="$mediaBin/ffprobe.exe"}
Write-JsonAtomic "$installRoot/runtime.json" $config
Run-Checked $python @("$pluginRoot/app/runtime.py", 'doctor', '--runtime', "$installRoot/runtime.json")
if (Test-Path -LiteralPath "$managedRoot/runtime.json") { Copy-Item -LiteralPath "$managedRoot/runtime.json" -Destination "$managedRoot/previous-runtime.json" -Force }
Write-JsonAtomic "$managedRoot/runtime.json" $config
Write-Host "Dependencias instaladas. Configuracao: $managedRoot/runtime.json"
Write-Host 'Codex integration and audiovisual review are separate steps.'
} finally {
    foreach ($name in $savedEnv.Keys) { [Environment]::SetEnvironmentVariable($name, $savedEnv[$name], 'Process') }
    $lock.Dispose()
}
