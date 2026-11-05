# NetHack Bald — instalador Windows PowerShell mediante WSL Ubuntu.
# Compila los binarios Linux dentro de WSL. No inicia el juego.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Write-Host 'NetHack Bald - Descargar y compilar con WSL (Ubuntu)' -ForegroundColor Cyan

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw 'WSL no está instalado. En PowerShell administrador: wsl --install -d Ubuntu; reinicia si se solicita.'
}

$command = @'
set -Eeuo pipefail
if ! command -v apt-get >/dev/null 2>&1; then
    echo "ERROR: instala y configura Ubuntu en WSL." >&2
    exit 1
fi
sudo apt-get update
sudo apt-get install -y git ca-certificates curl
mkdir -p "$HOME/proyectos"
cd "$HOME/proyectos"
if [ -d "net-hack-bald/.git" ]; then
    git -C net-hack-bald pull --ff-only
elif [ -e "net-hack-bald" ]; then
    echo "ERROR: ~/proyectos/net-hack-bald existe sin Git." >&2
    exit 1
else
    git clone --depth 1 --branch main https://github.com/glitchaka/net-hack-bald.git
fi
cd net-hack-bald
bash scripts/instalar_y_compilar.sh
'@

$command = $command.Replace([string][char]13, "")
& wsl.exe bash -lc $command
if ($LASTEXITCODE -ne 0) {
    throw "WSL falló con código $LASTEXITCODE. Revisa el error de la terminal."
}

Write-Host ''
Write-Host 'Compilación completada dentro de WSL.' -ForegroundColor Green
Write-Host 'Para jugar con la traducción disponible:'
Write-Host 'wsl.exe bash -lc ''cd ~/proyectos/net-hack-bald/upstream/nethack/playground && LANG=es.UTF-8 ./nethack'''
Write-Host ''
Write-Host 'ATENCIÓN: el modo de 2-6 personajes no está integrado todavía.' -ForegroundColor Yellow
