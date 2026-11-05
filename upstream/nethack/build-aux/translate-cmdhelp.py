#!/usr/bin/env python3
"""
NetHack-es: Traduce dat/cmdhelp en po/es.po.
Los comandos son mayoritariamente frases cortas y predecibles.
"""

import polib
import re

PO_FILE = "po/es.po"

# Diccionario de traducciones específicas (msgid exacto → traducción)
CMD_TRANSLATIONS = {
    # Líneas de configuración/comentarios (se dejan tal cual o se traducen los comentarios)
    "&# cmdhelp - became obsolete when 'BINDINGS=key:command' got added": "&# cmdhelp - quedó obsoleto cuando se añadió 'BINDINGS=tecla:comando'",
    "&# number_pad:": "&# number_pad:",
    "&#  -1 = numpad off, swap y with z (including Y with Z, ^Y with ^Z, M-y &c)": "&#  -1 = numpad off, intercambia y con z (incluye Y con Z, ^Y con ^Z, M-y, etc.)",
    "&#   0 = numpad off (default)": "&#   0 = numpad off (por defecto)",
    "&#   1 = numpad on, normal keypad layout, '5'->'g'": "&#   1 = numpad on, teclado normal, '5'->'g'",
    "&#   2 = numpad on, normal keypad layout, '5'->'G'": "&#   2 = numpad on, teclado normal, '5'->'G'",
    "&#   3 = numpad on, phone keypad layout, '5'->'g'": "&#   3 = numpad on, teclado de teléfono, '5'->'g'",
    "&#   4 = numpad on, phone keypad layout, '5'->'G'": "&#   4 = numpad on, teclado de teléfono, '5'->'G'",
    "&# y,Y handled below": "&# y,Y gestionados más abajo",
    # Comandos de movimiento con dirección
    "b	Go southwest 1 space": "b	Avanzar suroeste 1 espacio",
    "B	Go southwest until you are on top of something": "B	Avanzar suroeste hasta llegar a algo",
    "h	Go west 1 space": "h	Avanzar oeste 1 espacio",
    "H	Go west until you are on top of something": "H	Avanzar oeste hasta llegar a algo",
    "j	Go south 1 space": "j	Avanzar sur 1 espacio",
    "J	Go south until you are on top of something": "J	Avanzar sur hasta llegar a algo",
    "k	Go north 1 space": "k	Avanzar norte 1 espacio",
    "K	Go north until you are on top of something": "K	Avanzar norte hasta llegar a algo",
    "l	Go east 1 space": "l	Avanzar este 1 espacio",
    "L	Go east until you are on top of something": "L	Avanzar este hasta llegar a algo",
    "n	Go southeast 1 space": "n	Avanzar sureste 1 espacio",
    "N	Go southeast until you are on something": "N	Avanzar sureste hasta llegar a algo",
    "u	Go northeast 1 space": "u	Avanzar noreste 1 espacio",
    "U	Go northeast until you are on top of something": "U	Avanzar noreste hasta llegar a algo",
    "y	Go northwest 1 space": "y	Avanzar noroeste 1 espacio",
    "Y	Go northwest until you are on top of something": "Y	Avanzar noroeste hasta llegar a algo",
    "z	Go northwest 1 space": "z	Avanzar noroeste 1 espacio",
    "Z	Go northwest until you are on top of something": "Z	Avanzar noroeste hasta llegar a algo",
    # Movimiento con ^ (control) hacia algo
    "^B	Go southwest until you are near something": "^B	Avanzar suroeste hasta estar cerca de algo",
    "^H	Go west until you are near something": "^H	Avanzar oeste hasta estar cerca de algo",
    "^J	Go south until you are near something": "^J	Avanzar sur hasta estar cerca de algo",
    "^K	Go north until you are near something": "^K	Avanzar norte hasta estar cerca de algo",
    "^L	Go east until you are near something": "^L	Avanzar este hasta estar cerca de algo",
    "^N	Go southeast until you are near something": "^N	Avanzar sureste hasta estar cerca de algo",
    "^U	Go northeast until you are near something": "^U	Avanzar noreste hasta estar cerca de algo",
    "^Y	Go northwest until you are near something": "^Y	Avanzar noroeste hasta estar cerca de algo",
    "^Z	Go northwest until you are near something": "^Z	Avanzar noroeste hasta estar cerca de algo",
    # Comandos con letra
    "a	Apply (use) a tool or break a wand": "a	Aplicar (usar) una herramienta o romper una varita",
    "A	Remove all armor and/or all accessories and/or unwield weapons": "A	Quitar toda la armadura y/o accesorios y/o desequipar armas",
    "^A	Redo the previous command": "^A	Rehacer el comando anterior",
    "c	Close a door": "c	Cerrar una puerta",
    "C	Call (name) a monster, an individual object, or a type of object": "C	Llamar (nombrar) un monstruo, un objeto individual o un tipo de objeto",
    "^C	Interrupt: quit the game": "^C	Interrumpir: salir del juego",
    "d	Drop an item": "d	Soltar un objeto",
    "D	Drop specific item types": "D	Soltar tipos específicos de objetos",
    "^D	Kick something (usually a door, chest, or box)": "^D	Patear algo (normalmente una puerta, cofre o caja)",
    "e	Eat something": "e	Comer algo",
    "E	Engrave writing on the floor": "E	Grabar escritura en el suelo",
    "f	Fire ammunition from quiver": "f	Disparar munición del carcaj",
    "F	Followed by direction, fight a monster (even if you don't sense it)": "F	Seguido de dirección, luchar contra un monstruo (incluso si no lo percibes)",
    "g	Followed by direction, move until you are near something": "g	Seguido de dirección, moverse hasta estar cerca de algo",
    "G	Followed by direction, same as control-direction": "G	Seguido de dirección, igual que control-dirección",
    "h	Help: synonym for '?'": "h	Ayuda: sinónimo de '?'",
    "i	Show your inventory": "i	Mostrar tu inventario",
    "I	Inventory specific item types": "I	Inventario de tipos específicos de objetos",
    "j	Jump: shortcut for '#jump'": "j	Saltar: acceso directo a '#jump'",
    "k	Kick: synonym for '^D'": "k	Patear: sinónimo de '^D'",
    "l	Loot: shortcut for '#loot'": "l	Saquear: acceso directo a '#loot'",
    "m	Followed by direction, move without picking anything up or fighting": "m	Seguido de dirección, moverse sin recoger objetos ni luchar",
    "M	Followed by direction, move a distance without picking anything up": "M	Seguido de dirección, moverse una distancia sin recoger nada",
    "n	Start a count; continue with digit(s)": "n	Iniciar una cuenta; continuar con dígitos",
    "N	Name: shortcut for '#name'": "N	Nombrar: acceso directo a '#name'",
    "o	Open a door": "o	Abrir una puerta",
    "O	Show option settings, possibly change them": "O	Mostrar ajustes de opciones, posiblemente cambiarlos",
    "p	Pay your shopping bill": "p	Pagar la cuenta de la tienda",
    "P	Put on an accessory (ring, amulet, etc; will work for armor too)": "P	Ponerse un accesorio (anillo, amuleto, etc; también funciona con armadura)",
    "^P	Toggle through previously displayed game messages": "^P	Alternar entre mensajes del juego mostrados anteriormente",
    "q	Quaff (drink) something (potion, water, etc)": "q	Beber algo (poción, agua, etc)",
    "Q	Select ammunition for quiver (use '#quit' to quit)": "Q	Seleccionar munición para el carcaj (usa '#quit' para salir)",
    "r	Read a scroll or spellbook": "r	Leer un pergamino o libro de hechizos",
    "R	Remove an accessory (ring, amulet, etc; will work for armor too)": "R	Quitarse un accesorio (anillo, amuleto, etc; también funciona con armadura)",
    "^R	Redraw screen": "^R	Redibujar pantalla",
    "s	Search all immediately adjacent locations for traps and secret doors": "s	Buscar en ubicaciones adyacentes trampas y puertas secretas",
    'S	Save the game (and exit; there is no "save and keep going")': 'S	Guardar la partida (y salir; no existe "guardar y seguir jugando")',
    "t	Throw something (choose an item, then a direction--not a target)": "t	Lanzar algo (elige un objeto, luego una dirección, no un objetivo)",
    "T	Take off one piece of armor (will work for accessories too)": "T	Quitarse una pieza de armadura (también funciona con accesorios)",
    "^T	Teleport around level": "^T	Teletransportarse por el nivel",
    "u	Untrap: shortcut for '#untrap'": "u	Desactivar trampa: acceso directo a '#untrap'",
    "v	Show version ('#version' shows more information)": "v	Mostrar versión ('#version' muestra más información)",
    "V	Show history of game's development": "V	Mostrar historia del desarrollo del juego",
    "w	Wield a weapon (for dual weapons: 'w' secondary, 'x', 'w' primary, 'X')": "w	Equipar un arma (para dos armas: 'w' secundaria, 'x', 'w' principal, 'X')",
    "W	Wear a piece of armor (will work for accessories too)": "W	Ponerse una pieza de armadura (también funciona con accesorios)",
    "x	Swap wielded and secondary weapons": "x	Intercambiar armas equipada y secundaria",
    "X	Toggle two-weapon combat": "X	Activar/desactivar combate con dos armas",
    "^X	Show your attributes (shows more in debug or explore mode)": "^X	Mostrar tus atributos (muestra más en modo debug o exploración)",
    "z	Zap a wand": "z	Disparar una varita",
    "y	Zap a wand": "y	Disparar una varita",
    # Comandos Z (hechizos)
    "Z	Zap (cast) a spell": "Z	Lanzar un hechizo",
    "Y	Zap (cast) a spell": "Y	Lanzar un hechizo",
    # Comandos de depuración
    "^E	Search for nearby traps, secret doors, and unseen monsters": "^E	Buscar trampas cercanas, puertas secretas y monstruos invisibles",
    "^F	Map level; reveals traps and secret corridors but not secret doors": "^F	Mapa del nivel; revela trampas y pasillos secretos pero no puertas secretas",
    "^G	Create a monster by name or class": "^G	Crear un monstruo por nombre o clase",
    "^I	View inventory with all items identified": "^I	Ver inventario con todos los objetos identificados",
    "^O	List special level locations": "^O	Listar ubicaciones especiales del nivel",
    "^V	Teleport between levels": "^V	Teletransportarse entre niveles",
    "^W	Wish for something": "^W	Pedir un deseo",
    "^O	Shortcut for '#overview': list interesting levels you have visited": "^O	Acceso directo a '#overview': listar niveles interesantes visitados",
    # Comandos no disponibles
    "!	unavailable command: shell": "!	comando no disponible: shell",
    "^E	unavailable debugging command": "^E	comando de depuración no disponible",
    "^F	unavailable debugging command": "^F	comando de depuración no disponible",
    "^G	unavailable debugging command": "^G	comando de depuración no disponible",
    "^I	unavailable debugging command": "^I	comando de depuración no disponible",
    "^V	unavailable debugging command": "^V	comando de depuración no disponible",
    "^W	unavailable debugging command": "^W	comando de depuración no disponible",
    "^Z	unavailable command: suspend": "^Z	comando no disponible: suspender",
    "^Y	unavailable command: suspend": "^Y	comando no disponible: suspender",
    # Comandos de símbolo
    "&	Tell what command a keystroke invokes": "&	Decir qué comando invoca una tecla",
    "^	Show the type of an adjacent trap": "^	Mostrar el tipo de una trampa adyacente",
    "^[	Cancel command (same as ESCape key)": "^[	Cancelar comando (igual que la tecla ESC)",
    "!	Do a shell escape; 'exit' shell to come back": "!	Salir al shell; 'exit' para volver",
    '"	Show the amulet currently worn': '"	Mostrar el amuleto que llevas puesto',
    "$	Count your gold": "$	Contar tu oro",
    "(	Show the tools currently in use": "(	Mostrar las herramientas que estás usando",
    ")	Show the weapon(s) currently wielded or readied": ")	Mostrar las armas equipadas o preparadas",
    '*	Show all equipment in use (combination of the ),[,=,",( commands)': '*	Mostrar todo el equipo en uso (combinación de los comandos ),[,=,",()',
    "+	List known spells": "+	Listar hechizos conocidos",
    ",	Pick up things at the current location": ",	Recoger objetos en la ubicación actual",
    "-	'F' prefix; force fight": "-	Prefijo 'F'; forzar lucha",
    ".	Rest one move while doing nothing": ".	Descansar un turno sin hacer nada",
    "Rest one move while doing nothing": "Descansar un turno sin hacer nada",
    "/	Show what type of thing a symbol corresponds to": "/	Mostrar a qué tipo de cosa corresponde un símbolo",
    ":	Look at what is on the floor": ":	Mirar lo que hay en el suelo",
    ";	Show what type of thing a map symbol on the level corresponds to": ";	Mostrar a qué corresponde un símbolo del mapa en el nivel",
    "<	Go up a staircase": "<	Subir una escalera",
    ">	Go down a staircase": ">	Bajar una escalera",
    "?	Give a help message": "?	Dar un mensaje de ayuda",
    "@	Toggle the pickup option on/off": "@	Activar/desactivar la opción de recogida",
    "[	Show the armor currently worn": "[	Mostrar la armadura que llevas puesta",
    "=	Show the ring(s) currently worn": "=	Mostrar los anillos que llevas puestos",
    "\\	Show what object types have been discovered": "\\	Mostrar qué tipos de objetos se han descubierto",
    "`	Show discovered types for one class of objects": "`	Mostrar tipos descubiertos para una clase de objetos",
    "_	Travel via a shortest-path algorithm to a point on the map": "_	Viajar mediante algoritmo de ruta más corta a un punto del mapa",
    "Del	Display map without monsters or objects obstructing the view.": "Del	Mostrar mapa sin monstruos ni objetos que obstruyan la vista.",
    "#	Perform an extended command (use '#?' to list choices)": "#	Realizar un comando extendido (usa '#?' para ver opciones)",
    # Comandos numéricos
    "0	Show inventory": "0	Mostrar inventario",
    "0	Continue a count": "0	Continuar una cuenta",
    "4	Move west": "4	Avanzar oeste",
    "4	Start or continue a count": "4	Iniciar o continuar una cuenta",
    "6	Move east": "6	Avanzar este",
    "6	Start or continue a count": "6	Iniciar o continuar una cuenta",
    # Teclado numérico direcciones
    "1	Move northwest": "1	Avanzar noroeste",
    "1	Move southwest": "1	Avanzar suroeste",
    "1	Start or continue a count": "1	Iniciar o continuar una cuenta",
    "2	Move north": "2	Avanzar norte",
    "2	Move south": "2	Avanzar sur",
    "2	Start or continue a count": "2	Iniciar o continuar una cuenta",
    "3	Move northeast": "3	Avanzar noreste",
    "3	Move southeast": "3	Avanzar sureste",
    "3	Start or continue a count": "3	Iniciar o continuar una cuenta",
    "7	Move northwest": "7	Avanzar noroeste",
    "7	Move southwest": "7	Avanzar suroeste",
    "7	Start or continue a count": "7	Iniciar o continuar una cuenta",
    "8	Move north": "8	Avanzar norte",
    "8	Move south": "8	Avanzar sur",
    "8	Start or continue a count": "8	Iniciar o continuar una cuenta",
    "9	Move northeast": "9	Avanzar noreste",
    "9	Move southeast": "9	Avanzar sureste",
    "9	Start or continue a count": "9	Iniciar o continuar una cuenta",
    # Prefijos de movimiento numérico
    "5	'G' movement prefix": "5	Prefijo de movimiento 'G'",
    "5	'g' movement prefix": "5	Prefijo de movimiento 'g'",
    "5	Start or continue a count": "5	Iniciar o continuar una cuenta",
    "M-5	'G' movement prefix": "M-5	Prefijo de movimiento 'G'",
    "M-5	'g' movement prefix": "M-5	Prefijo de movimiento 'g'",
    "M-0	Inventory specific item types": "M-0	Inventario de tipos específicos de objetos",
    "M-2	Toggle two-weapon combat": "M-2	Activar/desactivar combate con dos armas",
    # Comandos Meta (Alt + tecla)
    "M-?	Display extended command help (if the platform allows this)": "M-?	Mostrar ayuda de comandos extendidos (si la plataforma lo permite)",
    "M-a	Adjust inventory letters": "M-a	Ajustar letras del inventario",
    "M-A	Annotate: supply a name for the current dungeon level": "M-A	Anotar: dar un nombre al nivel actual de la mazmorra",
    "M-c	Chat: talk to an adjacent creature": "M-c	Charlar: hablar con una criatura adyacente",
    "M-C	Conduct: list voluntary challenges you have maintained": "M-C	Conducta: listar desafíos voluntarios que has mantenido",
    "M-d	Dip an object into something": "M-d	Mojar un objeto en algo",
    "M-e	Enhance: check weapons skills, advance them if eligible": "M-e	Mejorar: revisar habilidades de armas, mejorarlas si es posible",
    "M-f	Force a lock": "M-f	Forzar una cerradura",
    "M-i	Invoke an object's special powers": "M-i	Invocar los poderes especiales de un objeto",
    "M-j	Jump to a nearby location": "M-j	Saltar a una ubicación cercana",
    "M-l	Loot a box on the floor": "M-l	Saquear una caja en el suelo",
    "M-m	When polymorphed, use a monster's special ability": "M-m	Cuando estés polimorfado, usar la habilidad especial del monstruo",
    "M-n	Name a monster, an individual object, or a type of object": "M-n	Nombrar un monstruo, un objeto individual o un tipo de objeto",
    "M-N	Name a monster, an individual object, or a type of object": "M-N	Nombrar un monstruo, un objeto individual o un tipo de objeto",
    "M-o	Offer a sacrifice to the gods": "M-o	Ofrecer un sacrificio a los dioses",
    "M-O	Overview: show a summary of the explored dungeon": "M-O	Vista general: mostrar un resumen de la mazmorra explorada",
    "M-p	Pray to the gods for help": "M-p	Rezar a los dioses pidiendo ayuda",
    "M-q	Quit (exit without saving)": "M-q	Salir (salir sin guardar)",
    "M-r	Rub a lamp or a touchstone": "M-r	Frotar una lámpara o una piedra de toque",
    "M-R	Ride: mount or dismount a saddled steed": "M-R	Montar: subir o bajar de una montura ensillada",
    "M-s	Sit down": "M-s	Sentarse",
    "M-t	Turn undead": "M-t	Ahuyentar no muertos",
    "M-T	Tip: empty a container": "M-T	Vaciar: vaciar un contenedor",
    "M-u	Untrap something (trap, door, or chest)": "M-u	Desactivar trampa (trampa, puerta o cofre)",
    "M-v	Print compile time options for this version of NetHack": "M-v	Mostrar opciones de compilación de esta versión de NetHack",
    "M-w	Wipe off your face": "M-w	Limpiarse la cara",
    "M-X	Switch from normal play to explore mode": "M-X	Cambiar de modo normal a modo exploración",
    # Suspend
    "^Z	Suspend game; 'fg' (foreground) to resume": "^Z	Suspender partida; 'fg' (foreground) para reanudar",
    "^Y	Suspend game; 'fg' (foreground) to resume": "^Y	Suspender partida; 'fg' (foreground) para reanudar",
    # Varios
    "  	Rest one move while doing nothing": "  	Descansar un turno sin hacer nada",
}


def main():
    if not polib:
        print("ERROR: polib no está instalado")
        return

    po = polib.pofile(PO_FILE)
    modified = 0
    total_cmd = 0

    for entry in po:
        is_cmd = any(ref[0] == "dat/cmdhelp" for ref in entry.occurrences)
        if not is_cmd:
            continue

        total_cmd += 1

        if entry.msgid in CMD_TRANSLATIONS:
            entry.msgstr = CMD_TRANSLATIONS[entry.msgid]
            modified += 1
        else:
            # Mostrar las que no se tradujeron
            pass

    po.save(PO_FILE)

    print(f"Total entradas dat/cmdhelp: {total_cmd}")
    print(f"Traducciones aplicadas: {modified}")
    print(f"Sin traducir: {total_cmd - modified}")

    # Mostrar las que faltan si las hay
    if modified < total_cmd:
        print("\n--- Sin traducir ---")
        for entry in po:
            is_cmd = any(ref[0] == "dat/cmdhelp" for ref in entry.occurrences)
            if is_cmd and not entry.msgstr:
                print(f"  [{entry.occurrences[0][1]}] {entry.msgid}")


if __name__ == "__main__":
    main()
