param([string]$Destination = "$env:LOCALAPPDATA/NarratedDemo/runtime", [switch]$AcceptDownloads)
$ErrorActionPreference = 'Stop'
if (-not [Environment]::Is64BitOperatingSystem) { throw 'Windows x64 é necessário.' }
if (-not $AcceptDownloads -and (Read-Host 'Baixar Python, Node, Chromium, bibliotecas e modelos locais? Digite SIM') -ne 'SIM') { throw 'Instalação cancelada.' }
$installRoot = [IO.Path]::GetFullPath($Destination)
if ($installRoot -eq [IO.Path]::GetPathRoot($installRoot)) { throw 'Destino inválido.' }
New-Item -ItemType Directory -Force -Path $installRoot | Out-Null
function Download-Verified($Url, $Name, $Hash) {
    $target = Join-Path $installRoot $Name
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
Expand-Archive -LiteralPath $uvArchive -DestinationPath "$installRoot/uv" -Force
$uv = (Get-ChildItem -LiteralPath "$installRoot/uv" -Filter uv.exe -Recurse | Select-Object -First 1).FullName
$env:UV_PYTHON_INSTALL_DIR = "$installRoot/python"
$env:UV_CACHE_DIR = "$installRoot/cache"
$env:UV_PYTHON_BIN_DIR = "$installRoot/python-bin"
Run-Checked $uv @('python', 'install', '3.12.10')
Run-Checked $uv @('venv', '--python', '3.12.10', "$installRoot/venv", '--allow-existing')
$python = "$installRoot/venv/Scripts/python.exe"
$sourceRoot = Split-Path $PSScriptRoot -Parent
$skill = "$sourceRoot/plugins/narrated-demo/skills/narrated-demo"
Run-Checked $uv @('pip', 'install', '--python', $python, '-r', "$skill/assets/requirements.txt")
$nodeArchive = Download-Verified 'https://nodejs.org/dist/v24.11.0/node-v24.11.0-win-x64.zip' 'node.zip' '1054540bce22b54ec7e50ebc078ec5d090700a77657607a58f6a64df21f49fdd'
Expand-Archive -LiteralPath $nodeArchive -DestinationPath "$installRoot/node" -Force
$nodeDir = "$installRoot/node/node-v24.11.0-win-x64"
$env:PLAYWRIGHT_BROWSERS_PATH = "$installRoot/browsers"
Run-Checked "$nodeDir/node.exe" @("$nodeDir/node_modules/npm/bin/npm-cli.js", 'install', '--prefix', "$installRoot/node-deps", '--no-audit', '--no-fund', 'playwright@1.63.0', 'ffmpeg-static@5.2.0', 'ffprobe-static@3.1.0')
Run-Checked "$nodeDir/node.exe" @("$installRoot/node-deps/node_modules/playwright/cli.js", 'install', 'chromium')
$model = Download-Verified 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx' 'kokoro-v1.0.onnx' 'beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a'
$voices = Download-Verified 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin' 'voices-v1.0.bin' 'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d'
@{schema_version=1; python=$python; node="$nodeDir/node.exe"; node_deps="$installRoot/node-deps"; browsers=$env:PLAYWRIGHT_BROWSERS_PATH; model=$model; voices=$voices; ffmpeg="$installRoot/node-deps/node_modules/ffmpeg-static/ffmpeg.exe"; ffprobe="$installRoot/node-deps/node_modules/ffprobe-static/bin/win32/x64/ffprobe.exe"} | ConvertTo-Json | Set-Content -LiteralPath "$installRoot/runtime.json" -Encoding UTF8
Write-Host "Dependências instaladas. Configuração: $installRoot/runtime.json"
Write-Host 'A instalação da integração Codex e a revisão audiovisual são etapas separadas.'
