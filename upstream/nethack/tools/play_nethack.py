#!/usr/bin/env python3
"""
Partida automática de NetHack-es para verificar traducciones durante gameplay real.

TRES MODOS:
  --mode wizard (por defecto): personaje invencible, explora mazmorra completa,
         baja niveles, usa todos los comandos. Para verificación exhaustiva.
  --mode normal: Valkyrie real con lógica de supervivencia (huir si HP bajo,
         curarse, etc.). Para probar combate y situaciones reales.
  --watch: MODO ESPECTADOR. Ralentiza el juego y muestra instrucciones para
         conectarte con tmux y ver la partida en tiempo real.

Uso:
    cd ~/proyectos/juego/nethack-es/playground
    LANG=es.UTF-8 ../tools/play_nethack.py                # modo wizard
    LANG=es.UTF-8 ../tools/play_nethack.py --mode normal  # modo real
    LANG=es.UTF-8 ../tools/play_nethack.py --watch        # Ver cómo juega
    LANG=es.UTF-8 ../tools/play_nethack.py --max-steps 1000
    LANG=es.UTF-8 ../tools/play_nethack.py --screenshot-dir /tmp/mi_test
"""

import subprocess, time, re, sys, os, signal, atexit, argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from word_lists import GAME_TERMS, SPANISH_WORDS, ENGLISH_WORDS

SESSION = f"nethack_play_{os.getpid()}"
PLAYGROUND = os.path.expanduser("~/proyectos/juego/nethack-es/playground")
LANG_VAR = "es.UTF-8"
os.environ["LANG"] = LANG_VAR

ALLOWED_ENGLISH = {
    "fruit",
    "autodig",
    "pickup",
    "autopickup",
    "number_pad",
    "rest_on_space",
    "safe_dog",
    "safe_pet",
    "pettype",
    "runmode",
    "travelmode",
    "menustyle",
    "menucolors",
    "menucolor",
    "align",
    "statuslines",
    "statushilites",
    "extended",
    "commands",
    "quest",
    "ludios",
    "fort",
    "gehennom",
    "oracle",
    "mines",
    "mine",
    "town",
    "sokoban",
    "endgame",
    "elemental",
    "planes",
    "astral",
    "hell",
    "vla",
    "sanctum",
    "valley",
    "adjust",
    "annotate",
    "apply",
    "chat",
    "close",
    "dip",
    "down",
    "drink",
    "drop",
    "eat",
    "engrave",
    "enhance",
    "fire",
    "force",
    "glory",
    "hide",
    "hold",
    "invoke",
    "jump",
    "kick",
    "loot",
    "monster",
    "offer",
    "pray",
    "quit",
    "read",
    "redraw",
    "ride",
    "rub",
    "search",
    "sit",
    "swap",
    "takeoff",
    "tip",
    "turn",
    "twoweapon",
    "up",
    "untrap",
    "versus",
    "wear",
    "wield",
    "wipe",
    "zap",
    "archeologist",
    "barbarian",
    "caveman",
    "healer",
    "knight",
    "monk",
    "priest",
    "ranger",
    "rogue",
    "samurai",
    "tourist",
    "valkyrie",
    "wizard",
    "arc",
    "bar",
    "cav",
    "hea",
    "kni",
    "mon",
    "pri",
    "ran",
    "rog",
    "sam",
    "tou",
    "val",
    "wiz",
    "dwarf",
    "elf",
    "gnome",
    "human",
    "orc",
    "male",
    "female",
    "dwar",
    "gnom",
    "hum",
    "incron",
    "defender",
    "minions",
}

DEATH_PATTERNS = [
    "you die",
    "you are dead",
    "killed",
    "muerto",
    "has muerto",
    "you were",
    "do you want your possessions identified",
    "do you want to see your killer?",
    "your quest is over",
]


# ─── Patrón de movimiento ──────────────────────────────────────────────
# Zigzag por el mapa: 40 filas de 14 pasos horiz + 1 abajo
MOVE_PATTERN = sum(
    [["l"] * 14 + ["j"] if i % 2 == 0 else ["h"] * 14 + ["j"] for i in range(80)], []
)

# ─── Funciones tmux ────────────────────────────────────────────────────


def send_key(key):
    special = {"Enter", "Space", "Escape", "Tab", "Backspace"}
    if key in special:
        subprocess.run(
            ["tmux", "send-keys", "-t", SESSION, key], capture_output=True, timeout=5
        )
    else:
        subprocess.run(
            ["tmux", "send-keys", "-t", SESSION, key], capture_output=True, timeout=5
        )


