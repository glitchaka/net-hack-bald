# Idiomas en NetHack-es — Guía para Añadir un Nuevo Idioma

NetHack-es soporta múltiples idiomas mediante detección automática de la
variable de entorno `LANG`. El sistema de traducción es propio de NetHack-es
(no usa gettext de glibc) y permite cargar dinámicamente:

- Traducciones de strings C (`.mo`)
- Archivos de datos localizados (`help.{lang}`, `data.{lang}`, etc.)
- Archivos Lua localizados (`quest.lua.{lang}`)

## Cómo funciona

1. `init_lang()` en `src/lang.c` lee `LANG` y extrae el código de idioma
2. `dlb_fopen()` busca `archivo.{lang}` antes de `archivo`
3. `nh_gettext()` busca en el `.mo` cargado para `LANG`
4. `s_suffix()` se adapta al idioma detectado (no-op para español)

## Idiomas actuales

| Código | Idioma  | Traducciones C (.mo)          | Datos (.{lang})      |
| ------ | ------- | ----------------------------- | -------------------- |
| `en`   | Inglés  | No necesita (nativo)          | No necesita (nativo) |
| `es`   | Español | ✅ `po/es.po` (4.117 activas) | ✅ 29 archivos `.es` |

## Cómo añadir un nuevo idioma (ej: francés)

### 1. Crear el archivo .po

```bash
cd /home/ricard/proyectos/juego/nethack-es

# Generar plantilla .pot desde el código fuente
xgettext --default-domain=nethack --directory=. \
  --keyword=_ --keyword=N_ --add-comments=TRANSLATORS: \
  --sort-by-file -o po/nethack.pot src/*.c include/optlist.h

# Crear .po para el nuevo idioma
msginit -l fr -o po/fr.po -i po/nethack.pot --no-translator

# Traducir con Poedit
poedit po/fr.po
```

> **Importante:** Preservar los placeholders `%s`, `%d`, `%c`, `%ld` en las
> traducciones. Si usas traducción automática (LibreTranslate, Google), aplica
> la **estrategia QWERT**: reemplaza `%s`→`QWERT0`, `%d`→`QWERT1` antes de
> traducir y restaura después.

### 2. Registrar el idioma en lang.c

Editar `src/lang.c` y añadir el código a la lista de idiomas válidos:

```c
if (strcmp(current_lang, "es") != 0
    && strcmp(current_lang, "en") != 0
    && strcmp(current_lang, "fr") != 0)  // ← añadir aquí
    strcpy(current_lang, "en");
```

### 3. Adaptar s_suffix() si es necesario

`src/hacklib.c` contiene `s_suffix()` que añade el posesivo `'s` inglés.
Para idiomas que no usan `'s` (como español), es no-op. Si tu idioma
tiene su propia forma de posesivo, modifica `s_suffix()` en `hacklib.c`:

```c
if (is_spanish) {
    Strcpy(buf, s);
    return buf;
}
/* Añadir aquí: if (is_french) { ... } */
```

> **Atención:** `hacklib.c` es usado por utilidades (`dlb`, `recover`) que
> no linkean todo el juego. Cualquier función nueva que llame a `get_lang()`
> o `nh_gettext()` necesita un stub débil. Ver `src/hacklib.c:345-360`.

### 4. Crear archivos de datos .{lang}

```bash
# Copiar cada archivo de datos y traducirlo
for f in help hh cmdhelp keyhelp history opthelp optmenu usagehlp wizhelp \
         data engrave epitaph oracles bogusmon rumors.tru rumors.fal \
         symbols tribute options; do
    cp dat/$f dat/$f.fr
done

cp dat/quest.lua dat/quest.lua.fr
```

Los archivos en `dat/` se empaquetan en `nhdat` con `make dlb`. Para que
los nuevos `.fr` se incluyan, hay que añadirlos al Makefile:

```makefile
DATHELP_FR = help.fr hh.fr cmdhelp.fr keyhelp.fr history.fr opthelp.fr \
             optmenu.fr usagehlp.fr wizhelp.fr

DATDLB = $(DATHELP) $(DATHELP_ES) $(DATHELP_FR) dungeon.lua tribute ...
```

> **Alternativa:** Si no se modifican los `.fr` dentro de `nhdat`, `dlb_fopen`
> también busca en el sistema de archivos local como fallback.

### 5. Compilar y probar

```bash
# Compilar el .mo
msgfmt -c po/fr.po -o locale/fr/LC_MESSAGES/nethack.mo

# Reconstruir nhdat con los nuevos archivos
make dlb
cp dat/nhdat playground/

# Probar
cd playground
LANG=fr_FR.UTF-8 ./nethack

# Ejecutar test (si existe para el idioma)
LANG=fr_FR.UTF-8 python3 /tmp/test_nethack_fr.py
```

### 6. Verificar integridad

