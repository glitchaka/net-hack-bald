# NetHack Bald — instalador NATIVO para Windows 10/11.
# Utiliza Git, CMake y un compilador C++17 instalado en Windows.
# NO utiliza Ubuntu, WSL ni PowerShell remoto.
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

try {
    Write-Host "NET-HACK BALD - Compilacion para Windows" -ForegroundColor Cyan

    foreach ($tool in @("git.exe", "cmake.exe")) {
        if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
            throw "No se encontro $tool. Instala Git for Windows y CMake."
        }
    }

    $repository = "https://github.com/glitchaka/net-hack-bald.git"
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $project = Split-Path -Parent $scriptDir

    # Si se ejecuta desde el repositorio, usar ese repositorio.
    # Si se ejecuta el .ps1 descargado fuera del repo, clonar a una
    # carpeta net-hack-bald junto al script.
    if (-not (Test-Path -LiteralPath (Join-Path $project "CMakeLists.txt"))) {
        $project = Join-Path (Get-Location).Path "net-hack-bald"
    }

    if (Test-Path -LiteralPath (Join-Path $project ".git")) {
        Write-Host "Actualizando $project..."
        & git -C $project pull --ff-only
        if ($LASTEXITCODE -ne 0) {
            throw "Git no pudo actualizar. Se conservaron tus cambios locales."
        }
    } else {
        if (Test-Path -LiteralPath $project) {
            throw "Existe la carpeta $project y no es un repositorio Git."
        }
        Write-Host "Clonando $repository..."
        & git clone --branch main $repository $project
        if ($LASTEXITCODE -ne 0) {
            throw "Fallo la descarga del repositorio."
        }
    }

    $buildDir = Join-Path $project "build"
    Write-Host "Configurando CMake (compilacion Windows nativa)..."
    & cmake -S $project -B $buildDir -DCMAKE_BUILD_TYPE=Release
    if ($LASTEXITCODE -ne 0) {
        throw "CMake no encontro un compilador compatible o fallo la configuracion."
    }

    Write-Host "Compilando el multijugador C++17 (2-6 personajes)..."
    & cmake --build $buildDir --config Release --parallel
    if ($LASTEXITCODE -ne 0) {
        throw "La compilacion C++ fallo. Los errores se muestran arriba."
    }

    $candidatePaths = @(
        (Join-Path $buildDir "Release\nethack-bald.exe"),
        (Join-Path $buildDir "nethack-bald.exe")
    )
    $exePath = $null
    foreach ($candidate in $candidatePaths) {
        if (Test-Path -LiteralPath $candidate) {
            $exePath = $candidate
            break
        }
    }
    if (-not $exePath) {
        throw "Compilacion terminada sin encontrar nethack-bald.exe."
    }
    Write-Host ""
    Write-Host "Compilacion Windows completada:" -ForegroundColor Green
    Write-Host $exePath -ForegroundColor Green
    Write-Host "Puedes abrir este EXE con doble clic: ahora incluye menu inicial."
    Write-Host ""
    Write-Host "NOTA: este es el motor multijugador C++ propio; la fidelidad"
    Write-Host "1:1 a NetHack, el spritesheet y la traduccion completa siguen pendientes."
} catch {
    Write-Host ""
    Write-Host ("ERROR: " + $_.Exception.Message) -ForegroundColor Red
    Write-Host "No se cerro la terminal para permitir revisar el error." -ForegroundColor Yellow
} finally {
    Write-Host ""
    Read-Host "Pulsa Intro para cerrar esta ventana"
}
