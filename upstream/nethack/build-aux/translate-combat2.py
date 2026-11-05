#!/usr/bin/env python3
"""
NetHack-es: Traducción inteligente de mensajes C.
Usa matching flexible: ignora mayúsculas, puntuación, espacios.
"""

import polib, subprocess, re

PO_FILE = "po/combined-es.po"


def normalize(s):
    """Normaliza para matching: minúsculas, sin puntuación, espacios simples."""
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(".,!?:; ")
    return s.lower()


# Diccionario de traducciones (msgid normalizado → traducción)
# Preservar %s, %d, etc.
# Usar NOMBRE_DE_OPCION como placeholder
T = {
    # COMBATE - impactos
    "hit your %s on the %s": "golpeas tu %s contra %s",
    "%s hit by a huge chunk of metal": "%s es golpeado por un enorme trozo de metal",
    "%s hit %s with a thud": "%s golpea a %s con un golpe sordo",
    "hit %s with %s": "golpeas a %s con %s",
    "splat you hit %s with %s %s egg%s": "zas golpeas a %s con %s %s de huevo%s",
    "hit %s with %s egg%s": "golpeas a %s con %s de huevo%s",
    "%s divides as you hit it%s": "%s se divide cuando lo golpeas%s",
    "hit it": "lo golpeas",
    "hit": "golpeas",
    "hit %d": "golpe %d",
    "hit": "golpeas",
    "hits": "golpeas",
    # COMBATE - fallos
    "miss %s": "fallas a %s",
    "miss it": "fallas",
    "miss": "fallas",
    "miss wildly and stumble forwards": "fallas salvajemente y tropiezas",
    "miss %s from behind": "fallas a %s por detrás",
    "miss wildly": "fallas salvajemente",
    "misses": "fallas",
    # COMBATE - ataques
    "strike %s from behind": "golpeas a %s por detrás",
    "strike %s": "golpeas a %s",
    "attack %s from behind": "atacas a %s por detrás",
    "attack %s": "atacas a %s",
    "uselessly attack %s": "atacas inútilmente a %s",
    "splat %s is hit with %s egg": "zas %s es golpeado con huevo de %s",
    "splat": "zas",
    "whack": "zas",
    "wham": "pum",
    "bam": "bam",
    "thump": "zumba",
    # COMBATE - monstruos atacan
    "%s claws itself out of the ground": "%s sale del suelo con sus garras",
    "divide as %s hits you": "te divides cuando %s te golpea",
    # DAÑO
    "you take %d damage": "recibes %d de daño",
    "%s takes %d damage": "%s recibe %d de daño",
    "you are killed by %s": "has muerto por %s",
    "you are killed": "has muerto",
    "%s is killed by %s": "%s ha muerto por %s",
    "%s is killed": "%s ha muerto",
    "killed by %s": "muerto por %s",
    "killed": "muerto",
    # SENSACIONES
    "feel great": "te sientes genial",
    "feel good": "te sientes bien",
    "feel bad": "te sientes mal",
    "feel terrible": "te sientes fatal",
    "feel very strange": "te sientes muy extraño",
    "feel strange": "te sientes extraño",
    "feel normal": "te sientes normal",
    "feel %s": "te sientes %s",
    "feel very %s": "te sientes muy %s",
    "seem unaffected by it": "pareces no afectado",
    "seem unhurt": "pareces ileso",
    # COMIDA
    "that food is bad": "esa comida está mala",
    "this tastes terrible": "esto sabe horrible",
    "this tastes delicious": "esto sabe delicioso",
    "this tastes like %s": "esto sabe a %s",
    "this tastes bland": "esto sabe insípido",
    "delicious": "delicioso",
    "yuck": "puaj",
    "eat %s": "comes %s",
    "eat it": "lo comes",
    # PUERTAS
    "the door opens": "la puerta se abre",
    "the door closes": "la puerta se cierra",
    "the door is locked": "la puerta está cerrada con llave",
    "the door is unlocked": "la puerta está abierta",
    "open the door": "abres la puerta",
    "close the door": "cierras la puerta",
    "the door resists": "la puerta resiste",
    "the door bursts open": "la puerta se abre de golpe",
    # TRAMPAS
    "you trigger a trap": "activaste una trampa",
    "you avoid a trap": "evitas una trampa",
    "%s triggers a trap": "%s activó una trampa",
    "you fall into a pit": "caes en una fosa",
    "%s falls into a pit": "%s cae en una fosa",
    "you are caught in a bear trap": "eres atrapado por un cepo",
    "poison gas": "gas venenoso",
    "an arrow shoots at you": "una flecha te dispara",
    # TIENDAS
    "hello %s care to buy anything": "hola %s quieres comprar algo",
    "hello %s care to sell anything": "hola %s quieres vender algo",
    "thank you for your patronage": "gracias por tu clientela",
    "you stole %s": "robaste %s",
    "you are accused of stealing": "te acusan de robar",
    "the shopkeeper demands payment": "el tendero exige el pago",
    # INVENTARIO
    "you have %s": "tienes %s",
    "you have nothing": "no tienes nada",
    "pick up %s": "recoges %s",
    "drop %s": "sueltas %s",
    "you can't carry that": "no puedes cargar con eso",
    "you can't carry %s": "no puedes cargar con %s",
    "your inventory is full": "tu inventario está lleno",
    # LEER
    "read the %s": "lees %s",
    "you read %s": "lees %s",
    "the scroll vanishes": "el pergamino se desvanece",
    "the spellbook glows": "el libro de hechizos brilla",
    # MAGIA
    "zap %s": "disparas %s",
    "you zap %s with %s": "disparas %s con %s",
    "%s is zapped by %s": "%s es alcanzado por %s",
    "nothing happens": "no ocurre nada",
    # RELIGION
    "you pray to %s": "rezas a %s",
    "your prayer is answered": "tu oración fue respondida",
    "your prayer is not answered": "tu oración no fue respondida",
    # EQUIPO
    "wield %s": "equipas %s",
    "wear %s": "te pones %s",
    "remove %s": "te quitas %s",
    "take off %s": "te quitas %s",
    "you are now wearing %s": "ahora llevas puesto %s",
    "you are now wielding %s": "ahora llevas equipado %s",
    # DORMIR
    "you fall asleep": "te quedas dormido",
    "you wake up": "te despiertas",
    "%s falls asleep": "%s se queda dormido",
    "%s wakes up": "%s se despierta",
    # AGARRES
    "you are grabbed by %s": "eres agarrado por %s",
    "%s is grabbed": "%s es agarrado",
    "you are held by %s": "eres sujetado por %s",
    "you are released": "eres liberado",
    # GENERAL
    "do what": "hacer qué",
    "i don't know how to %s": "no sé cómo %s",
    "nothing": "nada",
    "something": "algo",
    "someone": "alguien",
    # EXCLAMACIONES
    "oh": "oh",
    "ah": "ah",
    "huh": "eh",
    "wow": "vaya",
    "ouch": "ay",
    "great": "genial",
    "oops": "vaya",
    # PREFIJOS COMUNES (primera palabra de frases)
    "seems": "parece",
    "tries": "intenta",
    "begins": "empieza",
    "starts": "comienza",
    "stops": "para",
    "continues": "continúa",
    "ceases": "cesa",
    # ACCIONES
    "find": "encuentras",
    "smell": "hueles",
    "sense": "sientes",
    "notice": "notas",
    "try": "intentas",
    "seem": "pareces",
    "begin": "empiezas",
    "take": "tomas",
    "drops": "suelta",
    "falls": "cae",
    "gives": "da",
    "enters": "entra",
    "sits": "se sienta",
    "stands": "se levanta",
    "leaves": "sale",
    "moves": "se mueve",
    "jumps": "salta",
    "turns": "gira",
    "steps": "avanza",
    "walks": "camina",
    "runs": "corre",
    "swims": "nada",
    "flies": "vuela",
    "hides": "se esconde",
    "stops": "se para",
    "waits": "espera",
    "throws": "lanza",
    "catches": "atrapa",
    "pushes": "empuja",
    "pulls": "tira",
}

