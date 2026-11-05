# NetHack original 5.0 en Windows: motor real, GUI Win32 y juego individual.
# Este archivo no compila el prototipo alternativo de terminal.
param(
  [Parameter(Mandatory = $true)][string]$Root,
  [ValidateSet('Release','Debug')][string]$Configuration = 'Release',
  [ValidateSet('x64','Win32','ARM64')][string]$Platform = 'x64'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ProgressPreference = 'SilentlyContinue'

$rootDir = [IO.Path]::GetFullPath($Root)
$gameDir = Join-Path $rootDir 'upstream\nethack'
$solution = Join-Path $gameDir 'sys\windows\vs\NetHack.sln'
if (-not (Test-Path -LiteralPath $solution)) {
  throw "No se encontro la solucion original de NetHack: $solution"
}

function Find-MSBuild {
  $command = Get-Command 'MSBuild.exe' -ErrorAction SilentlyContinue
  if ($null -ne $command) { return $command.Source }
  $pf86 = [Environment]::GetFolderPath([Environment+SpecialFolder]::ProgramFilesX86)
  $vswhere = Join-Path $pf86 'Microsoft Visual Studio\Installer\vswhere.exe'
  if (-not (Test-Path -LiteralPath $vswhere)) {
    throw 'No se encontro MSBuild. Instala Visual Studio/Build Tools con Desarrollo de escritorio con C++.'
  }
  $installation = & $vswhere -latest -products '*' -requires Microsoft.Component.MSBuild -property installationPath
  if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($installation)) {
    throw 'No hay instalacion disponible de MSBuild.'
  }
  $candidate = Join-Path ($installation | Select-Object -First 1) 'MSBuild\Current\Bin\MSBuild.exe'
  if (-not (Test-Path -LiteralPath $candidate)) { throw "MSBuild no existe en $candidate" }
  return $candidate
}

function Fetch-Archive([string]$Uri, [string]$Destination) {
  Write-Host "Descargando: $Uri" -ForegroundColor DarkCyan
  Invoke-WebRequest -Uri $Uri -OutFile $Destination -MaximumRedirection 10
  if (-not (Test-Path -LiteralPath $Destination)) { throw "No se pudo descargar $Uri" }
}

Write-Host 'Preparando NetHack 5.0 grafico original para Windows' -ForegroundColor Cyan
$msbuild = Find-MSBuild
$libDir = Join-Path $gameDir 'lib'
New-Item -ItemType Directory -Path $libDir -Force | Out-Null
$temp = Join-Path ([IO.Path]::GetTempPath()) ('nethack-prereq-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temp -Force | Out-Null
try {
  $lua = Join-Path $libDir 'lua-5.4.8\src\lua.h'
  if (-not (Test-Path -LiteralPath $lua)) {
    $archive = Join-Path $temp 'lua-5.4.8.tar.gz'
    Fetch-Archive 'https://www.lua.org/ftp/lua-5.4.8.tar.gz' $archive
    & tar.exe -xf $archive -C $libDir
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $lua)) {
      throw 'Error al extraer Lua 5.4.8.'
    }
  }

  $pdc = Join-Path $libDir 'pdcursesmod\curses.h'
  if (-not (Test-Path -LiteralPath $pdc)) {
    $archive = Join-Path $temp 'pdcursesmod.zip'
    Fetch-Archive 'https://github.com/Bill-Gray/PDCursesMod/archive/refs/tags/v4.4.0.zip' $archive
    $unpacked = Join-Path $temp 'pdcurses'
    Expand-Archive -LiteralPath $archive -DestinationPath $unpacked -Force
    $source = Get-ChildItem -LiteralPath $unpacked -Directory | Select-Object -First 1
    if ($null -eq $source) { throw 'Archivo PDCurses sin carpeta de codigo fuente.' }
    $target = Join-Path $libDir 'pdcursesmod'
    if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
    Move-Item -LiteralPath $source.FullName -Destination $target
    if (-not (Test-Path -LiteralPath $pdc)) { throw 'No se encontro curses.h.' }
  }
} finally {
  if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}

Write-Host 'Compilando NetHackW.exe (ventana grafica y sprites originales)' -ForegroundColor Cyan
& $msbuild $solution '/t:Build' '/m:1' '/nologo' '/v:minimal' "/p:Configuration=$Configuration" "/p:Platform=$Platform"
if ($LASTEXITCODE -ne 0) { throw 'Fallo la compilacion de NetHack original.' }

$packageDir = Join-Path $gameDir 'vspackage'
$packages = @(Get-ChildItem -LiteralPath $packageDir -Filter '*.zip' -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like ('*win-' + $Platform + '.zip') } | Sort-Object LastWriteTime -Descending)
if ($packages.Count -lt 1) { throw 'No se genero el paquete original de NetHack con datos y tiles.' }
$outputDir = Join-Path $rootDir ('build\' + $Configuration)
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

foreach ($oldName in @('nethack-bald.exe','nethack-bald-multi.exe')) {
  $oldExe = Join-Path $outputDir $oldName
  if (Test-Path -LiteralPath $oldExe) {
    Move-Item -LiteralPath $oldExe -Destination ($oldExe + '.obsoleto') -Force
  }
}

Expand-Archive -LiteralPath $packages[0].FullName -DestinationPath $outputDir -Force
$gameExe = Join-Path $outputDir 'NetHackW.exe'
if (-not (Test-Path -LiteralPath $gameExe)) { throw "No se encontro $gameExe" }
Write-Host 'NetHack original compilado con interfaz Win32 para un jugador.' -ForegroundColor Green
Write-Host "Ejecutable: $gameExe"
Write-Host 'Pendiente: traduccion 100% y multijugador original de seis personajes.' -ForegroundColor Yellow
