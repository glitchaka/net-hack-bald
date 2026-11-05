&# cmdhelp - quedó obsoleto cuando se añadió 'BINDINGS=tecla:comando'
&	Decir qué comando invoca una tecla
^	Mostrar el tipo de una trampa adyacente
^[	Cancelar comando (igual que la tecla ESC)
&? debug
^E	Buscar trampas cercanas, puertas secretas y monstruos invisibles
^F	Mapa del nivel; revela trampas y pasillos secretos pero no puertas secretas
^G	Crear un monstruo por nombre o clase
^I	Ver inventario con todos los objetos identificados
^O	Listar ubicaciones especiales del nivel
^V	Teletransportarse entre niveles
^W	Pedir un deseo
&: #!debug
^E	comando de depuración no disponible
^F	comando de depuración no disponible
^G	comando de depuración no disponible
^I	comando de depuración no disponible
^O	Acceso directo a '#overview': listar niveles interesantes visitados
^V	comando de depuración no disponible
^W	comando de depuración no disponible
&. #?debug
&? number_pad=0,-1
b	Avanzar suroeste 1 espacio
B	Avanzar suroeste hasta llegar a algo
h	Avanzar oeste 1 espacio
H	Avanzar oeste hasta llegar a algo
j	Avanzar sur 1 espacio
J	Avanzar sur hasta llegar a algo
k	Avanzar norte 1 espacio
K	Avanzar norte hasta llegar a algo
l	Avanzar este 1 espacio
L	Avanzar este hasta llegar a algo
n	Avanzar sureste 1 espacio
N	Avanzar sureste hasta llegar a algo
u	Avanzar noreste 1 espacio
U	Avanzar noreste hasta llegar a algo
&# y,Y gestionados más abajo
&: #number_pad=1,2,3,4
h	Ayuda: sinónimo de '?'
j	Saltar: acceso directo a '#jump'
k	Patear: sinónimo de '^D'
l	Saquear: acceso directo a '#loot'
n	Iniciar una cuenta; continuar con dígitos
N	Nombrar: acceso directo a '#name'
u	Desactivar trampa: acceso directo a '#untrap'
&. #0,-1 vs 1,2,3,4
a	Aplicar (usar) una herramienta o romper una varita
A	Quitar toda la armadura y/o accesorios y/o desequipar armas
^A	Rehacer el comando anterior
^B	Avanzar suroeste hasta estar cerca de algo
c	Cerrar una puerta
C	Llamar (nombrar) un monstruo, un objeto individual o un tipo de objeto
^C	Interrumpir: salir del juego
d	Soltar un objeto
D	Soltar tipos específicos de objetos
^D	Patear algo (normalmente una puerta, cofre o caja)
e	Comer algo
E	Grabar escritura en el suelo
f	Disparar munición del carcaj
F	Seguido de dirección, luchar contra un monstruo (incluso si no lo percibes)
g	Seguido de dirección, moverse hasta estar cerca de algo
G	Seguido de dirección, igual que control-dirección
^H	Avanzar oeste hasta estar cerca de algo
i	Mostrar tu inventario
I	Inventario de tipos específicos de objetos
^J	Avanzar sur hasta estar cerca de algo
^K	Avanzar norte hasta estar cerca de algo
^L	Avanzar este hasta estar cerca de algo
m	Seguido de dirección, moverse sin recoger objetos ni luchar
M	Seguido de dirección, moverse una distancia sin recoger nada
^N	Avanzar sureste hasta estar cerca de algo
o	Abrir una puerta
O	Mostrar ajustes de opciones, posiblemente cambiarlos
p	Pagar la cuenta de la tienda
P	Ponerse un accesorio (anillo, amuleto, etc; también funciona con armadura)
^P	Alternar entre mensajes del juego mostrados anteriormente
q	Beber algo (poción, agua, etc)
Q	Seleccionar munición para el carcaj (usa '#quit' para salir)
r	Leer un pergamino o libro de hechizos
R	Quitarse un accesorio (anillo, amuleto, etc; también funciona con armadura)
^R	Redibujar pantalla
s	Buscar en ubicaciones adyacentes trampas y puertas secretas
S	Guardar la partida (y salir; no existe "guardar y seguir jugando")
t	Lanzar algo (elige un objeto, luego una dirección, no un objetivo)
T	Quitarse una pieza de armadura (también funciona con accesorios)
^T	Teletransportarse por el nivel
^U	Avanzar noreste hasta estar cerca de algo
v	Mostrar versión ('#version' muestra más información)
V	Mostrar historia del desarrollo del juego
w	Equipar un arma (para dos armas: 'w' secundaria, 'x', 'w' principal, 'X')
W	Ponerse una pieza de armadura (también funciona con accesorios)
x	Intercambiar armas equipada y secundaria
X	Activar/desactivar combate con dos armas
^X	Mostrar tus atributos (muestra más en modo debug o exploración)
&? number_pad=0,1,2,3,4
&? number_pad=0
y	Avanzar noroeste 1 espacio
Y	Avanzar noroeste hasta llegar a algo
&.
^Y	Avanzar noroeste hasta estar cerca de algo
z	Disparar una varita
Z	Lanzar un hechizo
&? suspend
^Z	Suspender partida; 'fg' (foreground) para reanudar
&:
^Z	comando no disponible: suspender
&.
&: number_pad=-1
y	Disparar una varita
Y	Lanzar un hechizo
&? suspend
^Y	Suspender partida; 'fg' (foreground) para reanudar
&:
^Y	comando no disponible: suspender
&.
z	Avanzar noroeste 1 espacio
Z	Avanzar noroeste hasta llegar a algo
^Z	Avanzar noroeste hasta estar cerca de algo
&. #0,1..4 vs -1
<	Subir una escalera
>	Bajar una escalera
/	Mostrar a qué tipo de cosa corresponde un símbolo
?	Dar un mensaje de ayuda
&? shell
!	Salir al shell; 'exit' para volver
&:
!	comando no disponible: shell
&.
\	Mostrar qué tipos de objetos se han descubierto
`	Mostrar tipos descubiertos para una clase de objetos
_	Viajar mediante algoritmo de ruta más corta a un punto del mapa
.	Descansar un turno sin hacer nada
&? rest_on_space
 	Descansar un turno sin hacer nada
&.
:	Mirar lo que hay en el suelo
;	Mostrar a qué corresponde un símbolo del mapa en el nivel
,	Recoger objetos en la ubicación actual
@	Activar/desactivar la opción de recogida
)	Mostrar las armas equipadas o preparadas
[	Mostrar la armadura que llevas puesta
=	Mostrar los anillos que llevas puestos
"	Mostrar el amuleto que llevas puesto
(	Mostrar las herramientas que estás usando
*	Mostrar todo el equipo en uso (combinación de los comandos ),[,=,",()
$	Contar tu oro
+	Listar hechizos conocidos
Del	Mostrar mapa sin monstruos ni objetos que obstruyan la vista.
#	Perform an extended command (use '#?' to list choices)
&# number_pad:
&#  -1 = numpad off, intercambia y con z (incluye Y con Z, ^Y con ^Z, M-y, etc.)
&#   0 = numpad off (por defecto)
&#   1 = numpad on, teclado normal, '5'->'g'
&#   2 = numpad on, teclado normal, '5'->'G'
&#   3 = numpad on, teclado de teléfono, '5'->'g'
&#   4 = numpad on, teclado de teléfono, '5'->'G'
&? number_pad = 1,2,3,4
0	Mostrar inventario
4	Avanzar oeste
6	Avanzar este
-	Prefijo 'F'; forzar lucha
&: #-1,0
0	Continuar una cuenta
4	Iniciar o continuar una cuenta
6	Iniciar o continuar una cuenta
&. #1,2,3,4 vs -1,0
&? number_pad=1,2
7	Avanzar noroeste
8	Avanzar norte
9	Avanzar noreste
1	Avanzar suroeste
2	Avanzar sur
3	Avanzar sureste
&: number_pad=3,4
1	Avanzar noroeste
2	Avanzar norte
3	Avanzar noreste
7	Avanzar suroeste
8	Avanzar sur
9	Avanzar sureste
&: #-1,0
1	Iniciar o continuar una cuenta
2	Iniciar o continuar una cuenta
3	Iniciar o continuar una cuenta
7	Iniciar o continuar una cuenta
8	Iniciar o continuar una cuenta
9	Iniciar o continuar una cuenta
&. #1,2 vs 3,4 vs -1,0
&? number_pad=1,3
5	Prefijo de movimiento 'g'
M-5	Prefijo de movimiento 'G'
&: number_pad=2,4
5	Prefijo de movimiento 'G'
M-5	Prefijo de movimiento 'g'
M-0	Inventario de tipos específicos de objetos
&: #-1,0
5	Iniciar o continuar una cuenta
M-2	Activar/desactivar combate con dos armas
&. #1,3 vs 2,4 vs -1,0
M-?	Mostrar ayuda de comandos extendidos (si la plataforma lo permite)
M-a	Ajustar letras del inventario
M-A	Anotar: dar un nombre al nivel actual de la mazmorra
M-c	Charlar: hablar con una criatura adyacente
M-C	Conducta: listar desafíos voluntarios que has mantenido
M-d	Mojar un objeto en algo
M-e	Mejorar: revisar habilidades de armas, mejorarlas si es posible
M-f	Forzar una cerradura
M-i	Invocar los poderes especiales de un objeto
M-j	Saltar a una ubicación cercana
M-l	Saquear una caja en el suelo
M-m	Cuando estés polimorfado, usar la habilidad especial del monstruo
M-n	Nombrar un monstruo, un objeto individual o un tipo de objeto
M-N	Nombrar un monstruo, un objeto individual o un tipo de objeto
M-o	Ofrecer un sacrificio a los dioses
M-O	Vista general: mostrar un resumen de la mazmorra explorada
M-p	Rezar a los dioses pidiendo ayuda
M-q	Salir (salir sin guardar)
M-r	Frotar una lámpara o una piedra de toque
M-R	Montar: subir o bajar de una montura ensillada
M-s	Sentarse
M-t	Ahuyentar no muertos
M-T	Vaciar: vaciar un contenedor
M-u	Desactivar trampa (trampa, puerta o cofre)
M-v	Mostrar opciones de compilación de esta versión de NetHack
M-w	Limpiarse la cara
M-X	Cambiar de modo normal a modo exploración
