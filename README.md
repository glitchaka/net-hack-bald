# NetHack Bald — NetHack original con interfaz gráfica Windows

**El ejecutable principal es ahora NetHackW.exe: el NetHack 5.0 original, no el prototipo de consola.** Permite jugar en solitario y utiliza el port gráfico Win32 y los tiles originales.

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

La compilación utiliza el proyecto oficial de NetHack para Windows, y obtiene sus dependencias Lua 5.4.8 y PDCursesMod 4.4.0. Si MSBuild falla, mostrará el error y no presentará el programa como compilado.

**Ejecutable que corresponde abrir: build/Release/NetHackW.exe.** Este es un programa gráfico de Windows; puedes jugar solo. Los ejecutables antiguos del roguelike experimental se marcarán como obsoletos.

## Qué corresponde realmente a cada parte

- **upstream/nethack/**: el código íntegro original de NetHack 5.0, distribuido según la NetHack General Public License (NGPL).
- **upstream/nethack/sys/windows/vs/NetHack.sln**: proyecto original que construye NetHackW.exe y empaqueta archivos de datos y gráficos.
- **scripts/compilar-nethack-original.ps1**: preparación y construcción del juego real en Windows.
- **src/multiplayer/**: prototipo independiente de 2 a 6 personajes; NO forma parte del juego original, NO es NetHack 1:1 y NO se compila por defecto.

**Pendiente:** la adaptación española importada de NetHack-es no es completa; el motor original sigue escrito en C99 y el multijugador de 2 a 6 personajes independientes no está integrado en NetHack. Tampoco se ha implementado la interfaz gráfica propia adicional solicitada: se utiliza la interfaz gráfica original.

No se volverá a presentar el prototipo de terminal como NetHack.

## Créditos y licencia

NetHack original: NetHack DevTeam. Adaptación parcial española: [Ricard1974/nethack-es](https://github.com/Ricard1974/nethack-es/tree/NetHack-5.0-es). Licencia del motor: upstream/nethack/dat/license.