def capture_pane():
    r = subprocess.run(
        ["tmux", "capture-pane", "-t", SESSION, "-p", "-S", "-500"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return r.stdout


def clear_more(max_iter=25):
    for _ in range(max_iter):
        txt = capture_pane()
        if "--More--" in txt or "Más--" in txt:
            send_key("Space")
            time.sleep(0.3)
        else:
            break


def wait_stable(timeout=8):
    last = ""
    for _ in range(int(timeout / 0.3)):
        time.sleep(0.3)
        txt = capture_pane()
        if txt == last:
            return txt
        last = txt
    return last


# ─── Prompt detection ─────────────────────────────────────────────────


def answer_prompts(skip_capture=False):
    """Detecta y responde prompts del juego (y/n, [yn], etc.)"""
    screen = capture_pane()
    last_lines = screen.strip().split("\n")[-3:]
    for line in last_lines:
        lower = line.lower()
        # "Die? [yn]" - answer 'n' (don't die!)
        if "die?" in lower and "[yn]" in line:
            send_key("n")
            time.sleep(0.3)
            return True
        # "[yn]" prompts (traps, etc.) - answer 'n' (no)
        if "[yn]" in line or "[ynq]" in line:
            send_key("n")
            time.sleep(0.3)
            return True
        # Direction prompts "In what direction?" - cancel with Escape
        if "direction" in lower or "dirección" in lower:
            send_key("Escape")
            time.sleep(0.3)
            return True
        # Level teleport or other getlin prompts - cancel with Escape
        if "level" in lower and "teleport" in lower:
            send_key("Escape")
            time.sleep(0.3)
            return True
        # "Pick up what?" prompt - cancel with Escape
        if "pick up" in lower:
            send_key("Escape")
            time.sleep(0.3)
            return True
    return False


# ─── Watch mode ────────────────────────────────────────────────────────


def watch_delay(seconds, action_desc="", watch=False):
    """Si watch=True, imprime la acción y espera más tiempo."""
    if watch and action_desc:
        log(f"  ⏳ {action_desc}")
    if watch:
        time.sleep(seconds * 2.5)  # mucho más lento
    else:
        time.sleep(seconds)


# ─── Análisis ──────────────────────────────────────────────────────────


def detect_english(text):
    words = set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))
    gt = {t.lower() for t in GAME_TERMS}
    eng = []
    for w in sorted(words):
        if (
            w in ENGLISH_WORDS
            and w not in SPANISH_WORDS
            and w not in gt
            and w not in ALLOWED_ENGLISH
        ):
            eng.append(w)
    return eng


def is_dead(text):
    for p in DEATH_PATTERNS:
        if p in text.lower():
            return True
    lines = text.strip().split("\n")
    non_empty = [l for l in lines if l.strip()]
    if len(non_empty) <= 2 and non_empty and non_empty[-1].startswith("  "):
        return True
    return False


def is_playing(text):
    lines = text.split("\n")
    for line in lines[-5:]:
        if re.search(r"HP:\d+", line, re.IGNORECASE):
            return True
        if re.search(r"Pw:\d+", line, re.IGNORECASE):
            return True
    return False


# ─── Creación de personaje ─────────────────────────────────────────────


