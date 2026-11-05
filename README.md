# NetHack Bald — estado del desarrollo

Proyecto Windows nativo en C++17. El objetivo del proyecto es un **NetHack fiel al original, traducido íntegramente al español, con gráficos por spritesheet y partidas compartidas por 2 a 6 personajes independientes**.

**No está terminado.** El código que compila actualmente es una base multijugador propia, no una conversión 1:1 de las reglas completas de NetHack.

## Compilar en Windows

Necesitas **Git, CMake y un compilador C++17 para Windows**, como MSVC (Visual Studio / Build Tools) o MinGW-w64. **Sin sistemas adicionales ni máquinas virtuales.**

Desde PowerShell:

~~~powershell
git clone https://github.com/glitchaka/net-hack-bald.git
cd net-hack-bald
cmake -S . -B build
cmake --build build --config Release
~~~

Ejecutable esperado: `build/Release/nethack-bald.exe` (Visual Studio) o `build/nethack-bald.exe` (otros generadores).

También existe el instalador [scripts/instalar_y_compilar.ps1](scripts/instalar_y_compilar.ps1), que descarga o actualiza el repositorio y utiliza exclusivamente herramientas C++ nativas de Windows.

Al ejecutar `nethack-bald.exe` **sin argumentos**, aparece el menú para crear partida y jugar, unirse, iniciar servidor, consultar ayuda o salir. Los errores del menú permanecen visibles en la ventana.

Para una partida de dos jugadores en el mismo equipo: abre el ejecutable y selecciona **Crear partida y jugar**; abre una segunda instancia y selecciona **Unirse a una partida** (IP `127.0.0.1`). Para equipos distintos, inicia un servidor dedicado en una LAN confiable usando `--bind=0.0.0.0` y `--clave=SECRETO`, y conecta los clientes con esa misma clave.

**Seguridad:** el protocolo multijugador de esta base todavía no tiene cifrado, por lo que **no se debe abrir directamente a Internet**.

## Código

- `src/multiplayer/`: motor C++17 con un único mundo, hasta seis personajes independientes, acciones sincronizadas por rondas, inventarios propios, mapa con visión individual, monstruos, combate y persistencia.
- `include/nhb/`: estructuras de mundo, red y terminal.
- `upstream/nethack/`: **fuente del NetHack 5.0 original** importada desde [NetHack-es](https://github.com/Ricard1974/nethack-es/tree/NetHack-5.0-es). Es C99 y **no está acoplada al ejecutable multijugador propio**.
- `upstream/nethack/win/share/`: recursos originales de tiles de NetHack en `monsters.txt`, `objects.txt`, `other.txt`, con `tilemap.c`. **La interfaz basada en sprites aún no se ha integrado.**
- `.github/workflows/compilar-cpp.yml`: compilación y pruebas automáticas exclusivamente en Windows.

## Pendientes obligatorios

- **Fidelidad 1:1:** faltan mecánicas completas de NetHack en el mundo multijugador C++.
- **Español 100 %:** la traducción de NetHack-es todavía contiene cadenas sin traducir, especialmente misiones y contenido auxiliar.
- **Spritesheet:** integrar el tileset original con la correspondencia exacta de cada casilla.
- **Experiencia multijugador:** revisar y validar simultaneidad, reconexión, guardado y reglas compartidas.
- **Verificación:** ampliar las pruebas de juego en Windows.

No presentar estos elementos como terminados hasta comprobarlos realmente.

## Licencia

La distribución importada de NetHack queda bajo la NetHack General Public License. Consultar `upstream/nethack/dat/license`.
