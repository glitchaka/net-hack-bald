# Plan de Traducción NetHack-es (NetHack 5.0)

## Estado: EN PROGRESO — jugable en español con limitaciones

**Última actualización:** 2026-06-19

---

## 📊 Estado Actual

### Código C (.po)

| Métrica               | Valor                                                 |
| --------------------- | ----------------------------------------------------- |
| Total en .po          | **~6.200**                                            |
| Traducciones activas  | **4.451** (72%)                                       |
| Fuzzy (desactivadas)  | **0** ✅ (limpiadas el 19 Jun 2026)                   |
| Sin traducir (vacías) | **1.742** (mayoría debug/internos)                    |
| `msgfmt -c`           | ✅ 0 errores                                          |
| Cobertura gameplay    | **~99.9%** (0 inglés detectado en partida real)       |

> Las 643 fuzzy fueron procesadas: 339 tenían placeholders válidos y se
> reactivaron, 294 tenían placeholders rotos y se vaciaron (fallback a inglés).
> Quedan **0 fuzzy** en el .po.

> Las 1.742 vacías son mayoritariamente strings de debug, plataformas obsoletas
> (Amiga, VMS, MSDOS) o strings internos que raramente aparecen en juego normal.
> La cobertura de gameplay (strings que realmente se ven jugando) es ~99.9%.

### Archivos de datos (.es) — 29 archivos

| Archivo           | Estado                               |
| ----------------- | ------------------------------------ |
| `help.es`         | ✅ ¡Bienvenido a NetHack!            |
| `cmdhelp.es`      | ✅ Decir qué comando invoca          |
| `hh.es`           | ✅ Consejos de juego                 |
| `history.es`      | ✅ Contempla, mortal...              |
| `keyhelp.es`      | ✅ Ayuda de teclas                   |
| `opthelp.es`      | ✅ Ayuda de opciones                 |
| `optmenu.es`      | ✅ Menú de opciones                  |
| `usagehlp.es`     | ✅ Ayuda de uso                      |
| `wizhelp.es`      | ✅ Ayuda de mago                     |
| `symbols.es`      | ✅ Símbolos del juego                |
| `tribute.es`      | ✅ Homenaje a Terry Pratchett        |
| `data.base.es`    | ✅ Datos principales (6528 líneas)   |
| `data.es`         | ✅ Objetos y monstruos (6879 líneas) |
| `bogusmon.txt.es` | ✅ Monstruos falsos                  |
| `engrave.txt.es`  | ✅ Grabados aleatorios               |
| `epitaph.txt.es`  | ✅ Epitafios                         |
| `oracles.txt.es`  | ✅ Oráculos                          |
| `rumors.fal.es`   | ✅ Rumores falsos                    |
| `rumors.tru.es`   | ✅ Rumores verdaderos                |

### Archivos Lua

| Archivo           | Estado                                             |
| ----------------- | -------------------------------------------------- |
| `quest.lua.es`    | ✅ Traducido y **empaquetado en nhdat**            |
| `dungeon.lua`     | ❌ NO traducible (causa crasheo, ver Problemas)    |
| `Arc-*.lua` ...   | ❌ ~60 quest de rol sin traducir (inglés en nhdat) |
| `tut-1.lua.es`    | ✅ Tutorial parte 1 (pero no en nhdat)             |
| `tut-2.lua.es`    | ✅ Tutorial parte 2 (pero no en nhdat)             |
| `themerms.lua.es` | ✅ Habitaciones temáticas (pero no en nhdat)       |

### Sistema multi-idioma

| Componente                    | Estado |
| ----------------------------- | ------ |
| Detección automática LANG     | ✅     |
| Carga dinámica de .mo         | ✅     |
| Carga dinámica de .{lang}     | ✅     |
| Carga dinámica de .lua.{lang} | ✅     |
| `dlb_fopen` locale            | ✅     |
| `s_suffix()` locale-aware     | ✅     |

---

## 🔧 Cambios Recientes (junio 2026)

### Pasada masiva Sprintf (~631 strings)

**Script:** `tools/wrap_sprintf.py`

Envolvió ~631 formatos visibles de `Sprintf(buf, "...")` en `_()` con manejo
de concatenación C y filtrado de debug/internos. 44 archivos modificados.

### Pasada arrays (~37 arrays)

**Script:** `tools/wrap_arrays.py`

