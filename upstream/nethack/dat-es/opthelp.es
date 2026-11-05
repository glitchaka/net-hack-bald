Opciones booleanas sin banderas de compilación específicas (con valores por defecto en []):
(Puedes saber qué opciones existen en tu versión consultando tu
configuración actual de opciones, a la que se accede con el comando 'O'.)

acoustics       si tu personaje puede oír algo                          [True]
armorstatus     mostrar campo de estado extra resumiendo armadura puesta [False]
autodescribe    describir el terreno bajo el cursor                     [False]
autodig         cavar si te mueves y llevas una herramienta de cavar    [False]
autoopen        caminar hacia una puerta intenta abrirla                [True]
autopickup      recoger automáticamente objetos al pasar sobre ellos    [True]
autoquiver      al disparar con carcaj vacío, seleccionar automáticamente [False]
               un arma adecuada del inventario para llenar el carcaj
BIOS            permitir el uso de llamadas BIOS ROM de IBM             [False]
blind           tu personaje está permanentemente ciego                 [False]
bones           permitir cargar archivos de restos                      [True]
clicklook       mirar el mapa haciendo clic derecho del ratón           [False]
cmdassist       dar ayuda sobre errores de dirección y otros comandos   [True]
color           usar diferentes colores para objetos en pantalla        [True for micros]
confirm         preguntar antes de golpear monstruos dóciles o pacíficos [True]
dark_room       mostrar suelo no visible en diferente color             [True]
dropped_nopick  excluir objetos soltados de la recogida automática      [True]
eight_bit_tty   enviar caracteres de 8 bits directamente al terminal    [False]
extmenu         tty, curses: usar menú para # (comandos extendidos)     [False]
               X11: el menu tiene todos los comandos (T) o el subconjunto tradicional (F)
female          obsoleto; usar opción compuesta gender:female           [False]
fixinv          intentar conservar la misma letra para el mismo objeto  [True]
force_invmenu   comandos que piden objeto del inventario muestran un menú [False]
goldX           al filtrar objetos por estado de bendición/maldición,   [False]
               si clasificar el oro como X (desconocido) o U (sin bendecir)
help            mostrar toda la información disponible al usar el comando / [True]
herecmd_menu   mostrar menu de algunos comandos posibles al hacer clic
               sobre ti o junto a ti con el raton                              [False]
hilite_pet     mostrar mascotas de forma resaltada                       [False]
hilite_pile    mostrar pilas de objetos de forma resaltada              [False]
ignintr        ignorar la senal de interrupcion, incluidas las pausas   [False]
implicit_uncursed  omitir "sin bendecir" del inventario, si es posible [True]
legacy         imprimir mensaje introductorio                          [True]
lit_corridor   mostrar un pasillo oscuro como iluminado si esta a la vista [False]
lootabc        usar a/b/c en lugar de o/i/b al saquear                 [False]
mail           activar el demonio de correo                            [True]
mention_decor  avisar al caminar sobre escaleras, altares,           [False]
               fuentes y similares aunque no haya objetos ocultandolos
mention_walls  avisar al chocar contra una pared                       [False]
menu_overlay   superponer menus en la pantalla y alinearlos a la derecha [True]
menucolors     activar coincidencia de patrones MENUCOLOR para resaltar [False]
               lineas en menus de objetos como el inventario; podria resaltar con
               negrita, inverso, etc. aunque el color no este disponible o desactivado
nudist         empezar tu personaje sin armadura                       [False]
null           permitir envio de nulos a tu terminal                   [True]
               intenta desactivar esta opcion (forzando a NetHack a usar su propio
               codigo de retardo) si los objetos en movimiento parecen teletransportarse entre salas
pauper         empezar tu personaje sin posesiones                     [False]
perm_invent    mantener inventario en una ventana permanente          [False]
pickup_stolen  anular pickup_types para objetos robados               [True]
pickup_thrown  anular pickup_types para objetos lanzados              [True]
price_quotes   mostrar cotizaciones recordadas para objetos sin ID    [False]
pushweapon     al empunar un arma nueva, poner tu arma              [False]
               empunada anteriormente en la ranura de arma secundaria
