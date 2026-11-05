# NetHack Bald — NetHack 5.0 en español + cooperativo C++17

El proyecto incorpora **el código completo de NetHack 5.0**, a través de su [adaptación española NetHack-es](https://github.com/Ricard1974/nethack-es/tree/NetHack-5.0-es), y un **servidor/cliente multijugador escrito en C++17**.

**Estado:** fuentes publicadas en GitHub. **Todavía no compiladas ni probadas**, respetando la pauta de subir todo antes de las pruebas.

| Componente | Lenguaje | Funcionalidad |
| --- | --- | --- |
| `upstream/nethack/` | C99, Lua | **Motor original completo** (no una imitación simplificada) |
| `upstream/nethack/po/es.po` y datos | gettext/Lua | Traducción al español **parcial** |
| `multiplayer/main.cpp` | C++17 | Hasta ocho jugadores compartiendo una partida de NetHack por TCP |

El modo multijugador permite **ver una misma partida, conversar y cederse el control del mismo personaje**. **No** dispone de varios héroes simultáneos. Ese modo requerirá refactorización profunda del motor y sigue pendiente. No es correcto llamar a esta versión "clon 1:1 en C++": el **motor genuino** se conserva en C99.

## Compilar el NetHack original en español

Desde la raíz del repositorio, en Linux/WSL:

```bash
sudo apt install build-essential cmake libncurses-dev flex bison gettext
cd upstream/nethack
cd sys/unix && sh setup.sh hints/linux.500 && cd ../..
make fetch-lua && make
msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo
make dlb
cp dat/nhdat playground/
cd playground
LANG=es.UTF-8 ./nethack
```

Consultar también el README propio dentro de `upstream/nethack`. En Windows se puede recurrir a WSL para el motor original y el **servidor**. Se incluye también un **cliente Windows nativo**, compilado con C++17/WinSock.

## Compilar y conectar el multijugador C++17

Desde la raíz del repositorio:

```bash
cmake -S . -B build
cmake --build build --config Release
./build/nethack-bald-multi servidor --juego=upstream/nethack/playground/nethack --puerto=7777
```

En otras terminales:

```bash
./build/nethack-bald-multi cliente --ip=127.0.0.1 --nombre=Uno
./build/nethack-bald-multi cliente --ip=127.0.0.1 --nombre=Dos
```

En **Windows nativo**, la compilación CMake genera el **cliente** `nethack-bald-multi.exe` (no el servidor). Se ejecuta con `nethack-bald-multi.exe cliente --ip=127.0.0.1 --nombre=Uno`, conectado al servidor Linux/WSL.

- **Ctrl+T:** ceder control al siguiente participante.
- **Ctrl+G:** chat.
- **Ctrl+]:** desconectarse.

Por defecto escucha solamente en 127.0.0.1. Para LAN: servidor con `--bind=0.0.0.0 --clave=SECRETO` y clientes con `--clave=SECRETO`. **No usa TLS: únicamente LAN de confianza, nunca exponer directamente a Internet.**

Más información: [docs/MULTIJUGADOR.md](docs/MULTIJUGADOR.md).

## Estado real de los requisitos

- **Mecánicas NetHack 5.0:** fuente genuina incorporada.
- **Español:** gran parte traducida; quedan textos y secuencias de misiones sin traducir.
- **C++:** infraestructura multijugador implementada; motor original aún C99.
- **Multijugador:** hasta ocho clientes Linux/Windows; sesión compartida de un personaje, no varios héroes independientes.
- **Pruebas:** no realizadas.
- **Licencia:** NetHack General Public License, véase [upstream/nethack/dat/license](upstream/nethack/dat/license) y [LICENCIA.md](LICENCIA.md).

Código original NetHack DevTeam. Adaptación española Ricard1974. Módulo cooperativo NetHack Bald. El prototipo independiente anterior se retiró por no cumplir el requisito de fidelidad.