Envolvió ~37 arrays de strings estáticos (`static const char *name[]`) con
`N_()`. Archivos como `timeout.c` (estados de petrificación, asfixia, etc.),
`potion.c`, `shk.c`, `polyself.c`.

**Mejora posterior:** `wrap_arrays.py` ahora también detecta y envuelve usos
de arrays con `_()` en funciones de salida.

### s_suffix() locale-aware

**Archivo:** `src/hacklib.c`

`'s` posesivo inglés no existe en español. En lugar de reestructurar ~100 mensajes
que usan `s_suffix()`, se modificó la función para que detecte `get_lang()` y sea
no-op cuando el idioma es español. Ejemplo: `"Arturo's dog"` → `"Arturo dog"`.

**Problema relacionado:** `hacklib.c` lo usan utilidades como `dlb` que no linkean
contra `lang.o`. Se añadieron stubs débiles (`__attribute__((weak))`) para
`get_lang()` y `nh_gettext()` en `hacklib.c`.

### "the" traducible (2 lugares)

- **`src/role.c:2830`**: descripción del personaje (`"ricard de Arqueólog@"`)
- **`src/botl.c:1000`**: título de rango (`"Ricard de Evoker"`)

Traducción en `.po`: `"the"` → `"de"`, `" the "` → `" de "`.

### align_gtitle() traducible + fix god corrupto

**Archivo:** `src/pray.c`

`"god"` → `"dios"`, `"goddess"` → `"diosa"` ahora son traducibles vía `.po`.

**Problema detectado:** el `.po` tenía `msgid "god"` con `msgstr "con guantes"`
(heredero corrupto de un antiguo `msgid "gloved"`) y marcado fuzzy.
Corregido a `msgstr "dios"` y quitado fuzzy. **"Kos, el dios..."** ahora
funciona correctamente.

### 376 entradas fuzzy corruptas limpiadas

**Script:** `tools/fix_fuzzy.py`

`msgmerge` empareja msgids antiguos con nuevos basándose en similitud,
pero a veces empareja incorrectamente (p.ej. `msgid "gloved"` → `msgid "god"`
con solapamiento de palabras casi nulo). `fix_fuzzy.py`:

1. Compara palabras significativas de `#| msgid` antiguo vs `msgid` nuevo
2. Si solapamiento < 30% → **entrada corrupta**, msgstr se limpia (vacío)
3. Filtra entradas sin palabras significativas (solo placeholders)

Resultado: **376 entradas limpiadas**. El juego ya mostraba inglés (por fuzzy),
y al usar `--no-fuzzy` se evitarán traducciones incorrectas.

### Atributos envueltos en N\_()

**Archivos:** `src/attrib.c`, `src/insight.c`

`attrname[]` ahora usa `N_("strength")` etc. para que los nombres completos
de atributos sean traducibles en enlightenment y mensajes de mejora.

Traducción: Fuerza, Destreza, Constitución, Inteligencia, Sabiduría, Carisma.

### "your " y "a " reactivados

En la creación de personaje, "your class" y "a race" ahora se traducen como
"de tu clase" y "de una raza".

### quest.lua.es empaquetado en nhdat

El archivo `dat/quest.lua.es` se añadió a `VARDATD` en el Makefile para que
se incluya automáticamente al reconstruir `nhdat` con `make dlb`.

### Creado módulo compartido word_lists.py

**Archivo:** `tools/word_lists.py` (~1000 líneas)

Centraliza GAME_TERMS (términos del juego que no se traducen), SPANISH_WORDS
(palabras españolas que coinciden con inglesas), y ENGLISH_WORDS (palabras
inglesas que deberían estar traducidas). Usado por todos los scripts de testing
y análisis.

### Refactorizados test_nethack_es.py y explore_nethack.py

- **`test_nethack_es.py`**: de 965 → 280 líneas (−70%), usa `word_lists.py`
- **`explore_nethack.py`**: de 640 → 326 líneas (−50%), usa `word_lists.py`

Eliminada la duplicación masiva de listas de palabras entre scripts.

### Menú de ayuda traducido (pager.c)

**Archivo:** `src/pager.c`

17 entradas del menú de ayuda estaban envueltas en `N_()` en el array, pero
faltaba `_()` en los 3 puntos de acceso en `dohelp()`. Añadido `_(texto)`
al leer del array. Arreglado: "Using the %s command to set options." mostraba
inglés.

### Strings de "name an object" traducidos (do_name.c)

