#!/usr/bin/env python3
"""
NetHack-es: Traduce dat/data.base en po/es.po.
Estrategia:
- Clasifica entradas como: claves, descripciones, citas, diálogos
- Traduce las claves y descripciones cortas
- Para citas literarias largas, traduce manteniendo el estilo
"""

import polib, re

PO_FILE = "po/es.po"

# Traducciones de criaturas/monstruos/objetos comunes (claves)
KEYS = {
    # Razas
    "human": "humano",
    "elf": "elfo",
    "dwarf": "enano",
    "gnome": "gnomo",
    "orc": "orco",
    "hobbit": "hobbit",
    "giant": "gigante",
    "troll": "troll",
    "goblin": "goblin",
    "ogre": "ogro",
    "dragon": "dragón",
    "demon": "demonio",
    "angel": "ángel",
    "bat": "murciélago",
    "snake": "serpiente",
    "spider": "araña",
    "vampire": "vampiro",
    # Objetos
    "scroll": "pergamino",
    "potion": "poción",
    "ring": "anillo",
    "wand": "varita",
    "amulet": "amuleto",
    "armor": "armadura",
    "weapon": "arma",
    "helmet": "casco",
    "shield": "escudo",
    "boots": "botas",
    "gloves": "guantes",
    "cloak": "capa",
    "shirt": "camiseta",
    "leather armor": "armadura de cuero",
    "chain mail": "cota de malla",
    "plate mail": "armadura de placas",
    "sword": "espada",
    "axe": "hacha",
    "spear": "lanza",
    "dagger": "daga",
    "bow": "arco",
    "arrow": "flecha",
    "crossbow": "ballesta",
    "sling": "honda",
    "mace": "maza",
    "club": "porra",
    # Adjetivos comunes
    "blessed": "bendecido",
    "uncursed": "no maldito",
    "cursed": "maldito",
    "rustproof": "inoxidable",
    "erodeproof": "resistente",
    "dilithium": "dilitio",
    # Materiales
    "wooden": "de madera",
    "iron": "de hierro",
    "steel": "de acero",
    "silver": "de plata",
    "golden": "de oro",
    "crystal": "de cristal",
    "glass": "de vidrio",
    "bone": "de hueso",
    "diamond": "de diamante",
    "ruby": "de rubí",
    "emerald": "de esmeralda",
    "sapphire": "de zafiro",
    "jade": "de jade",
    "opal": "de ópalo",
    "amethyst": "de amatista",
    # Objetos varios
    "suit or piece of armor": "armadura o pieza de armadura",
    "thonged club": "porra con correa",
    "oil skin": "piel aceitada",
    "oil lamp": "lámpara de aceite",
    "magic lamp": "lámpara mágica",
    "food ration": "ración de comida",
    "skeleton key": "llave maestra",
    "iron ball": "bola de hierro",
    "sink": "fregadero",
    "fountain": "fuente",
    "altar": "altar",
    "throne": "trono",
    "tree": "árbol",
    "statue": "estatua",
    "grave": "tumba",
    "door": "puerta",
    "drawbridge": "puente levadizo",
    "corridor": "pasillo",
    "stairs": "escaleras",
    # Monstruos comunes
    "ant": "hormiga",
    "ape": "mono",
    "blob": "ameba",
    "ooze": "limo",
    "* ooze": "* limo",
    "*pudding": "* pudin",
    "* slime": "* moho",
    "cave(wo)man": "cavernícola",
    "dog": "perro",
    "cat": "gato",
    "fox": "zorro",
    "rat": "rata",
    "eel": "anguila",
    "imp": "diablillo",
    "ice": "hielo",
    "pit": "fosa",
    "bag": "bolsa",
    "egg": "huevo",
    "bow": "arco",
    "god": "dios",
    "set": "conjunto",
    "axe": "hacha",
    "ant": "hormiga",
    "anu": "anu",
    "ya": "ya",
    "mog": "mog",
    "kos": "kos",
    "ac": "ca",
    # Niveles y lugares
    "the gnomish mines": "las minas gnomish",
    "sokoban": "sokoban",
    "the quest": "la búsqueda",
    "the castle": "el castillo",
    "gehennom": "gehennom",
    "the astral plane": "el plano astral",
    "the oracle": "el oráculo",
    "the sanctum": "el sanctasanctórum",
    "the valley of the dead": "el valle de los muertos",
    "medusa's lair": "la guarida de medusa",
}


# Patrones de citas literarias
def translate_citation(text):
    """Traduce el formato de citas [ Obra, por Autor ]"""
    m = re.match(r"^\[\s*(.*?)\s*\]\s*$", text)
    if m:
        inner = m.group(1)
        # Traducir "by" si aparece
        inner = re.sub(r"\bby\b", "por", inner)
        inner = re.sub(r"\band\b", "y", inner)
        return f"[ {inner} ]"
    return text


# Frases hechas en descripciones
DESC_PATTERNS = {
    "These giant amoeboid creatures look like nothing more than": "Estas criaturas ameboides gigantes parecen no ser más que",
    "puddles of slime, but they both live and move, feeding on": "charcos de limo, pero viven y se mueven, alimentándose de",
    "metal or wood as well as the occasional dungeon explorer to": "metal o madera, así como del ocasional explorador de mazmorras para",
    "supplement their diet.": "complementar su dieta.",
}

# Diálogos comunes
DIALOG_TRANSLATIONS = {}

SHORT_TRANSLATIONS = {}


def main():
    po = polib.pofile(PO_FILE)
    modified = 0
    total = 0
    by_type = {"keys": 0, "descriptions": 0, "citations": 0, "other": 0}

    for entry in po:
        is_db = any(ref[0] == "dat/data.base" for ref in entry.occurrences)
        if not is_db or entry.msgstr:
            continue

        total += 1
        msgid = entry.msgid
        translated = None

        # 1. Citas [ ... ]
        if msgid.startswith("[") and msgid.endswith("]"):
            translated = translate_citation(msgid)
            by_type["citations"] += 1

        # 2. Claves cortas
        elif (
            len(msgid) < 60 and not msgid.startswith('"') and not msgid.startswith("'")
        ):
            # Buscar en diccionario de claves
            key = msgid.strip().lower()
            # Quitar comodines
            clean = key.lstrip("*~").strip()
            if clean in KEYS:
                orig = KEYS[clean]
                if key.startswith("*"):
                    translated = f"* {orig}"
                elif key.startswith("~"):
                    translated = f"~{orig}"
                else:
                    translated = orig
                by_type["keys"] += 1
            elif key in KEYS:
                translated = KEYS[key]
                by_type["keys"] += 1

        # 3. Descripciones y diálogos
        if not translated:
            if msgid.startswith('"') or msgid.startswith("'"):
                by_type["other"] += 1
            else:
                by_type["descriptions"] += 1

        if translated:
            entry.msgstr = translated
            modified += 1

    po.save(PO_FILE)

    print(f"Total entradas: {total}")
    print(f"Traducidas: {modified}")
    print(
        f"Por tipo: claves={by_type['keys']}, citas={by_type['citations']}, "
        f"descripciones={by_type['descriptions']}, otros={by_type['other']}"
    )
    print(f"Sin traducir: {total - modified}")


if __name__ == "__main__":
    main()
