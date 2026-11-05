#!/usr/bin/env python3
"""
NetHack-es: Traduce dat/hh, dat/optmenu, dat/usagehlp, dat/wizhelp
"""

import polib

PO_FILE = "po/es.po"

TRANSLATIONS = {}

# ====== dat/hh ======
HH = {
    "y k u   7 8 9   Move commands:": "y k u   7 8 9   Comandos de movimiento:",
    " \\|/     \\|/            yuhjklbn: go one step in specified direction": " \\|/     \\|/            yuhjklbn: avanzar un paso en la dirección indicada",
    "h-.-l   4-.-6           YUHJKLBN: go in specified direction until you": "h-.-l   4-.-6           YUHJKLBN: avanzar en dirección indicada hasta que",
    " /|\\     /|\\                        hit a wall or run into something": " /|\\     /|\\                        choques con una pared u obstáculo",
    "b j n   1 2 3           g<dir>:   run in direction <dir> until something": "b j n   1 2 3           g<dir>:   correr en dirección <dir> hasta que algo",
    "      numberpad                     interesting is seen": "      teclado numérico              interesante se vea",
    "                        G<dir>,   same, except a branching corridor isn't": "                        G<dir>,   igual, excepto que un pasillo ramificado no",
    " <  up                  ^<dir>:     considered interesting (the ^ in this": " <  arriba              ^<dir>:     se considera interesante (la ^ en este",
    "                                    case means the Control key, not a caret)": "                                    caso significa la tecla Control, no un acento circunflejo)",
    " >  down                m<dir>:   move without picking up objects/fighting": " >  abajo               m<dir>:   moverse sin recoger objetos/luchar",
    "                        F<dir>:   fight even if you don't sense a monster": "                        F<dir>:   luchar aunque no percibas un monstruo",
    "If the number_pad option is set, the digit keys move instead.": "Si la opción number_pad está activada, las teclas de dígitos mueven en su lugar.",
    "Depending on the platform, Shift digit (on the numberpad),": "Dependiendo de la plataforma, Mayús+dígito (en el teclado numérico),",
    "Meta digit, or Alt digit will invoke the YUHJKLBN commands.": "Meta+dígito, o Alt+dígito invocarán los comandos YUHJKLBN.",
    "Control <dir> may or may not work when number_pad is enabled,": "Control <dir> puede o no funcionar cuando number_pad está activado,",
    "depending on the platform's capabilities.": "dependiendo de las capacidades de la plataforma.",
    "Digit '5' acts as 'G' prefix, unless number_pad is set to 2": "El dígito '5' actúa como prefijo 'G', a menos que number_pad esté en 2",
    "in which case it acts as 'g' instead.": "en cuyo caso actúa como 'g'.",
    "If number_pad is set to 3, the roles of 1,2,3 and 7,8,9 are": "Si number_pad está en 3, los roles de 1,2,3 y 7,8,9 están",
    "reversed; when set to 4, behaves same as 3 combined with 2.": "invertidos; en 4, se comporta igual que 3 combinado con 2.",
    "If number_pad is set to -1, alphabetic movement commands are": "Si number_pad está en -1, se usan comandos de movimiento alfabéticos",
    "used but 'y' and 'z' are swapped.": "pero 'y' y 'z' están intercambiados.",
    "General commands:": "Comandos generales:",
    "?     help      display one of several informative texts": "?     help      mostrar uno de varios textos informativos",
    "#quit quit      end the game without saving current game": "#quit quit      terminar la partida sin guardar la partida actual",
    "S     save      save the game (to be continued later) and exit": "S     save      guardar la partida (para continuar después) y salir",
    "[to restore, play again and use the same character name;": "[para restaurar, juega de nuevo y usa el mismo nombre de personaje;",
    "use #quit to quit without saving]": "usa #quit para salir sin guardar]",
    "!     sh        escape to some SHELL (if allowed; 'exit' to resume play)": "!     sh        salir al SHELL (si está permitido; 'exit' para reanudar)",
    "^Z    suspend   suspend the game (independent of your current suspend char)": "^Z    suspend   suspender la partida (independiente de tu char de suspensión actual)",
    "[on UNIX(tm)-based systems, use the 'fg' command to resume]": "[en sistemas basados en UNIX, usa el comando 'fg' para reanudar]",
    "O     options   set options": "O     options   ajustar opciones",
    "/     what-is   tell what a map symbol represents": "/     what-is   decir qué representa un símbolo del mapa",
    "\\     known     display list of what's been discovered": "\\     known     mostrar lista de lo descubierto",
    "|     perminv   interact with persistent inventory window instead of hero+map": "|     perminv   interactuar con ventana de inventario persistente",
    "v     chronicle display a list of important events": "v     chronicle mostrar una lista de eventos importantes",
    "V     version   display version number": "V     version   mostrar número de versión",
    "^A    again     redo the previous command": "^A    again     rehacer el comando anterior",
    "^R    redraw    redraw the screen": "^R    redraw    redibujar la pantalla",
    "^X    attributes  show your attributes (shows more in debug or explore mode)": "^X    attributes  mostrar tus atributos (más en modo debug o exploración)",
    ".     rest      rest for one turn while doing nothing": ".     rest      descansar un turno sin hacer nada",
    # ... more hh entries
    # Movement commands in hh
    "h     west      move one step to the west": "h     west      avanzar un paso al oeste",
    "l     east      move one step to the east": "l     east      avanzar un paso al este",
    "j     south     move one step to the south": "j     south     avanzar un paso al sur",
    "k     north     move one step to the north": "k     north     avanzar un paso al norte",
    "y     nw        move one step to the northwest": "y     nw        avanzar un paso al noroeste",
    "u     ne        move one step to the northeast": "u     ne        avanzar un paso al noreste",
    "b     sw        move one step to the southwest": "b     sw        avanzar un paso al suroeste",
    "n     se        move one step to the southeast": "n     se        avanzar un paso al sureste",
    "H     W-west    run west until something interesting": "H     W-oeste   correr al oeste hasta algo interesante",
    "L     E-east    run east until something interesting": "L     E-este    correr al este hasta algo interesante",
    "J     S-south   run south until something interesting": "J     S-sur     correr al sur hasta algo interesante",
    "K     N-north   run north until something interesting": "K     N-norte   correr al norte hasta algo interesante",
    "Y     NW-nw     run northwest until something interesting": "Y     NW-nw     correr al noroeste hasta algo interesante",
    "U     NE-ne     run northeast until something interesting": "U     NE-ne     correr al noreste hasta algo interesante",
    "B     SW-sw     run southwest until something interesting": "B     SW-sw     correr al suroeste hasta algo interesante",
    "N     SE-se     run southeast until something interesting": "N     SE-se     correr al sureste hasta algo interesante",
    # Action commands in hh
    "a     apply     use a tool (pick-axe, key, lamp, etc.) or break a wand": "a     apply     usar una herramienta (pico, llave, lámpara, etc.) o romper una varita",
    "A     remove    remove all armor and/or accessories": "A     remove    quitar toda la armadura y/o accesorios",
    "c     close     close a door": "c     close     cerrar una puerta",
    "C     name      call (name) a monster, an object, or a type of object": "C     name      llamar (nombrar) un monstruo, objeto o tipo de objeto",
    "d     drop      drop one item": "d     drop      soltar un objeto",
    "D     drop      drop specific types of items": "D     drop      soltar tipos específicos de objetos",
    "e     eat       eat food": "e     eat       comer comida",
    "E     engrave   engrave a message on the floor": "E     engrave   grabar un mensaje en el suelo",
    "f     fire      fire something from quiver": "f     fire      disparar algo del carcaj",
    "F     fight     fight a monster (even if you don't sense it)": "F     fight     luchar contra un monstruo (incluso si no lo percibes)",
    "i     inv       display your inventory": "i     inv       mostrar tu inventario",
    "I     inv       display inventory of a specific type of item": "I     inv       mostrar inventario de un tipo específico de objeto",
    "o     open      open a door": "o     open      abrir una puerta",
    "p     pay       pay your shopping bill": "p     pay       pagar la cuenta de la tienda",
    "P     puton     put on an accessory (ring, amulet, etc)": "P     puton     ponerse un accesorio (anillo, amuleto, etc)",
    "q     quaff     drink something (potion, water, etc)": "q     quaff     beber algo (poción, agua, etc)",
    "r     read      read a scroll or spellbook": "r     read      leer un pergamino o libro de hechizos",
    "R     remove    remove an accessory (ring, amulet, etc)": "R     remove    quitarse un accesorio (anillo, amuleto, etc)",
    "s     search    search for traps and secret doors": "s     search    buscar trampas y puertas secretas",
    "t     throw     throw something (choose an item, direction--not a target)": "t     throw     lanzar algo (elige objeto, dirección--no un objetivo)",
    "T     takeoff   take off armor": "T     takeoff   quitarse la armadura",
    "w     wield     wield a weapon": "w     wield     equipar un arma",
    "W     wear      wear armor": "W     wear      ponerse armadura",
    "x     swap      swap wielded and secondary weapons": "x     swap      intercambiar armas equipada y secundaria",
    "X     twoweap   toggle two-weapon combat": "X     twoweap   activar/desactivar combate con dos armas",
    "z     zap       zap a wand": "z     zap       disparar una varita",
    "Z     cast      cast a spell": "Z     cast      lanzar un hechizo",
    # More hh entries
    ">     down      go down a staircase": ">     down      bajar una escalera",
    "<     up        go up a staircase": "<     up        subir una escalera",
    "_     travel    travel via shortest-path algorithm to a point on the map": "_     travel    viajar mediante ruta más corta a un punto del mapa",
    ":     look      look at what is on the floor": ":     look      mirar lo que hay en el suelo",
    ";     look      look at a map symbol on the level": ";     look      mirar un símbolo del mapa en el nivel",
    ",     pickup    pick up things at current location": ",     pickup    recoger objetos en la ubicación actual",
    "@     pickup    toggle the pickup option": "@     pickup    activar/desactivar la opción de recogida",
    ")     wielded   show currently wielded weapon(s)": ")     wielded   mostrar arma(s) equipada(s)",
    "[     worn      show currently worn armor": "[     worn      mostrar armadura puesta",
    "=     worn      show ring(s) currently worn": "=     worn      mostrar anillo(s) puestos",
    '"     worn      show amulet currently worn': '"     worn      mostrar amuleto puesto',
    "(     used      show tools currently in use": "(     used      mostrar herramientas en uso",
    "*     used      show equipment in use (combines preceding five)": "*     used      mostrar equipo en uso (combina los cinco anteriores)",
    "$     gold      count your gold": "$     gold      contar tu oro",
    "+     spells    list known spells": "+     spells    listar hechizos conocidos",
    "\\     known     display list of what's been discovered": "\\     known     mostrar lista de lo descubierto",
    "\`     known     display discovered types for one class of objects": "\`     known     mostrar tipos descubiertos para una clase de objetos",
    "&     what-does describe the command a keystroke invokes": "&     what-does describir el comando que invoca una tecla",
    "^     trap      show type of an adjacent trap": "^     trap      mostrar tipo de una trampa adyacente",
    "^D    kick      kick something (usually a door, chest, or box)": "^D    kick      patear algo (normalmente una puerta, cofre o caja)",
    "^R    redraw    redraw the screen": "^R    redraw    redibujar la pantalla",
    "^X    attrib    show your attributes": "^X    attrib    mostrar tus atributos",
    "Del   clear     display map without monsters or objects obstructing view": "Del   clear     mostrar mapa sin monstruos u objetos que obstruyan la vista",
    "#     extended  perform an extended command; '#?' for list": "#     extended  realizar un comando extendido; '#?' para lista",
    "    additional commands available with number_pad on:": "    comandos adicionales disponibles con number_pad activado:",
    "h     help      display the help menu": "h     help      mostrar el menú de ayuda",
    "j     jump      jump to another location": "j     jump      saltar a otra ubicación",
    "k     kick      kick (for doors, usually)": "k     kick      patear (para puertas, normalmente)",
    "l     loot      loot a box on the floor": "l     loot      saquear una caja en el suelo",
    "n     count     prefix: start a count; continue with digit(s)": "n     count     prefijo: iniciar una cuenta; continuar con dígitos",
    "N     name      name a monster, an object, or a type of object": "N     name      nombrar un monstruo, objeto o tipo de objeto",
    "u     untrap    untrap a trapped object or door": "u     untrap    desactivar trampa de un objeto o puerta",
    "5     g         prefix: 'g' movement/run prefix": "5     g         prefijo: prefijo de movimiento 'g'",
}