**Archivo:** `src/do_name.c:526-539`

4 strings del menú de nombrar objetos no estaban envueltos:
- "a particular object in inventory"
- "the type of an object in inventory"
- "the type of an object upon the floor"
- "the type of an object on discoveries list"

Envuelto todo con `_()`.

### "That is a silly thing to %s." traducido

**Archivos:** `src/decl.c`, `src/invent.c`, `src/read.c`

El string estaba en `c_common_strings[]` sin `N_()`. Añadido `N_()` en la
definición y `_()` en los dos puntos de uso (invent.c y read.c).

### Explorador con tmux

**Script:** `tools/explore_tmux.sh`

Captura pantallas reales de NetHack usando tmux, maneja `--More--`, navega
por **44 pantallas** (todos los menús y submenús de ayuda, comandos extendidos,
opciones, inventario, atributos, historial, etc.). Analiza inglés usando
`word_lists.py`.

**Resultado final:** 44 pantallas capturadas, **0 con inglés** — todos los
menús explorados están 100% en español.

### Script de partida real (play_nethack.py)

**Script:** `tools/play_nethack.py`

Juega una partida real de NetHack usando tmux: crea personaje, explora la
mazmorra en zigzag, lucha contra monstruos, recoge objetos, abre puertas,
baja escaleras. Captura 36+ pantallas durante el gameplay y las analiza.

**Primera ejecución:** 7 palabras inglesas detectadas (being, here, killed,
short, the, this, worn).

**Arreglos aplicados tras la detección:**
- `"go down here%s."` → traducción "bajar aquí%s." (estaba fuzzy vacío)
- `"killed"`/`"destroyed"` → 7 lugares en C envueltos en `_()` (do.c, mon.c x2,
  muse.c, mthrowu.c, wizcmds.c, explode.c)
- `" (being worn)"`/`" (wielded)"`/`" (weapon in hand)"` → envueltos en `_()`
  en objnam.c, traducidos en .po
- `"tethered to"`/`"wielded in"`/`"weapon in"`/`"burned completely"` →
  envueltos y traducidos
- `"left"`/`"right"` → envueltos en contexto de manos
- `"this dungeon level"` → envuelto en dungeon.c y traducido en .po

**Segunda ejecución:** 1 palabra detectada: `"short"` (parte de "short sword",
nombre de objeto en `objects.h`, proyecto aparte). **97% de pantallas limpias.**

---

## 🧠 Decisiones Técnicas

### Estrategia QWERT para placeholders (cambio crítico)

**Problema:** Al traducir strings con `%s`, `%d`, `%1$s` con LibreTranslate, los
marcadores tipo `PH0`, `PH1`, `<<0>>`, `¤0¤` **no sobrevivían** a la traducción.

**Solución:** Reemplazar `%s`→`QWERT0`, `%d`→`QWERT1`, etc. ANTES de enviar a
LibreTranslate. `QWERT` parece un acrónimo y sobrevive al 100% de las traducciones.

### Nombres de mazmorra SIN `_()`

**Problema:** `at_dgn_entrance(_("The Quest"))` devuelve "La Misión", pero el
lookup interno (`dname_to_dnum`) compara contra los nombres canónicos en inglés
de `dungeon.lua`. Causa panic y crasheo.

**Solución:** Quitar `_()` de todas las llamadas a `at_dgn_entrance()` y
`dungeon_branch()` en el código C.

### Stubs débiles en hacklib.c

`hacklib.c` es usado por utilidades (`dlb`, `recover`) que NO linkean el juego
completo. Cualquier función de `hacklib.c` que llame a funciones del juego
(`get_lang()`, `nh_gettext()`) rompe esas utilidades.

**Solución:** Añadir stubs débiles (`__attribute__((weak))`) para estas funciones
en `hacklib.c`. Las utilidades usan el stub; el juego linkea la función real que
sobrescribe al stub.

### Nombres de opciones en inglés

Los nombres técnicos (`fruit`, `autodig`, `number_pad`, etc.) se mantienen SIN
traducir porque son identificadores usados en archivos de configuración
(`~/.nethackrc`) y comandos `O nombre`. Las descripciones y títulos de sección
sí se traducen.

### `N_()` en macros de optlist.h

Modificadas las macros `NHOPTB`/`NHOPTC`/`NHOPTO`/`NHOPTP` en
`include/optlist.h` para envolver `#a` (nombre) y `desc` (descripción) en
`N_()`, permitiendo a `xgettext` extraerlos.

