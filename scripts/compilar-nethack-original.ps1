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
  $ok = $false
  for ($attempt = 1; $attempt -le 2 -and -not $ok; $attempt++) {
    if (Test-Path -LiteralPath $Destination) {
      Remove-Item -LiteralPath $Destination -Force
    }
    if (Get-Command 'curl.exe' -ErrorAction SilentlyContinue) {
      & curl.exe --fail --location --retry 1 --retry-delay 2 --connect-timeout 15 --max-time 55 --output $Destination $Uri
      $ok = ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $Destination))
    }
    if (-not $ok) {
      try {
        Invoke-WebRequest -Uri $Uri -OutFile $Destination -MaximumRedirection 10 -TimeoutSec 45
        $ok = (Test-Path -LiteralPath $Destination)
      } catch {
        Write-Warning ("Intento " + $attempt + ": " + $_.Exception.Message)
      }
    }
    if (-not $ok) { Start-Sleep -Seconds ($attempt * 2) }
  }
  if (-not $ok -or (Get-Item -LiteralPath $Destination).Length -lt 2048) {
    throw "No fue posible descargar la dependencia desde $Uri despues de varios intentos."
  }
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
    try {
      Fetch-Archive 'https://www.lua.org/ftp/lua-5.4.8.tar.gz' $archive
      & tar.exe -xf $archive -C $libDir
      if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $lua)) {
        throw 'El tarball oficial de Lua no se extrajo correctamente.'
      }
    } catch {
      # Respaldo versionado y verificable: tag v5.4.8 del repositorio Lua.
      Write-Warning 'Utilizando el respaldo de Lua v5.4.8 en GitHub.'
      $archive = Join-Path $temp 'lua-source-v5.4.8.zip'
      Fetch-Archive 'https://codeload.github.com/lua/lua/zip/refs/tags/v5.4.8' $archive
      $unpackedLua = Join-Path $temp 'lua-github'
      Expand-Archive -LiteralPath $archive -DestinationPath $unpackedLua -Force
      $sourceLua = Get-ChildItem -LiteralPath $unpackedLua -Directory | Select-Object -First 1
      if ($null -eq $sourceLua) { throw 'El respaldo no contiene fuentes Lua.' }
      $targetLua = Join-Path $libDir 'lua-5.4.8\src'
      New-Item -ItemType Directory -Path $targetLua -Force | Out-Null
      Copy-Item -Path (Join-Path $sourceLua.FullName '*') -Destination $targetLua -Recurse -Force
      if (-not (Test-Path -LiteralPath $lua)) { throw 'No apareció lua.h en el respaldo.' }
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

# Limpiar binarios del prototipo, sin tocar partidas guardadas ni datos.
foreach ($oldName in @('nethack-bald.exe','nethack-bald-multi.exe')) {
  $oldExe = Join-Path $outputDir $oldName
  if (Test-Path -LiteralPath $oldExe) {
    Move-Item -LiteralPath $oldExe -Destination ($oldExe + '.obsoleto') -Force
  }
}

Expand-Archive -LiteralPath $packages[0].FullName -DestinationPath $outputDir -Force

# Es el NetHackW original del subsistema GRAFICO Win32, no un ejecutable
# de consola. Cambiamos su nombre para que el usuario abra el correcto.
$graphicExe = Join-Path $outputDir 'NetHackW.exe'
$gameExe = Join-Path $outputDir 'nethack-bald.exe'
if (-not (Test-Path -LiteralPath $graphicExe)) {
  throw "No se encontro NetHackW.exe en el paquete original."
}
Move-Item -LiteralPath $graphicExe -Destination $gameExe -Force

# Retirar el otro ejecutable original (NetHack.exe es de consola).
# No es necesario ni deseable en una distribucion grafica.
$consoleExe = Join-Path $outputDir 'NetHack.exe'
if (Test-Path -LiteralPath $consoleExe) {
  Remove-Item -LiteralPath $consoleExe -Force
}

# Verificar en el encabezado PE que el programa es GUI (subsystem = 2)
# en vez de CUI/console (subsystem = 3).
$binary = [IO.File]::ReadAllBytes($gameExe)
if ($binary.Length -lt 512) { throw 'Ejecutable grafico demasiado pequeno.' }
$peOffset = [BitConverter]::ToInt32($binary, 0x3c)
if ($peOffset -lt 64 -or $peOffset -gt ($binary.Length - 96)) {
  throw 'Encabezado PE invalido.'
}
$subsystem = [BitConverter]::ToUInt16($binary, $peOffset + 24 + 68)
if ($subsystem -ne 2) {
  throw "El ejecutable no es grafico. PE subsystem=$subsystem"
}

# NetHack-es contiene traducciones en es.po. La importacion anterior
# no lo convertia a .mo ni lo incluia en los binarios Windows.
$po = Join-Path $gameDir 'po\es.po'
$mo = Join-Path $outputDir 'locale\es\LC_MESSAGES\nethack.mo'
& (Join-Path $rootDir 'scripts\compilar-traduccion.ps1') -Po $po -Mo $mo
if (-not (Test-Path -LiteralPath $mo)) {
  throw 'No se genero el catalogo espanol nethack.mo.'
}

Write-Host ''
Write-Host 'Compilacion completada del NetHack ORIGINAL con ventana propia en Windows.' -ForegroundColor Green
Write-Host "Abrir: $gameExe"
Write-Host "Traduccion incluida: $mo"
Write-Host 'El catalogo disponible NO cubre aun el 100% del juego.' -ForegroundColor Yellow
Write-Host 'El multijugador 2-6 sigue pendiente en el motor original.' -ForegroundColor Yellow