quick_farsight normalmente saltarse la opcion de examinar el mapa   [False]
               cuando se active clarividencia aleatoria
rawio          permitir el uso de E/S cruda                           [False]
reroll         permitir relanzar el inventario inicial                 [False]
rest_on_space  contar la barra espaciadora como caracter de descanso [False]
safe_pet       impedir que ataques (a sabiendas) a tu(s) mascota(s)  [True]
safe_wait      requerir el uso del prefijo 'm' antes de '.' o 's'   [True]
               para esperar o buscar junto a un monstruo hostil
sanity_check   realizar comprobaciones de integridad de datos       [False]
showexp        mostrar tus puntos de experiencia acumulados          [False]
showrace       mostrarte por tu raza en vez de por tu rol            [False]
showvers       mostrar numero de version en las lineas de estado     [False]
silent         no usar el sonido de campana de tu terminal            [True]
sortpack       agrupar tipos similares de objetos en el inventario    [True]
sparkle        mostrar efecto brillante para ataques magicos         [True]
               resistidos (p. ej. ataque de fuego contra monstruo resistente al fuego)
standout       usar modo destacado para --More-- en los mensajes     [False]
status_updates actualizar las lineas de estado                        [True]
terrainstatus  mostrar campo extra de estado describiendo la ubicacion actual [False]
time           mostrar tiempo de juego transcurrido, en turnos        [False]
tips           mostrar algunos consejos utiles durante el juego       [True]
tombstone      imprimir lapida cuando mueras                          [True]
toptenwin      imprimir el top ten en una ventana en vez de stdout    [False]
travel         activa el viaje por clic del raton si esta soportado;  [True]
               puede desactivarse para impedir que los clics del raton en el mapa
               intenten mover al heroe; no afecta al viaje con '_'
use_darkgray   usar negro en negrita en lugar de azul para glifos negros [True]
use_inverse    mostrar monstruos detectados de forma resaltada       [False]
verbose        imprimir mas comentarios durante el juego              [True]
weaponstatus   mostrar campo extra de estado listando arma(s) empunadas [False]
whatis_menu    mostrar menu al obtener una ubicacion del mapa        [False]
whatis_moveskip saltar glifos iguales al obtener ubicacion del mapa [False]


Hay mas opciones booleanas controladas por banderas de compilacion.

Opcion booleana si INSURANCE se definio en compilacion:
checkpoint     guardar el estado del juego tras cada cambio de nivel, [True]
               para una posible recuperacion tras un fallo del programa

Opcion booleana si NEWS se definio en compilacion:
news           imprimir noticias del administrador del juego al inicio [True]

Opcion booleana si SCORE_ON_BOTL se definio en compilacion:
showscore      mostrar tu puntuacion acumulada aproximada             [False]

Opcion booleana si TIMED_DELAY se definio en compilacion (solo tty o curses):
timed_delay    en unix y VMS, usar un temporizador en vez de enviar  [True]
               salida adicional de pantalla al intentar pausar para
               mostrar el efecto.  en MSDOS sin la libreria termcap,
               si pausar o no para el efecto visual.

Opcion booleana si ALTMETA se definio en compilacion:
altmeta        En unix y VMS, tratar la secuencia de dos caracteres
               "ESC c" como M-c (Meta+c, bit 8 activo) cuando nethack        [False]
               obtiene un comando del teclado del jugador.

Opcion booleana si TILES_IN_GLYPHMAP se definio en compilacion (MSDOS):
preload_tiles  controla si los tiles se precargan en RAM al          [True]
               comienzo de la partida.  Hacerlo mejora el rendimiento
               de los graficos de tiles, pero usa mas memoria.

Opcion booleana si TTY_TILES_ESCCODES se definio en compilacion (solo tty):
vt_tiledata    insertar marcadores de codigos de escape de datos extra en la salida [False]

Opcion booleana si TTY_SOUND_ESCCODES se definio en compilacion (solo tty):
vt_sounddata   insertar marcadores de codigos de escape de datos de sonido en la salida [False]

