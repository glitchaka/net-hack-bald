Esta es una descripción breve de los argumentos de línea de comandos de nethack.
Está orientado a UNIX (incluyendo descendientes como linux y macOS)
y puede no ser exacto para otras plataformas.

Al empezar a jugar, si existe un fichero de guardado para el nombre de personaje elegido
se restaurará, si no, empezará una nueva partida con ese nombre.

nethack
  sin argumentos; usa el nombre de personaje de la entrada OPTIONS=nombre:personaje
  entrada OPTIONS=nombre:personaje, o el nombre de usuario del jugador si no hay.

nethack -u nombre-personaje [-X o -D]
  '-u nombre-personaje' especifica el nombre a usar para el personaje de esta partida;
       -u debe ser minúscula; el espacio entre ella y el nombre del personaje puede
       omitirse;
  '-X' juega en modo exploración sin puntuación, también llamado modo descubrimiento;
       -X debe ser mayúscula; el personaje empieza con una varita de deseos y
       el jugador puede optar a ser salvado por vida y continuar si el personaje muere;
  '-D' ejecuta en modo debug, también conocido como modo wizard; -D debe ser mayúscula;
       si no se permite al jugador, nethack cambiará a -X; si se permite
       se permite, el nombre del personaje se cambiará a "wizard".

  Un nombre de personaje puede tener un sufijo que especifique todo o parte de rol, raza,
  género y alineamiento, como -u Conan-Bar-Hum-Mal-Neu o -u Tim-Wiz.
  Los componentes presentes deben tener al menos tres letras pero pueden
  más largos; su caso no importa.  Ver también -p y -r, a continuación,

nethack -p Ppp -r Rrr [-@]
  '-p Ppp' especifica el rol; se usa p de "profesión" porque -r ya está en uso;
       'Ppp' son tres o más letras del nombre del rol, como Val para
       Valkyrie; a diferencia de la propia -p, no importa si Ppp va en mayúscula o minúscula
  '-r Rrr' especifica la raza o especie: Hum[ano], Elf, Orc, Dwa[rf], Gno[mo];
  '-@' forzar inicio no interactivo; cualquiera de rol, raza, género y
       alineamiento que no se especifique en la línea de comandos o en el
       fichero de configuración se elige al azar sin preguntar;
       el signo @ puede necesitar comillas precediéndolo con barra invertida.

  La forma antigua del rol también se sigue aceptando:  -A o -Arc[heologist],
  -B o -Bar[barian], -C o -Cav[ernícola] o -Cavew[oman], -H o -Hea[ler],
  -K o -Kni[ght], -M o -Mon[k], -P o -Pri[est] o -Prieste[ss],
  -Ran[ger], -R o -Rog[ue], -S o -Sam[urai], -T o -Tou[rist],
  -V o -Val[kyrie], -W o -Wiz[ard].  La forma de una sola letra debe estar en
  mayúscula, la forma de tres o más letras puede ir en cualquier caso.  No hay
  no hay opción de una sola letra para el rol Ranger.

nethack -DEC[graphics]
nethack -IBM[graphics]
  selecciona el conjunto de símbolos DEC o IBM para usar caracteres de dibujo de líneas en un
  mapa de texto; puede ignorarse según la interfaz, o no ser efectivo o
  incluso desordenados según la capacidad de pantalla; -DECgraphics y
  -IBMgraphics son excluyentes; pueden ir en cualquier caso pero deben usar
  al menos tres letras.

nethack -wIii
nethack --windowtype:Iii
  donde 'Iii' representa una designación de interfaz:  tty, curses, X11 o
  Qt; solo útil si el programa se compiló con soporte para más de una
  interfaz (el comando '#version' del juego lo mostrará); sobrescribe
  OPTIONS=windowtype:Iii en el fichero de configuración y en el valor por defecto
  por defecto; '-w' o '--windowtype' deben ir en minúscula, la interfaz
  en sí puede ir en cualquier caso; las variantes '--windowtype Iii' y
  '-w Iii' también funciona.

  En Windows, nethack.exe admite tty o curses o ambos según los
  ajustes en el momento de compilar el programa; nethackW.exe
  admite mswin (también conocido como Win GUI) y opcionalmente curses.
  Para MS-DOS, el programa admite tty o curses o ambos.

nethack -n
  no muestra el fichero 'news' si hay uno en el directorio de nethack.

nethack --nethackrc:fichero-RC
  usa fichero-RC en lugar del fichero de configuración por defecto (que suele ser
  normalmente '~/.nethackrc'); el nombre de fichero debe incluir la ruta completa a menos que
  ubicado en el directorio de nethack;
nethack --no-nethackrc
  no usa ningún fichero de configuración; equivale a
  --nethackrc:/dev/null que se comporta como un fichero vacío.

nethack -dDir
nethack --directory:Dir
  puede usarse para sobrescribir el valor de compilación de NETHACKDIR con
  ubicación Dir; si se usa, debe preceder a otros argumentos de la línea de comandos.

Las opciones anteriores se pueden combinar en una sola línea de comandos;
se listan por separado por legibilidad.

*******

Otras opciones que realizan alguna acción y luego salen en lugar de jugar
la partida:

nethack -s
nethack --scores
  muestra las puntuaciones del personaje por defecto; argumentos opcionales adicionales:
nethack -s -v
  muestra las puntuaciones de todas las versiones presentes en el fichero de récords
  si contiene puntuaciones de versiones anteriores; por defecto, solo se muestran
  para la versión actual de nethack; cuando se use '-v', debe ir
  inmediatamente después de -s o --scores, antes de cualquier nombre o -p o -r;
nethack -s nombre-personaje [nombre-personaje2 [nombre-personaje3 [...]]]
  muestra las puntuaciones de uno o varios nombres de personaje específicos (puede no ser
  efectivo si PERS_IS_UID=1 se especifica en el sysconf de nethack);
  los nombres de personaje pueden ir precedidos por '-u' pero no es obligatorio;
  el nombre de personaje especial "all" se usa para mostrar todas las puntuaciones que pasen
  otros criterios;
nethack -s -p Ppp -r Rrr
  muestra las puntuaciones de roles o razas específicos; pueden usarse varias instancias;
  si se usan tanto '-p' como '-r', se muestran las puntuaciones que coincidan con cualquiera
  en lugar de las que coincidan con ambos;
nethack -dDir -s
nethack --directory:Dir -s
  como arriba; el directorio alternativo, si se especifica, debe ir primero.

nethack --version o --version:copy o --version:dump o --version:show
  '--version' mostrar el número de versión del programa más la fecha y
  la hora de compilación del código fuente, y luego sale;
  '--version:copy' mostrar número de versión y copiarlo al
  portapapeles (debería funcionar en macOS y Windows; puede no funcionar en otros
  sistemas) para poder pegarlo desde ahí en un correo electrónico posterior
  o formulario de contacto web, y luego sale;
  '--version:dump' muestra varios valores internos y luego sale;
  '--version:show' igual que '--version'.

nethack --showpaths
  lista las ubicaciones esperadas de varios ficheros y directorios y luego sale;
  incluye el nombre y la ubicación del fichero de configuración que
  puede variar de plataforma a plataforma.

nethack --usage
nethack --help
  muestra este texto; 'nethack -?' y 'nethack ?' también funcionan, pero el signo de
  marca de interrogación puede necesitar comillas para evitar que el shell la intercepte.

*******

Este texto está disponible durante el juego en el menú del comando '?' del juego
o verse con 'nethack --usage | more' en el prompt del shell.

