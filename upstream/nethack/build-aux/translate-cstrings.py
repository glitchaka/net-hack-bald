#!/usr/bin/env python3
"""
NetHack-es: Traducción masiva de cadenas del código C.
Usa reglas + diccionario para traducir el máximo posible automáticamente.
"""

import polib, re, subprocess

PO_FILE = "po/combined-es.po"

# Diccionario principal
DICT = {
    # verbos comunes
    "are": "estás",
    "have": "tienes",
    "get": "recibes",
    "is": "es",
    "don't": "no",
    "can't": "no puedes",
    "cannot": "no puedes",
    "aren't": "no estás",
    "isn't": "no es",
    "doesn't": "no",
    "didn't": "no",
    "won't": "no",
    "wasn't": "no estaba",
    "weren't": "no estabas",
    "don't have": "no tienes",
    "are not": "no estás",
    "is not": "no es",
    # articulos
    "the": "el",
    "a": "un",
    "an": "un",
    "The": "El",
    "A": "Un",
    "in": "en",
    "on": "en",
    "at": "en",
    "to": "a",
    "from": "de",
    "with": "con",
    "for": "para",
    "by": "por",
    "of": "de",
    "into": "en",
    "under": "bajo",
    "over": "sobre",
    "without": "sin",
    # partes del cuerpo
    "head": "cabeza",
    "face": "cara",
    "neck": "cuello",
    "chest": "pecho",
    "stomach": "estómago",
    "arm": "brazo",
    "leg": "pierna",
    "hand": "mano",
    "foot": "pie",
    "shoulder": "hombro",
    "eye": "ojo",
    "nose": "nariz",
    "finger": "dedo",
    "back": "espalda",
    "heart": "corazón",
    "throat": "garganta",
    "skin": "piel",
    "blood": "sangre",
    "head.": "cabeza.",
    "face.": "cara.",
    "neck.": "cuello.",
    "arm.": "brazo.",
    "hand.": "mano.",
    # estados
    "thirsty": "sediento",
    "hungry": "hambriento",
    "weak": "débil",
    "confused": "confundido",
    "hallucinating": "alucinando",
    "blind": "ciego",
    "deaf": "sordo",
    "stunned": "aturdido",
    "sick": "enfermo",
    "satiated": "saciado",
    "full": "lleno",
    # monstruos (básicos)
    "goblin": "goblin",
    "orc": "orco",
    "dwarf": "enano",
    "elf": "elfo",
    "gnome": "gnomo",
    "giant": "gigante",
    "troll": "troll",
    "ogre": "ogro",
    "dragon": "dragón",
    "demon": "demonio",
    "imp": "diablillo",
    "bat": "murciélago",
    "rat": "rata",
    "snake": "serpiente",
    "spider": "araña",
    "vampire": "vampiro",
    "zombie": "zombi",
    "mummy": "momia",
    "skeleton": "esqueleto",
    "golem": "gólem",
    "lich": "liche",
    "worm": "gusano",
    "ghost": "fantasma",
    # objetos
    "door": "puerta",
    "chest": "cofre",
    "sword": "espada",
    "axe": "hacha",
    "bow": "arco",
    "spear": "lanza",
    "dagger": "daga",
    "mace": "maza",
    "helmet": "casco",
    "shield": "escudo",
    "armor": "armadura",
    "ring": "anillo",
    "amulet": "amuleto",
    "potion": "poción",
    "scroll": "pergamino",
    "wand": "varita",
    # sonidos
    "click!": "¡clic!",
    "bang!": "¡bang!",
    "boom!": "¡boom!",
    "pop!": "¡pop!",
    "ZAP!": "¡ZAS!",
    "ZAP!!!": "¡ZAS!!!",
    # frases completas
    "You die...": "Has muerto...",
    "You die.": "Has muerto.",
    "You are hungry.": "Tienes hambre.",
    "You are weak.": "Estás débil.",
    "Nothing happens.": "No ocurre nada.",
    "Nothing seems to happen.": "No parece ocurrir nada.",
    "It is very dark.": "Está muy oscuro.",
    "You feel much better.": "Te sientes mucho mejor.",
    "Do you want your possessions identified?": "¿Quieres que identifiquen tus pertenencias?",
    "There is something lying here.": "Hay algo tirado aquí.",
    "What do you want to read?": "¿Qué quieres leer?",
    "What do you want to eat?": "¿Qué quieres comer?",
    "What do you want to drink?": "¿Qué quieres beber?",
    "What do you want to drop?": "¿Qué quieres soltar?",
    "Shall I pick": "¿Quieres que elija",
    "Is this ok?": "¿Está bien?",
    "Yes; start game": "Sí; empezar partida",
    "No; choose role again": "No; elegir rol de nuevo",
    "Random": "Aleatorio",
    "Quit": "Salir",
    # roles
    "Archeologist": "Arqueólogo",
    "Barbarian": "Bárbaro",
    "Caveman": "Hombre de las cavernas",
    "Cavewoman": "Mujer de las cavernas",
    "Healer": "Curandero",
    "Knight": "Caballero",
    "Monk": "Monje",
    "Priest": "Sacerdote",
    "Priestess": "Sacerdotisa",
    "Ranger": "Explorador",
    "Rogue": "Pícaro",
    "Samurai": "Samurái",
    "Tourist": "Turista",
    "Valkyrie": "Valquiria",
    "Wizard": "Mago",
    "human": "humano",
    "elf": "elfo",
    "dwarf": "enano",
    "gnome": "gnomo",
    "orc": "orco",
    "lawful": "legal",
    "neutral": "neutral",
    "chaotic": "caótico",
    "male": "masculino",
    "female": "femenino",
    # atributos
    "Strength": "Fuerza",
    "Dexterity": "Destreza",
    "Constitution": "Constitución",
    "Intelligence": "Inteligencia",
    "Wisdom": "Sabiduría",
    "Charisma": "Carisma",
    "Hit Points": "Puntos de Golpe",
    "Armor Class": "Clase de Armadura",
}

