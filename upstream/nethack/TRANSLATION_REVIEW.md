# Revisión: Traducción NetHack 5.0 al Español

## Estado Actual

| Métrica              | Valor                                 |
| -------------------- | ------------------------------------- |
| Strings en .po       | **~6.200**                            |
| Traducciones activas | **4.451** (72%)                       |
| Fuzzy (desactivadas) | **0** ✅ (Jun 2026)                   |
| Sin traducir (vacías)| **1.742** (debug/internos)            |
| `msgfmt -c`          | ✅ 0 errores                          |
| Archivos .es         | 29                                    |
| Archivos .lua.es     | 1 (**quest.lua.es** en nhdat)         |
| Binario              | Compila sin errores                   |
| OPTIONS=language:es  | ✅ funciona sin LANG env              |

---

## Componentes Traducidos

### Código C (.po) — ~72% activo

- Pantalla de bienvenida, menús, prompts
- Combate, objetos, estado del personaje, daño elemental
- Menú de opciones (títulos, descripciones, secciones)
- Ayuda de dirección (teclas, cmdassist)
- Creación de personaje, inventario, nombres de objeto
- **Atributos** (Fuerza, Destreza, etc.) en enlightenment y mensajes
- **"the" traducible** en descripciones de personaje y títulos
- **"god"/"goddess"** traducibles en mensajes de rezo
- **s_suffix() locale-aware**: el posesivo `'s` no se añade en español
- **Verbos**: eats, drops, bites, kicks, misses, falls, floats, etc.
- **Artículos**: the→el, your→tu, it→lo
- **Comandos**: descripciones completas en español (?, c)
- **Tiendas, fuentes, trampas, hechizos, pociones, puertas**
- **Recipientes**: bottle, flagon, barrel, etc.
- **OPTIONS=language:es** en nethackrc (sin LANG env)

### Archivos de datos (.es) — 29 archivos

`help.es`, `cmdhelp.es`, `hh.es`, `history.es`, `keyhelp.es`, `opthelp.es`,
`optmenu.es`, `usagehlp.es`, `wizhelp.es`, `symbols.es`, `tribute.es`,
`data.base.es`, `data.es`, `bogusmon.txt.es`, `engrave.txt.es`,
`epitaph.txt.es`, `oracles.txt.es`, `rumors.fal.es`, `rumors.tru.es` y más.

### Archivos Lua

- **`quest.lua.es`**: ✅ traducido y empaquetado en `nhdat`
- **`dungeon.lua`**: ❌ no traducible (causa crasheo)
- **Arc-_.lua, Bar-_.lua, etc.**: ❌ ~60 quest de rol sin traducir

---

## Componentes NO Traducidos (por decisión)

1. **Nombres de mazmorra en C**: `at_dgn_entrance("The Quest")` se mantiene en
   inglés — traducirlo crashea el juego.
2. **Nombres de opciones**: `fruit`, `autodig` son identificadores de configuración.
3. **dat/tribute**: ~6.800 citas de Terry Pratchett en inglés (homenaje).
4. **Mensajes de plataformas obsoletas**: Amiga, VMS, MSDOS.

---

## Problemas Conocidos

1. **766 fuzzy**: 376 con traducciones corruptas limpiadas (vacías), ~390 con
   placeholders rotos. Todas muestran inglés en juego normal.
2. **1.570 sin traducir**: 1.182 debug/internos (baja prioridad), 388 de fuzzy
   corruptas recién limpiadas.
3. **~60 quest Lua de rol sin traducir**: diálogos específicos por clase.
4. **Layout**: el español es ~15-20% más largo. Posibles recortes.
5. **s_suffix()**: la solución es correcta pero hacklib.c necesita stubs débiles
   para que las utilidades (dlb, recover) linken.
6. **Nombres de rol sin traducir**: Footpad, Digger, Evoker no tienen entrada
   en el `.po`.

---

## Decisiones Técnicas

| Decisión                      | Motivo                                              |
| ----------------------------- | --------------------------------------------------- |
| Nombres de opciones en inglés | Son identificadores de configuración                |
| Nombres de mazmorra sin `_()` | lookup interno usa nombres canónicos en inglés      |
| `N_()` en macros de optlist.h | Para que xgettext extraiga nombres y descripciones  |
| Estrategia QWERT              | Único marcador que sobrevive a LibreTranslate       |
| `s_suffix()` locale-aware     | Solución global para ~100 usos de `'s` en el código |
| Stubs débiles en hacklib.c    | `get_lang()` y `nh_gettext()` para utilidades       |
| "the" → "de"                  | Más natural en español para descripciones y títulos |

---

## Fecha de revisión: 19 de junio de 2026

## Rama: `NetHack-5.0-es`
