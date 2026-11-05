# Problemas Encontrados en NetHack-es

Este documento recopila los problemas recurrentes encontrados durante el desarrollo de la traducción al español de NetHack 5.0.

**Última actualización:** 2026-06-19

---

## Problema 1: Nombres de mazmorra con `_()` causan crasheo

**Síntoma:** `panic("Couldn't resolve dungeon number for name ...")` en `dname_to_dnum()` durante el juego (al abrir puertas, invocar quest, etc.).

**Causa:** Envolver nombres de mazmorra en `_()` en llamadas a `at_dgn_entrance()` y `dungeon_branch()`: el lookup interno compara contra nombres canónicos en inglés de `dungeon.lua`, pero `_()` devuelve el nombre traducido.

**Ejemplo de código que CRASHEABA:**

```c
at_dgn_entrance(_("The Quest"));  // ❌ "La Misión" no existe en datos de mazmorra
```

**Solución:** NO usar `_()` en nombres de mazmorra. Pasar siempre el nombre inglés.

```c
at_dgn_entrance("The Quest");     // ✅ lookup correcto
```

**Archivos corregidos (6 referencias):**

- `src/dungeon.c:2435` — `at_dgn_entrance("The Quest")`
- `src/dungeon.c:3137` — `at_dgn_entrance("The Quest")`
- `src/do.c:1896` — `at_dgn_entrance("The Quest")`
- `src/mklev.c:2634` — `dungeon_branch("Fort Ludios")`
- `src/quest.c:191` — `dungeon_branch("The Quest")`
- `src/trap.c:4335` — `at_dgn_entrance("The Quest")`

---

## Problema 2: Placeholders no sobreviven a traducción automática

**Síntoma:** Strings con `%s`, `%d`, `%1$s` aparecen con los placeholders en posiciones incorrectas, duplicados, o convertidos a texto natural después de traducir con LibreTranslate.

**Causa:** LibreTranslate modifica o elimina placeholders. Marcadores como `PH0`, `PH1`, `<<0>>`, `¤0¤` no sobreviven porque el traductor los interpreta como texto y los "traduce".

**Solución (estrategia QWERT):**

1. Reemplazar `%s`→`QWERT0`, `%d`→`QWERT1`, etc. ANTES de enviar a traducción
2. `QWERT` sobrevive al 100% porque parece un acrónimo
3. Restaurar `QWERT0`→`%s` después de traducir

**Resultado:** 748 strings traducidas correctamente. 598 strings que ya habían perdido sus placeholders en traducciones previas fueron marcadas como sin traducir.

---

## Problema 3: El .mo no se regenera automáticamente

**Síntoma:** Las traducciones no aparecen aunque estén en el `.po`.

**Causa:** El `.mo` no se regenera solo. Hay que ejecutar manualmente:

```bash
msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo
```

---

## Problema 4: El juego necesita `nhdat` en el directorio actual

**Síntoma:** `nhl_loadlua: Error opening (nhlib.lua)` seguido de `panic: 'nhl_init' failed`.

**Causa:** `dlb_init()` abre el contenedor `nhdat` para cargar los archivos Lua. Sin él, `dlb_fopen` devuelve NULL y el juego no puede inicializar el motor Lua.

**Solución:** Copiar `dat/nhdat` al directorio de juego:

```bash
cp dat/nhdat playground/
cd playground
LANG=es.UTF-8 ./nethack
```

---

## Problema 5: Nombres de opciones en inglés (por diseño)

Los nombres técnicos de opciones (`fruit`, `autodig`, `number_pad`) se mantienen SIN traducir porque son identificadores usados en:

- Archivos de configuración (`~/.nethackrc`)
- Comandos en juego (`O nombre`)

Las descripciones y títulos de sección SÍ se traducen.

---

## Problema 6: Contenido Lua dentro de `nhdat` sin traducir

**Síntoma:** Mensajes como "Saludos ricard, welcome to NetHack!" y el libro de Lugh aparecen en inglés.

**Causa:** Los `.lua.es` existen en `dat/` pero no están empaquetados dentro del contenedor `nhdat`. El juego carga los Lua desde `nhdat`, no del filesystem.

**Solución pendiente:** Reconstruir `nhdat` incluyendo los `.lua.es`, o extraer los Lua del contenedor y ponerlos en el filesystem.

---

## Problema 7: Layout con texto en español

**Precaución:** El español es ~15-20% más largo que el inglés. Puede haber recortes en menús, cuadros de diálogo, o nombres de objetos que excedan los buffers reservados.

**Verificación:**

- Nombres de mazmorra: buffer `dname[24]` en `include/dungeon.h` — máximo 24 caracteres
- Nombres de opciones: `OPTION_LEN` en `include/optlist.h`
- Mensajes de `pline()`: buffer `BUFSZ` (generalmente 256)

