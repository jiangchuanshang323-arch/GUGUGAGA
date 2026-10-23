$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$destination = 'F:\GUGUGAGA_Backup_20261023'
$branch = 'backup/download-20261023'
$repo = 'jiangchuanshang323-arch/GUGUGAGA'
$rawBase = "https://raw.githubusercontent.com/$repo/$branch/packages"
$mediaBase = "https://github.com/$repo/raw/refs/heads/$branch/packages"
try {
    if (-not (Test-Path 'F:\')) { throw 'F: drive was not found.' }
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    $zipDir = Join-Path $destination '_download_packages'
    New-Item -ItemType Directory -Force -Path $zipDir | Out-Null
    $manifestPath = Join-Path $zipDir 'manifest.json'
    Invoke-WebRequest -UseBasicParsing -Uri "$rawBase/manifest.json" -OutFile $manifestPath
    $manifest = Get-Content -Raw -Encoding UTF8 $manifestPath | ConvertFrom-Json
    $required = ([long](($manifest.packages | Measure-Object bytes -Sum).Sum) + [long](($manifest.files | Measure-Object bytes -Sum).Sum))
    if ((Get-PSDrive F).Free -lt $required) { throw 'Insufficient free space on F:. Keep at least 14 GB free.' }
    $index = 0
    foreach ($package in $manifest.packages) {
        $index++
        $local = Join-Path $zipDir $package.name
        Write-Host "[$index/$($manifest.packages.Count)] Downloading $($package.name)"
        $valid = (Test-Path $local) -and ((Get-Item $local).Length -eq $package.bytes)
        if ($valid) { $valid = ((Get-FileHash -Algorithm SHA256 $local).Hash.ToLower() -eq $package.sha256) }
        if (-not $valid) {
            if ((Test-Path $local) -and (Get-Item $local).Length -ge $package.bytes) { Remove-Item -LiteralPath $local }
            & curl.exe --fail --location --retry 5 --retry-delay 3 --continue-at - --output $local "$mediaBase/$($package.name)"
            if ($LASTEXITCODE -ne 0) { throw 'Download failed. Check your connection and run this script again. A private repository may require downloading in your signed-in browser.' }
            if ((Get-Item $local).Length -ne $package.bytes -or (Get-FileHash -Algorithm SHA256 $local).Hash.ToLower() -ne $package.sha256) { throw "Checksum mismatch: $($package.name)" }
        }
        Write-Host "Extracting $($package.name)"
        Expand-Archive -LiteralPath $local -DestinationPath $destination -Force
    }
    Write-Host 'Checking extracted files...'
    foreach ($file in $manifest.files) {
        $p = Join-Path $destination ($file.path.Replace('/', '\'))
        if (-not (Test-Path -LiteralPath $p) -or (Get-Item -LiteralPath $p).Length -ne $file.bytes) { throw "Missing or incomplete file: $($file.path)" }
    }
    Write-Host "DONE: $destination" -ForegroundColor Green
    Start-Process explorer.exe -ArgumentList $destination
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host 'The backup is NOT complete. Keep the downloaded packages and run again.'
} finally {
    Read-Host 'Press Enter to close'
}