# ====== dat/optmenu ======
OPTMENU = {
    "How dynamically setting options works:": "Cómo funciona el ajuste dinámico de opciones:",
    "At the start of each of the two sections are the values of some": "Al inicio de cada una de las dos secciones están los valores de algunas",
    "simple option variables which may be specified by toggling on/off.": "variables de opción simples que pueden especificarse activando/desactivando.",
    "For toggling boolean (True/False or On/Off) options, selecting them": "Para opciones booleanas (Verdadero/Falso o Activo/Inactivo), seleccionarlas",
    "will toggle them.  For other options, selecting them yields a dialog": "las alternará.  Para otras opciones, seleccionarlas muestra un diálogo",
    "which allows you to set them.": "que permite ajustarlas.",
    'After the compound section are some "other" options which take a set': 'Después de la sección compuesta hay algunas opciones "otras" que toman un',
    "of values.  Selecting them will yield a list of possible values.": "conjunto de valores.  Seleccionarlas mostrará una lista de valores posibles.",
    "Others use one long page and you need to use a scrollbar; once past": "Otras usan una página larga y necesitas usar una barra de desplazamiento; una vez pasada",
    "the scrollable page, you'll see another batch of options.": "la página desplazable, verás otro lote de opciones.",
    "For the two help pages on compound options, both are presented": "Para las dos páginas de ayuda sobre opciones compuestas, ambas se presentan",
    "scrollably if appropriate.": "con desplazamiento si es necesario.",
}