---

## Problema 8: Variables de entorno para locale

**Síntoma:** El juego no carga las traducciones (todo en inglés).

**Causa:** `LANG=es.UTF-8` debe estar definida. Adicionalmente, `NETHACK_LOCALE_DIR` y `NETHACKDIR` pueden configurarse para rutas personalizadas.

**Solución:**

```bash
export LANG=es.UTF-8
export NETHACKDIR="$HOME/.local/games/nethack-es"
export NETHACK_LOCALE_DIR="$HOME/.local/games/nethack-es/locale"
cd "$NETHACKDIR"
./nethack
```

---

## Problema 9: s_suffix() rompe utilidades (dlb, recover)

**Síntoma:** `undefined reference to 'get_lang'` al compilar `dlb` o `recover`.

**Causa:** `hacklib.c` (usado por utilidades) ahora llama a `get_lang()` y
`nh_gettext()`, pero las utilidades no linkean `lang.o` ni `nh_gettext.o`.

**Solución:** Stubs débiles en `hacklib.c`:

```c
const char *get_lang(void) __attribute__((weak));
const char *get_lang(void) { return "en"; }

const char *nh_gettext(const char *msgid) __attribute__((weak));
const char *nh_gettext(const char *msgid) { return msgid; }
```

Las utilidades usan el stub. El juego linkea la función real que sobrescribe
al stub. Ver `src/hacklib.c:345-360`.

**Archivos afectados:**

- `src/hacklib.c` — stubs débiles añadidos + `s_suffix()` locale-aware

---

## Problema 10: "the" hardcodeado en descripciones y títulos

**Síntoma:** El test de traducción detecta "the" en inglés en la descripción
del personaje ("ricard the Archeologist") y en el título ("Ricard the Stripling").

**Causa:** `" the "` hardcodeado en `src/botl.c:1000` y `"the"` hardcodeado en
`src/role.c:2830` sin `_()`.

**Solución:** Envolver en `_()`:

```c
/* role.c */
Sprintf(qbuf, "%.20s %s %.20s %.20s %.20s %.20s",
        svp.plname, _("the"), ...);

/* botl.c */
Strcpy(nb = eos(nb), _(" the "));
```

Traducción al español: `"the"` → `"de"`, `" the "` → `" de "`.

**Archivos corregidos:**

- `src/role.c:2830` — descripción de personaje
- `src/botl.c:1000` — título de rango

---

## Problema 11: quest.lua.es no se incluía en nhdat

**Síntoma:** El texto del quest aparecía en inglés aunque `quest.lua.es`
existiera en `dat/`.

**Causa:** Makefile no incluía `quest.lua.es` en `VARDATD`, por lo que `make dlb`
no lo empaquetaba en `nhdat`.

**Solución:** Añadir `quest.lua.es` a `VARDATD` en el Makefile:

```makefile
VARDATD = bogusmon data engrave epitaph oracles options quest.lua quest.lua.es rumors
```

**Archivos corregidos:**

- `Makefile:2227` — añadido quest.lua.es a VARDATD

---

## Problema 12: Nombres de atributos sin traducir

**Síntoma:** "Strength", "Dexterity" aparecen en inglés en mensajes de
mejora de atributos y pantalla de enlightenment.

**Causa:** `attrname[]` en `src/attrib.c` no estaba envuelto en `N_()`.

**Solución:** Envolver con `N_()` y usar `_()` en los usos:

```c
/* attrib.c */
const char *const attrname[] = {
    N_("strength"), N_("intelligence"), N_("wisdom"),
    N_("dexterity"), N_("constitution"), N_("charisma")
};

/* insight.c */
Sprintf(subjbuf, _("Your %s "), _(attrname[attrindx]));
```

**Archivos corregidos:**

- `src/attrib.c:19-21` — `N_()` en definición
- `src/attrib.c:182` — `_()` en uso de mensaje
- `src/insight.c:897` — `_()` en enlightenment

---

## Problema 13: "killed" y "destroyed" sin `_()` en ternarias de combate

**Síntoma:** Los mensajes de muerte de monstruos muestran "killed" o "destroyed"
en inglés aunque el formato `"%s is %s!"` está traducido.

**Causa:** En 7 lugares del código C se usa el patrón ternario:
```c
nonliving(mtmp->data) ? "destroyed" : "killed"
```
sin envolver los strings literales en `_()`.

**Solución:** Envolver cada string en `_()`:
```c
nonliving(mtmp->data) ? _("destroyed") : _("killed")
```