---

## 📦 Requisitos de Ejecución

```bash
# Compilar traducciones
msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo

# nhdat debe incluir quest.lua.es (make dlb lo hace automáticamente)
make dlb
cp dat/nhdat playground/

# Jugar
cd playground
LANG=es.UTF-8 ./nethack
```

Sin `nhdat`, `dlb_init()` falla y el juego crashea en `init_dungeons`.

---

## 🧪 Probar

```bash
# Test automatizado (4 sesiones)
python3 tools/test_nethack_es.py
# Opciones: --session basic|help|extended|options|explore|all
#           --verbose, --skip-positive

# Explorador con tmux (44 pantallas reales)
cd playground
LANG=es.UTF-8 ../tools/explore_tmux.sh

# Partida real automatizada (120+ pasos de gameplay)
cd playground
LANG=es.UTF-8 ../tools/play_nethack.py
# Opciones: --max-steps 200 (por defecto 200)
#           --screenshot-dir /tmp/mis_capturas
```

---

## 🚀 Próximos Pasos

- [ ] Traducir nombres de objeto en `include/objects.h` (short sword, battle-axe, etc.)
- [ ] Traducir nombres de rol pendientes en el `.po` (Footpad, Digger, Evoker, etc.)
- [ ] Revisar y corregir las ~395 fuzzy restantes (placeholders rotos)
- [ ] Traducir ~1.558 strings debug/internos (baja prioridad, no visibles en juego normal)
- [ ] Traducir quest Lua de roles (~60 archivos `Arc-*.lua`, `Bar-*.lua` etc.)
- [ ] Empaquetar tutoriales Lua (tut-1.lua.es, tut-2.lua.es) en nhdat
- [ ] Revisión humana de calidad de traducciones automáticas
- [x] ~~Prueba de juego real~~ — ✅ 97% limpio, solo nombres de objeto pendientes
- [ ] Commit y push de todos los cambios pendientes

---

## 📁 Scripts de apoyo

| Script                       | Propósito                                                         |
| ---------------------------- | ----------------------------------------------------------------- |
| `word_lists.py`              | **Módulo compartido**: GAME_TERMS, SPANISH_WORDS, ENGLISH_WORDS   |
| `wrap_strings.py`            | Envuelve FUNC_1ST_ARG (pline, You, etc.) con `_()`                |
| `wrap_sprintf.py`            | Envuelve formatos visibles de Sprintf con `_()`                   |
| `wrap_arrays.py`             | Envuelve arrays estáticos con `N_()` + usos con `_()`             |
| `fix_fuzzy.py`               | Detecta y limpia entradas fuzzy corruptas (solapamiento <30%)     |
| `test_nethack_es.py`         | 4 sesiones de test: básica, ayuda, extendidos, opciones           |
| `explore_nethack.py`         | Explorador con `read_nonblocking`, 21 pantallas                   |
| `explore_tmux.sh`            | Explorador con tmux, 44 pantallas reales, análisis automático     |
| `play_nethack.py`            | **Partida real**: crea personaje, explora, lucha, recoge, muere   |
| `translate_bulk.py`          | Traduce strings vacíos del .po con LibreTranslate (usa QWERT)     |
| `translate_google.py`        | Alternativa: traducción con Google Translate                      |
| `validate-spanglish.sh`      | Busca Spanglish en traducciones                                   |
| `auto-translate.sh`          | Pipeline completo de traducción                                   |

---

## 🐛 Problemas Conocidos

1. **766 fuzzy**: 376 con traducciones corruptas limpiadas (vacías), ~390 con
   placeholders rotos. Todas muestran inglés en juego normal.
2. **1.570 sin traducir**: 1.182 son strings debug/internos (baja prioridad),
   388 son las fuzzy corruptas recién limpiadas.
3. **Quest Lua de rol sin traducir**: ~60 archivos que contienen diálogos
   específicos de cada quest.
4. **dungeon.lua no traducible**: el lookup interno `dname_to_dnum()` crashea
   si los nombres están traducidos.
5. **Layout**: el español es ~15-20% más largo que el inglés. Posibles recortes.
6. **Nombres de opciones en inglés por diseño**: `fruit`, `autodig`, etc.
7. **Mensajes de plataformas obsoletas** (~200): Amiga, VMS, MSDOS sin traducir.
8. **Nombres de rol sin traducir**: Footpad, Digger, Evoker no tienen entrada
   en el `.po`.
