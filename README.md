# NetHack Bald

**NetHack Bald** es un roguelike de mazmorras desarrollado en **C++17**, inspirado por la tradición de **NetHack**. La interfaz, la ayuda, los mensajes y las descripciones están en **español**.

> **Alcance:** es una reinterpretación independiente y jugable, **no** una conversión completa del código de NetHack original. El NetHack histórico tiene muchas más mecánicas y contenido.

## Funcionalidades

- Generación procedural de niveles con salas, pasillos, puertas y escaleras.
- Cuatro clases: guerrero, maga, pícaro y valquiria.
- Movimiento por turnos en ocho direcciones, exploración con campo de visión y memoria de mapa.
- Monstruos, combate cuerpo a cuerpo, armas a distancia, magia, experiencia y subida de nivel.
- Inventario, equipo, comida, pociones, pergaminos, botín y oro.
- Trampas, hambre, veneno y recuperación de recursos.
- Diez profundidades y objetivo de rescatar el **Amuleto de Bald** y volver a la superficie.
- Partida guardada y recuperable en archivo local; muerte permanente dentro de la aventura.

## Compilación (cuando decidas probarlo)

Requiere CMake 3.16 o superior y compilador compatible con C++17.

```bash
cmake -S . -B build
cmake --build build --config Release
```

Linux/macOS: `./build/nethack-bald` (según generador).

Windows: `build\Release\nethack-bald.exe` con Visual Studio, o `build\nethack-bald.exe` con otros generadores.

Utiliza una terminal de al menos **80 columnas × 32 filas**, con compatibilidad ANSI y UTF-8. En Windows se recomienda Windows Terminal.

## Controles

| Tecla | Acción |
| --- | --- |
| `h j k l` | Moverse izquierda, abajo, arriba y derecha |
| `y u b n` | Moverse en diagonal |
| Flechas y teclado numérico `1-9` | Movimiento en ocho direcciones (5 = esperar) |
| `.` | Esperar |
| `,` o `g` | Recoger objeto |
| `i` | Revisar inventario |
| `e` | Comer |
| `q` | Beber una poción |
| `r` | Leer un pergamino |
| `w` | Empuñar arma |
| `W` | Ponerse armadura |
| `T` | Quitarse armadura |
| `f` | Disparar una flecha (si tienes) |
| `z` | Lanzar un hechizo |
| `d` | Soltar un objeto |
| `o` | Abrir puerta |
| `>` / `<` | Bajar / subir escaleras |
| `S` | Guardar |
| `?` | Ayuda |
| `Q` | Abandonar la partida |

Al realizar una acción direccional se solicita la dirección con las mismas teclas de movimiento.

## Objetivo

Encuentra el Amuleto de Bald en el nivel 10, vuelve por las escaleras hasta el nivel 1 y sube a la superficie para ganar.

## Estado

**Primera implementación:** fuente subida a GitHub antes de compilar o ejecutar, siguiendo la política de trabajo del proyecto. El funcionamiento no se presenta como verificado hasta que se realicen pruebas.

## Licencia

Código original de este proyecto: licencia MIT (véase `LICENSE`). No incorpora código fuente ni recursos de NetHack original.