Opciones booleanas que pueden estar disponibles segun que interfaces
soporte el programa al construirse.  Si soporta varios,
algunos pueden aparecer disponibles para configurar pero no hacer nada si
estas usando una interfaz distinta de aquella(s) para la(s) que son:
ascii_map      mostrar mapa como texto, fuerza tiles_map a Off; Qt, X11
guicolor       curses
hitpointbar    curses, tty, Windows GUI si statushilites esta activo;
               Qt sin statushilites; X11 si 'fancy_status' esta desactivado
               (via valores por defecto de aplicacion X) y statushilities activo
popup_dialog   curses, Qt, Windows GUI
selectsaved    tty (Qt y Windows GUI lo hacen incondicionalmente)
splash_screen  curses, Qt, Windows GUI
tiled_map      mostrar mapa como tiles, fuerza ascii_map a Off; Qt, X11

Opciones booleanas disponibles en modo debug (tambien llamado modo mago):
menu_tab_sep   formato del menu -- no tocar
monpolycontrol dejar al jugador elegir la nueva forma de los monstruos cambiantes
montelecontrol dejar al jugador elegir el destino de los monstruos teletransportados
travel_debug   mostrar el estado del algoritmo de busqueda de rutas en el mapa
wizweight      incluir los pesos de los objetos en la vista de inventario

Cualquier opcion booleana puede activarse incluyendola entre las opciones que se
establecen, o negarse (fijar en False) prefijando su nombre con '!' o 'no'.
Alternativamente, puede usarse la sintaxis de opcion compuesta: 'optname:true' y
'optname:false'.

 - - - - -

Las opciones compuestas se escriben como nombre_opcion:valor_opcion.

Opciones compuestas que se pueden establecer durante el juego:

autounlock    al intentar abrir una puerta cerrada o saquear        [Apply-Key]
              un contenedor cerrado, especifica la accion a realizar: puede ser
              None, o uno o mas de Untrap + Apply-Key + Kick + Force;
              si se incluye Untrap, se gestionara primero; las
              demas se aplican si respondes "no" a "buscar trampas?";
              para "si", no necesariamente encontrara nada aunque haya
              una trampa presente, y consumira el resto del
              turno actual independientemente de si encuentra algo;
              Kick solo es util para puertas y Force solo es util para
              contenedores; ambos solo se intentaran si Untrap se
              omite o se salta y Apply-Key se omite o no llevas
              una herramienta de apertura o rechazas usarla