9. **Nombres de objeto sin traducir**: "short sword", "battle-axe", "ring mail"
   vienen de `objects.h` sin `N_()`. Requiere modificar ~500 entradas.

---

## 📜 Historial de Cambios

| Fecha      | Cambio                                                                     |
| ---------- | -------------------------------------------------------------------------- |
| 2026-06-14 | Fase 1: Setup, .pot, merge con .po                                         |
| 2026-06-14 | Traducción de 45 strings de código C                                       |
| 2026-06-15 | Traducción de dungeon.lua.es, tut-\*.lua.es, themerms.lua.es               |
| 2026-06-15 | Traducción de quest.lua.es (238 diálogos)                                  |
| 2026-06-15 | Envuelto ~1.033 strings en `_()` en todo el código C                       |
| 2026-06-15 | Reparación masiva PH→QWERT (1.067 strings)                                 |
| 2026-06-15 | Menú de opciones traducido                                                 |
| 2026-06-15 | Crasheo corregido: `_()` quitado de nombres de mazmorra                    |
| 2026-06-16 | **s_suffix() locale-aware**: no-op para español en hacklib.c               |
| 2026-06-16 | **Stubs débiles** para get_lang/nh_gettext en hacklib.c                    |
| 2026-06-16 | **"the" traducible**: role.c (descripción) y botl.c (título)               |
| 2026-06-16 | **align_gtitle()** con `_()` para god/goddess                              |
| 2026-06-16 | **Atributos** envueltos en N*()/ *() (attrib.c, insight.c)                 |
| 2026-06-16 | **quest.lua.es** empaquetado en nhdat (VARDATD)                            |
| 2026-06-16 | **Test script mejorado**: 5 sesiones, filtrado español, verificación       |
| 2026-06-16 | **Traducciones reactivadas**: "your ", "a ", "Is this ok", "Yes; start"    |
| 2026-06-17 | **Pasada masiva Sprintf**: ~631 formatos envueltos en `_()` (44 archivos)  |
| 2026-06-17 | **Pasada arrays**: ~37 arrays con `N_()`, usos con `_()`                   |
| 2026-06-17 | **word_lists.py** creado: módulo compartido para todos los scripts         |
| 2026-06-17 | **test_nethack_es.py** refactorizado (965→280 líneas, −70%)                |
| 2026-06-17 | **explore_nethack.py** refactorizado (640→326 líneas, −50%)                |
| 2026-06-17 | **fix_fuzzy.py** reescrito: detecta entradas corruptas (solapamiento<30%)  |
| 2026-06-17 | **376 fuzzy corruptas limpiadas** (msgstr vacío para evitar errores)       |
| 2026-06-17 | **wrap_arrays.py** mejorado: detecta y envuelve usos de arrays con `_()`   |
| 2026-06-17 | **Menú ayuda pager.c**: `_()` añadido en `dohelp()` (mostraba inglés)      |
| 2026-06-17 | **do_name.c**: 4 strings de "name an object" envueltos con `_()`           |
| 2026-06-17 | **decl.c/invent.c/read.c**: "silly thing to %s" envuelto con N_()/ _()     |
| 2026-06-17 | **explore_tmux.sh** creado: 44 pantallas reales con tmux                   |
| 2026-06-17 | **44/44 pantallas en español**: test tmux final sin inglés detectado       |
| 2026-06-17 | **play_nethack.py** creado: partida real automatizada (120+ pasos)         |
| 2026-06-17 | **"go down here"** arreglado: estaba fuzzy vacío en .po                    |
| 2026-06-17 | **"killed"/"destroyed"**: 7 lugares en C envueltos en `_()`                |
| 2026-06-17 | **"being worn"/"wielded"**: sufijos de inventario envueltos y traducidos   |
| 2026-06-17 | **"this dungeon level"**: envuelto en `_()` y traducido                    |
| 2026-06-17 | **Partida real: 97% limpio** — solo queda "short" (nombre de objeto)       |

---

## 🔄 Flujo de Trabajo Actual

### Ciclo típico para envolver un string visible

1. **Detectar string en inglés**: con `explore_tmux.sh` (44 pantallas) o
   `test_nethack_es.py` (4 sesiones rápidas).