# ====== dat/usagehlp ======
USAGEHLP = {
    "'-@' force non-interactive start; any of role, race, gender, and": "'-@' forzar inicio no interactivo; cualquiera de rol, raza, género y",
    "alignment can still be specified if desired, otherwise random:": "alineamiento aún pueden especificarse si se desea, si no aleatorio:",
    "'--version' display the program's version number plus the date and": "'--version' mostrar el número de versión del programa más la fecha y",
    "time of the last source-code change,": "hora del último cambio del código fuente,",
    "'--version:copy' display version number and also copy it into system": "'--version:copy' mostrar número de versión y copiarlo al",
    "clipboard; '--version:dump' display several internal values, then exit;": "portapapeles; '--version:dump' mostrar varios valores internos, luego salir;",
    "'--version:show' same as '--version'.": "'--version:show' igual que '--version'.",
}

# ====== dat/wizhelp ======
WIZHELP = {
    "Debug-Mode Quick Reference:": "Referencia Rápida del Modo Debug:",
    "Options:": "Opciones:",
    "[Opt] = conditionally available depending upon build-time settings": "[Opt] = disponible condicionalmente según opciones de compilación",
    "== allows stairs to be replaced by other terrain": "== permite reemplazar escaleras por otro terreno",
    "^E  ==  detect secret doors and traps nearby": "^E  ==  detectar puertas secretas y trampas cercanas",
    "^F  ==  map level, revealing traps and secret corridors": "^F  ==  mapear nivel, revelando trampas y pasillos secretos",
    "^G  ==  create a monster by name or class": "^G  ==  crear un monstruo por nombre o clase",
    "^I  ==  view inventory with all items identified": "^I  ==  ver inventario con todos los objetos identificados",
    "^O  ==  list special level locations": "^O  ==  listar ubicaciones especiales del nivel",
    "^V  ==  teleport between levels": "^V  ==  teletransportarse entre niveles",
    "^W  ==  wish for something": "^W  ==  pedir un deseo",
    "escape (or ^[)  ==  cancel (or ESC)": "escape (o ^[)  ==  cancelar (o ESC)",
}

# Combinar todos
TRANSLATIONS.update(HH)
TRANSLATIONS.update(OPTMENU)
TRANSLATIONS.update(USAGEHLP)
TRANSLATIONS.update(WIZHELP)


def main():
    po = polib.pofile(PO_FILE)
    modified = 0
    total = 0

    targets = ["dat/hh", "dat/optmenu", "dat/usagehlp", "dat/wizhelp"]

    for entry in po:
        is_target = any(ref[0] in targets for ref in entry.occurrences)
        if not is_target:
            continue
        total += 1
        if entry.msgid in TRANSLATIONS:
            entry.msgstr = TRANSLATIONS[entry.msgid]
            modified += 1

    po.save(PO_FILE)

    print(f"Total: {total}")
    print(f"Traducidas: {modified}")
    print(f"Sin traducir: {total - modified}")

    if modified < total:
        print("\n--- Sin traducir ---")
        for entry in po:
            is_target = any(ref[0] in targets for ref in entry.occurrences)
            if is_target and not entry.msgstr:
                print(f"  [{entry.occurrences[0][1]}] {entry.msgid[:80]}")


if __name__ == "__main__":
    main()