def create_character(wizard_mode=False, watch=False):
    log("  [1/5] Iniciando sesión tmux...")

    cmd = f"LANG={LANG_VAR} ./nethack"
    if wizard_mode:
        cmd += " -D"

    subprocess.run(
        ["tmux", "new-session", "-d", "-s", SESSION, "-x", "132", "-y", "50", cmd],
        capture_output=True,
        timeout=5,
    )
    watch_delay(3, "Lanzando NetHack...", watch)

    log("  [2/5] Pasando pantallas de introducción...")
    clear_more()
    watch_delay(1, "", watch)

    if wizard_mode:
        # En modo wizard, puede pedir confirmación o mostrar avisos
        screen = capture_pane()
        if "wizard" in screen.lower() or "Wizard" in screen:
            watch_delay(0.3, "Confirmando modo wizard...", watch)
            send_key("Enter")
            watch_delay(1, "", watch)
            clear_more()

    watch_delay(0.3, "Who are you? → Enter", watch)
    send_key("Enter")
    watch_delay(1.5, "", watch)
    clear_more()

    watch_delay(0.3, "Eligiendo personaje aleatorio...", watch)
    send_key("y")
    watch_delay(2, "", watch)

    # Pasar descripción del personaje
    clear_more()
    watch_delay(1, "", watch)

    # Tutorial?
    screen = capture_pane()
    if "tutorial" in screen.lower():
        send_key("n")
        watch_delay(1, "", watch)

    # Mensajes iniciales
    log("  [3/5] Pasando mensajes iniciales...")
    for _ in range(30):
        screen = capture_pane()
        if is_playing(screen):
            break
        send_key("Space")
        watch_delay(0.3, "", watch)

    wait_stable(4)
    screen = capture_pane()

    if is_playing(screen):
        log("  [4/5] Personaje creado, empezando partida.")
    else:
        log("  [4/5] ⚠️  No se detecta mapa, intentando continuar...")
        for _ in range(20):
            send_key("Space")
            watch_delay(0.3, "", watch)
        watch_delay(2, "", watch)
        screen = capture_pane()
        if not is_playing(screen):
            log("  ⚠️  No se pudo iniciar la partida. Captura de diagnóstico:")
            log(f"  ---{screen[:500]}---")

    return screen


# ─── Comandos wizard ───────────────────────────────────────────────────


