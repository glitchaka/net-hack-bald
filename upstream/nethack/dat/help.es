        ¡Bienvenido a NetHack!                ( descripción de la versión 3.6 )

        NetHack es un juego al estilo de Calabozos y Dragones donde tú (el aventurero)
desciendes a las profundidades de la mazmorra en busca del Amuleto de Yendor,
que se dice está escondido en algún lugar más allá del nivel veinte.  Empiezas tu
aventura con una mascota que puede ayudarte de muchas formas, y puede ser entrenada
para hacer todo tipo de cosas.  Por el camino encontrarás objetos útiles (o inútiles)
posiblemente con propiedades mágicas, y toda clase de monstruos.  Puedes
atacar a un monstruo intentando moverte a su casilla (pero a menudo
es mucho más sensato dejarlo en paz).

        A diferencia de la mayoría de juegos de aventura, que te dan una descripción verbal de
tu ubicación, NetHack te da una imagen visual del nivel de la mazmorra en el que
estás.

        NetHack usa los siguientes símbolos:

        - y |        Las paredes de una sala, o quizás puertas abiertas o una tumba.
        .        El suelo de una sala o un vano de puerta.
        #        A corridor, or iron bars, or a tree, or possibly a kitchen
                 (si tu mazmorra tiene fregaderos), o un puente levadizo.
        >        Escaleras abajo: camino al siguiente nivel.
        <        Escaleras arriba: camino al nivel anterior.
        @        Tú (normalmente), u otro humano.
        )        Un arma de algún tipo.
        [        Una armadura o pieza de armadura.
        %        Algo comestible (no necesariamente sano).
        /        Una varita.
        =        Un anillo.
        ?        Un pergamino.
        !        Una poción.
        (        Otro objeto útil (pico, llave, lámpara ...)
        $        Un montón de oro.
        *        Una gema o roca (posiblemente valiosa, posiblemente inútil).
        +        Una puerta cerrada, o un libro de hechizos que contiene un hechizo
                 que puedes aprender.
        ^        Una trampa (una vez que la detectas).
        "        Un amuleto, o una telaraña.
        0        Una bola de hierro.
        _        Un altar, o una cadena de hierro.
        {        Una fuente.
        }        Una charca de agua o foso o una charca de lava.
        \        Un trono opulento.
        `        Una roca o estatua.
        De la A a la Z, de la a a la z, y varios otros:  Monstruos.
        I        Última ubicación conocida de un monstruo invisible

                 Puedes averiguar qué representa un símbolo tecleando
                 '/' siguiendo las direcciones para mover el cursor
                 hasta el símbolo en cuestión.  Por ejemplo, una 'd' puede
                 resultar ser un perro.


y k u   7 8 9   Comandos de movimiento:
 \|/     \|/            yuhjklbn: avanzar un paso en la dirección indicada
h-.-l   4-.-6           YUHJKLBN: avanzar en dirección indicada hasta que
 /|\     /|\                        chocar con una pared u obstáculo
b j n   1 2 3           g<dir>:   correr en dirección <dir> hasta que algo
      teclado numérico              interesante se vea
                        G<dir>,   igual, excepto que un pasillo ramificado no
 <  arriba              ^<dir>:     se considera interesante (la ^ en este
                                    caso significa la tecla Control, no un acento circunflejo)
 >  abajo               m<dir>:   moverse sin recoger objetos
                        F<dir>:   luchar aunque no percibas un monstruo
                Si la opción number_pad está activada, las teclas numéricas mueven en su lugar.
                Dependiendo de la plataforma, Mayús+número (en el teclado numérico),
                Meta+número, o Alt+número invocarán los comandos YUHJKLBN.
                Control <dir> puede o no funcionar cuando number_pad está activado,
                dependiendo de las capacidades de la plataforma.
                El dígito '5' actúa como prefijo 'G', a menos que number_pad esté en 2
                en cuyo caso actúa como 'g'.
                Si number_pad está en 3, los roles de 1,2,3 y 7,8,9 están
                invertidos; en 4, se comporta igual que 3 combinado con 2.
                Si number_pad está en -1, se usan comandos de movimiento alfabéticos
                pero 'y' y 'z' están intercambiados.

Comandos:
        NetHack conoce los siguientes comandos:
        ?       Menú de ayuda.
        /       Qué-es, dice qué representa un símbolo.  Puedes elegir
                especificar una ubicación o dar un símbolo como argumento.  Activar la
                opción autodescribe dará información sobre el símbolo
                en cada ubicación donde muevas el cursor.
        &       Dice qué hace un comando.
        <       Subir una escalera (si estás sobre ella).
        >       Bajar una escalera (si estás sobre ella).
        .       Descansar, no hacer nada durante un turno.
        _       Viajar mediante algoritmo de ruta más corta a un punto del mapa.
        a       Aplicar (usar) una herramienta (pico, llave, lámpara ...).
        A       Quitar toda la armadura.
        ^A      Rehacer el comando anterior.
        c       Cerrar una puerta.
        C       Llamar (nombrar) un monstruo, objeto individual, o tipo de objeto.
        d       Soltar algo.  d7a:  soltar siete unidades del objeto a.
        D       Soltar varios objetos.  Este comando está implementado de dos
                formas distintas.  Una forma es:
                "D" muestra una lista de todos tus objetos, de la que puedes
                elegir qué soltar.  Un "+" junto a un objeto significa
                que será soltado, un "-" significa que no será
                soltado.  Cambia la selección de un objeto tecleando
                la letra junto a su descripción.  Selecciona todos los objetos
                con "+", deselecciona todos con "=".  La <BARRA ESPACIADORA> pasa
                de una página del listado a la siguiente.
                La otra forma es:
                "D" preguntará "¿Qué tipos de cosas quieres
                soltar? [!%= au]".  Debes teclear cero o más símbolos de objeto
                posiblemente seguidos de 'a' y/o 'u'.
                Da - soltar todos los objetos, sin pedir confirmación.
                Du - soltar solo objetos no pagados (cuando estés en una tienda).
                D%u - soltar solo comida no pagada.
        ^D      Patear (para puertas, normalmente).
        e       Comer comida.
        E       Grabar un mensaje en el suelo.
                E- - escribir en el polvo con los dedos.
        f       Disparar munición del carcaj.
        F       Seguido de dirección, lucha contra un monstruo (incluso si no
                lo percibes).
        i       Mostrar tu inventario.
        I       Mostrar partes seleccionadas de tu inventario, como
                I* - listar todas las gemas del inventario.
                Iu - listar todos los objetos no pagados.
                Ix - listar todos los objetos gastados que están en tu cuenta de la tienda.
                I$ - contar tu dinero.
        o       Abrir una puerta.
        O       Revisar las opciones actuales y posiblemente cambiarlas.
                Se mostrará un menú con los ajustes de opciones
                y la mayoría pueden cambiarse simplemente seleccionando su entrada.
                Las opciones normalmente se ajustan antes de la partida con la variable
                de entorno NETHACKOPTIONS o mediante un fichero de configuración (defaults.nh,
                NetHack Defaults, nethack.cnf, ~/.nethackrc, etc.) en lugar de
                con el comando 'O'.
        p       Pagar la cuenta de la tienda.
        P       Ponerse un accesorio (anillo, amuleto, etc).
        ^P      Repetir el último mensaje (^P sucesivos repiten mensajes anteriores).
                El comportamiento puede variarse mediante la opción msg_window.
        q       Beber algo (poción, agua, etc).
        Q       Seleccionar munición para el carcaj.
        #quit   Exit the program without saving the current game.
        r       Leer un pergamino o libro de hechizos.
        R       Quitarse un accesorio (anillo, amuleto, etc).
        ^R      Redibujar la pantalla.
        s       Buscar puertas secretas y trampas a tu alrededor.
        S       Guardar la partida.  También sale del programa.
                [Para restaurar, solo juega de nuevo y usa el mismo nombre de personaje.]
                [No existe la capacidad de "guardar datos actuales pero seguir jugando".]
        t       Lanzar un objeto o disparar un proyectil.
        T       Quitarse la armadura.
        ^T      Teletransportarse, si eres capaz.
        v       Muestra el número de versión.
        V       Muestra una identificación más larga de la versión, incluyendo la
                historia del juego.
        w       Equipar arma.  w- significa no equipar nada, usar las manos.
        W       Ponerse armadura.
        x       Intercambiar armas equipada y secundaria.
        X       Activar/desactivar combate con dos armas.
        ^X      Mostrar tus atributos.
        #explore  Switch to Explore Mode (aka Discovery Mode) where dying and
                borrar el fichero guardado durante la restauración no tendrán efecto.
        z       Disparar una varita.  (Usa y en lugar de z si number_pad es -1.)
        Z       Lanzar un hechizo.  (Usa Y en lugar de Z si number_pad es -1.)
        ^Z      Suspender la partida.  (^Y en lugar de ^Z si number_pad es -1.)
                [Para reanudar, usa el comando de shell 'fg'.]
        :       Mirar lo que hay aquí.
        ;       Mirar lo que hay en otro lugar.
        ,       Recoger algunos objetos.
        @       Activar/desactivar la opción de recogida.
        ^       Preguntar por el tipo de una trampa que encontraste antes.
        )       Dice qué arma llevas equipada.
        [       Dice qué armadura llevas puesta.
        =       Dice qué anillos llevas puestos.
        "       Dice qué amuleto llevas puesto.
        (       Dice qué herramientas estás usando.
        *       Dice qué equipo estás usando; combina los cinco anteriores.
        $       Contar tus monedas de oro.
        +       Listar los hechizos que conoces; también reordenarlos si lo deseas.
        \       Mostrar qué tipos de objetos se han descubierto.
        `       Mostrar tipos descubiertos para una clase de objetos.
        !       Salir al shell, si está soportado en tu versión y SO.
                [Para reanudar, termina el subproceso del shell con 'exit'.]
        #       Introduces one of the "extended" commands.  To get a list of
                los comandos que puedes usar con "#" teclea "#?".  Los comandos
                extendidos disponibles dependen de las opciones con las que se compiló
                el juego, de tu clase y del tipo de monstruo
                al que más te pareces en cada momento.  Si tu teclado
                tiene tecla Alt, puedes invocar los comandos extendidos
                pulsando Alt + la primera letra del comando.
                [Si tu teclado no tiene Alt, prueba con la tecla
                Modificador o la tecla de Windows.]

        Si la opción "number_pad" está activada, algunos comandos de letras adicionales
        están disponibles:

        h       muestra el menú de ayuda, como '?'
        j       Saltar a otra ubicación.
        k       Patear (para puertas, normalmente).
        l       Saquear una caja en el suelo.
        n       seguido del número de veces para repetir el siguiente comando.
        N       Nombrar un monstruo, un objeto individual, o un tipo de objeto.
        u       Desactivar la trampa de un objeto o puerta.

        Puedes poner un número antes de un comando para repetirlo ese número de veces,
        como en "40." o "20s".  Si tienes la opción number_pad activada,
        debes teclear 'n' para prefijar la cuenta, como en "n40." o "n20s".


        Parte de la información se muestra en la línea inferior o quizás en una
        ventana, dependiendo de la plataforma que uses.  Ves tus
        atributos, tu alineamiento, en qué nivel de la mazmorra estás, cuántos
        puntos de golpe tienes ahora (y tendrás cuando te recuperes), cuál
        es tu clase de armadura (cuanto más baja mejor), tu nivel de experiencia,
        y el estado de tu estómago.  Opcionalmente, puedes ver o no
        otra información como puntos de hechizo, cuánto oro tienes, etc.

        ¡Diviértete, y feliz hacking!