boulder       anular el simbolo por defecto de la roca                [`]
crash_email   direccion de correo para informes de fallo              []
crash_name    nombre a usar en los informes de fallo                   []
crash_urlmax  longitud maxima del URL generado para un informe de fallo []
disclose      los tipos de informacion que quieres    [ni na nv ng nc no]
              ofrecidos al final de la partida
              (lista separada por espacios de valores de dos caracteres;
              prefijo: '+' divulgar siempre, '-' no divulgar nunca,
              'n' preguntar por defecto "no", 'y' preguntar por defecto "si",
              'a' preguntar para elegir el orden (solo para el sufijo 'v');
              sufijo: 'i' inventario, 'a' atributos, 'v' monstruos
              derrotados, 'g' monstruos genocidados y extintos, 'c' conducta
              y logros, 'o' vista general de la mazmorra)
fruit         el nombre de una fruta que te gusta comer    [slime mold]
              (basicamente un capricho que NetHack usa de vez en cuando).
hilite_status especifica una regla para resaltar un campo de estado   []
              (se permiten multiples instancias)
menustyle     interfaz de usuario para seleccionar varios objetos:   [Full]
              Traditional -- preguntar por clases de interes, luego
                             preguntar objeto por objeto para esas clases;
              Combination -- preguntar por clases de interes, luego
                             usar un menu para elegir los objetos;
              Full        -- menu para clases de interes, luego menu de objetos;
              Partial     -- saltar filtrado por clase, usar menu de todos los objetos;
              solo importa la primera letra ('T','C','F','P')
              (Con Traditional, muchas acciones permiten la pseudoclase 'm' para
              solicitar un menu de eleccion: un Combination puntual.)
menu_objsyms  si incluir simbolos de clase de objeto en los menus:     [4]
              0 - none    -- no anadir simbolos de objeto a los menus;
              1 - headers -- anadir simbolo de clase de objeto a las cabeceras;
              2 - entries -- mostrar glifos de objeto (igual que el simbolo de clase
                             para interfaces ASCII) en cada linea del menu;
              3 - both    -- 1 y 2 combinados;
              4 - conditional  -- como 2 pero solo si no hay cabeceras;
              5 - one-or-other -- 1 y 4 combinados;
              las opciones 0 y 1 deberian funcionar con cualquier interfaz; 2 a 5
              estan soportadas por tty y curses
msg_window    comportamiento del repaso de mensajes ^P en tty:        [s]
              single      -- un mensaje cada vez
              full        -- ventana completa con todos los mensajes guardados
              reverse     -- completo con mensajes impresos del mas reciente al mas antiguo
              combination -- los dos primeros ^P consecutivos muestran
                             mensajes individuales, el tercero muestra el conjunto completo
msg_window    comportamiento del repaso de mensajes ^P en curses:     [r]
              reverse     -- ventana completa, mas reciente primero
              full        -- completo con mensajes impresos del menos reciente al mas antiguo,
                             inicialmente posicionado en la ultima pagina para empezar
                             con los mensajes mas recientes a la vista
number_pad    control del movimiento alfabetico o numerico:          [0]
               0 -- movimiento tradicional hjkl + yubn (por defecto);
               1 -- los digitos controlan el movimiento, para teclado numerico;
               2 -- igual que 1, pero '5' actua como prefijo 'g' en vez de 'G';
               3 -- numerico para teclado de telefono (1,2,3 arriba, 7,8,9 abajo);
               4 -- teclado de telefono (3) combinado con preferencia '5' (2);
              -1 -- "qwertz"; movimiento alfabetico pero 'z' intercambiado con 'y'.
              Ajustar number_pad (a un valor positivo) afecta a como se
              gestionan todas las teclas de digito, no solo las del teclado numerico.
packorder     lista de simbolos por defecto para tipos de     [")[%?+!=/(*`0_]
              objetos que da el orden en que tu inventario (y
              algunas otras cosas) se muestra si 'sortpack' esta activado
              (Si solo especificas algunos tipos de objetos, los demas del
              orden por defecto se anadiran al final.)
paranoid_confirmation  lista separada por espacios [paranoid_confirm:pray swim]
              de situaciones en que se desea confirmacion alternativa
              Confirm -- al requerir "si", requerir tambien "no" para rechazar;
                      tambien requiere "yes" en vez de "y" para rezar, trampas, Autoall
              quit    -- "yes" vs "y" para confirmar salir o entrar en modo explorar
              die     -- "yes" vs "y" para confirmar morir (modo explorar o debug)
              bones           permitir cargar archivos de restos                      
              attack  -- "yes" vs "y" para confirmar atacar a un monstruo pacifico
              wand-break  -- "yes" vs "y" para confirmar romper una varita
              eating  -- "yes" vs "y" para confirmar si seguir comiendo
              Were-change -- "yes" vs "y" para confirmar cambio de forma por
                      licantropia cuando el heroe tiene control de polimorfia;
              pray    -- "y" para confirmar un intento de rezar; activado por defecto
              trap    -- "y" para entrar en una trampa conocida salvo que sea inofensiva;
              swim    -- requerir prefijo "m" para entrar en agua o lava cuando
                      el heroe la ha visto y no esta mermado; activado por defecto;
              AutoAll -- "y" para confirmar si usas menustyle:Full y eliges 'A'
                      en el menu de filtrado por clase de objeto;
              Remove  -- siempre elegir del inventario para 'R' y 'T' aunque
                      solo lleves un objeto aplicable para quitar o sacar
perminv_mode  si la interfaz soporta una ventana persistente de inventario [a]
              y perm_invent es true, controla que se mostrara:
              se mostrara:
              none/off -- comportarse como si perm_invent fuera false
              all/on   -- mostrar inventario excepto el oro (por defecto)
              full     -- mostrar inventario incluyendo el oro
              in-use   -- mostrar solo objetos puestos y empunados
              (el soporte opcional de perm_invent en tty incluye
              un par de opciones adicionales que varian all y full)
pickup_burden al recoger un objeto que supere este nivel de carga   [S]
              (Sin carga, Cargado, estresado, forzado, sobrecargado
              o muy sobrecargado), se te preguntara si quieres continuar.
