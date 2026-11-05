#!/usr/bin/env python3
"""
NetHack-es: Traduce dat/keyhelp en po/es.po.
Texto técnico sobre teclas especiales, control characters y terminales.
"""

import polib

PO_FILE = "po/es.po"

TRANSLATIONS = {
    "Depending upon hardware or operating system or NetHack's interface,": "Dependiendo del hardware, del sistema operativo o de la interfaz de NetHack,",
    "some keystrokes may be off-limits.": "algunas combinaciones de teclas pueden no estar disponibles.",
    "For example, ^S and ^Q are often used for XON/XOFF flow-control,": "Por ejemplo, ^S y ^Q se usan a menudo para control de flujo XON/XOFF,",
    "meaning that ^S suspends output and subsequent ^Q resumes suspended": "lo que significa que ^S suspende la salida y ^Q reanuda la salida",
    "output.  When that is the case, neither of those characters will": "suspendida.  Cuando esto ocurre, ninguno de esos caracteres",
    "reach NetHack when it is waiting for a command keystroke.  So they": "llegará a NetHack cuando esté esperando una tecla de comando.  Por lo tanto, no",
    "aren't used as commands, but 'whatdoes' might not be able to tell": "se usan como comandos, pero 'whatdoes' puede no ser capaz de indicarte",
    "you that if they don't get passed through to NetHack.": "que no llegan a NetHack.",
    "^M or <return> or <enter> is likely to be transformed into ^J or": "^M o <return> o <enter> probablemente se transformarán en ^J o",
    "<linefeed> or 'newline' before being passed to NetHack for handling.": "<linefeed> o 'newline' antes de pasarse a NetHack.",
    "So it isn't used as a command, and 'whatdoes' might seem as if it": "Por lo tanto, no se usa como comando, y 'whatdoes' puede parecer como si",
    "is reporting the wrong character but will be operating correctly if": "notificara el carácter incorrecto pero funcionará correctamente si",
    "it describes ^J when you type ^M.": "describe ^J cuando tecleas ^M.",
    "A NUL character, which is typed as ^<space> on some keyboards,": "Un carácter NUL, que se teclea como ^<espacio> en algunos teclados,",
    "^@ on others, and maybe not typeable at all on yet others, is not": "^@ en otros, y quizás ni siquiera se pueda teclear en otros, no se",
    "used as a command, and will be converted into ESC before reaching": "usa como comando, y se convertirá en ESC antes de llegar a",
    "'whatdoes'.  Unlike ^M, this transformation is performed within": "'whatdoes'.  A diferencia de ^M, esta transformación se realiza dentro de",
    "NetHack.  But like ^M, if you type NUL and get feedback about ESC,": "NetHack.  Pero como con ^M, si tecleas NUL y recibes respuesta sobre ESC,",
    "the situation is expected.": "la situación es la esperada.",
    "ESC itself is a synonym for ^[, and is another source of oddity.": "El propio ESC es un sinónimo de ^[, y es otra fuente de rarezas.",
    "Various function keys, including cursor arrow keys, may transmit": "Varias teclas de función, incluyendo las teclas de cursor, pueden transmitir",
    'an "escape sequence" of ESC + [ + other stuff, confusing NetHack': 'una "secuencia de escape" de ESC + [ + otras cosas, confundiendo a NetHack',
    "as to what command was intended since the ESC will be processed": "sobre qué comando se pretendía ya que el ESC se procesará",
    "and then whatever follows will seem to NetHack like--and be used": "y luego lo que siga parecerá a NetHack como--y se usará",
    "as--something typed by the user.  (If you press a function key and": "como--algo tecleado por el usuario.  (Si pulsas una tecla de función y",
    "a menu of the armor your hero is wearing appears, what happened": "aparece un menú con la armadura que lleva tu héroe, lo que ocurrió",
    "was that an escape sequence was sent to NetHack, its ESC aborted": "fue que se envió una secuencia de escape a NetHack, su ESC canceló",
    "any pending key operation, its '[' was then treated as a command": "cualquier operación de tecla pendiente, su '[' se trató entonces como un comando",
    'to show worn armor, and the "other stuff" probably got silently': 'para mostrar la armadura puesta, y el "otro material" probablemente se ignoró',
    "discarded as invalid choices while you dismissed the menu.)": "silenciosamente como opciones inválidas mientras descartabas el menú.)",
    "If you have NetHack's 'altmeta' option enabled, meaning that the": "Si tienes activada la opción 'altmeta' de NetHack, lo que significa que la",
    "<alt> or <option> key, when used as shift while typing some other": "tecla <alt> o <option>, al usarse como shift mientras tecleas otra",
    "character, transmits ESC and then the other character so NetHack": "tecla, transmite ESC y luego el otro carácter para que NetHack",
    "should treat that other character as a meta-character, then ESC": "trate ese otro carácter como un meta-carácter, entonces ESC",
    "takes on added potential for confusion.  Implicit in the handling": "adquiere un potencial adicional de confusión.  Implícito en el manejo",
    "of a two character sequence ESC + something is the fact that when": "de una secuencia de dos caracteres ESC + algo está el hecho de que cuando",
    "NetHack sees ESC, it needs to wait for another character before": "NetHack ve ESC, necesita esperar otro carácter antes de",
    "it can decide what to do.  So if you type ESC manually, you'll": "poder decidir qué hacer.  Así que si tecleas ESC manualmente, tendrás",
    "need to type it a second time or NetHack will sit there waiting.": "que teclearlo una segunda vez o NetHack se quedará esperando.",
    "(It will then be treated as if you typed ESC rather than M-ESC.)": "(Entonces se tratará como si hubieras tecleado ESC en lugar de M-ESC.)",
    "On some systems, typing ^\\ will send a QUIT signal to the current": "En algunos sistemas, teclear ^\\ enviará una señal QUIT al",
    "process, probably killing it and possibly causing it to save a": "proceso actual, probablemente terminándolo y posiblemente haciendo que guarde un",
    "core dump.  It is not used for any NetHack command, so don't type": "volcado de memoria.  No se usa para ningún comando de NetHack, así que no teclees",
    "that character.": "ese carácter.",
    "One last note:  characters shown as ^x mean that you should hold": "Una última nota: los caracteres que se muestran como ^x significan que debes mantener",
    "down the <control> or <ctrl> key as a shift and then type 'x'.": "pulsada la tecla <control> o <ctrl> como modificador y luego teclear 'x'.",
    "Control characters are all implicitly uppercase, but you don't": "Los caracteres de control son todos implícitamente mayúsculas, pero no",
    "need to press the shift key while typing them.  The opposite is": "necesitas pulsar shift mientras los tecleas.  Lo contrario ocurre",
    "true for meta-characters:  they can be either case, so you need": "con los meta-caracteres: pueden ser en mayúsculas o minúsculas, así que necesitas",
    "to use shift as well as <meta> or <alt> to generate an uppercase": "usar shift además de <meta> o <alt> para generar un meta-carácter",
    "letter meta-character.": "en mayúsculas.",
}


def main():
    po = polib.pofile(PO_FILE)
    modified = 0
    total = 0

    for entry in po:
        is_kh = any(ref[0] == "dat/keyhelp" for ref in entry.occurrences)
        if not is_kh:
            continue

        total += 1
        if entry.msgid in TRANSLATIONS:
            entry.msgstr = TRANSLATIONS[entry.msgid]
            modified += 1

    po.save(PO_FILE)

    print(f"Total entradas dat/keyhelp: {total}")
    print(f"Traducciones aplicadas: {modified}")
    print(f"Sin traducir: {total - modified}")

    if modified < total:
        print("\n--- Sin traducir ---")
        for entry in po:
            is_kh = any(ref[0] == "dat/keyhelp" for ref in entry.occurrences)
            if is_kh and not entry.msgstr:
                print(f"  [{entry.occurrences[0][1]}] {entry.msgid}")


if __name__ == "__main__":
    main()