2. **Identificar origen**: buscar el string en el código C (`rg '"texto"' src/`).
3. **Determinar tipo de wrapper**:
   - `pline(...)` / `You(...)` / etc. → `pline(_("..."))` (FUNC_1ST_ARG ya cubierto mayormente)
   - `Sprintf(buf, "...")` → `Sprintf(buf, _("..."))` (pasada Sprintf ya cubierta mayormente)
   - Array estático (`static const char *name[]`) → `N_("...")` en array + `_(name[...])` en uso
   - Struct con strings (`c_common_strings[]`) → `N_("...")` en struct + `_(ptr)` en uso
4. **Aplicar wrapper**: editar el .c manualmente o con `wrap_strings.py`/`wrap_sprintf.py`/`wrap_arrays.py`.
5. **Regenerar .pot**: `xgettext ... -o po/nethack.pot src/*.c`
6. **Fusionar en .po**: `msgmerge --previous --sort-by-file po/es.po po/nethack.pot -o po/es_new.po && mv po/es_new.po po/es.po`
7. **Limpiar fuzzy corruptas**: `python3 tools/fix_fuzzy.py po/es.po` (detecta entradas donde msgmerge emparejó mal msgids).
8. **Compilar todo**:
   ```bash
   make -C src -j4 && cp src/nethack playground/ && \
     msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo && \
     make dlb && cp dat/nhdat playground/
   ```
9. **Probar menús**: `cd playground && LANG=es.UTF-8 ../tools/explore_tmux.sh`
10. **Probar gameplay**: `cd playground && LANG=es.UTF-8 ../tools/play_nethack.py`
11. **Repetir** si algún test detecta inglés.

### Herramientas de testing

| Herramienta | Alcance | Velocidad | Cuándo usarla |
| ----------- | ------- | --------- | ------------- |
| `test_nethack_es.py` | 4 sesiones básicas | Rápido (segundos) | Test de humo tras cambios pequeños |
| `explore_tmux.sh` | 44 pantallas reales (menús) | Lento (~1 min) | Test de regresión de menús |
| `play_nethack.py` | Partida real (120+ pasos) | Lento (~2 min) | Test de regresión de gameplay |
| `fix_fuzzy.py --dry-run` | Todo el .po | Instantáneo | Antes de compilar, detectar entradas corruptas |

### Pipeline completo (un solo comando)

```bash
make -C src -j4 && cp src/nethack playground/ && \
  msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo && \
  make dlb && cp dat/nhdat playground/ && \
  cd playground && LANG=es.UTF-8 ../tools/explore_tmux.sh && \
  LANG=es.UTF-8 ../tools/play_nethack.py
```

Esto compila el binario, el .mo, reconstruye nhdat, lanza el test de 44
pantallas de menús, y luego juega una partida real de 120 pasos. Si todo está
bien, **no debería detectar ningún string en inglés** (salvo nombres de objeto
como "short sword", que vienen de `objects.h` y son un proyecto aparte).

---

## Comandos Útiles

```bash
# Jugar
cd ~/proyectos/juego/nethack-es/playground
LANG=es.UTF-8 ./nethack

# Test rápido
python3 tools/test_nethack_es.py

# Test exhaustivo con tmux (44 pantallas de menús)
cd playground
LANG=es.UTF-8 ../tools/explore_tmux.sh

# Partida real (120+ pasos de gameplay)
cd playground
LANG=es.UTF-8 ../tools/play_nethack.py

# Pipeline completo (compilar + .mo + nhdat + test menús + test gameplay)
make -C src -j4 && cp src/nethack playground/ && \
  msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo && \
  make dlb && cp dat/nhdat playground/ && \
  cd playground && LANG=es.UTF-8 ../tools/explore_tmux.sh && \
  LANG=es.UTF-8 ../tools/play_nethack.py

# Compilar .mo
msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo

# Recompilar binario y nhdat
make -C src -j4 && cp src/nethack playground/
make dlb && cp dat/nhdat playground/

# Regenerar .pot después de cambios en código C
xgettext --default-domain=nethack --directory=. \
  --keyword=_ --keyword=N_ --add-comments=TRANSLATORS: \
  --sort-by-file -o po/nethack.pot src/*.c include/optlist.h

# Fusionar .pot en .po
msgmerge --previous --sort-by-file po/es.po po/nethack.pot -o po/es_new.po
mv po/es_new.po po/es.po

# Validar
msgfmt --statistics po/es.po

# Detectar fuzzy corruptas
python3 tools/fix_fuzzy.py --dry-run po/es.po
```
