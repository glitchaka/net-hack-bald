# NetHack-es — NetHack en Español

Traducción al español de **NetHack 5.0**.

**Estado actual:**

- Código C: **2.580 traducciones activas**, 134 fuzzy (desactivadas — muestran inglés)
- Archivos de datos: **29 archivos `.es`** (ayuda, epitafios, oráculos, etc.)
- Archivos Lua: **`quest.lua.es`** traducido y empaquetado en `nhdat`
- Script de test: **5 sesiones automáticas**, 0 falsos positivos
- `msgfmt -c`: ✅ 0 errores

Rama: `NetHack-5.0-es`

---

## ⌨️ Teclas básicas

| Tecla           | Acción                          |
| --------------- | ------------------------------- |
| `h` `j` `k` `l` | Mover (izq, abajo, arriba, der) |
| `y` `u` `b` `n` | Diagonal                        |
| `?`             | Ayuda (en español)              |
| `,`             | Recoger objetos                 |
| `d`             | Soltar objetos                  |
| `>`             | Bajar escaleras                 |
| `<`             | Subir escaleras                 |
| `i`             | Ver inventario                  |
| `q`             | Beber                           |
| `e`             | Comer                           |
| `r`             | Leer                            |
| `w`             | Equipar arma                    |
| `W`             | Ponerse armadura                |
| `S`             | Guardar partida                 |
| `Q`             | Salir                           |
| Espacio         | Continuar tras `--More--`       |

---

## ✅ Traducido al español

### Código C (~2.580 traducciones activas)

- Pantalla de bienvenida, ayuda y comandos
- Epitafios, grabados, rumores, oráculos
- Descripciones de monstruos y objetos
- Menú de opciones (nombres, descripciones, títulos de sección)
- Prompts de creación de personaje, combate, inventario
- **Atributos**: Fuerza, Destreza, Constitución, Inteligencia, Sabiduría, Carisma (en enlightenment y mensajes)
- **"the" traducible**: descripciones de personaje ("ricard **de** Arqueólog@") y títulos de rango ("Ricard **de** Evoker")
- **Posesivo `'s` desactivado** para español: `s_suffix()` es no-op con `LANG=es`
- **"god"/"goddess"** traducibles ("dios"/"diosa") en mensajes de rezo
- **"your"/"a"** en selección de personaje ("de tu"/"de un")

### Archivos de datos `.es` (29 archivos)

`help.es`, `cmdhelp.es`, `hh.es`, `history.es`, `keyhelp.es`, `opthelp.es`,
`optmenu.es`, `usagehlp.es`, `wizhelp.es`, `symbols.es`, `tribute.es`,
`data.base.es`, `data.es`, `bogusmon.txt.es`, `engrave.txt.es`,
`epitaph.txt.es`, `oracles.txt.es`, `rumors.fal.es`, `rumors.tru.es` y más.

### Archivos Lua

- **`quest.lua.es`**: texto de introducción de quest traducido y empaquetado en `nhdat`
- **`dungeon.lua`**: NO traducido (los nombres de mazmorra causan crasheo si se traducen)

---

## ⏳ Pendiente

- **134 traducciones fuzzy** en `es.po`: traducciones automáticas con placeholders rotos. Se mantienen desactivadas (fuzzy) para mostrar el inglés original. Requieren traducción manual.
- **Archivos Lua de quest por rol** (`Arc-*.lua`, `Bar-*.lua`, etc. ~60 archivos): sin traducir. Se cargan desde `nhdat` en inglés.
- **`dat/tribute`** (~6.800 citas): homenaje a Terry Pratchett, se mantienen en inglés original.
- **Mensajes de plataformas obsoletas** (~200 strings): depuración de Amiga, VMS, MSDOS, etc.

---

## 🔧 Compilar desde cero

```bash
git clone https://github.com/Ricard1974/nethack-es.git
cd nethack-es
git checkout NetHack-5.0-es
sudo apt install build-essential libncurses-dev flex bison gettext
cd sys/unix && sh setup.sh hints/linux.500 && cd ../..
make fetch-lua && make

# Compilar traducciones
msgfmt po/es.po -o playground/locale/es/LC_MESSAGES/nethack.mo

# Reconstruir nhdat con quest.lua.es incluido
make dlb
cp dat/nhdat playground/

# Jugar
cd playground
LANG=es.UTF-8 ./nethack
```

## 🧪 Probar traducciones

```bash
cd playground
LANG=es.UTF-8 python3 /tmp/test_nethack_es.py
```

El script ejecuta 5 sesiones automáticas (comandos básicos, ayuda, comandos extendidos,
opciones, exploración) y detecta strings en inglés, con verificación positiva de
traducciones esperadas.

Opciones: `--session basic|help|extended|options|explore|all`, `--verbose`, `--skip-positive`

---

## 📋 Requisitos

- Linux (probado en Ubuntu/Debian bajo WSL)
- Terminal compatible (xterm, gnome-terminal, etc.)
- `LANG=es.UTF-8` para activar las traducciones
- Python 3 + `pexpect` para el script de test (`pip install pexpect`)

---

## 📜 Licencia

NetHack-es está bajo la **NetHack General Public License (NGPL)**.
El código original de NetHack es © 1985-2026 Stichting Mathematisch Centrum y M. Stephenson.

## 🙏 Créditos

- **NetHack original**: Stichting Mathematisch Centrum y M. Stephenson
- **Traducción al español**: Ricard1974 (NetHack-es)
- **Sistema de traducción**: `nh_gettext` propio con `_()` / `N_()` / `dlb_fopen` locale

## 📁 Repositorio

`https://github.com/Ricard1974/nethack-es` — rama `NetHack-5.0-es`