def wizard_commands(step, screenshot_dir, save_screenshot_func, watch=False):
    """En modo wizard, ejecuta comandos adicionales para explorar más.

    Ahora con tour completo de la mazmorra: baja de nivel en nivel,
    genera monstruos, desea objetos, etc.
    """
    cmds = []

    # ─── Comandos periódicos ──────────────────────────────────────────
    # IMPORTANTE: usar teclas directas en lugar de formato #nombre
    # para evitar que el prompt de comandos extendidos se quede abierto.
    # Teclas: \177=DEL(terrain), Escape+m=monster, Escape+s=sit,
    #         Escape+p=pray, Ctrl+i=wizidentify, Ctrl+v=wizlevelport

    # Cada 15 pasos: mirar alrededor (usamos ';' que mira el suelo sin prompt)
    if step % 15 == 0:
        cmds.append((";", "look", "Mirando alrededores"))

    # Cada 30 pasos: mapa completo (DEL = \177)
    if step % 30 == 0:
        cmds.append(("\177", "terrain", "Mapa del nivel"))

    # Cada 45 pasos: N/A (dungeon no tiene tecla directa, lo saltamos)

    # Cada 60 pasos: monsters (Escape + m)
    if step % 60 == 0:
        cmds.append(("\033m", "monsters", "Monstruos presentes"))

    # Cada 80 pasos: sentarse (Escape + s)
    if step % 80 == 0:
        cmds.append(("\033s", "sit", "Sentándose"))

    # Cada 120 pasos: rezar (Escape + p)
    if step % 120 == 0:
        cmds.append(("\033p", "pray", "Rezando"))

    # Cada 90 pasos: identificar inventario (Ctrl+i)
    if step % 90 == 0:
        cmds.append(("\011", "wizident", "🔍 Identificando inventario"))

    # Cada 150 pasos: N/A (stats no tiene tecla directa, lo saltamos)

    # ─── Tour de la mazmorra ─────────────────────────────────────────
    # En wizard mode, baja de nivel progresivamente
    # Cada comando multi-paso (wishing, genesis) se ejecuta COMPLETO en un
    # solo step, con delays intermedios, para evitar que el movimiento
    # del siguiente paso interfiera con el prompt abierto.
    if step == 82:
        cmds.append(
            (
                "__multi__|#levelchange|0.3|2|0.3|Enter|0.5",
                "lvl2",
                "📈 Subiendo a nivel de experiencia 2",
            )
        )
    elif step == 142:
        cmds.append(
            (
                "__multi__|#levelchange|0.3|4|0.3|Enter|0.5",
                "lvl4",
                "📈 Subiendo a nivel de experiencia 4",
            )
        )
    elif step == 202:
        cmds.append(
            (
                "__multi__|#levelchange|0.3|6|0.3|Enter|0.5",
                "lvl6",
                "📈 Subiendo a nivel de experiencia 6",
            )
        )
    elif step == 262:
        cmds.append(
            (
                "__multi__|\026|0.5|mines|0.3|Enter|0.5",
                "mines",
                "⛏️ Teletransporte a las Minas",
            )
        )
    elif step == 322:
        cmds.append(
            (
                "__multi__|\026|0.5|sokoban|0.3|Enter|0.5",
                "sokoban",
                "📦 Teletransporte a Sokoban",
            )
        )
    elif step == 382:
        cmds.append(
            (
                "__multi__|\026|0.5|oracle|0.3|Enter|0.5",
                "oracle",
                "🔮 Teletransporte al Oráculo",
            )
        )
    elif step == 442:
        cmds.append(
            (
                "__multi__|#levelchange|0.3|14|0.3|Enter|0.5",
                "lvl14",
                "📈 Subiendo a nivel de experiencia 14",
            )
        )
    elif step == 502:
        cmds.append(
            (
                "__multi__|\026|0.5|quest|0.3|Enter|0.5",
                "quest",
                "⚔️ Teletransporte a la Quest",
            )
        )
    elif step == 562:
        cmds.append(
            (
                "__multi__|\026|0.5|gehennom|0.3|Enter|0.5",
                "gehennom",
                "🔥 Teletransporte a Gehennom",
            )
        )
    elif step == 622:
        cmds.append(
            (
                "__multi__|\026|0.5|valley|0.3|Enter|0.5",
                "valley",
                "🏜️ Teletransporte al Valle de la Muerte",
            )
        )
    elif step == 682:
        cmds.append(
            (
                "__multi__|\026|0.5|castle|0.3|Enter|0.5",
                "castle",
                "🏰 Teletransporte al Castillo",
            )
        )
    elif step == 742:
        cmds.append(
            (
                "__multi__|\026|0.5|sanctum|0.3|Enter|0.5",
                "sanctum",
                "💀 Teletransporte al Sanctum",
            )
        )
    elif step == 802:
        cmds.append(
            (
                "__multi__|#levelchange|0.3|20|0.3|Enter|0.5",
                "lvl20",
                "📈 Subiendo a nivel de experiencia 20",
            )
        )
    elif step == 862:
        cmds.append(
            (
                "__multi__|\026|0.5|astral|0.3|Enter|0.5",
                "astral",
                "✨ Teletransporte a los Planos Astrales",
            )
        )
    elif step == 902:
        cmds.append(
            (
                "__multi__|#levelchange|0.3|30|0.3|Enter|0.5",
                "lvl30",
                "📈 Subiendo a nivel de experiencia 30",
            )
        )

    # ─── Ejecutar ─────────────────────────────────────────────────────
    for cmd, label, desc in cmds:
        if watch and desc:
            log(f"  ⏳ {desc}")

        if cmd.startswith("__multi__"):
            # Formato: __multi__|<cmd1>|<delay1>|<cmd2>|<delay2>|...
            # Ejemplo: __multi__|#wishing|0.5|blessed scroll of teleport|0.3|Enter|0.3
            parts = cmd.split("|")
            i = 1  # skip "__multi__"
            while i < len(parts) - 1:
                sub_cmd = parts[i]
                sub_delay = float(parts[i + 1]) if i + 1 < len(parts) else 0.3
                send_key(sub_cmd)
                watch_delay(sub_delay, "", watch)
                i += 2
            screen = capture_pane()
            save_screenshot_func(f"wizard_{label}_{step:04d}", screen)
            clear_more()
            send_key("Escape")
            watch_delay(0.3, "", watch)
            clear_more()
        else:
            send_key(cmd)
            watch_delay(0.5, "", watch)
            screen = capture_pane()
            save_screenshot_func(f"wizard_{label}_{step:04d}", screen)
            clear_more()
            # Cancelar si el comando abre un prompt
            send_key("Escape")
            watch_delay(0.3, "", watch)
            clear_more()


# ─── Bucle de juego ────────────────────────────────────────────────────


