# Contribuir a NetHack-es

## Formas de ayudar

### 1. Traducir strings

El archivo `po/es.po` contiene ~2.714 strings. **2.580 están traducidas** y
**134 están marcadas como fuzzy** (desactivadas — muestran inglés porque la
traducción automática dañó los placeholders).

Para corregir una fuzzy:

1. Abre `po/es.po` con un editor de texto o Poedit
2. Busca `#, fuzzy` — las líneas siguientes tienen la traducción rota
3. Corrige el `msgstr` manteniendo los placeholders `%s`, `%d`, etc.
4. Elimina la línea `#, fuzzy`
5. Verifica: `msgfmt -c po/es.po`

### 2. Traducir quest Lua de rol

Los archivos `dat/???-*.lua` (~60 archivos, uno por rol y etapa del quest)
contienen diálogos específicos. Para crear la versión española:

```bash
cp dat/Arc-goal.lua dat/Arc-goal.lua.es
# Traducir el contenido (solo texto visible, no estructuras Lua)
```

Luego añadir a `VARDATD` en el Makefile y reconstruir `nhdat`.

### 3. Probar el juego

```bash
cd playground
LANG=es.UTF-8 python3 /tmp/test_nethack_es.py
```

El script ejecuta 5 sesiones automáticas. Si encuentra strings en inglés
sin traducir, los reporta con severidad.

### 4. Reportar problemas

Si encuentras texto en inglés dentro del juego:

1. Anota el mensaje exacto
2. Indica en qué contexto apareció
3. Abre un issue en GitHub o corrige directamente en `po/es.po`

## Normas de traducción

Ver `docs/GLOSARIO.md` para las convenciones terminológicas.

Reglas básicas:

- **Español de España** (no latinoamericano ni argentino)
- **Tuteo**: "tú", no "usted"
- **Género por defecto**: masculino para monstruos
- **Placeholders**: preservar `%s`, `%d`, `%c` exactamente como en el original
- **Nombres de mazmorra**: NO traducir (causa crasheo)
- **Nombres de opciones**: NO traducir (identificadores de configuración)

## Compilar y probar cambios

```bash
# 1. Compilar .mo
msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo

# 2. Recompilar binario (si hay cambios en C)
make -C src -j4 && cp src/nethack playground/

# 3. Reconstruir nhdat (si hay cambios en dat/)
make dlb && cp dat/nhdat playground/

# 4. Probar
cd playground && LANG=es.UTF-8 ./nethack

# 5. Ejecutar test automático
python3 /tmp/test_nethack_es.py
```

## Estructura del proyecto

```
po/es.po           → Traducciones del código C (strings visibles)
dat/*.es           → Archivos de datos traducidos
dat/*.lua.es       → Archivos Lua traducidos
src/hacklib.c      → s_suffix() locale-aware + stubs débiles
src/role.c         → "the" traducible en descripciones
src/botl.c         → " the " traducible en títulos
src/attrib.c       → Nombres de atributos con N_()
src/insight.c      → Atributos traducidos en enlightenment
src/pray.c         → "god"/"goddess" traducibles
docs/GLOSARIO.md   → Convenciones terminológicas
docs/IDIOMAS.md    → Guía para añadir otros idiomas
```