# Cargar .po
po = polib.pofile(PO_FILE)

# Recolectar todas las cadenas C sin traducir
c_entries = []
for entry in po:
    if not entry.msgstr and entry.msgid:
        is_c = any(ref[0].startswith("src/") for ref in entry.occurrences)
        if is_c:
            c_entries.append(entry)

print(f"Cadenas C sin traducir: {len(c_entries)}")

# Intentar match exacto primero
applied_exact = 0
for entry in c_entries:
    if entry.msgid in T:
        entry.msgstr = T[entry.msgid]
        applied_exact += 1

print(f"Match exacto: {applied_exact}")

# Match normalizado
applied_norm = 0
norm_map = {}
for k, v in T.items():
    norm_map[normalize(k)] = v

for entry in c_entries:
    if entry.msgstr:
        continue
    norm_msgid = normalize(entry.msgid)
    if norm_msgid in norm_map:
        # Reconstruir con preservación de %s, %d, etc.
        trans = norm_map[norm_msgid]
        # Verificar que los format specifiers coinciden
        orig_formats = re.findall(r"%[sd]", entry.msgid)
        trans_formats = re.findall(r"%[sd]", trans)
        if len(orig_formats) == len(trans_formats):
            entry.msgstr = trans
            applied_norm += 1

print(f"Match normalizado: {applied_norm}")

# Match por primera palabra
applied_first = 0
for entry in c_entries:
    if entry.msgstr:
        continue
    msgid = entry.msgid
    first_word = msgid.split()[0] if msgid.split() else ""
    fw_clean = first_word.strip(".,!?:;\"' ")
    if fw_clean in T and fw_clean.lower() == fw_clean:
        # Solo para palabras sueltas o frases cortas
        if len(msgid.split()) <= 3:
            trans_start = T[fw_clean]
            rest = msgid[len(fw_clean) :]
            # Preservar formato
            entry.msgstr = trans_start + rest
            applied_first += 1

print(f"Match primera palabra: {applied_first}")

# Guardar
po.save(PO_FILE)
subprocess.run(["msgfmt", PO_FILE, "-o", "po/combined-es.mo"])
subprocess.run(
    ["cp", "po/combined-es.mo", "playground/locale/es/LC_MESSAGES/nethack.mo"]
)

remaining = sum(
    1
    for e in po
    if not e.msgstr and any(ref[0].startswith("src/") for ref in e.occurrences)
)
print(f"\nTotal C traducidas: {applied_exact + applied_norm + applied_first}")
print(f"Pendientes C: {remaining}")
print(f"Total global: {sum(1 for e in po if e.translated())}/{len(po)}")
