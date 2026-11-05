#!/usr/bin/env python3
"""
translate_lua.py
Traduce archivos Lua de NetHack usando LibreTranslate local.
Crea archivos .lua.es que son cargados automáticamente por dlb_fopen.
"""

import requests
import re
import os
import json
import sys
import time

LIBRETRANSLATE_URL = "http://localhost:5000/translate"


def traducir(texto, source="en", target="es"):
    """Envía texto a LibreTranslate y devuelve traducción"""
    if not texto.strip():
        return texto
    try:
        resp = requests.post(
            LIBRETRANSLATE_URL,
            json={"q": texto, "source": source, "target": target},
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json().get("translatedText", texto)
        else:
            print(f"  ⚠️  Error HTTP {resp.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"  ❌ No se puede conectar a LibreTranslate en {LIBRETRANSLATE_URL}")
        print("  💡 Asegúrate de que el contenedor Docker esté funcionando:")
        print("     docker start libretranslate")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def post_editar(traduccion):
    """Correcciones post-traducción para NetHack"""
    # Aplicar después de la traducción para corregir términos específicos
    traduccion = re.sub(
        r"(?i)Dungeons?\s+of\s+Doom", "Mazmorras de la Perdición", traduccion
    )
    traduccion = re.sub(r"(?i)Elemental\s+Planes?\b", "Planos Elementales", traduccion)
    traduccion = re.sub(
        r"(?i)Planes?\s+Elementales?\b", "Planos Elementales", traduccion
    )
    traduccion = re.sub(r"(?i)Gnomish\s+Mines?\b", "Minas de los Gnomos", traduccion)
    traduccion = re.sub(
        r"(?i)Vlad\s*\'\s*s\s+W*[Tt]ower\b", "Torre de Vlad", traduccion
    )
    traduccion = re.sub(r"(?i)Vlad's?\s+[Tt]ower\b", "Torre de Vlad", traduccion)
    traduccion = re.sub(r"(?i)Fort\s+Ludios\b", "Fortaleza Ludios", traduccion)
    traduccion = re.sub(r"(?i)\bQuest\b", "Misión", traduccion)
    traduccion = re.sub(r"(?i)\bTutorial\b", "Tutorial", traduccion)
    traduccion = re.sub(r"(?i)\bthe\s+", "", traduccion)
    traduccion = re.sub(r"(?i)\bThe\s+", "", traduccion)
    return traduccion


def es_frase_traducible(texto):
    """Determina si un texto debe ser traducido"""
    # Demasiado corto
    if len(texto) < 3:
        return False

    # Nombres de archivo (contienen extensión)
    if ".lua" in texto.lower() or ".txt" in texto.lower():
        return False

    # Identificadores de Lua (solo letras minúsculas y _)
    if re.match(r"^[a-z_][a-z_0-9]*$", texto):
        return False

    # Constantes (mayúsculas y _)
    if re.match(r"^[A-Z_][A-Z_0-9]*$", texto):
        return False

    # Nombres de nivel como "soko1", "tower1", "wizard1", etc.
    if re.match(r"^[a-z]+-?\d+$", texto) or re.match(r"^[a-z]+\d+$", texto):
        return False

    # Nombres propios de NetHack (personajes, lugares específicos)
    nethack_names = [
        "Gehennom",
        "Sokoban",
        "Fort Ludios",
        "Vlad",
        "fakewiz",
        "soko1",
        "soko2",
        "soko3",
        "soko4",
        "tower1",
        "tower2",
        "tower3",
        "wizard1",
        "wizard2",
        "wizard3",
        "tut-1",
        "tut-2",
        "x-goal",
        "x-loca",
        "x-strt",
        "the",
        "The",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "at",
    ]
    if texto.strip() in nethack_names:
        return False

    # Archivos de quest por rol
    for role in [
        "Arc",
        "Bar",
        "Cav",
        "Hea",
        "Kni",
        "Mon",
        "Pri",
        "Ran",
        "Rog",
        "Sam",
        "Tou",
        "Val",
        "Wiz",
    ]:
        for suffix in ["fila", "filb", "goal", "loca", "strt"]:
            if texto == f"{role}-{suffix}":
                return False

    # Ya está en español (contiene acentos)
    if re.search(r"[áéíóúñÁÉÍÓÚÑ]", texto):
        return False

    # Tiene placeholders de formato NetHack
    if re.search(r"%[pcrRsSlioOngGHaAdDeCxZNLA%]", texto):
        return False

    # Empieza con caracteres especiales de NetHack
    if texto.startswith("\\") or texto.startswith("#"):
        return False

    return True


def extraer_textos_lua(contenido):
    """
    Extrae strings traducibles de un archivo Lua.
    Devuelve lista de (linea_inicio, linea_fin, texto_original)
    """
    textos = []
    lineas = contenido.split("\n")

    i = 0
    while i < len(lineas):
        linea = lineas[i]
        stripped = linea.strip()

        # Saltar comentarios de una línea
        if stripped.startswith("--"):
            i += 1
            continue

        # Buscar strings entre comillas dobles
        for match in re.finditer(r'"([^"]+)"', linea):
            texto = match.group(1)
            if es_frase_traducible(texto):
                textos.append((i, i, texto))

        # Buscar strings entre [[ y ]]
        if "[[" in linea:
            inicio_texto = linea.index("[[") + 2
            if "]]" in linea[inicio_texto:]:
                texto = linea[inicio_texto : linea.index("]]", inicio_texto)]
                if es_frase_traducible(texto):
                    textos.append((i, i, texto))
            else:
                # Multilínea
                texto = linea[inicio_texto:] + "\n"
                j = i + 1
                while j < len(lineas):
                    if "]]" in lineas[j]:
                        texto += lineas[j][: lineas[j].index("]]")]
                        if es_frase_traducible(texto):
                            textos.append((i, j, texto))
                        break
                    texto += lineas[j] + "\n"
                    j += 1
                i = j

        i += 1

    return textos


def traducir_archivo_lua(ruta_original):
    """Traduce un archivo Lua y crea su versión .es"""
    print(f"\n📄 Procesando: {os.path.basename(ruta_original)}")

    with open(ruta_original, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Extraer textos
    textos = extraer_textos_lua(contenido)
    print(f"   📝 {len(textos)} strings encontrados")

    if not textos:
        print("   ⏩ Sin textos para traducir")
        return

    # Traducir cada texto (sin duplicados)
    traducidos = {}
    stats = {"ok": 0, "err": 0, "skip": 0}

    # Ordenar por línea (de abajo a arriba para no alterar índices)
    textos_ordenados = sorted(set((t[2] for t in textos)))

    for texto_original in textos_ordenados:
        if texto_original in traducidos:
            continue

        # Saltar strings que parecen ya traducidos
        if any(c in texto_original for c in "áéíóúñÁÉÍÓÚÑ"):
            stats["skip"] += 1
            continue

        # Saltar placeholders de NetHack
        if re.search(r"%[pcrRsSlioOngGHaAdDeCxZNLA%]", texto_original):
            stats["skip"] += 1
            continue

        # Saltar formatos de NetHack
        if texto_original.startswith("\\") or texto_original.startswith("#"):
            stats["skip"] += 1
            continue

        print(
            f"   🌐 Traduciendo [{stats['ok'] + 1}/{len(textos_ordenados)}]: '{texto_original[:50]}...'",
            end=" ",
        )
        sys.stdout.flush()

        traduccion = traducir(texto_original)
        if traduccion:
            traduccion = post_editar(traduccion)
            traducidos[texto_original] = traduccion
            stats["ok"] += 1
            print(f" ✅ -> '{traduccion[:50]}...'")
        else:
            stats["err"] += 1
            print(" ❌")

        # Pequeña pausa para no sobrecargar LibreTranslate
        time.sleep(0.5)

    print(
        f"\n   📊 Resultado: {stats['ok']} traducidos, {stats['skip']} saltados, {stats['err']} errores"
    )

    if stats["ok"] == 0:
        print("   ⏩ Sin traducciones nuevas")
        return

    # Aplicar traducciones al contenido
    nuevo_contenido = contenido
    for original, traduccion in reversed(list(traducidos.items())):
        if original in nuevo_contenido and traduccion:
            nuevo_contenido = nuevo_contenido.replace(
                f'"{original}"', f'"{traduccion}"'
            )
            nuevo_contenido = nuevo_contenido.replace(
                f"[[{original}]]", f"[[{traduccion}]]"
            )

    # Guardar archivo .es
    ruta_es = ruta_original + ".es"
    with open(ruta_es, "w", encoding="utf-8") as f:
        f.write(nuevo_contenido)

    print(f"   💾 Guardado: {os.path.basename(ruta_es)}")


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 translate_lua.py <archivo.lua> [archivo2.lua ...]")
        print("  O:  python3 translate_lua.py --all  (traduce todos los Lua)")
        print("  O:  python3 translate_lua.py --priority  (solo los más importantes)")
        return

    dat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dat")

    if sys.argv[1] == "--all":
        archivos = sorted([f for f in os.listdir(dat_dir) if f.endswith(".lua")])
        archivos = [os.path.join(dat_dir, f) for f in archivos]
    elif sys.argv[1] == "--priority":
        # Archivos prioritarios con más texto visible
        priority = [
            "dungeon.lua",  # Nombres de ramas de la mazmorra
            "themerms.lua",  # Descripciones de habitaciones temáticas
            "tut-1.lua",  # Tutorial
            "tut-2.lua",  # Tutorial
            "nhcore.lua",  # Textos del core
            "nhlib.lua",  # Librería con textos
        ]
        archivos = [
            os.path.join(dat_dir, f)
            for f in priority
            if os.path.exists(os.path.join(dat_dir, f))
        ]
    else:
        archivos = sys.argv[1:]

    print(f"🎯 Traduciendo {len(archivos)} archivos Lua...")
    print("═" * 60)

    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"❌ No encontrado: {archivo}")
            continue

        # Saltar si ya existe .es (ya traducido)
        if os.path.exists(archivo + ".es"):
            print(f"⏩ Ya existe traducción: {os.path.basename(archivo)}.es")
            continue

        traducir_archivo_lua(archivo)
        print("─" * 40)

    print("\n✅ Proceso completado")


if __name__ == "__main__":
    main()