pickup_types  lista de simbolos por defecto para tipos de objetos     []
              autopickup      recoger automáticamente objetos al pasar sobre ellos    
pile_limit    para el aviso al caminar sobre objetos del suelo,      [5]
              umbral a partir del cual se muestra "hay objetos aqui"
              en lugar de listarlos.  (0 significa "listar siempre los objetos.")
runmode       controla la frecuencia de actualizacion del mapa en   [run]
              movimiento multipaso (varios modos de correr o el comando de viaje):
              teleport -- no actualizar el mapa hasta que el movimiento pare;
              run      -- actualizar el mapa periodicamente (cada siete pasos);
              walk     -- actualizar el mapa tras cada paso;
              crawl    -- como walk, pero con retardo tras cada paso.
              (Esto solo afecta a la pantalla, no al movimiento real.)
scores        las partes de la lista de puntuaciones que quieres [!own/3 top/2 around]
              ver cuando termine la partida.  Eliges una combinacion de
              mejores puntuaciones, puntuaciones cercanas a las mejores y
              todas tus puntuaciones.
sortdiscoveries orden preferido al ver la lista de objetos descubiertos [o]
              o -- en orden de descubrimiento dentro de cada clase
              s -- orden "loot" de sortloot
              c -- alfabetico dentro de cada clase
              a -- alfabetico entre todas las clases
sortloot      orden preferido al examinar un conjunto de objetos      [n]
              none -- sin ordenar
              loot -- ordenar pilas de objetos en el suelo y en contenedores
              full -- 'loot' mas objetos del inventario
sortvanquished orden preferido al ver la lista de monstruos derrotados [t]
              t -- tradicional, por nivel del monstruo
              d -- por indice de dificultad del monstruo
              a -- alfabetico, primero monstruos unicos luego los demas
              c -- por clase, de menor a mayor nivel dentro de cada clase
              n -- por cantidad, de mayor a menor
              z -- por cantidad, de menor a mayor
statushilites si mostrar realces de estado (si no es cero) y cuantos   [0]
              turnos mostrar realces temporales (para las reglas de
              hilite_status 'up', 'down' y 'changed')
statuslines   si usar lineas de estado expandidas (3) o condensadas (2) [2]
              (para tty y curses; 2 es tradicional, 3 es recomendado;
              tambien para Qt, donde 3 es tradicional y 2 es recomendado)
suppress_alert desactivar varios avisos especificos de version sobre cambios []
              en el juego o la interfaz, como el aviso de que salir
              se hace ahora con #quit en lugar de con 'Q'
              (p. ej., usa suppress_alert:3.3.1 para desactivar ese y
              cualquier otro aviso anadido en esa version o anterior)
versinfo      que informacion se muestra cuando showvers       [1 o 4]
              es true (el valor por defecto depende del estado de desarrollo)
whatis_coord  controla si incluir coordenadas del mapa al            [n]
              autodescribe    describir el terreno bajo el cursor                     
              El valor es la primera letra de uno de
              compass      -- (relativo a ti; 'este' o '3s' o '2n,4w')
              full compass -- ('este' o '3sur' o '2norte,4oeste')
              map          -- <x,y>        (la columna x=0 del mapa no se usa)
              screen       -- [fila,columna] (fila ajustada al uso de tty)
              none         -- no se muestran coordenadas.
whatis_filter controla como filtrar coordenadas validas del mapa al  [n]
              obtener una ubicacion del mapa, p. ej. el comando de viaje.
              El valor es uno de
              n - sin filtrado
              v - solo ubicaciones a la vista
              a - ubicaciones de la misma zona (sala, pasillo, etc.)

Opciones compuestas que solo pueden establecerse al inicio:

align      tu alineamiento inicial (legal, neutral, caotico,         [random]
           o random).  Muchos roles restringen la eleccion a un subconjunto.
           Puedes especificar solo la primera letra.
catname    nombre de tu mascota inicial si es un gatito             [none]
dogname    nombre de tu mascota inicial si es un perrito            [none]
           Algunos roles que empiezan con un perro tienen uno con nombre
           predefinido (por ejemplo, "Hachi" para Samurai), pero ese nombre
           se sobrescribira si especificas dogname.
