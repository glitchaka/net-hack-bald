#!/usr/bin/env python3
"""
NetHack-es: Traduce dat/opthelp y dat/history
"""

import polib, re

PO_FILE = "po/es.po"


def translate_opt_value(text):
    """Traduce valores True/False/On/Off en descripciones de opciones."""
    text = text.replace("True", "Verdadero")
    text = text.replace("False", "Falso")
    text = text.replace("On", "Activado")
    text = text.replace("Off", "Desactivado")
    return text


# Patrones de traducción para opthelp
OPTHELP_PREFIX = {
    "Boolean options not under specific compile flags (with default values in []):": "Opciones booleanas sin banderas de compilación específicas (con valores por defecto en []):",
    "Compound options (with default values in [])": "Opciones compuestas (con valores por defecto en [])",
}

OPTHELP_PATTERNS = [
    (
        r"^(acoustics|armorstatus|autodescribe|autodig|autoopen|autopickup|autoquiver|BIOS|blind|bones|clicklook|cmdassist|color|confirm|dark_room|dropped_nopick|eight_bit_tty|extmenu|female|fixinv|force_invmenu|goldX|help|hilite_pile|hilite_pile_no_invert|hitpointbar|ignintr|implicit_uncursed|lootabox|mail|menuchangescore|menucolors|menudefaultactions|menudisable_columnheaders|menuhist_return|menuhead_align|menuknown_align|menuline_escape|menusort_autog|menustyle|menutab_sign|mention_walls|movecmd|multiple_guis|news|no_dig_to_sym|number_pad|old_apport|packorder|paranoid_confirm|pilesize|popup_dialog|prayconfirm|preload_tiles|pushweapon|rest_on_space|ribbon|ringmenu|runoffstmt|save_menurmes|score|show_badge|show_race|show_score|silent|sortloot|sparkle|statushilites|suppress_alert|tiledelay|tilesize|time|toptenwin|tombstone|travel|travelcommand|use_inverse|verbose|video|videocolors|videotiles|warn_of_sticky_monster|weapon_ombination|what_is_say_unknown|windowtype|wrap_margin|zero)",
        r"\1",
    ),
]

TRANSLATIONS = {}

# --- dat/opthelp translations ---
OPTHELP = {
    "Boolean options not under specific compile flags (with default values in []):": "Opciones booleanas sin banderas de compilación específicas (con valores por defecto en []):",
    "(You can learn which options exist in your version by checking your current": "(Puedes saber qué opciones existen en tu versión consultando tu",
    "option setting, which is reached via the 'O' command.)": "configuración actual de opciones, a la que se accede con el comando 'O'.)",
    "Compound options (with default values in [])": "Opciones compuestas (con valores por defecto en [])",
    "Other options": "Otras opciones",
}

OPTHELP_DESC = {}

# Leer las descripciones de opthelp
opthelp_desc_en = """
acoustics      can your character hear anything                    [True]
armorstatus    show extra status field summarizing worn armor     [False]
autodescribe   describe the terrain under cursor                  [False]
autodig        dig if moving and wielding digging tool            [False]
autoopen       walking into a door attempts to open it             [True]
autopickup     automatically pick up objects you move over         [True]
"""

# Construir diccionario de opción->descripción
opt_desc_es = {
    "acoustics": "si tu personaje puede oír algo",
    "armorstatus": "mostrar campo de estado extra resumiendo armadura puesta",
    "autodescribe": "describir el terreno bajo el cursor",
    "autodig": "cavar si te mueves y llevas una herramienta de cavar",
    "autoopen": "caminar hacia una puerta intenta abrirla",
    "autopickup": "recoger automáticamente objetos al pasar sobre ellos",
    "autoquiver": "al disparar con carcaj vacío, seleccionar automáticamente",
    "BIOS": "permitir el uso de llamadas BIOS ROM de IBM",
    "blind": "tu personaje está permanentemente ciego",
    "bones": "permitir cargar archivos de restos",
    "clicklook": "mirar el mapa haciendo clic derecho del ratón",
    "cmdassist": "dar ayuda sobre errores de dirección y otros comandos",
    "color": "usar diferentes colores para objetos en pantalla",
    "confirm": "preguntar antes de golpear monstruos dóciles o pacíficos",
    "dark_room": "mostrar suelo no visible en diferente color",
    "dropped_nopick": "excluir objetos soltados de la recogida automática",
    "eight_bit_tty": "enviar caracteres de 8 bits directamente al terminal",
    "extmenu": "tty, curses: usar menú para # (comandos extendidos)",
    "female": "obsoleto; usar opción compuesta gender:female",
    "fixinv": "intentar conservar la misma letra para el mismo objeto",
    "force_invmenu": "comandos que piden objeto del inventario muestran un menú",
    "goldX": "al filtrar objetos por estado de bendición/maldición,",
    "help": "mostrar toda la información disponible al usar el comando /",
}

# --- dat/history translations ---
HISTORY = {}


def main():
    po = polib.pofile(PO_FILE)

    files_to_translate = ["dat/opthelp", "dat/history"]

    for fname in files_to_translate:
        count = 0
        for entry in po:
            is_file = any(ref[0] == fname for ref in entry.occurrences)
            if not is_file or entry.msgstr:
                continue

            msgid = entry.msgid

            # Buscar en diccionarios
            translated = None

            # Diccionarios principales
            for d in [OPTHELP, OPTHELP_DESC, HISTORY, TRANSLATIONS]:
                if msgid in d:
                    translated = d[msgid]
                    break

            # Patrón de opción (opthelp): "nombre  descripción  [valor]"
            if not translated and fname == "dat/opthelp":
                m = re.match(r"^([a-zA-Z_]+)\s+(.+?)\s*(\[.*\])?\s*$", msgid)
                if m:
                    opt_name = m.group(1)
                    opt_desc = m.group(2).strip()
                    opt_default = m.group(3) or ""

                    if opt_name in opt_desc_es:
                        desc_es = opt_desc_es[opt_name]
                        if desc_es:
                            # Mantener nombre de opción y valor por defecto en inglés
                            translated = f"{opt_name:<15s} {desc_es:<55s} {opt_default}"

            if translated:
                entry.msgstr = translated
                count += 1

        print(f"{fname}: {count} traducidas")

    po.save(PO_FILE)
    print("\nGuardado.")


if __name__ == "__main__":
    main()