**Archivos corregidos (7 ocurrencias):**
- `src/do.c:209-211` — boulder aplasta monstruo
- `src/mon.c:3056` — log de muertes
- `src/mon.c:3386` — mensaje de muerte por ataque
- `src/muse.c:3190-3191` — muerte por fuego
- `src/mthrowu.c:451-452` — objeto arrojado mata
- `src/wizcmds.c:323` — #wizkill
- `src/explode.c:572-574` — explosión mata (incluye "burned completely")

---

## Problema 14: Sufijos de inventario sin `_()` en objnam.c

**Síntoma:** En el inventario, sufijos como "(being worn)", "(wielded)",
"(weapon in hand)" aparecen en inglés.

**Causa:** `doname()` en `src/objnam.c` concatena estos sufijos sin `_()`:
- `"(being worn)"` (3 veces: amulet, armor, tool)
- `"(embedded in your skin)"`, `"(being doffed)"`, `"(being donned)"`
- `"(wielded)"`
- `"(weapon in hand)"`, `"(wielded in)"`, `"(tethered to)"`
- `"(alternate weapon%s; not wielded)"`
- `"(wielded in %s %s)"`

**Solución:** Envolver cada string literal en `_()`.

**Archivo corregido:**
- `src/objnam.c` — 9 strings envueltos

---

## Problema 15: "this dungeon level" sin `_()` en dungeon.c

**Síntoma:** El prompt para nombrar un nivel muestra "¿Cómo quieres llamar a
this dungeon level?" (mixto español/inglés).

**Causa:** En `src/dungeon.c:2538`:
```c
Strcpy(lbuf, "this dungeon level");  // ❌ sin _()
```
El formato `_("What do you want to call %s?")` ya está traducido, pero el
`%s` se reemplaza con "this dungeon level" sin traducir.

**Solución:** Envolver con `_()`:
```c
Strcpy(lbuf, _("this dungeon level"));  // ✅
```

**Archivo corregido:**
- `src/dungeon.c:2538`

---

## Problema 16: Entradas fuzzy corruptas por msgmerge

**Síntoma:** Traducciones incorrectas que aparecen al usar `--no-fuzzy` (p.ej.
"god" traducido como "con guantes" porque el msgid antiguo era "gloved").

**Causa:** `msgmerge --previous` empareja msgids antiguos con nuevos basándose
en similitud de cadenas. Cuando un msgid cambia drásticamente (p.ej. refactor
de "gloved" a "god"), msgmerge a veces los empareja incorrectamente si hay
pocos candidatos mejores. El `#| msgid` antiguo queda como pista, pero el msgstr
hereda una traducción que no corresponde al msgid nuevo.

**Ejemplo real:**
```
#, fuzzy
#| msgid "gloved"
msgid "god"
msgstr "con guantes"
```

**Solución:** Script `tools/fix_fuzzy.py` que:

1. Extrae el `#| msgid` antiguo y el `msgid` nuevo de cada entrada fuzzy
2. Filtra solo palabras significativas (excluye placeholders, artículos, etc.)
3. Calcula solapamiento (intersección / media de tamaños)
4. Si solapamiento < 30% → **entrada corrupta**, limpia el msgstr

```bash
# Detectar corruptas (dry-run)
python3 tools/fix_fuzzy.py --dry-run po/es.po

# Aplicar limpieza
python3 tools/fix_fuzzy.py po/es.po
```

**Resultado:** 376 entradas corruptas detectadas y limpiadas (msgstr vacío).
Al usar `--no-fuzzy` aparecerán en inglés en lugar de con texto incorrecto.

**Archivo:** `tools/fix_fuzzy.py`

---

## Problema 17: Menú de ayuda con `N_()` pero sin `_()` en acceso

**Síntoma:** Las entradas del menú de ayuda ("Introduction", "Basic commands",
etc.) aparecen en inglés aunque el array está envuelto en `N_()`.

**Causa:** En `src/pager.c`, el array `static const char *help_menu_entries[]`
está definido con `N_()`:
```c
static const char *help_menu_entries[] = {
    N_("Introduction"),
    N_("Basic commands"),
    ...
};
```
pero los 3 puntos de acceso en `dohelp()` usaban el array directamente:
```c
any.a_void = help_menu_entries[selected];   // ❌ sin _()
```
`N_()` solo marca para extracción por xgettext; no traduce en runtime.
Para traducir en runtime hace falta `_()`.

**Solución:** Añadir `_()` en los 3 puntos de acceso en `dohelp()`:
```c
any.a_void = _(help_menu_entries[selected]);  // ✅
```

**Archivos corregidos:**
- `src/pager.c:2873-2877` — 3 usos de `_(help_menu_entries[...])`

---

## Problema 18: Strings de "name an object" sin `_()`

