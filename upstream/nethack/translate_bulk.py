#!/usr/bin/env python3
"""
translate_bulk.py
Traduce strings no traducidas en po/es.po usando LibreTranslate local.
Preserva placeholders (%s, %d, etc.) durante la traducción.
"""

import requests
import re
import sys
import time

LIBRETRANSLATE_URL = "http://localhost:5000/translate"

# Placeholder pattern: %s, %d, %ld, %c, %n, %1s, %-4s, %.2d, etc.
PH_PATTERN = re.compile(r"%[-#+0]*\d*(?:\.\d+)?[hlL]?[sdlnpcS]")

# Lua placeholders: %s, %d, etc. same as C
# Also handle %% (literal %)


def protect_placeholders(text):
    """Replace placeholders with safe markers and return mapping."""
    markers = {}

    def replacer(m):
        key = f"__PH{len(markers)}__"
        markers[key] = m.group(0)
        return key

    protected = PH_PATTERN.sub(replacer, text)
    return protected, markers


def restore_placeholders(text, markers):
    """Restore placeholders from markers."""
    result = text
    for key, value in markers.items():
        result = result.replace(key, value)
    return result


def traducir(texto, source="en", target="es", max_retries=3):
    """Envía texto a LibreTranslate y devuelve traducción."""
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                LIBRETRANSLATE_URL,
                json={"q": texto, "source": source, "target": target},
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json().get("translatedText", texto)
            else:
                print(f"  ⚠️  Error HTTP {resp.status_code}, intento {attempt + 1}")
                time.sleep(1)
        except requests.exceptions.ConnectionError:
            print(f"  ❌ No se puede conectar a LibreTranslate en {LIBRETRANSLATE_URL}")
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"  ❌ Error: {e}")
                return None
    return None


def post_process(translation, original):
    """Apply post-processing fixes to translation."""
    fixes = [
        # Verb forms
        (r"\bYou\b", ""),  # Remove "You" subject (Spanish doesn't need it)
        (r"\byou\b", ""),  # lowercase too
        (r"\bYour\b", "Tu"),
        (r"\byour\b", "tu"),
        # Remove spurious English words
        (r"\bthe\b", ""),
        # Articles
        (r"\bun\b", "un"),
        (r"\buna\b", "una"),
        # Clean up double spaces
        (r"\s{2,}", " "),
        # Clean up leading/trailing spaces
        (r"^ ", ""),
        (r" $", ""),
        # Fix punctuation spacing
        (r" \?", "?"),
        (r" \!", "!"),
        (r" \.", "."),
        (r" ,", ","),
        (r" :", ":"),
        (r" ;", ";"),
    ]

    result = translation
    for pattern, replacement in fixes:
        result = re.sub(pattern, replacement, result)

    # Trim
    result = result.strip()

    return result


def main():
    # 1. Read .po file
    with open("po/es.po", "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("\n\n")

    print(f"🔍 Analizando {len(blocks)} bloques en po/es.po...")

    # Find all untranslated entries (empty msgstr, non-fuzzy, non-header)
    untranslated_indices = []
    for i, block in enumerate(blocks):
        if not block.strip():
            continue
        if "#, fuzzy" in block:
            continue

        msgid_m = re.search(r'^msgid "((?:[^"\\]|\\.)*)"', block, re.MULTILINE)
        msgstr_m = re.search(r'^msgstr "((?:[^"\\]|\\.)*)"', block, re.MULTILINE)

        if msgid_m and msgstr_m and not msgstr_m.group(1):
            msgid = msgid_m.group(1)
            # Skip header entry
            if not msgid:
                continue
            # Skip very long strings (literature, etc.)
            if len(msgid) > 300:
                print(
                    f"  ⏩ Saltando string muy largo ({len(msgid)} chars): '{msgid[:50]}...'"
                )
                continue
            untranslated_indices.append(i)

    total = len(untranslated_indices)
    print(f"📝 {total} strings sin traducir encontrados\n")

    if total == 0:
        print("✅ No hay strings sin traducir. Todo listo!")
        return

    # Process each untranslated string
    translated_count = 0
    error_count = 0
    skip_count = 0

    for idx, block_idx in enumerate(untranslated_indices):
        block = blocks[block_idx]
        msgid_m = re.search(r'^msgid "((?:[^"\\]|\\.)*)"', block, re.MULTILINE)
        msgstr_m = re.search(r'^(msgstr ")((?:[^"\\]|\\.)*)(")', block, re.MULTILINE)

        if not msgid_m or not msgstr_m:
            continue

        msgid = msgid_m.group(1)

        # Skip short strings (single chars, empty)
        if len(msgid) < 2:
            skip_count += 1
            continue

        # Protect placeholders
        protected, markers = protect_placeholders(msgid)

        # Skip if after removing placeholders there's nothing left
        clean = protected.replace("__PH", "")
        if len(clean.strip()) < 2:
            skip_count += 1
            continue

        print(f"  [{idx + 1}/{total}] '{msgid[:60]}...' ", end="", flush=True)

        # Translate
        translation = traducir(protected)
        if translation is None:
            error_count += 1
            print("❌")
            continue

        # Restore placeholders
        translation = restore_placeholders(translation, markers)

        # Post-process
        translation = post_process(translation, msgid)

        # Update the block
        old_msgstr = msgstr_m.group(0)
        new_msgstr = f'msgstr "{translation}"'
        blocks[block_idx] = block.replace(old_msgstr, new_msgstr, 1)
        translated_count += 1

        print(f"✅ → '{translation[:50]}...'")

        # Small delay to avoid overwhelming LibreTranslate
        if idx % 10 == 9:
            time.sleep(0.5)

    # Rebuild .po
    new_content = "\n\n".join(blocks)

    with open("po/es.po", "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\n{'=' * 50}")
    print(f"📊 Resumen:")
    print(f"   ✅ Traducidos: {translated_count}")
    print(f"   ⏩ Omitidos: {skip_count}")
    print(f"   ❌ Errores: {error_count}")
    print(f"{'=' * 50}")

    # Final stats
    import subprocess

    r = subprocess.run(
        ["msgfmt", "--statistics", "po/es.po"], capture_output=True, text=True
    )
    print(f"\n📊 Estado final: {r.stderr or r.stdout}")


if __name__ == "__main__":
    main()
