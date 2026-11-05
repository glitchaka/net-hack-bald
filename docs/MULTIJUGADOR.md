# Multijugador de NetHack Bald (C++17)

**Estado actual:** módulo multijugador nativo de Windows para **entre dos y seis personajes distintos**. Es un motor propio parcial: **NO es todavía el motor completo de NetHack 1:1**.

## Cómo funciona

- Un servidor mantiene la única mazmorra compartida.
- Cada jugador tiene su propio personaje, nombre, clase, posición, salud, maná, equipo, inventario, descubrimiento de mapa y progresión.
- Los participantes envían una acción por ronda. Cuando han enviado órdenes todos los jugadores conectados que siguen activos, el servidor resuelve la ronda y las acciones de los monstruos.
- El servidor guarda el estado en `partida-multi.nhb`.
- Máximo seis personajes registrados y conectados; no se comparte un único avatar.

## Windows nativo

Se necesita compilador C++17 para Windows, Git y CMake:

~~~powershell
git clone https://github.com/glitchaka/net-hack-bald.git
cd net-hack-bald
cmake -S . -B build
cmake --build build --config Release
~~~

Abre `build/Release/nethack-bald.exe` (Visual Studio), o `build/nethack-bald.exe` (MinGW), **con doble clic** y aparecerá un menú interactivo.

En el primer equipo selecciona **Crear partida y jugar**. En el segundo ejecutable selecciona **Unirse a partida**. Si quieres jugar desde distintos equipos, inicia un servidor dedicado vinculado a la LAN y conecta los clientes mediante la dirección IPv4 del servidor.

Los comandos por terminal son una alternativa:

~~~powershell
.\build\Release\nethack-bald.exe servidor --bind=127.0.0.1 --puerto=7777
.\build\Release\nethack-bald.exe cliente --ip=127.0.0.1 --nombre=Ada --clase=maga
.\build\Release\nethack-bald.exe cliente --ip=127.0.0.1 --nombre=Bran --clase=guerrero
~~~

Las clases disponibles son `guerrero`, `maga`, `picaro` y `valquiria`.

**Importante:** el protocolo TCP todavía carece de cifrado, así que no abras el puerto directamente a Internet. Se admite `--clave=SECRETO` para LAN confiable, pero esa clave no se cifra.

## Controles

Movimiento con `hjklyubn`, diagonales o teclado numérico; `.` espera; `g` recoge; `e` come; `q` bebe curación; `m` bebe maná; `w` equipa arma; `W` equipa armadura; `r` lee; `f` dispara; `z` usa magia; `o` abre puertas; `<` y `>` cambian de profundidad. `Ctrl+G` abre el chat y `Ctrl+]` se desconecta.

## Limitaciones pendientes

- Reproducir las mecánicas completas del NetHack original.
- Traducir todos los textos del juego original, incluidas misiones y descripciones especiales.
- Integrar gráficamente el spritesheet original y las correspondencias exactas de los tiles.
- Validar íntegramente jugabilidad, reconexión, guardado y seguridad en Windows.

El código completo del NetHack original permanece en `upstream/nethack/`, pero está escrito en C99 y **no está acoplado** a esta variante multijugador C++.