**Síntoma:** 4 strings del menú de nombrar objetos aparecen en inglés:
- "a particular object in inventory"
- "the type of an object in inventory"
- "the type of an object upon the floor"
- "the type of an object on discoveries list"

**Causa:** En `src/do_name.c:526-539`, estos strings se usan directamente
en `Sprintf()` sin `_()`:
```c
Sprintf(buf, "a particular object in inventory");  // ❌
```

**Solución:** Envolver con `_()`:
```c
Sprintf(buf, _("a particular object in inventory"));  // ✅
```

**Archivos corregidos:**
- `src/do_name.c:526-539` — 4 strings envueltos con `_()`

---

## Problema 19: "That is a silly thing to %s." sin `N_()` / `_()`

**Síntoma:** El mensaje aparece en inglés al intentar poner/quitar objetos
en situación incorrecta.

**Causa:** El string está en `c_common_strings[]` en `src/decl.c` sin `N_()`,
y los puntos de uso en `src/invent.c` y `src/read.c` no llaman `_()`.

**Solución:**
1. Envolver con `N_()` en la definición del array en `decl.c`
2. Añadir `_()` en los puntos de uso en `invent.c` y `read.c`

```c
/* decl.c */
N_("That is a silly thing to %s.")  // ✅ N_()

/* invent.c / read.c */
_(silly_thing_to)  // ✅ _()
```

**Archivos corregidos:**
- `src/decl.c:43` — añadido `N_()`
- `src/invent.c:2126` — añadido `_()`
- `src/read.c:546` — añadido `_()`

---

## Checklist de Verificación

Después de cualquier cambio:

- [ ] `.po` válido: `msgfmt -c po/es.po`
- [ ] `.mo` compilado: `msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo`
- [ ] Binario compila: `make -C src`
- [ ] `nhdat` presente: `cp dat/nhdat playground/`
- [ ] `LANG=es.UTF-8` al ejecutar
- [ ] Nombres de mazmorra sin `_()` en C (grep `at_dgn_entrance\(_\|dungeon_branch\(_`)
- [ ] Sin fuzzy corruptas: `python3 tools/fix_fuzzy.py --dry-run po/es.po`
- [ ] Test tmux: `cd playground && LANG=es.UTF-8 ../tools/explore_tmux.sh`

---

## Comandos Rápidos

```bash
# Compilar .mo y copiar
msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo

# Recompilar binario
make -C src -j4 && cp src/nethack playground/

# Poner nhdat y jugar
cp dat/nhdat playground/
cd playground && LANG=es.UTF-8 ./nethack

# Pipeline completo (todo + test tmux)
make -C src -j4 && cp src/nethack playground/ && \
  msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo && \
  make dlb && cp dat/nhdat playground/ && \
  cd playground && LANG=es.UTF-8 ../tools/explore_tmux.sh

# Detectar fuzzy corruptas
python3 tools/fix_fuzzy.py --dry-run po/es.po
```

---

## Problema 16: Verbos hardcodeados en `otense()` y `getobj()`

**Síntoma:** Mensajes como "¿Qué quieres drop?" en español con el verbo en inglés.

**Causa:** Las funciones `otense(obj, "verb")` y `getobj("verb", ...)` reciben verbs ingleses hardcodeados. El formato `_("¿Qué quieres %s?")` está traducido, pero el `%s` (verb) no.

**Solución:** Envolver los 24 verbs de `getobj()` con `_()` en 13 archivos fuente.

## Problema 17: Strings con comillas escapadas no se envuelven bien

**Síntoma:** Error de compilación al usar `_()"texto\"mas\""`

**Causa:** La macro `_()` interpreta las comillas escapadas `\"` como final de string.

**Solución:** Revisar manualmente estos casos y escribir la macro alrededor de todo el string, no parcial.

## Problema 18: 643 entradas fuzzy corrompidas por msgmerge

**Síntoma:** ~15% de las traducciones no se aplicaban aunque tuvieran msgstr.

**Causa:** `msgmerge` marca como `#, fuzzy` cualquier entrada cuyo msgid original haya cambiado, aunque la traducción sea válida.

**Solución:** Script automatizado que verifica placeholders, quita fuzzy si coinciden, o vacía el msgstr si no.

**Resultado:** 643→0 fuzzy (339 recuperadas, 294 vaciadas por placeholders rotos).

## Problema 19: Captura de pantalla tmux corrupta

**Síntoma:** El minimapa del bot muestra múltiples caracteres `@` en lugar de uno solo.

**Causa:** El buffer de tmux mezcla frames de capturas anteriores. No afecta a la detección de texto inglés.

**Solución:** Usar `capture-pane -S` con límite adecuado y limpiar el buffer antes de cada captura. No crítico para la funcionalidad del bot.
```