gender     tu genero inicial (masculino, femenino o random).        [random]
           Puedes especificar solo la primera letra.  Aunque puedes
           seguir indicando tu genero con las antiguas opciones booleanas
           "male" y "female", la opcion "gender" tendra precedencia.
horsename  nombre de tu mascota inicial si es un poni               [none]
menu_*     especifica aceleradores de un caracter para comandos de menu.
           Aqui va la lista de todos los comandos con su tecla por defecto
           seguida de la lista de window-ports que las implementan:
           (t es tty, c es curses, w es Windows GUI, x es X11, q es Qt)
           menu_first_page    saltar a la primera pagina de un menu    [^](tcwxq)
           menu_last_page     saltar a la ultima pagina de un menu     [|](tcwxq)
           menu_next_page     avanzar a la siguiente pagina del menu   [>](tcwxq)
           menu_previous_page volver a la pagina anterior del menu    [<](tcwxq)
           menu_shift_left    desplazar la vista a la izquierda (solo perm_invent) [{](cx)
           menu_shift_right   desplazar la vista a la derecha (solo perm_invent)  [}](cx)
           menu_select_all    seleccionar todos los objetos de un menu [.](tcwxq)
           menu_select_page   seleccionar todos los objetos de esta pagina [,](tcwq)
           menu_deselect_all  deseleccionar todos los objetos de un menu [-](tcwxq)
           menu_deselect_page deseleccionar todos los objetos de esta pagina [\](tcwq)
           menu_invert_all    invertir todos los objetos de un menu     [@](tcwxq)
           menu_invert_page   invertir todos los objetos de esta pagina  [~](tcwq)
           menu_search        pedir texto objetivo e invertir                [:](tcwxq)
                              los objetos que coincidan
msghistory numero de mensajes de la linea superior a guardar          [20]
name       el nombre de tu personaje   [por defecto, el nombre de usuario en siste-
           mas multiusuario, pregunta "quien eres?" en sistemas monousuario o si
           el nombre de usuario se clasifica como generico como "games"]
           MS Windows se trata como monousuario aunque soporta
           nombres de usuario.  Si el nombre del personaje se especifica en la linea de
           en linea de comandos (normalmente con 'nethack -u minombre') segun el tipo
           de sistema y el metodo de acceso), ese nombre tiene precedencia sobre
           'name' de tus opciones.
pettype    tu tipo preferido de mascota (cat, dog, horse, random, [random]
           o none), si tu rol permite mas de un tipo (o si quieres
           quieres evitar una mascota inicial).  La mayoria de roles admiten dog o cat
           pero no horse.  Para roles que imponen un tipo concreto,
           pettype se ignora a menos que especifique 'none'.
playmode   juego normal, modo explorar sin puntuar o modo debug   [normal]
race       tu raza inicial (p. ej., race:Human, race:Elf).        [random]
           La mayoria de roles restringen la eleccion de raza a un subconjunto.
role       tu rol inicial (p. ej., role:Barbarian, role:Valk).     [random]
           Aunque puedes especificar solo la primera letra o letras, el sistema
           elije solo el primer rol que coincida; por tanto, se
           se recomienda que escribas el nombre del rol lo mas completo
           posible.  Tambien puedes seguir indicando tu rol
           anadiendolo a la opcion "name" (p. ej., name:Vic-V), pero
           la opcion "role" tendra precedencia.
windowtype sistema de ventanas a usar    [depende del sistema operativo y de la
           configuracion de compilacion]   si hay mas de una opcion disponible.
           Algunas instancias del programa solo admiten un tipo de ventana;
           cuando es asi, no necesitas especificar nada.
           La lista de tipos de ventana soportados en tu programa puede verse
           visible mientras el programa se ejecuta usando el comando #version
           comando o desde fuera del programa examinando el archivo de texto
           llamado 'options' que se genera al compilarlo.

Algunos ejemplos de listas de opciones son:
!autopickup,!tombstone,name:Gandalf,scores:own/3 top/2 around
female,nonews,dogname:Rover,rest_on_space,!verbose,menustyle:traditional
