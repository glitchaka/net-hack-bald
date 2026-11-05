# Windows nativo: descargar/actualizar y compilar NET-HACK ORIGINAL.
# Genera build/Release/NetHackW.exe. No inicia el prototipo de consola.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
try {
    foreach ($program in @('git.exe', 'cmake.exe')) {
        if (-not (Get-Command $program -ErrorAction SilentlyContinue)) {
            throw "Falta $program en Windows."
        }
    }
    $project = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
    if (-not (Test-Path -LiteralPath (Join-Path $project '.git'))) {
        $project = Join-Path (Get-Location).Path 'net-hack-bald'
    }
    if (Test-Path -LiteralPath (Join-Path $project '.git')) {
        & git -C $project pull --ff-only
        if ($LASTEXITCODE -ne 0) { throw 'Git no pudo actualizar el repositorio.' }
    } elseif (-not (Test-Path -LiteralPath $project)) {
        & git clone https://github.com/glitchaka/net-hack-bald.git $project
        if ($LASTEXITCODE -ne 0) { throw 'Git no pudo descargar el repositorio.' }
    } else {
        throw "La carpeta $project existe sin un repositorio Git."
    }
    $build = Join-Path $project 'build'
    & cmake -S $project -B $build
    if ($LASTEXITCODE -ne 0) { throw 'Falló la configuración de CMake.' }
    & cmake --build $build --config Release
    if ($LASTEXITCODE -ne 0) { throw 'Falló la compilación del NetHack original.' }
    $exe = Join-Path $build 'Release\NetHackW.exe'
    if (-not (Test-Path -LiteralPath $exe)) { throw "No se generó $exe" }
    Write-Host "NetHack original gráfico listo: $exe" -ForegroundColor Green
    Write-Host 'Permite jugar solo. El multijugador original todavía está pendiente.'
} catch {
    Write-Host ("ERROR: " + $_.Exception.Message) -ForegroundColor Red
} finally {
    Read-Host 'Pulsa Intro para cerrar'
}
