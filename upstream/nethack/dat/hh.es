y k u   7 8 9   Comandos de movimiento:
 \|/     \|/            yuhjklbn: avanzar un paso en la dirección indicada
h-.-l   4-.-6           YUHJKLBN: avanzar en dirección indicada hasta que
 /|\     /|\                        chocar con una pared u obstáculo
b j n   1 2 3           g<dir>:   correr en dirección <dir> hasta que algo
      teclado numérico              interesante se vea
                        G<dir>,   igual, excepto que un pasillo ramificado no
 <  arriba              ^<dir>:     se considera interesante (la ^ en este
                                    caso significa la tecla Control, no un acento circunflejo)
 >  abajo                m<dir>:   moverse sin recoger objetos ni luchar
                        F<dir>:   luchar aunque no percibas un monstruo
                Si la opción number_pad está activada, las teclas de dígitos mueven en su lugar.
                Dependiendo de la plataforma, Mayús+dígito (en el teclado numérico),
                Meta+dígito, o Alt+dígito invocarán los comandos YUHJKLBN.
                Control <dir> puede o no funcionar cuando number_pad está activado,
                dependiendo de las capacidades de la plataforma.
                El dígito '5' actúa como prefijo 'G', a menos que number_pad esté en 2
                en cuyo caso actúa como 'g'.
                Si number_pad está en 3, los roles de 1,2,3 y 7,8,9 están
                invertidos; en 4, se comporta igual que 3 combinado con 2.
                Si number_pad está en -1, se usan comandos de movimiento alfabéticos
                pero 'y' y 'z' están intercambiados.