def play_game(
    max_steps=200,
    screenshot_dir="/tmp/nethack_play_screens",
    wizard_mode=False,
    watch=False,
):
    os.makedirs(screenshot_dir, exist_ok=True)

    screen = create_character(wizard_mode, watch)
    step = 0
    all_english = set()
    bad_screens = 0
    total_screens = 0

    def save_screenshot(name, text):
        nonlocal total_screens, bad_screens
        with open(f"{screenshot_dir}/{name}.txt", "w", encoding="utf-8") as f:
            f.write(text)
        total_screens += 1
        eng = detect_english(text)
        if eng:
            bad_screens += 1
            all_english.update(eng)
            log(f"  ⚠️  INGLÉS [{name}]: {eng}")
        return eng

    save_screenshot("00_inicio", screen)

    if not wizard_mode and is_dead(screen):
        log("  ⚰️  Personaje muerto al inicio!")
        save_screenshot("00_muerte_inicio", screen)
        return all_english, bad_screens, total_screens

    log("  [5/5] Jugando...")

    move_name = {
        "h": "← oeste",
        "j": "↓ sur",
        "k": "↑ norte",
        "l": "→ este",
        "u": "↗ noreste",
        "n": "↘ sureste",
        "b": "↙ suroeste",
        "y": "↖ noroeste",
        ".": "esperar",
        ",": "recoger",
        ">": "bajar",
        "<": "subir",
    }

    for i, move in enumerate(MOVE_PATTERN[:max_steps]):
        step = i + 1

        # --- Responder prompts pendientes (trampas, direcciones) ---
        answer_prompts()

        # Progreso cada 50 pasos
        if step % 50 == 0:
            log(f"  📊 Progreso: paso {step}/{max_steps}")

        # --- MOVIMIENTO ---
        mname = move_name.get(move, move)
        watch_delay(0.15, f"Paso {step}: mover {mname}", watch)
        send_key(move)
        watch_delay(0.15, "", watch and step % 2 == 0)

        # Capturar cada 3 movimientos
        if step % 3 == 0:
            screen = capture_pane()
            if "--More--" in screen or "Más--" in screen:
                clear_more()
                screen = capture_pane()
            if step % 6 == 0:
                save_screenshot(f"move_{step:04d}", screen)

        # --- ACCIONES PERIÓDICAS ---

        if step % 8 == 0:  # recoger objetos
            answer_prompts()
            watch_delay(0.05, "Recogiendo objetos del suelo...", watch)
            send_key(",")
            watch_delay(0.3, "", watch)
            screen = capture_pane()
            if "--More--" in screen or "Más--" in screen:
                save_screenshot(f"pickup_{step:04d}", screen)
                clear_more()

        if step % 12 == 0:  # buscar
            answer_prompts()
            watch_delay(0.05, "Buscando puertas secretas...", watch)
            send_key("s")
            watch_delay(0.5, "", watch)
            screen = capture_pane()
            if "--More--" in screen or "Más--" in screen:
                clear_more()

        if step % 15 == 0:  # abrir puertas
            answer_prompts()
            watch_delay(0.05, "Abriendo puertas...", watch)
            send_key("o")
            watch_delay(0.3, "", watch)
            screen = capture_pane()
            if "direction" in screen.lower() or "dirección" in screen.lower():
                send_key(move)
                watch_delay(0.3, "", watch)
            clear_more()

        if step % 20 == 0:  # bajar escaleras
            answer_prompts()
            watch_delay(0.05, "Buscando escaleras hacia abajo...", watch)
            send_key(">")
            watch_delay(0.5, "", watch)
            screen = capture_pane()
            save_screenshot(f"stairs_{step:04d}", screen)
            if "--More--" in screen or "Más--" in screen:
                clear_more()

        if step % 30 == 0:  # inventario
            answer_prompts()
            watch_delay(0.05, "Abriendo inventario...", watch)
            send_key("i")
            watch_delay(1, "", watch)
            screen = capture_pane()
            save_screenshot(f"inv_{step:04d}", screen)
            clear_more()
            send_key("Escape")
            watch_delay(0.3, "", watch)

        if step % 40 == 0:  # nombre de objeto (C)
            answer_prompts()
            watch_delay(0.05, "Nombrando objeto...", watch)
            send_key("C")
            watch_delay(1, "", watch)
            screen = capture_pane()
            save_screenshot(f"name_{step:04d}", screen)
            clear_more()
            send_key("Escape")
            watch_delay(0.3, "", watch)

        if step % 50 == 0:  # subir escaleras
            answer_prompts()
            watch_delay(0.05, "Buscando escaleras hacia arriba...", watch)
            send_key("<")
            watch_delay(0.5, "", watch)
            screen = capture_pane()
            save_screenshot(f"upstairs_{step:04d}", screen)
            clear_more()

        if step % 60 == 0:  # atributos (#enhance)
            answer_prompts()
            watch_delay(0.05, "Revisando atributos...", watch)
            send_key("#enhance")
            watch_delay(1, "", watch)
            screen = capture_pane()
            save_screenshot(f"enhance_{step:04d}", screen)
            clear_more()
            send_key("q")
            watch_delay(0.3, "", watch)

        # --- COMANDOS WIZARD ---
        if wizard_mode:
            wizard_commands(step, screenshot_dir, save_screenshot, watch)

        # --- Sin muerte en wizard mode ---
        if not wizard_mode and step % 5 == 0:
            screen = capture_pane()
            if is_dead(screen):
                save_screenshot(f"death_{step:04d}", screen)
                log(f"  ⚰️  Fin de partida en paso {step}")
                break

    return all_english, bad_screens, total_screens