```bash
# El .mo debe compilar sin errores
msgfmt -c po/fr.po

# Verificar estadísticas
msgfmt --statistics po/fr.po

# Revisar placeholders (todos deben coincidir entre msgid y msgstr)
grep -c '%s' po/fr.po  # deben aparecer el mismo número en msgid y msgstr
```

## Consideraciones importantes

### Placeholders (%s, %d, etc.)

**CRÍTICO:** Cada `%s`, `%d`, `%c`, `%ld` en el msgid DEBE tener su
correspondiente en el msgstr. Si faltan o sobran, `msgfmt -c` falla y la
traducción no se carga.

Usar la estrategia QWERT para traducción automática:

```python
# Antes de traducir
texto = texto.replace("%s", "QWERT0").replace("%d", "QWERT1")
# Después de traducir
texto = texto.replace("QWERT0", "%s").replace("QWERT1", "%d")
```

### s_suffix() y hacklib.c

`s_suffix()` en `src/hacklib.c` es una función de utilidad que añade el
posesivo `'s`. Por defecto asume inglés. Para otros idiomas:

- Si el idioma no usa `'s` (español, francés→"de", etc.): hacer no-op
- Si usa otro sufijo posesivo: modificar la función

**IMPORTANTE:** `hacklib.c` lo linkean utilidades (`dlb`, `recover`) que
NO disponen de `get_lang()` ni `nh_gettext()`. Si modificas `s_suffix()`
para llamar a estas funciones, DEBES añadir stubs débiles:

```c
/* Stub débil para utilidades */
const char *get_lang(void) __attribute__((weak));
const char *get_lang(void) { return "en"; }
```

### Nombres de mazmorra NO traducir

Los nombres de mazmorra en llamadas a `at_dgn_entrance()` y
`dungeon_branch()` NO deben envolverse en `_()`. El lookup interno
`dname_to_dnum()` compara contra los nombres canónicos en inglés
definidos en `dungeon.lua`. Traducirlos causa crasheo.

### Nombres de opciones NO traducir

Los nombres técnicos de opciones (`fruit`, `autodig`, `number_pad`)
son identificadores de configuración. No traducirlos. Las descripciones
y títulos de sección SÍ se traducen.

### Archivos Lua dentro de nhdat

Los archivos Lua se cargan desde el contenedor `nhdat` mediante
`dlb_fopen()`. Para que un archivo `{nombre}.lua.{lang}` sea encontrado:

1. Debe existir en `dat/` como `{nombre}.lua.{lang}`
2. Debe estar incluido en `DATDLB` en el Makefile
3. `nhdat` debe reconstruirse con `make dlb`

`dlb_fopen()` busca primero `{nombre}.lua.{lang}` y fallback a
`{nombre}.lua` si no encuentra.

### Stubs débiles en hacklib.c

Cualquier función en `hacklib.c` que llame a una función del juego
(`get_lang()`, `nh_gettext()`, etc.) necesita un stub débil porque
`hacklib.c` también se compila como parte de utilidades independientes.

Patrón recomendado:

```c
/* Stub débil — sobrescrito por el juego al linkear */
return_type mi_funcion(void) __attribute__((weak));
return_type mi_funcion(void) { return valor_por_defecto; }
```

## Estructura de archivos

```
locale/
├── es/LC_MESSAGES/nethack.mo    ← español
├── fr/LC_MESSAGES/nethack.mo    ← francés (futuro)
└── de/LC_MESSAGES/nethack.mo    ← alemán (futuro)

po/
├── es.po          ← español (actual)
├── fr.po          ← francés (futuro)
├── de.po          ← alemán (futuro)
├── nethack.pot    ← plantilla para nuevos idiomas
└── LINGUAS        ← lista de idiomas disponibles

dat/
├── help           ← inglés (original)
├── help.es        ← español
├── help.fr        ← francés (futuro)
├── quest.lua      ← inglés (original)
├── quest.lua.es   ← español
├── quest.lua.fr   ← francés (futuro)
└── ...
```

## Variables de entorno

| Variable             | Propósito                                 | Ejemplo                                |
| -------------------- | ----------------------------------------- | -------------------------------------- |
| `LANG`               | Idioma del sistema (detección automática) | `LANG=fr_FR.UTF-8`                     |
| `NETHACKDIR`         | Directorio de datos (opcional)            | `NETHACKDIR=~/.local/games/nethack-es` |
| `NETHACK_LOCALE_DIR` | Directorio de traducciones (opcional)     | (Usa `NETHACKDIR/locale` por defecto)  |

## Referencias

- `src/lang.c` — detección de idioma (`init_lang`, `get_lang`)
- `src/nh_gettext.c` — carga de `.mo` y resolución de traducciones
- `src/hacklib.c:345-360` — stubs débiles + `s_suffix()` locale-aware
- `src/role.c:2830` — "the" traducible en descripciones
- `src/botl.c:1000` — " the " traducible en títulos
- `src/attrib.c:19-21` — nombres de atributos con `N_()`
- `include/config.h:750-755` — macros `_()` y `N_()`
- `util/dlb.c` — empaquetado de archivos en `nhdat`