Comandos generales:
?     help      mostrar uno de varios textos informativos
#quit quit      end the game without saving current game
S     save      guardar la partida (para continuar después) y salir
                [para restaurar, juega de nuevo y usa el mismo nombre de personaje;
                usa #quit para salir sin guardar]
!     sh        salir al SHELL (si está permitido; 'exit' para reanudar)
^Z    suspend   suspender la partida (independiente de tu char de suspensión actual)
                [en sistemas basados en UNIX, usa el comando 'fg' para reanudar]
O     options   ajustar opciones
/     what-is   decir qué representa un símbolo del mapa
\     known     mostrar lista de lo descubierto
|     perminv   interactuar con ventana de inventario persistente
v     chronicle mostrar una lista de eventos importantes
V     version   mostrar número de versión
^A    again     rehacer el comando anterior
^R    redraw    redibujar la pantalla
^P    prevmsg   repetir el mensaje anterior (varios ^P seguidos repiten los previos)
#               introduces an extended command (#? for a list of them)
&     what-does describir el comando que invoca una tecla

Los caracteres de control se representan como '^' seguido de una letra.  Pulsa Ctrl
o Control como una tecla modificadora y luego escribe la letra.  Los caracteres de control son
no distingue mayúsculas; ^D es lo mismo que ^d, Ctrl+d es lo mismo que Ctrl+Shift+d.
Hay algunos caracteres de control que no son letras; nethack usa ^[ como sinónimo
para Escape (o viceversa) y ^_ para #retravel, pero ninguno de los otros.

Comandos de juego:
^D    kick      patear (una puerta u otra cosa)
^T    Tport     teletransportarse (si puedes)
^X    show      mostrar tus atributos
a     apply     usar una herramienta (pico, llave, cámara, etc.)
A     takeoffall  elegir múltiples objetos de armadura, accesorios y armas
                para quitar, desequipar, desarmar (usa el mismo tiempo de juego
                como quitarlos uno a uno con T,R,w- llevaría)
c     close     cerrar una puerta
C     call      nombrar un monstruo, un objeto individual o un tipo de objeto
d     drop      soltar un objeto.  d7a:  soltar siete objetos del objeto 'a'
D     Drop      soltar tipos de objetos seleccionados
e     eat       comer algo
E     engrave   escribir un mensaje en el polvo del suelo  (E-  usar los dedos)
f     fire      disparar munición del carcaj
F     fight     seguido de dirección, luchar contra un monstruo
i     invent    listar tu inventario (todos los objetos que llevas)
I     Invent    listar partes seleccionadas de tu inventario; por ejemplo
                  I(  listar todas las herramientas, o  I"  listar todos los amuletos
                  IB  listar todos los objetos conocidos por estar benditos
                  IU  sin bendecir, o  IC  malditos, o  IX  estado de bendición desconocido
                  Iu  en una tienda, listar objetos no pagados que llevas encima
                  Ix  en una tienda, listar tasas y objetos de la tienda ya consumidos
o     open      abrir una puerta
p     pay       pagar la cuenta (en una tienda)
P     puton     ponerse un accesorio (anillo, amuleto, etc; puede usarse para llevar
                también armadura, pero las armaduras no se listan como candidatas probables)
q     quaff     beber algo (poción, agua, etc)
Q     quiver    seleccionar munición para el carcaj (usa '#quit' para salir)
r     read      leer un pergamino o libro de hechizos
R     remove    quitarse un accesorio (anillo, amuleto, etc; puede usarse para
                también la armadura)
s     search    buscar puertas secretas, trampas ocultas y monstruos
t     throw     lanzar o disparar un arma
T     takeoff   quitarse algo de armadura; también puede usarse para quitar accesorios,
                pero esos no se listan como candidatos probables)
w     wield     empuñar un arma  (w-  no empuñar nada para desequipar el arma actual)
W     wear      ponerse un objeto de armadura; también puede usarse para ponerse accesorios,
                pero esos no se listan como candidatos probables)
x     xchange   intercambiar el arma principal y la secundaria
X     twoweapon activar combate con dos armas si el rol lo permite
z     zap       disparar una varita  (usa y en vez de z si number_pad es -1)
Z     Zap       lanzar un hechizo  (usa Y en vez de Z si number_pad es -1)
<     up        subir las escaleras
>     down      bajar las escaleras
^     trap_id   identificar una trampa encontrada previamente
),[,=,",(       mostrar objetos en uso del símbolo especificado
*               mostrar la combinación de ),[,=,",( todos a la vez
$     gold      contar tu oro
+     spells    listar los hechizos que conoces; también reordenarlos si lo deseas
`     classkn   mostrar objetos conocidos de una clase de objetos
_     travel    moverse por el camino más corto a un punto del mapa
^_    retravel  reanudar el viaje hacia el destino indicado previamente
.     rest      esperar un momento
,     pickup    recoger todo lo que puedas cargar
@               activar/desactivar la opción "pickup" (recogida automática)
:     look      mirar lo que hay aquí
;     farlook   mirar lo que hay en otro sitio seleccionando una ubicación del mapa
                (para un monstruo sobre uno o más objetos, solo describe
                ese monstruo; para una pila de objetos, solo describe el de arriba)

Los teclados que tienen tecla meta (algunos usan Alt para eso, así que escribir Alt como
más 'e' generaría 'M-e') también pueden usar estos comandos extendidos
con el modificador meta como alternativa a usar el prefijo #.  A diferencia de los
los caracteres de control, los meta sí distinguen mayúsculas así que M-a es distinto
de M-A.  Escribe el último con dos teclas como modificadores, Meta+Shift+a.

M-?             mostrar ayuda de comandos extendidos (si la plataforma lo permite)
M-2   twoweapon activar combate con dos armas (si number_pad no está activado)
M-a   adjust    ajustar las letras del inventario
M-A   annotate  añadir una nota de una línea al nivel de mazmorra actual (ver M-O)
M-c   chat      hablar con alguien
M-C   conduct   ver retos opcionales
M-d   dip       sumergir un objeto en algo
M-e   enhance   mostrar habilidades con armas y hechizos, mejorarlas si procede
M-f   force     forzar una cerradura
M-g   genocided listar tipos de monstruos genocidados y extinguidos, si los hay
M-i   invoke    invocar los poderes especiales de un objeto
M-j   jump      saltar a otra ubicación
M-l   loot      saquear una caja en el suelo
M-m   monster   cuando estés polimorfado, usar la habilidad especial del monstruo
M-n   name      nombrar un monstruo, un objeto individual o un tipo de objeto
M-N   name      sinónimo de M-n  (ambos son iguales que C)
M-o   offer     ofrecer un sacrificio a los dioses
M-O   overview  mostrar información sobre niveles visitados y anotaciones
M-p   pray      rezar a los dioses pidiendo ayuda
M-q   quit      dejar de jugar sin guardar (usa S para guardar y salir)
M-r   rub       frotar una lámpara o una piedra
M-R   ride      montar o desmontar una montura con silla
M-s   sit       sentarte
M-t   turn      ahuyentar no-muertos si el rol lo permite
M-T   tip       volcar un recipiente para vaciar su contenido
M-u   untrap    desactivar la trampa de algo
M-V   vanquished listar número y tipo de monstruos vencidos
M-v   version   imprimir opciones de compilación de esta versión
M-w   wipe      limpiarte la cara
M-X   explore   cambiar del juego normal al modo exploración sin puntuación

Si la opción 'number_pad' está activada, las teclas usadas normalmente para moverse pueden
usarse para varios comandos:

n               seguido del número de veces a repetir el siguiente comando
h     help      mostrar uno de varios textos informativos, como '?'
j     jump      saltar a otra ubicación
k     kick      patear algo (normalmente una puerta)
l     loot      saquear una caja en el suelo
N     name      nombrar un objeto o tipo de objeto
u     untrap    desactivar la trampa de algo (normalmente un objeto)

Hay comandos adicionales disponibles en modo debug (también conocido como modo wizard).
