#!/usr/bin/env python3
"""
NetHack-es: Traduce dat/engrave.txt en po/es.po.
Grabados en el suelo - referencias culturales, chistes, etc.
Algunos se mantienen en inglés (Elbereth, etc.).
"""

import polib

PO_FILE = "po/es.po"

TRANSLATIONS = {
    # Nombres propios y referencias culturales - se mantienen en inglés
    "Elbereth": "Elbereth",
    "Vlad was here": "Vlad estuvo aquí",
    "ad aerarium": "ad aerarium",
    "Owlbreath": "Owlbreath",
    "Galadriel": "Galadriel",
    "Kilroy was here": "Kilroy estuvo aquí",
    "Frodo lives": "Frodo vive",
    "A.S. ->": "A.S. ->",
    "<- A.S.": "<- A.S.",
    # Traducciones
    "Well Come": "Bienvenido",
    "We apologize for the inconvenience.": "Disculpen las molestias.",
    "See you next Wednesday": "Nos vemos el próximo miércoles",
    "Please don't feed the animals.": "Por favor, no alimentes a los animales.",
    "For a good time call 8?7-5309": "Para un buen rato llama al 8?7-5309",
    "Madam, in Eden, I'm Adam.": "Señora, en el Edén, soy Adán.",
    "Two thumbs up!": "¡Dos pulgares arriba!",
    "Hello, World!": "¡Hola, mundo!",
    "As if!": "¡Cómo si!",
    "BAD WOLF": "MAL LOBO",
    "Arooo!  Werewolves of Yendor!": "¡Aúúú! ¡Hombres lobo de Yendor!",
    "Dig for Victory here": "Cava hacia la Victoria aquí",
    "Gaius Julius Primigenius was here.  Why are you late?": "Gaius Julius Primigenius estuvo aquí.  ¿Por qué llegas tarde?",
    "Go left --->": "Ve a la izquierda --->",
    "<--- Go right": "<--- Ve a la derecha",
    "X marks the spot": "X marca el lugar",
    "X <--- You are here.": "X <--- Tú estás aquí.",
    "Here be dragons": "Aquí hay dragones",
    "Don't go this way": "No vayas por aquí",
    "Watch out, there's a gnome with a wand of death behind that door!": "¡Cuidado, hay un gnomo con una varita de muerte detrás de esa puerta!",
    "Save now, and do your homework!": "¡Guarda ahora, y haz los deberes!",
    "There was a hole here.  It's gone now.": "Aquí había un agujero.  Ya no está.",
    "This is a pit!": "¡Esto es una fosa!",
    "This is not the dungeon you are looking for.": "Esta no es la mazmorra que buscas.",
    "This square deliberately left blank.": "Esta casilla se ha dejado intencionadamente en blanco.",
    "The Vibrating Square": "La Casilla Vibrante",
    "The cake is a lie": "La tarta es un engaño",
    "Haermund Hardaxe carved these runes": "Haermund Hacha Dura grabó estas runas",
    "Need a light?  Come visit the Minetown branch of Izchak's Lighting Store!": "¿Necesitas luz?  ¡Visita la sucursal de Minetown de la Tienda de Iluminación de Izchak!",
    "Snakes on the Astral Plane - Soon in a dungeon near you": "Serpientes en el Plano Astral - Pronto en una mazmorra cerca de ti",
    "Warning, Exploding runes!": "¡Aviso, runas explosivas!",
    "You are the one millionth visitor to this place!  Please wait 200 turns for your wand of wishing.": "¡Eres el visitante un millón de este lugar!  Espera 200 turnos para tu varita de deseos.",
    "You won't get it up the steps": "No lo subirás por las escaleras",
    "You've got mail!": "¡Tienes correo!",
    "If you can read these words then you are not only a nerd but probably dead.": "Si puedes leer estas palabras, no solo eres un friki sino que probablemente estás muerto.",
    "Lasciate ogni speranza o voi ch'entrate.": "Lasciate ogni speranza o voi ch'entrate.",
    "notary sojak": "notario sojak",
    "^.": "^.",
    "^?MAIL": "^?CORREO",
}


def main():
    po = polib.pofile(PO_FILE)
    modified = 0
    total = 0

    for entry in po:
        is_en = any(ref[0] == "dat/engrave.txt" for ref in entry.occurrences)
        if not is_en:
            continue

        total += 1
        if entry.msgid in TRANSLATIONS:
            entry.msgstr = TRANSLATIONS[entry.msgid]
            modified += 1

    po.save(PO_FILE)

    print(f"Total entradas dat/engrave.txt: {total}")
    print(f"Traducciones aplicadas: {modified}")
    print(f"Sin traducir: {total - modified}")

    if modified < total:
        print("\n--- Sin traducir ---")
        for entry in po:
            is_en = any(ref[0] == "dat/engrave.txt" for ref in entry.occurrences)
            if is_en and not entry.msgstr:
                print(f"  [{entry.occurrences[0][1]}] {entry.msgid}")


if __name__ == "__main__":
    main()
