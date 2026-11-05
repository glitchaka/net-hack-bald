# Multijugador cooperativo: especificación

## Implementado

El servidor en **C++17** inicia un proceso **real del motor NetHack-es** a través de un pseudo-terminal POSIX (PTY), retransmite el estado visible a los participantes y controla cuál de ellos puede mandar teclas. **Hasta ocho clientes** ven **una única aventura con un único personaje**, comparten el inventario, el progreso y los turnos de la partida.

El primer jugador toma el control. **Ctrl+T** lo cede al siguiente. **Ctrl+G** permite escribir en un chat de la sesión; **Ctrl+]** sale del cliente. Los demás participantes observan la misma pantalla durante los turnos ajenos. No hay tecnologías web ni navegador.

## Protocolo TCP

Tramas: byte de tipo, longitud uint32 en orden de red y carga binaria hasta 8192 bytes.

| Tipo | Origen | Significado |
| --- | --- | --- |
| H | Cliente | Nombre y clave separados por salto de línea |
| D | Servidor | Salida ANSI original del juego |
| K | Cliente | Pulsación, solo válida para el controlador activo |
| P | Cliente | Ceder control |
| C | Cliente | Mensaje de chat |
| N | Servidor | Notificación |
| E | Servidor | Error |

Servidor autoritativo. Conserva 128 KiB de historial de terminal para nuevos clientes. El motor NetHack original no es reemplazado ni aproximado.

## Conexión y seguridad

Puerto por defecto **7777**, limitado a \`127.0.0.1\`. Para conexión por red local usar \`--bind=0.0.0.0 --clave=SECRETO\` y pasar esa clave a los clientes. El protocolo **no cifra** el tráfico: no abrir el puerto a Internet. Usar terminal compatible ANSI y de al menos **80 x 36**.

## Límites y pendientes

- No hay múltiples personajes separados en la misma mazmorra.
- No hay combate conjunto de personajes independientes.
- Falta implementar arquitectura multiavatar autoritativa para el motor completo de NetHack.
- No hay servidor nativo de Windows (requiere Linux/WSL).
- No se ha compilado, ejecutado ni validado el multijugador.

Para jugadores independientes habrá que ampliar los datos de criaturas, inventario, visibilidad, contexto y reglas de interacción del motor original, preservando todas las demás reglas. El código actual **no** pretende que esa extensión esté realizada.
