# NetHack Bald — NetHack original con interfaz gráfica Windows

**Estado:** se está reparando el empaquetado de la aplicación gráfica original de NetHack 5.0 para Windows. **Esto NO es todavía el clon propio 1:1 en C++ con 2-6 jugadores que pediste.** La descarga y compilación del motor original es solo una base de referencia. El modo solitario está disponible en el motor original, pero la extensión multijugador no está integrada.

El objetivo final sigue siendo preservar NetHack 1:1, completarlo en español, trabajar en C++ e incorporar multijugador de 2 a 6 personajes independientes. **Ese objetivo aún no está terminado.**

## Windows: compilar el juego original

Requisitos: Visual Studio o Visual Studio Build Tools con el componente **Desarrollo de escritorio con C++**, Windows SDK y MSBuild; Git y CMake 3.20+. Todo es Windows nativo.

Clona si todavía no existe:

~~~powershell
git clone https://github.com/glitchaka/net-hack-bald.git
cd net-hack-bald
cmake -S . -B build
cmake --build build --config Release
~~~

Si ya lo tienes:

~~~powershell
git pull --ff-only
cmake -S . -B build
cmake --build build --config Release
~~~

La compilación utiliza el proyecto oficial de NetHack para Windows, y obtiene sus dependencias Lua 5.4.8 y PDCursesMod 4.4.0. El script también convierte el catálogo `po/es.po` a `locale/es/LC_MESSAGES/nethack.mo`, y la entrada gráfica configura el idioma español por defecto. **La traducción actual no cubre el 100 % de los textos.** Si MSBuild falla, mostrará el error y no presentará el programa como compilado.

**Ejecutable principal: `build/Release/nethack-bald.exe`.** Se construye desde el port gráfico original de Windows, comprueba su subsistema PE de aplicación gráfica y no necesita abrir una ventana de CMD. Se elimina del paquete final el ejecutable `NetHack.exe` de consola y se archivan los prototipos anteriores. **Importante:** se trata del NetHackW original empaquetado, no de una GUI nueva diseñada para este proyecto.

## Qué corresponde realmente a cada parte

- **upstream/nethack/**: el código íntegro original de NetHack 5.0, distribuido según la NetHack General Public License (NGPL).
- **upstream/nethack/sys/windows/vs/NetHack.sln**: proyecto original que construye NetHackW.exe y empaqueta archivos de datos y gráficos.
- **scripts/compilar-nethack-original.ps1**: preparación y construcción del juego real en Windows.
- **src/multiplayer/**: prototipo independiente de 2 a 6 personajes; NO forma parte del juego original, NO es NetHack 1:1 y NO se compila por defecto.

**Pendiente:** la adaptación española importada de NetHack-es no es completa, aunque ya se genera el catálogo para Windows; el motor original sigue escrito en C99 y el multijugador de 2 a 6 personajes independientes no está integrado en NetHack. Sigue pendiente la GUI propia que solicitaste. Tampoco se ha implementado la interfaz gráfica propia adicional solicitada: se utiliza la interfaz gráfica original.

No se volverá a presentar el prototipo de terminal como NetHack.

## Créditos y licencia

NetHack original: NetHack DevTeam. Adaptación parcial española: [Ricard1974/nethack-es](https://github.com/Ricard1974/nethack-es/tree/NetHack-5.0-es). Licencia del motor: upstream/nethack/dat/license.
