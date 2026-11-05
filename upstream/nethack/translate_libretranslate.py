#!/usr/bin/env python3
"""
translate_libretranslate.py
Traduce strings sin traducir en po/es.po usando LibreTranslate local
También corrige Spanglish básico en traducciones existentes (opcional)
"""

import requests
import re
import sys

LIBRETRANSLATE_URL = "http://localhost:5000/translate"


def traducir(texto, source="en", target="es"):
    """Envía texto a LibreTranslate y devuelve traducción"""
    try:
        resp = requests.post(
            LIBRETRANSLATE_URL,
            json={"q": texto, "source": source, "target": target},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("translatedText", texto)
        else:
            print(f"  ⚠️  Error HTTP {resp.status_code}: {resp.text}")
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
    """
    Correcciones post-traducción para evitar Spanglish común.
    Aplica solo a ciertos patrones conocidos.
    """
    correcciones = [
        # Verbos modales: "can" -> "poder" -> "puede"
        (r"\bhe can\b", "él puede"),
        (r"\bhe will\b", "él"),
        (r"\bhe was\b", "él estaba"),
        (r"\bit is\b", "es"),
        (r"\bit was\b", "era"),
        (r"\bye can\b", "puedes"),
        (r"\bye will\b", ""),
        (r"\byou are\b", "estás"),
        (r"\bthey are\b", "son"),
        (r"\bthey were\b", "eran"),
        # Artículos incorrectos
        (r"\bel Dios\b", "el dios"),
        (r"\bel dios\b", "el dios"),
        # "s" final extraña
        (r"\byous\b", "tú"),
        # Eliminar "the" suelto en medio de frases en español
        (r"\bthe\b", ""),
    ]
    for patron, reemplazo in correcciones:
        traduccion = re.sub(patron, reemplazo, traduccion, flags=re.IGNORECASE)
    return traduccion


def main():
    # 1. Leer el archivo .po
    with open("po/es.po", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 2. Identificar strings sin traducir o fuzzy
    stats = {"traducidos": 0, "fuzzy": 0, "vacios": 0, "errores": 0}
    cambios = 0

    print("🔍 Analizando archivo po/es.po...")

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detectar msgstr vacío
        if line.startswith('msgstr ""') and i > 0:
            # Buscar msgid anterior
            msgid_line = None
            for j in range(i - 1, max(i - 5, -1), -1):
                if lines[j].startswith('msgid "'):
                    msgid_line = lines[j]
                    break

            if msgid_line:
                match = re.search(r'msgid "(.+)"', msgid_line)
                if match:
                    texto_original = match.group(1)

                    # Saltar strings de metadatos (Project-Id-Version, etc.)
                    if texto_original.startswith("P") and len(texto_original) < 30:
                        i += 1
                        continue
                    if not texto_original.strip():
                        i += 1
                        continue

                    # Verificar si es un string muy largo (literatura)
                    if len(texto_original) > 200:
                        stats["vacios"] += 1
                        print(
                            f"  ⏩ Saltando string muy largo ({len(texto_original)} chars)"
                        )
                        i += 1
                        continue

                    # Traducir
                    stats["vacios"] += 1
                    print(f"  🌐 Traduciendo: '{texto_original[:60]}...' ", end="")

                    traduccion = traducir(texto_original)
                    if traduccion:
                        traduccion = post_editar(traduccion)
                        lines[i] = f'msgstr "{traduccion}"\n'
                        cambios += 1
                        stats["traducidos"] += 1
                        print(f"✅ -> '{traduccion[:60]}...'")
                    else:
                        stats["errores"] += 1
                        print("❌")

        # Detectar fuzzy entries (tienen msgstr vacío o están marcados como fuzzy)
        if line.startswith("#, fuzzy") and i + 2 < len(lines):
            # Buscar msgstr vacío después del fuzzy
            for k in range(i + 1, min(i + 5, len(lines))):
                if lines[k].startswith('msgstr ""') and k > 0:
                    # Buscar msgid
                    for j in range(k - 1, max(k - 5, -1), -1):
                        if lines[j].startswith('msgid "'):
                            msgid_line = lines[j]
                            match = re.search(r'msgid "(.+)"', msgid_line)
                            if match:
                                texto_original = match.group(1)
                                if not texto_original.strip():
                                    break

                                stats["fuzzy"] += 1
                                print(
                                    f"  🌐 Fuzzy: '{texto_original[:60]}...' ", end=""
                                )

                                traduccion = traducir(texto_original)
                                if traduccion:
                                    traduccion = post_editar(traduccion)
                                    lines[k] = f'msgstr "{traduccion}"\n'
                                    # Quitar marca fuzzy
                                    lines[i] = (
                                        f"# {lines[i][2:]}"  # convertir #, fuzzy en comentario
                                    )
                                    cambios += 1
                                    stats["traducidos"] += 1
                                    print(f"✅ -> '{traduccion[:60]}...'")
                                else:
                                    stats["errores"] += 1
                                    print("❌")
                            break
                    break

        i += 1

    # 3. Guardar archivo actualizado
    with open("po/es.po", "w", encoding="utf-8") as f:
        f.writelines(lines)

    # 4. Resumen
    print(f"\n{'=' * 50}")
    print(f"📊 Resumen de traducción:")
    print(f"   ✅ Traducidos nuevos: {stats['traducidos']}")
    print(f"   📝 Fuzzy procesados: {stats['fuzzy']}")
    print(f"   ⏩ Vacíos procesados: {stats['vacios']}")
    print(f"   ❌ Errores: {stats['errores']}")
    print(f"{'=' * 50}")

    if cambios > 0:
        print(f"\n✅ {cambios} cambios realizados en po/es.po")
    else:
        print("\n⚠️  No se hicieron cambios")


if __name__ == "__main__":
    main()
