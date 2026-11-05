	Dependiendo del hardware, del sistema operativo o de la interfaz de NetHack,
	algunas combinaciones de teclas pueden no estar disponibles.

	Por ejemplo, ^S y ^Q se usan a menudo para control de flujo XON/XOFF,
	lo que significa que ^S suspende la salida y ^Q reanuda la salida
	suspendida.  Cuando esto ocurre, ninguno de esos caracteres
	llegará a NetHack cuando esté esperando una tecla de comando.  Por lo tanto, no
	se usan como comandos, pero 'whatdoes' puede no ser capaz de indicarte
	que no llegan a NetHack.

	^M o <return> o <enter> probablemente se transformarán en ^J o
	<linefeed> o 'newline' antes de pasarse a NetHack.
	Por lo tanto, no se usa como comando, y 'whatdoes' puede parecer como si
	notificara el carácter incorrecto pero funcionará correctamente si
	describe ^J cuando tecleas ^M.

	Un carácter NUL, que se teclea como ^<espacio> en algunos teclados,
	^@ en otros, y quizás ni siquiera se pueda teclear en otros, no se
	usa como comando, y se convertirá en ESC antes de llegar a
	'whatdoes'.  A diferencia de ^M, esta transformación se realiza dentro de
	NetHack.  Pero como con ^M, si tecleas NUL y recibes respuesta sobre ESC,
	la situación es la esperada.

	El propio ESC es un sinónimo de ^[, y es otra fuente de rarezas.
	Varias teclas de función, incluyendo las teclas de cursor, pueden transmitir
	una "secuencia de escape" de ESC + [ + otras cosas, confundiendo a NetHack
	sobre qué comando se pretendía ya que el ESC se procesará
	y luego lo que siga parecerá a NetHack como--y se usará
	como--algo tecleado por el usuario.  (Si pulsas una tecla de función y
	aparece un menú con la armadura que lleva tu héroe, lo que ocurrió
	fue que se envió una secuencia de escape a NetHack, su ESC canceló
	cualquier operación de tecla pendiente, su '[' se trató entonces como un comando
	para mostrar la armadura puesta, y el "otro material" probablemente se ignoró
	silenciosamente como opciones inválidas mientras descartabas el menú.)

	Si tienes activada la opción 'altmeta' de NetHack, lo que significa que la
	tecla <alt> o <option>, al usarse como shift mientras tecleas otra
	tecla, transmite ESC y luego el otro carácter para que NetHack
	trate ese otro carácter como un meta-carácter, entonces ESC
	adquiere un potencial adicional de confusión.  Implícito en el manejo
	de una secuencia de dos caracteres ESC + algo está el hecho de que cuando
	NetHack ve ESC, necesita esperar otro carácter antes de
	poder decidir qué hacer.  Así que si tecleas ESC manualmente, tendrás
	que teclearlo una segunda vez o NetHack se quedará esperando.
	(Entonces se tratará como si hubieras tecleado ESC en lugar de M-ESC.)

	En algunos sistemas, teclear ^\ enviará una señal QUIT al
	proceso actual, probablemente terminándolo y posiblemente haciendo que guarde un
	volcado de memoria.  No se usa para ningún comando de NetHack, así que no teclees
	ese carácter.

	Una última nota: los caracteres que se muestran como ^x significan que debes mantener
	pulsada la tecla <control> o <ctrl> como modificador y luego teclear 'x'.
	Los caracteres de control son todos implícitamente mayúsculas, pero no
	necesitas pulsar shift mientras los tecleas.  Lo contrario ocurre
	con los meta-caracteres: pueden ser en mayúsculas o minúsculas, así que necesitas
	usar shift además de <meta> o <alt> para generar un meta-carácter
	en mayúsculas.
