# Compilar un catalogo gettext .po a .mo utilizando PowerShell 5.1/.NET.
# No requiere Python, gettext ni paquetes externos.
param(
    [Parameter(Mandatory = $true)][string]$Po,
    [Parameter(Mandatory = $true)][string]$Mo
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Decode-PoString([string]$line) {
    # Las cadenas .po son cadenas entre comillas con escapes estilo JSON.
    # En un caso de los datos importados aparece un ESC literal.
    $json = $line.Replace([string][char]27, '\u001b')
    try {
        return [string](ConvertFrom-Json -InputObject $json)
    } catch {
        throw "Literal de .po mal formado: $line"
    }
}

$catalog = New-Object 'System.Collections.Generic.Dictionary[string,string]' ([StringComparer]::Ordinal)
[string]$id = ''
[string]$translated = ''
[string]$section = ''
[bool]$hasId = $false
[bool]$fuzzy = $false

function Add-Entry {
    if ($script:hasId -and -not $script:fuzzy -and
        $script:id.Length -gt 0 -and $script:translated.Length -gt 0) {
        $script:catalog[$script:id] = $script:translated
    }
    $script:id = ''
    $script:translated = ''
    $script:section = ''
    $script:hasId = $false
    $script:fuzzy = $false
}

foreach ($line in [IO.File]::ReadLines([IO.Path]::GetFullPath($Po), [Text.Encoding]::UTF8)) {
    $part = $line.Trim()
    if ($part.Length -eq 0) {
        Add-Entry
    } elseif ($part -match '^#,\s*.*\bfuzzy\b') {
        $fuzzy = $true
    } elseif ($part -match '^msgid\s+(".*")$') {
        if ($hasId) { Add-Entry }
        $id = Decode-PoString $Matches[1]
        $hasId = $true
        $section = 'id'
    } elseif ($part -match '^msgstr\s+(".*")$') {
        $translated = Decode-PoString $Matches[1]
        $section = 'translated'
    } elseif ($part -match '^(".*")$') {
        if ($section -eq 'id') {
            $id += Decode-PoString $Matches[1]
        } elseif ($section -eq 'translated') {
            $translated += Decode-PoString $Matches[1]
        }
    }
}
Add-Entry

if ($catalog.Count -lt 1000) {
    throw "El catalogo solo contiene $($catalog.Count) traducciones; el archivo .po no se interpreto correctamente."
}

[string[]]$keys = @($catalog.Keys)
[Array]::Sort($keys, [StringComparer]::Ordinal)
$encoding = New-Object System.Text.UTF8Encoding($false)
$originals = New-Object 'System.Collections.Generic.List[byte[]]'
$translations = New-Object 'System.Collections.Generic.List[byte[]]'
foreach ($key in $keys) {
    $originals.Add($encoding.GetBytes($key))
    $translations.Add($encoding.GetBytes($catalog[$key]))
}

$folder = Split-Path -Parent ([IO.Path]::GetFullPath($Mo))
New-Item -ItemType Directory -Path $folder -Force | Out-Null
$writer = New-Object System.IO.BinaryWriter(
    ([IO.File]::Open($Mo, [IO.FileMode]::Create)),
    $encoding
)
try {
    $count = $keys.Length
    $firstTable = 28
    $secondTable = 28 + $count * 8
    $originalBytes = 28 + $count * 16
    $translationBytes = $originalBytes
    foreach ($item in $originals) { $translationBytes += $item.Length + 1 }

    # GNU gettext .mo: little-endian header, longitud/offset de cada
    # msgid, longitud/offset de cada msgstr, y cadenas NUL-terminated.
    $writer.Write([uint32]0x950412de)
    $writer.Write([uint32]0)
    $writer.Write([uint32]$count)
    $writer.Write([uint32]$firstTable)
    $writer.Write([uint32]$secondTable)
    $writer.Write([uint32]0)
    $writer.Write([uint32]0)

    $offset = $originalBytes
    foreach ($bytes in $originals) {
        $writer.Write([uint32]$bytes.Length)
        $writer.Write([uint32]$offset)
        $offset += $bytes.Length + 1
    }
    $offset = $translationBytes
    foreach ($bytes in $translations) {
        $writer.Write([uint32]$bytes.Length)
        $writer.Write([uint32]$offset)
        $offset += $bytes.Length + 1
    }
    foreach ($bytes in $originals) {
        $writer.Write($bytes)
        $writer.Write([byte]0)
    }
    foreach ($bytes in $translations) {
        $writer.Write($bytes)
        $writer.Write([byte]0)
    }
} finally {
    $writer.Dispose()
}
Write-Host ("Traducciones empaquetadas: {0} -> {1}" -f $catalog.Count, $Mo)