po = polib.pofile(PO_FILE)
applied = 0
remaining = []

for entry in po:
    if entry.msgstr or not entry.msgid:
        continue
    is_c = any(ref[0].startswith("src/") for ref in entry.occurrences)
    if not is_c:
        continue

    msgid = entry.msgid
    trans = None

    # 1. Traducción exacta
    if msgid in DICT:
        trans = DICT[msgid]

    # 2. Empieza con %s - traducir el resto
    if not trans and msgid.startswith("%s"):
        rest = msgid[2:].strip()
        # Quitar puntuación inicial
        rest = rest.lstrip(" ,.!?")
        if rest in DICT:
            trans = "%s " + DICT[rest]
        elif rest.lower() in DICT:
            trans = "%s " + DICT[rest.lower()]

    # 3. Es una palabra sola traducible
    if not trans and msgid.strip() in DICT:
        trans = DICT[msgid.strip()]

    # 4. Empieza con palabra traducible seguida de espacio/puntuación
    if not trans:
        first_word = msgid.split()[0] if msgid.split() else ""
        first_word_clean = first_word.strip(".,!?\"' \t")
        if first_word_clean in DICT:
            # Traducir la primera palabra, mantener el resto
            trans = DICT[first_word_clean] + msgid[len(first_word_clean) :]

    if trans:
        entry.msgstr = trans
        applied += 1
    else:
        remaining.append(msgid)

po.save(PO_FILE)

print(f"Traducidas: {applied}")
print(f"Sin traducir: {len(remaining)}")

# Compilar .mo
result = subprocess.run(
    ["msgfmt", PO_FILE, "-o", "po/combined-es.mo"], capture_output=True, text=True
)
errors = [l for l in result.stderr.split("\n") if l.strip()]
if errors:
    for e in errors[:5]:
        print(f"  msgfmt: {e}")

subprocess.run(
    ["cp", "po/combined-es.mo", "playground/locale/es/LC_MESSAGES/nethack.mo"]
)

# Test
result = subprocess.run(["/tmp/test_mo"], capture_output=True, text=True)
print(f"Test: {result.stdout.strip()}")
