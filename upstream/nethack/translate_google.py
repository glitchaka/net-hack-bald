from google.cloud import translate_v2 as translate
import re
import os


def traducir_po_google():
    """
    Traduce strings sin traducir en po/combined-es.po usando Google Translate
    """
    # Verificar si el archivo existe
    if not os.path.exists("po/combined-es.po"):
        print("❌ Error: po/combined-es.po no encontrado")
        return

    # Inicializar cliente de Google Translate
    try:
        client = translate.Client()
        print("✅ Cliente de Google Translate conectado")
    except Exception as e:
        print(f"❌ Error conectando a Google Translate: {e}")
        print("💡 Instala Google Cloud SDK o usa otro servicio")
        return

    # Leer archivo .po
    with open("po/combined-es.po", "r", encoding="utf-8") as f:
        content = f.read()

    # Contadores
    traducidos = 0
    errores = 0

    # Función para reemplazar strings sin traducir
    def reemplazar_sin_traducir(match):
        nonlocal traducidos, errores

        # Obtener msgid y msgstr
        msgid_line = match.group(1)
        msgstr_line = match.group(2)

        # Extraer texto de msgid
        texto_match = re.search(r'"([^"]+)"', msgid_line)
        if not texto_match:
            return match.group(0)

        texto_original = texto_match.group(1)

        # Saltar si ya está traducido
        if 'msgstr "' in msgstr_line and len(msgstr_line.strip()) > 10:
            return match.group(0)

        # Traducir con Google
        try:
            result = client.translate(texto_original, target_language="es")

            # Reemplazar msgstr
            nueva_msgstr = f'msgstr "{result["translatedText"]}"'
            traducidos += 1
            print(f"✅ Traducido: '{texto_original}' -> '{result['translatedText']}'")

            return f"{msgid_line}{nueva_msgstr}\n"

        except Exception as e:
            errores += 1
            print(f"❌ Error traduciendo '{texto_original}': {e}")
            return match.group(0)  # Mantener original en caso de error

    # Aplicar traducción a todos los strings sin traducir
    pattern = r'^(msgid\s+".*"\s*\n)(msgstr\s+"")'
    content_traducido = re.sub(
        pattern, reemplazar_sin_traducir, content, flags=re.MULTILINE
    )

    # Guardar archivo actualizado
    with open("po/combined-es.po", "w", encoding="utf-8") as f:
        f.write(content_traducido)

    print(f"\n📊 Resumen de traducción:")
    print(f"   ✅ Traducidos: {traducidos}")
    print(f"   ❌ Errores: {errores}")
    print(f"   📝 Total en archivo: {content.count('msgstr ""')} (antes)")


if __name__ == "__main__":
    traducir_po_google()