# ─── Main ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Partida automática NetHack-es - detecta inglés en gameplay real"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=0,
        help="Pasos máximos (wizard: 1000, normal: 200 por defecto)",
    )
    parser.add_argument(
        "--screenshot-dir",
        default="/tmp/nethack_play_screens",
        help="Directorio de capturas",
    )
    parser.add_argument(
        "--mode",
        choices=["wizard", "normal"],
        default="wizard",
        help="wizard=invencible (defecto), normal=Valkyrie real",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Modo espectador: ralentiza el juego y muestra la sesión tmux para que te conectes",
    )
    args = parser.parse_args()

    wizard = args.mode == "wizard"
    mode_name = "WIZARD (invencible)" if wizard else "NORMAL (Valkyrie)"
    is_watch = args.watch
    max_steps = args.max_steps if args.max_steps > 0 else (1000 if wizard else 200)

    print("=" * 60)
    print(f"  PARTIDA AUTOMÁTICA NETHACK-ES — MODO {mode_name}")
    print("  Detecta strings en inglés durante gameplay real")
    print("=" * 60)
    print()
    log(f"Sesión tmux: {SESSION}")
    log(f"Modo:        {args.mode}")
    log(f"Capturas:    {args.screenshot_dir}")
    log(f"Pasos max:   {max_steps}")
    if is_watch:
        log("  🎬 MODO ESPECTADOR activado")
    if wizard:
        log("  🧙 Personaje invencible - explora toda la mazmorra")
    else:
        log("  ⚔️  Valkyrie real - combate, supervivencia, muerte")
    print()

    if is_watch:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  🎬  MODO ESPECTADOR ACTIVADO                              ║")
        print("║                                                              ║")
        print(f"║  Para VER la partida en directo, abre OTRA TERMINAL y        ║")
        print(f"║  ejecuta:                                                    ║")
        print(f"║                                                              ║")
        print(f"║    tmux attach -t {SESSION}                         ║")
        print(f"║                                                              ║")
        print(f"║  La partida irá más lenta para que puedas seguirla.          ║")
        print(f"║  Ctrl+C aquí para salir.                                     ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        log("  Esperando 5 segundos para que te conectes...")
        time.sleep(5)

    subprocess.run(["rm", "-f", f"{PLAYGROUND}/save/*"], capture_output=True)

    def cleanup():
        subprocess.run(["rm", "-f", f"{PLAYGROUND}/save/*"], capture_output=True)
        log(f"\n  Sesión tmux '{SESSION}' dejada activa.")
        log(f"  Conéctate con: tmux attach -t {SESSION}")

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(0)))

    try:
        english_words, bad_screens, total_screens = play_game(
            max_steps=max_steps,
            screenshot_dir=args.screenshot_dir,
            wizard_mode=wizard,
            watch=is_watch,
        )

        print()
        print("=" * 60)
        print("  RESULTADOS")
        print("=" * 60)
        print(f"  Modo:                    {mode_name}")
        print(f"  Pantallas capturadas:    {total_screens}")
        print(f"  Con inglés detectado:    {bad_screens}")
        if total_screens > 0:
            pct = ((total_screens - bad_screens) / total_screens) * 100
            print(f"  Tasa de acierto:         {pct:.0f}%")
        print(f"  Palabras inglés:         {len(english_words)}")
        if english_words:
            print(f"  Palabras: {sorted(english_words)}")
        print()

        if not english_words:
            print("  ✅ PARTIDA LIMPIA: ¡Ningún inglés detectado!")
        else:
            print("  ⚠️  SE DETECTÓ INGLÉS - Revisar capturas:")
            for w in sorted(english_words):
                print(f"       - {w}")
            print(f"  Capturas: {args.screenshot_dir}")
        print()

    except Exception as e:
        log(f"Error: {e}")
        raise


def log(msg):
    print(msg, flush=True)


if __name__ == "__main__":
    main()
