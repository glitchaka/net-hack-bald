#!/usr/bin/env python3
"""
NetHack-es: Aplica traducciones de dat/help a po/es.po usando polib.
Maneja correctamente todos los escapes del formato .po.
"""

import polib
import json
import os

PO_FILE = "po/es.po"

# Traducciones de dat/help (clave = msgid original, valor = traducción)
TRANSLATIONS = {
    # === BIENVENIDA ===
    "Welcome to NetHack!                ( description of version 3.6 )": "¡Bienvenido a NetHack!                ( descripción de la versión 3.6 )",
    "NetHack is a Dungeons and Dragons like game where you (the adventurer)": "NetHack es un juego al estilo de Calabozos y Dragones donde tú (el aventurero)",
    "descend into the depths of the dungeon in search of the Amulet of Yendor,": "desciendes a las profundidades de la mazmorra en busca del Amuleto de Yendor,",
    "reputed to be hidden somewhere below the twentieth level.  You begin your": "que se dice está escondido en algún lugar más allá del nivel veinte.  Empiezas tu",
    "adventure with a pet that can help you in many ways, and can be trained": "aventura con una mascota que puede ayudarte de muchas formas, y puede ser entrenada",
    "to do all sorts of things.  On the way you will find useful (or useless)": "para hacer todo tipo de cosas.  Por el camino encontrarás objetos útiles (o inútiles)",
    "items, quite possibly with magic properties, and assorted monsters.  You can": "posiblemente con propiedades mágicas, y toda clase de monstruos.  Puedes",
    "attack a monster by trying to move onto the space a monster is on (but often": "atacar a un monstruo intentando moverte a su casilla (pero a menudo",
    "it is much wiser to leave it alone).": "es mucho más sensato dejarlo en paz).",
    "Unlike most adventure games, which give you a verbal description of": "A diferencia de la mayoría de juegos de aventura, que te dan una descripción verbal de",
    "your location, NetHack gives you a visual image of the dungeon level you are": "tu ubicación, NetHack te da una imagen visual del nivel de la mazmorra en el que",
    "on.": "estás.",
    "NetHack uses the following symbols:": "NetHack usa los siguientes símbolos:",
    # === SÍMBOLOS ===
    "- and |  The walls of a room, possibly also open doors or a grave.": "- y |        Las paredes de una sala, o quizás puertas abiertas o una tumba.",
    ".        The floor of a room or a doorway.": ".        El suelo de una sala o un vano de puerta.",
    "#        A corridor, or iron bars, or a tree, or possibly a kitchen": "#        Un pasillo, o rejas, o un árbol, o quizás un fregadero",
    "sink (if your dungeon has sinks), or a drawbridge.": "(si tu mazmorra tiene fregaderos), o un puente levadizo.",
    ">        Stairs down: a way to the next level.": ">        Escaleras abajo: camino al siguiente nivel.",
    "<        Stairs up: a way to the previous level.": "<        Escaleras arriba: camino al nivel anterior.",
    "@        You (usually), or another human.": "@        Tú (normalmente), u otro humano.",
    ")        A weapon of some sort.": ")        Un arma de algún tipo.",
    "[        A suit or piece of armor.": "[        Una armadura o pieza de armadura.",
    "%        Something edible (not necessarily healthy).": "%        Algo comestible (no necesariamente sano).",
    "/        A wand.": "/        Una varita.",
    "=        A ring.": "=        Un anillo.",
    "?        A scroll.": "?        Un pergamino.",
    "!        A potion.": "!        Una poción.",
    "(        Some other useful object (pick-axe, key, lamp...)": "(        Otro objeto útil (pico, llave, lámpara ...)",
    "$        A pile of gold.": "$        Un montón de oro.",
    "*        A gem or rock (possibly valuable, possibly worthless).": "*        Una gema o roca (posiblemente valiosa, posiblemente inútil).",
    "+        A closed door, or a spellbook containing a spell": "+        Una puerta cerrada, o un libro de hechizos que contiene un hechizo",
    "you can learn.": "que puedes aprender.",
    "^        A trap (once you detect it).": "^        Una trampa (una vez que la detectas).",
    '"        An amulet, or a spider web.': '"        Un amuleto, o una telaraña.',
    "0        An iron ball.": "0        Una bola de hierro.",
    "_        An altar, or an iron chain.": "_        Un altar, o una cadena de hierro.",
    "{        A fountain.": "{        Una fuente.",
    "}        A pool of water or moat or a pool of lava.": "}        Una charca de agua o foso o una charca de lava.",
    "\\        An opulent throne.": "\\        Un trono opulento.",
    "`        A boulder or statue.": "`        Una roca o estatua.",
    "A to Z, a to z, and several others:  Monsters.": "De la A a la Z, de la a a la z, y varios otros:  Monstruos.",
    "I        Invisible or unseen monster's last known location": "I        Última ubicación conocida de un monstruo invisible",
    "You can find out what a symbol represents by typing": "Puedes averiguar qué representa un símbolo tecleando",
    "'/' and following the directions to move the cursor": "'/' siguiendo las direcciones para mover el cursor",
    "to the symbol in question.  For instance, a 'd' may": "hasta el símbolo en cuestión.  Por ejemplo, una 'd' puede",
    "turn out to be a dog.": "resultar ser un perro.",
    # === MOVIMIENTO ===
    "y k u   7 8 9   Move commands:": "y k u   7 8 9   Comandos de movimiento:",
    " \\|/     \\|/            yuhjklbn: go one step in specified direction": " \\|/     \\|/            yuhjklbn: avanzar un paso en la dirección indicada",
    "h-.-l   4-.-6           YUHJKLBN: go in specified direction until you": "h-.-l   4-.-6           YUHJKLBN: avanzar en dirección indicada hasta que",
    " /|\\     /|\\                        hit a wall or run into something": " /|\\     /|\\                        choques con una pared u obstáculo",
    "b j n   1 2 3           g<dir>:   run in direction <dir> until something": "b j n   1 2 3           g<dir>:   correr en dirección <dir> hasta que algo",
    "      numberpad                     interesting is seen": "      teclado numérico              interesante se vea",
    "                         G<dir>,   same, except a branching corridor isn't": "                         G<dir>,   igual, excepto que un pasillo ramificado no",
    "  <  up                  ^<dir>:     considered interesting (the ^ in this": "  <  arriba              ^<dir>:     se considera interesante (la ^ en este",
    "                                     case means the Control key, not a caret)": "                                     caso significa la tecla Control, no un acento circunflejo)",
    "  >  down                m<dir>:   move without picking up objects": "  >  abajo               m<dir>:   moverse sin recoger objetos",
    "                         F<dir>:   fight even if you don't sense a monster": "                         F<dir>:   luchar aunque no percibas un monstruo",
    "If the number_pad option is set, the number keys move instead.": "Si la opción number_pad está activada, las teclas numéricas mueven en su lugar.",
    "Depending on the platform, Shift number (on the numberpad),": "Dependiendo de la plataforma, Mayús+número (en el teclado numérico),",
    "Meta number, or Alt number will invoke the YUHJKLBN commands.": "Meta+número, o Alt+número invocarán los comandos YUHJKLBN.",
    "Control <dir> may or may not work when number_pad is enabled,": "Control <dir> puede o no funcionar cuando number_pad está activado,",
    "depending on the platform's capabilities.": "dependiendo de las capacidades de la plataforma.",
    "Digit '5' acts as 'G' prefix, unless number_pad is set to 2": "El dígito '5' actúa como prefijo 'G', a menos que number_pad esté en 2",
    "in which case it acts as 'g' instead.": "en cuyo caso actúa como 'g'.",
    "If number_pad is set to 3, the roles of 1,2,3 and 7,8,9 are": "Si number_pad está en 3, los roles de 1,2,3 y 7,8,9 están",
    "reversed; when set to 4, behaves same as 3 combined with 2.": "invertidos; en 4, se comporta igual que 3 combinado con 2.",
    "If number_pad is set to -1, alphabetic movement commands are": "Si number_pad está en -1, se usan comandos de movimiento alfabéticos",
    "used but 'y' and 'z' are swapped.": "pero 'y' y 'z' están intercambiados.",
    # === COMANDOS ===
    "Commands:": "Comandos:",
    "NetHack knows the following commands:": "NetHack conoce los siguientes comandos:",
    "?       Help menu.": "?       Menú de ayuda.",
    "/       What-is, tell what a symbol represents.  You may choose to": "/       Qué-es, dice qué representa un símbolo.  Puedes elegir",
    "specify a location or give a symbol argument.  Enabling the": "especificar una ubicación o dar un símbolo como argumento.  Activar la",
    "autodescribe option will give information about the symbol": "opción autodescribe dará información sobre el símbolo",
    "at each location you move the cursor onto.": "en cada ubicación donde muevas el cursor.",
    "&       Tell what a command does.": "&       Dice qué hace un comando.",
    "<       Go up a staircase (if you are standing on it).": "<       Subir una escalera (si estás sobre ella).",
    ">       Go down a staircase (if you are standing on it).": ">       Bajar una escalera (si estás sobre ella).",
    ".       Rest, do nothing for one turn.": ".       Descansar, no hacer nada durante un turno.",
    "_       Travel via a shortest-path algorithm to a point on the map.": "_       Viajar mediante algoritmo de ruta más corta a un punto del mapa.",
    "a       Apply (use) a tool (pick-axe, key, lamp...).": "a       Aplicar (usar) una herramienta (pico, llave, lámpara ...).",
    "A       Remove all armor.": "A       Quitar toda la armadura.",
    "^A      Redo the previous command.": "^A      Rehacer el comando anterior.",
    "c       Close a door.": "c       Cerrar una puerta.",
    "C       Call (name) monster, individual object, or type of object.": "C       Llamar (nombrar) un monstruo, objeto individual, o tipo de objeto.",
    "d       Drop something.  d7a:  drop seven items of object a.": "d       Soltar algo.  d7a:  soltar siete unidades del objeto a.",
    "D       Drop multiple items.  This command is implemented in two": "D       Soltar varios objetos.  Este comando está implementado de dos",
    "different ways.  One way is:": "formas distintas.  Una forma es:",
    '"D" displays a list of all of your items, from which you can': '"D" muestra una lista de todos tus objetos, de la que puedes',
    'pick and choose what to drop.  A "+" next to an item means': 'elegir qué soltar.  Un "+" junto a un objeto significa',
    'that it will be dropped, a "-" means that it will not be': 'que será soltado, un "-" significa que no será',
    "dropped.  Toggle an item to be selected/deselected by typing": "soltado.  Cambia la selección de un objeto tecleando",
    "the letter adjacent to its description.  Select all items": "la letra junto a su descripción.  Selecciona todos los objetos",
    'with "+", deselect all items with "=".  The <SPACEBAR> moves': 'con "+", desselecciona todos con "=".  La <BARRA ESPACIADORA> pasa',
    "you from one page of the listing to the next.": "de una página del listado a la siguiente.",
    "The other way is:": "La otra forma es:",
    '"D" will ask the question "What kinds of things do you want': '"D" preguntará "¿Qué tipos de cosas quieres',
    'to drop? [!%= au]".  You should type zero or more object': 'soltar? [!%= au]".  Debes teclear cero o más símbolos de objeto',
    "symbols possibly followed by 'a' and/or 'u'.": "posiblemente seguidos de 'a' y/o 'u'.",
    "Da - drop all objects, without asking for confirmation.": "Da - soltar todos los objetos, sin pedir confirmación.",
    "Du - drop only unpaid objects (when in a shop).": "Du - soltar solo objetos no pagados (cuando estés en una tienda).",
    "D%u - drop only unpaid food.": "D%u - soltar solo comida no pagada.",
    "^D      Kick (for doors, usually).": "^D      Patear (para puertas, normalmente).",
    "e       Eat food.": "e       Comer comida.",
    "E       Engrave a message on the floor.": "E       Grabar un mensaje en el suelo.",
    "E- - write in the dust with your fingers.": "E- - escribir en el polvo con los dedos.",
    "f       Fire ammunition from quiver.": "f       Disparar munición del carcaj.",
    "F       Followed by direction, fight a monster (even if you don't": "F       Seguido de dirección, lucha contra un monstruo (incluso si no",
    "sense it).": "lo percibes).",
    "i       Display your inventory.": "i       Mostrar tu inventario.",
    "I       Display selected parts of your inventory, as in": "I       Mostrar partes seleccionadas de tu inventario, como",
    "I* - list all gems in inventory.": "I* - listar todas las gemas del inventario.",
    "Iu - list all unpaid items.": "Iu - listar todos los objetos no pagados.",
    "Ix - list all used up items that are on your shopping bill.": "Ix - listar todos los objetos gastados que están en tu cuenta de la tienda.",
    "I$ - count your money.": "I$ - contar tu dinero.",
    "o       Open a door.": "o       Abrir una puerta.",
    "O       Review current options and possibly change them.": "O       Revisar las opciones actuales y posiblemente cambiarlas.",
    "A menu displaying the option settings will be displayed": "Se mostrará un menú con los ajustes de opciones",
    "and most can be changed by simply selecting their entry.": "y la mayoría pueden cambiarse simplemente seleccionando su entrada.",
    "Options are usually set before the game with NETHACKOPTIONS": "Las opciones normalmente se ajustan antes de la partida con la variable",
    "environment variable or via a configuration file (defaults.nh,": "de entorno NETHACKOPTIONS o mediante un fichero de configuración (defaults.nh,",
    "NetHack Defaults, nethack.cnf, ~/.nethackrc, etc.) rather": "NetHack Defaults, nethack.cnf, ~/.nethackrc, etc.) en lugar de",
    "than with the 'O' command.": "con el comando 'O'.",
    "p       Pay your shopping bill.": "p       Pagar la cuenta de la tienda.",
    "P       Put on an accessory (ring, amulet, etc).": "P       Ponerse un accesorio (anillo, amuleto, etc).",
    "^P      Repeat last message (subsequent ^P's repeat earlier messages).": "^P      Repetir el último mensaje (^P sucesivos repiten mensajes anteriores).",
    "The behavior can be varied via the msg_window option.": "El comportamiento puede variarse mediante la opción msg_window.",
    "q       Drink (quaff) something (potion, water, etc).": "q       Beber algo (poción, agua, etc).",
    "Q       Select ammunition for quiver.": "Q       Seleccionar munición para el carcaj.",
    "#quit   Exit the program without saving the current game.": "#quit   Salir del programa sin guardar la partida actual.",
    "r       Read a scroll or spellbook.": "r       Leer un pergamino o libro de hechizos.",
    "R       Remove an accessory (ring, amulet, etc).": "R       Quitarse un accesorio (anillo, amuleto, etc).",
    "^R      Redraw the screen.": "^R      Redibujar la pantalla.",
    "s       Search for secret doors and traps around you.": "s       Buscar puertas secretas y trampas a tu alrededor.",
    "S       Save the game.  Also exits the program.": "S       Guardar la partida.  También sale del programa.",
    "[To restore, just play again and use the same character name.]": "[Para restaurar, solo juega de nuevo y usa el mismo nombre de personaje.]",
    '[There is no "save current data but keep playing" capability.]': '[No existe la capacidad de "guardar datos actuales pero seguir jugando".]',
    "t       Throw an object or shoot a projectile.": "t       Lanzar un objeto o disparar un proyectil.",
    "T       Take off armor.": "T       Quitarse la armadura.",
    "^T      Teleport, if you are able.": "^T      Teletransportarse, si eres capaz.",
    "v       Displays the version number.": "v       Muestra el número de versión.",
    "V       Display a longer identification of the version, including the": "V       Muestra una identificación más larga de la versión, incluyendo la",
    "history of the game.": "historia del juego.",
    "w       Wield weapon.  w- means wield nothing, use bare hands.": "w       Equipar arma.  w- significa no equipar nada, usar las manos.",
    "W       Wear armor.": "W       Ponerse armadura.",
    "x       Swap wielded and secondary weapons.": "x       Intercambiar armas equipada y secundaria.",
    "X       Toggle two-weapon combat.": "X       Activar/desactivar combate con dos armas.",
    "^X      Show your attributes.": "^X      Mostrar tus atributos.",
    "#explore  Switch to Explore Mode (aka Discovery Mode) where dying and": "#explore  Cambiar al Modo Exploración (también Modo Descubrimiento) donde morir y",
    "deleting the save file during restore can both be overridden.": "borrar el fichero guardado durante la restauración pueden ser anulados.",
    "z       Zap a wand.  (Use y instead of z if number_pad is -1.)": "z       Disparar una varita.  (Usa y en lugar de z si number_pad es -1.)",
    "Z       Cast a spell.  (Use Y instead of Z if number_pad is -1.)": "Z       Lanzar un hechizo.  (Usa Y en lugar de Z si number_pad es -1.)",
    "^Z      Suspend the game.  (^Y instead of ^Z if number_pad is -1.)": "^Z      Suspender la partida.  (^Y en lugar de ^Z si number_pad es -1.)",
    "[To resume, use the shell command 'fg'.]": "[Para reanudar, usa el comando de shell 'fg'.]",
    ":       Look at what is here.": ":       Mirar lo que hay aquí.",
    ";       Look at what is somewhere else.": ";       Mirar lo que hay en otro lugar.",
    ",       Pick up some things.": ",       Recoger algunos objetos.",
    "@       Toggle the pickup option.": "@       Activar/desactivar la opción de recogida.",
    "^       Ask for the type of a trap you found earlier.": "^       Preguntar por el tipo de una trampa que encontraste antes.",
    ")       Tell what weapon you are wielding.": ")       Dice qué arma llevas equipada.",
    "[       Tell what armor you are wearing.": "[       Dice qué armadura llevas puesta.",
    "=       Tell what rings you are wearing.": "=       Dice qué anillos llevas puestos.",
    '"       Tell what amulet you are wearing.': '"       Dice qué amuleto llevas puesto.',
    "(       Tell what tools you are using.": "(       Dice qué herramientas estás usando.",
    "*       Tell what equipment you are using; combines the preceding five.": "*       Dice qué equipo estás usando; combina los cinco anteriores.",
    "$       Count your gold pieces.": "$       Contar tus monedas de oro.",
    "+       List the spells you know; also rearrange them if desired.": "+       Listar los hechizos que conoces; también reordenarlos si lo deseas.",
    "\\       Show what types of objects have been discovered.": "\\       Mostrar qué tipos de objetos se han descubierto.",
    "`       Show discovered types for one class of objects.": "`       Mostrar tipos descubiertos para una clase de objetos.",
    "!       Escape to a shell, if supported in your version and OS.": "!       Salir al shell, si está soportado en tu versión y SO.",
    "[To resume play, terminate the shell subprocess via 'exit'.]": "[Para reanudar, termina el subproceso del shell con 'exit'.]",
    '#       Introduces one of the "extended" commands.  To get a list of': '#       Introduce uno de los comandos "extendidos".  Para obtener una lista de',
    'the commands you can use with "#" type "#?".  The extended': 'los comandos que puedes usar con "#" teclea "#?".  Los comandos',
    "commands you can use depends upon what options the game was": "extendidos que puedes usar dependen de las opciones con las que se compiló",
    "compiled with, along with your class and what type of monster": "el juego, junto con tu clase y qué tipo de monstruo",
    "you most closely resemble at a given moment.  If your keyboard": "más te pareces en un momento dado.  Si tu teclado",
    "has a meta key (which, when pressed in combination with another": "tiene una tecla meta (que, al pulsarse en combinación con otra",
    "key, modifies it by setting the 'meta' (8th, or 'high') bit),": "tecla, la modifica activando el bit 'meta' (8º, o 'alto')),",
    "these extended commands can be invoked by meta-ing the first": "estos comandos extendidos pueden invocarse pulsando meta con la primera",
    "letter of the command.  An alt key may have a similar effect.": "letra del comando.  La tecla Alt puede tener un efecto similar.",
    'If the "number_pad" option is on, some additional letter commands': 'Si la opción "number_pad" está activada, algunos comandos de letras adicionales',
    "are available:": "están disponibles:",
    "h       displays the help menu, like '?'": "h       muestra el menú de ayuda, como '?'",
    "j       Jump to another location.": "j       Saltar a otra ubicación.",
    "k       Kick (for doors, usually).": "k       Patear (para puertas, normalmente).",
    "l       Loot a box on the floor.": "l       Saquear una caja en el suelo.",
    "n       followed by number of times to repeat the next command.": "n       seguido del número de veces para repetir el siguiente comando.",
    "N       Name a monster, an individual object, or a type of object.": "N       Nombrar un monstruo, un objeto individual, o un tipo de objeto.",
    "u       Untrap a trapped object or door.": "u       Desactivar la trampa de un objeto o puerta.",
    "You can put a number before a command to repeat it that many times,": "Puedes poner un número antes de un comando para repetirlo ese número de veces,",
    'as in "40." or "20s".  If you have the number_pad option set, you': 'como en "40." o "20s".  Si tienes la opción number_pad activada,',
    'must type \'n\' to prefix the count, as in "n40." or "n20s".\n': 'debes teclear \'n\' para prefijar la cuenta, como en "n40." o "n20s".',
    'must type \'n\' to prefix the count, as in "n40." or "n20s".': 'debes teclear \'n\' para prefijar la cuenta, como en "n40." o "n20s".',
    "Some information is displayed on the bottom line or perhaps in a": "Parte de la información se muestra en la línea inferior o quizás en una",
    "box, depending on the platform you are using.  You see your": "ventana, dependiendo de la plataforma que uses.  Ves tus",
    "attributes, your alignment, what dungeon level you are on, how many": "atributos, tu alineamiento, en qué nivel de la mazmorra estás, cuántos",
    "hit points you have now (and will have when fully recovered), what": "puntos de golpe tienes ahora (y tendrás cuando te recuperes), cuál",
    "your armor class is (the lower the better), your experience level,": "es tu clase de armadura (cuanto más baja mejor), tu nivel de experiencia,",
    "and the state of your stomach.  Optionally, you may or may not see": "y el estado de tu estómago.  Opcionalmente, puedes ver o no",
    "other information such as spell points, how much gold you have, etc.": "otra información como puntos de hechizo, cuánto oro tienes, etc.",
    "Have Fun, and Happy Hacking!": "¡Diviértete, y feliz hacking!",
    "@        pet- You are riding your saddled pet.": "@        mascota- Estás montando a tu mascota ensillada.",
}


def main():
    if not os.path.exists(PO_FILE):
        print(f"ERROR: {PO_FILE} no encontrado")
        return 1

    po = polib.pofile(PO_FILE, encoding="utf-8")
    modified = 0
    total_help = 0

    for entry in po:
        # Verificar si es de dat/help
        is_help = any(ref[0] == "dat/help" for ref in entry.occurrences)
        if not is_help:
            continue

        total_help += 1
        msgid = entry.msgid

        if msgid in TRANSLATIONS:
            entry.msgstr = TRANSLATIONS[msgid]
            modified += 1

    po.save(PO_FILE)

    print(f"Total entradas dat/help: {total_help}")
    print(f"Traducciones aplicadas: {modified}")
    print(f"Sin traducir: {total_help - modified}")

    # Validar
    if modified > 0:
        stats = po.percent_translated()
        print(f"Porcentaje traducido total: {stats:.1f}%")

    return 0


if __name__ == "__main__":
    exit(main())
