#!/usr/bin/env python3
"""
Bot inteligente para NetHack-es v2.
- Captura mensajes del juego en CADA paso (no cada 5)
- Extrae específicamente los mensajes de la esquina superior izquierda
- Guarda mensajes únicos en inglés para traducción
- Mapa con tipos de terreno usando la leyenda de símbolos
- Pathfinding A* que evita paredes
- Exploración con prioridades (escaleras > objetos > zonas nuevas)
- Tracking de coordenadas reales (actualiza dun_x/dun_y al moverse)
"""

import subprocess, time, re, sys, os, signal, atexit, argparse, heapq
from collections import deque

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

SESSION = f"nethack_bot_{os.getpid()}"
PLAYGROUND = os.path.expanduser("~/proyectos/juego/nethack-es/playground")

# ─── Símbolos del mapa (según help.es) ──────────────────────────────
SYMBOL_WALL = {"#", "-", "|"}
SYMBOL_FLOOR = {".", ",", ";", ":"}
SYMBOL_OBJ = {"$", "%", "!", "?", "=", '"', "/", "*", "(", "[", "]", "\\", "{", "}"}
SYMBOL_STAIRS_DOWN = ">"
SYMBOL_STAIRS_UP = "<"
SYMBOL_CLOSED_DOOR = "+"
SYMBOL_TRAP = "^"
SYMBOL_PLAYER = "@"

# Mapa de símbolo -> tipo de terreno
TERRAIN_MAP = {}
for ch in SYMBOL_WALL:
    TERRAIN_MAP[ch] = "wall"
for ch in SYMBOL_FLOOR:
    TERRAIN_MAP[ch] = "floor"
for ch in SYMBOL_OBJ:
    TERRAIN_MAP[ch] = "object"
TERRAIN_MAP[SYMBOL_STAIRS_DOWN] = "stairs_down"
TERRAIN_MAP[SYMBOL_STAIRS_UP] = "stairs_up"
TERRAIN_MAP[SYMBOL_CLOSED_DOOR] = "closed_door"
TERRAIN_MAP[SYMBOL_TRAP] = "trap"
TERRAIN_MAP[SYMBOL_PLAYER] = "player"

# Tipos transitables (sin abrir)
TERRAIN_WALKABLE = {"floor", "object", "stairs_down", "stairs_up", "trap", "player"}
# Tipos transitables con acción (abrir puerta)
TERRAIN_OPENABLE = {"closed_door"}

DIR_VEC = {
    "h": (-1, 0),
    "j": (0, 1),
    "k": (0, -1),
    "l": (1, 0),
    "y": (-1, -1),
    "u": (1, -1),
    "b": (-1, 1),
    "n": (1, 1),
}
DIR_NAMES = {
    "h": "oeste",
    "j": "sur",
    "k": "norte",
    "l": "este",
    "y": "noroeste",
    "u": "noreste",
    "b": "suroeste",
    "n": "sureste",
}

DEATH_PATTERNS = [
    "you die",
    "you are dead",
    "killed",
    "muerto",
    "has muerto",
    "do you want your possessions identified",
    "your quest is over",
]
ALLOWED_ENGLISH = {"fruit", "autodig", "pickup"}

# ─── Tmux ────────────────────────────────────────────────────────────


def send(key):
    subprocess.run(
        ["tmux", "send-keys", "-t", SESSION, key], capture_output=True, timeout=5
    )


def capture():
    r = subprocess.run(
        ["tmux", "capture-pane", "-t", SESSION, "-p", "-S", "-500"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return r.stdout


def clear_more(max_iter=15):
    for _ in range(max_iter):
        txt = capture()
        if "--More--" in txt or "Más--" in txt:
            send("Space")
            time.sleep(0.2)
        else:
            break


# ─── Análisis de pantalla ────────────────────────────────────────────


def get_hp(screen):
    m = re.search(r"HP:(\d+)\((\d+)\)", screen)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def is_playing(screen):
    return bool(re.search(r"HP:\d+", screen))


def is_dead(screen):
    return any(p in screen.lower() for p in DEATH_PATTERNS)


def extract_game_messages(screen):
    """Extrae los mensajes del juego de la zona superior izquierda.
    Los mensajes están en las primeras líneas, ANTES del mapa.
    Ignora líneas de estado y vacías.
    """
    lines = screen.split("\n")
    messages = []
    in_map = False
    for line in lines:
        # Si encontramos un patrón de mapa (muchos espacios o caracteres de pared),
        # dejamos de recoger mensajes
        stripped = line.strip()
        if not stripped:
            continue
        # Detectar cuando entramos en la zona del mapa
        if "@" in line and ("." in line or "#" in line or "|" in line):
            in_map = True
            continue
        if in_map:
            continue
        # Ignorar líneas de estado
        if re.search(r"HP:|St:|Dx:|Co:|In:|Wi:|Ch:|AC:|Xp|T:|\$:", stripped):
            continue
        # Ignorar líneas con solo números (coordenadas)
        if re.match(r"^[\d\s\-]+$", stripped):
            continue
        # Esto es un mensaje del juego
        messages.append(stripped)
    return messages


def parse_surroundings(screen):
    """Encuentra @ y analiza las 8 casillas alrededor.
    Devuelve: (px, py, dict_dir->char, map_lines)
    """
    lines = screen.split("\n")
    px = py = -1
    for y, line in enumerate(lines):
        x = line.find("@")
        if x >= 0:
            px, py = x, y
            break
    if px < 0:
        return None, None, {}, []

    surr = {}
    for key, (dx, dy) in DIR_VEC.items():
        nx, ny = px + dx, py + dy
        if 0 <= ny < len(lines) and 0 <= nx < len(lines[ny]):
            surr[key] = lines[ny][nx]
        else:
            surr[key] = " "

    # Líneas del mapa visible (±8 alrededor de @)
    map_start = max(0, py - 8)
    map_end = min(len(lines), py + 6)
    map_lines = []
    for y in range(map_start, map_end):
        line = lines[y]
        if not re.search(r"HP:|St:|Dx:|Co:", line):
            map_lines.append(line)

    return px, py, surr, map_lines


def render_minimap(surr):
    if not surr:
        return ""
    view = {
        (-1, -1): "y",
        (0, -1): "k",
        (1, -1): "u",
        (-1, 0): "h",
        (0, 0): "@",
        (1, 0): "l",
        (-1, 1): "b",
        (0, 1): "j",
        (1, 1): "n",
    }
    rows = []
    for dy in [-1, 0, 1]:
        row = ""
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                row += "@"
            else:
                row += surr.get(view[(dx, dy)], " ")
        rows.append(row)
    return "\n".join(rows)


# ─── Prompt handling ────────────────────────────────────────────────

ALL_PROMPTS = [
    ("die?", lambda: send("n")),
    ("[yn]", lambda: send("n")),
    ("[ynq]", lambda: send("n")),
    ("direction", lambda: send("Escape")),
    ("dirección", lambda: send("h")),  # send direction h (west) instead of Escape
    ("in what direction", lambda: send("Escape")),
    ("¿en qué dirección", lambda: send("Escape")),
    ("pick up", lambda: send("Escape")),
    ("recoger", lambda: send("Escape")),
    ("what do you want to", lambda: send("Escape")),
    ("qué quieres", lambda: send("Escape")),
    ("identify what", lambda: send("Escape")),
]


def answer_prompts():
    screen = capture()
    lines = screen.strip().split("\n")
    for line in lines[-5:]:
        lower = line.lower()
        for pat, action in ALL_PROMPTS:
            if pat in lower:
                action()
                time.sleep(0.3)
                return True
    return False


# ─── Creación de personaje ───────────────────────────────────────────


def create_character():
    log("  Creando personaje Valkyrie...")
    # Limpiar saves de partidas anteriores
    subprocess.run(["rm", "-f", f"{PLAYGROUND}/save/*"], capture_output=True)
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", SESSION, "-x", "132", "-y", "50"],
        capture_output=True,
        timeout=5,
    )
    time.sleep(1)
    subprocess.run(
        ["tmux", "set", "-t", SESSION, "remain-on-exit", "on"],
        capture_output=True,
        timeout=5,
    )
    send(f"cd {PLAYGROUND} && ./nethack")
    send("Enter")
    time.sleep(3)
    clear_more()
    time.sleep(1)
    send("Enter")
    time.sleep(1.5)
    clear_more()
    send("y")
    time.sleep(1)
    clear_more()
    screen = capture()
    if "ynq" in screen or "yn" in screen:
        send("y")
        time.sleep(1)
        clear_more()
    screen = capture()
    if "tutorial" in screen.lower():
        send("n")
        time.sleep(1)
    for _ in range(40):
        screen = capture()
        if is_playing(screen):
            break
        send("Space")
        time.sleep(0.2)
    for _ in range(20):
        time.sleep(0.3)
        if is_playing(capture()):
            break
    screen = capture()
    if is_playing(screen):
        log("  ✅ Personaje creado")
    else:
        log("  ⚠️  No se pudo crear el personaje")
    return screen


# ─── Bot v2 ──────────────────────────────────────────────────────────


class Bot:
    def __init__(self, watch=False):
        self.watch = watch
        # Coordenadas de mazmorra (se actualizan con cada movimiento)
        self.dun_x = 0
        self.dun_y = 0
        # Mapa: (x,y) -> {'char': '#', 'type': 'wall', 'known': bool}
        self.dmap = {}
        # Mensajes en inglés detectados
        self.seen_messages = set()
        self.english_messages = []  # [{msg, words, step}]
        # Path planning
        self.path = []
        self.path_target = None
        self.blocked_frontiers = set()  # tiles desconocidos que fallaron
        # Estado
        self.stuck = 0
        self.stairs_cd = 0
        self.step = 0
        # Últimas posiciones para detectar bucles
        self.last_positions = deque(maxlen=10)
        # Direcciones recientes para evitar péndulo
        self.recent_dirs = deque(maxlen=6)
        # Tracking de habitación
        self.steps_in_room = 0
        self.room_visited_count = 0
        self.force_exit_mode = False
        self.escape_steps = 0
        # Modo navegación (seguir dirección fija)
        self.wander_dir = "l"  # dirección de vagabundeo
        self.wander_steps = 0  # pasos en esta dirección

    def log(self, msg):
        if self.watch:
            print(f"  🤖 {msg}", flush=True)

    def save_screenshot(self, name, screen):
        with open(f"/tmp/nethack_bot/{name}.txt", "w") as f:
            f.write(screen)

    # ─── Sistema de mensajes ──────────────────────────────────────────

    def process_messages(self, screen):
        """Extrae mensajes, detecta nuevos en inglés y los guarda."""
        msgs = extract_game_messages(screen)
        for msg in msgs:
            if msg not in self.seen_messages:
                self.seen_messages.add(msg)
                eng = self.detect_english(msg)
                if eng:
                    # Verificar que no sea un falso positivo
                    clean_eng = [w for w in eng if w not in ALLOWED_ENGLISH]
                    if clean_eng:
                        self.english_messages.append(
                            {
                                "message": msg,
                                "english_words": clean_eng,
                                "step": self.step,
                            }
                        )
                        self.log(f"⚠️  INGLÉS [{self.step}]: {msg}")
                        self.log(f"    Palabras: {clean_eng}")

    def save_english_log(self):
        """Guarda todos los mensajes en inglés detectados."""
        if not self.english_messages:
            return
        path = "/tmp/nethack_bot/english_messages.txt"
        with open(path, "w") as f:
            for item in self.english_messages:
                f.write(f"Paso {item['step']}: {item['message']}\n")
                f.write(f"  Inglés: {', '.join(item['english_words'])}\n\n")
        self.log(f"📝 Mensajes inglés guardados en: {path}")

    def detect_english(self, text):
        """Detecta palabras inglesas en un texto."""
        words = set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))
        from word_lists import GAME_TERMS, SPANISH_WORDS, ENGLISH_WORDS

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

    # ─── Mapa con tipos de terreno ────────────────────────────────────

    def get_terrain_type(self, ch):
        """Retorna el tipo de terreno según la leyenda de símbolos."""
        if ch in SYMBOL_WALL:
            return "wall"
        if ch in SYMBOL_FLOOR:
            return "floor"
        if ch == SYMBOL_STAIRS_DOWN:
            return "stairs_down"
        if ch == SYMBOL_STAIRS_UP:
            return "stairs_up"
        if ch == SYMBOL_CLOSED_DOOR:
            return "closed_door"
        if ch == SYMBOL_TRAP:
            return "trap"
        if ch == SYMBOL_PLAYER:
            return "player"
        # Monstruos (letras)
        if ch.isalpha() and ch != "@":
            return "monster"
        # Objetos
        if ch in SYMBOL_OBJ:
            return "object"
        return "unknown"

    def is_walkable(self, terrain_type, ch=" "):
        """Determina si un tipo de terreno es caminable.
        ' ' (espacio/fuera de mapa) NO es caminable.
        'unknown' solo es caminable si está en el mapa conocido (dmap).
        """
        if ch == " ":
            return False  # Fuera del mapa visible
        if terrain_type in TERRAIN_WALKABLE:
            return True
        if terrain_type == "unknown":
            return True  # Asumir caminable para explorar
        return False

    def update_map(self, surr):
        """Actualiza el mapa de mazmorra con tipos de terreno."""
        # Posición actual
        self.dmap[(self.dun_x, self.dun_y)] = {
            "char": "@",
            "type": "player",
            "known": True,
        }
        # Casillas adyacentes
        for key, ch in (surr or {}).items():
            dx, dy = DIR_VEC.get(key, (0, 0))
            wx, wy = self.dun_x + dx, self.dun_y + dy
            if (wx, wy) not in self.dmap:
                self.dmap[(wx, wy)] = {
                    "char": ch,
                    "type": self.get_terrain_type(ch),
                    "known": True,
                }

    def update_visible_map(self, screen, px, py, map_lines):
        """Registra todas las casillas visibles en el mapa."""
        if not map_lines:
            return
        map_top = max(0, py - 8)
        for y_off, line in enumerate(map_lines):
            scr_y = map_top + y_off
            for scr_x, ch in enumerate(line):
                if ch == " " or ch == "@":
                    continue
                dx, dy = scr_x - px, scr_y - py
                wx, wy = self.dun_x + dx, self.dun_y + dy
                if (wx, wy) not in self.dmap:
                    self.dmap[(wx, wy)] = {
                        "char": ch,
                        "type": self.get_terrain_type(ch),
                        "known": True,
                    }

    # ─── Pathfinding A* ──────────────────────────────────────────────

    def walkable_neighbors(self, pos, include_diag=False):
        """Retorna vecinos caminables desde una posición."""
        x, y = pos
        dirs = ["l", "j", "h", "k"] + (["u", "n", "b", "y"] if include_diag else [])
        neighbors = []
        for dk in dirs:
            dx, dy = DIR_VEC[dk]
            nx, ny = x + dx, y + dy
            terrain = self.dmap.get((nx, ny), {"type": "unknown", "char": " "})
            ch = terrain.get("char", " ")
            if self.is_walkable(terrain["type"], ch):
                neighbors.append((nx, ny))
        return neighbors

    def astar(self, start, goal, max_dist=50, force_diag=False):
        """Pathfinding A* desde start hasta goal (incluye diagonales).
        Devuelve: lista de direcciones o None.
        """
        if start == goal:
            return []

        # Usar diagonales si: ruta larga, forzado, o si va a puerta
        dist = max(abs(start[0] - goal[0]), abs(start[1] - goal[1]))
        use_diag = force_diag or dist > 2 or dist > 0

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(start[0] - goal[0]) + abs(start[1] - goal[1])}
        closed = set()

        while open_set:
            _, current = heapq.heappop(open_set)
            if current in closed:
                continue
            closed.add(current)

            if current == goal or len(closed) > max_dist:
                path = []
                while current in came_from:
                    prev = came_from[current]
                    dx, dy = current[0] - prev[0], current[1] - prev[1]
                    for dk, (ddx, ddy) in DIR_VEC.items():
                        if (dx, dy) == (ddx, ddy):
                            path.insert(0, dk)
                            break
                    current = prev
                return path

            for neighbor in self.walkable_neighbors(current, include_diag=use_diag):
                if neighbor in closed:
                    continue
                # Coste: 1 para cardinal, 1.4 para diagonal
                dx, dy = neighbor[0] - current[0], neighbor[1] - current[1]
                cost = 1.4 if (dx != 0 and dy != 0) else 1.0
                tentative_g = g_score[current] + cost

                terrain = self.dmap.get(neighbor, {"type": "unknown"})
                if terrain["type"] == "trap":
                    tentative_g += 3
                if terrain["type"] == "closed_door":
                    tentative_g += 2

                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h = abs(neighbor[0] - goal[0]) + abs(neighbor[1] - goal[1])
                    f = tentative_g + h
                    heapq.heappush(open_set, (f, neighbor))

        return None

    # ─── Búsqueda de objetivos ───────────────────────────────────────

    def find_targets(self, terrain_types):
        """Encuentra todas las posiciones de un tipo de terreno."""
        targets = []
        for pos, data in self.dmap.items():
            if data["type"] in terrain_types and data["known"]:
                targets.append(pos)
        return targets

    def find_nearest(self, terrain_types):
        """Encuentra el objetivo más cercano de cierto tipo."""
        targets = self.find_targets(terrain_types)
        if not targets:
            return None, None
        px, py = self.dun_x, self.dun_y
        best_dist = float("inf")
        best_target = None
        for tx, ty in targets:
            dist = abs(tx - px) + abs(ty - py)
            if dist < best_dist and dist > 0:
                best_dist = dist
                best_target = (tx, ty)
        return best_target, best_dist

    def find_nearest_door(self, max_dist=40):
        """Busca la puerta o paso más cercano para salir de la habitación."""
        px, py = self.dun_x, self.dun_y
        best = None
        best_dist = max_dist + 1
        for pos, data in self.dmap.items():
            if data["type"] in ("closed_door",):
                dist = abs(pos[0] - px) + abs(pos[1] - py)
                if dist < best_dist and dist > 0:
                    best_dist = dist
                    best = pos
        if best:
            return best, self.astar(
                (px, py), best, max_dist=best_dist + 5, force_diag=True
            )
        return None, None

    def find_unvisited_frontier(self, max_dist=30):
        """Encuentra la casilla fronteriza sin visitar más cercana
        usando BFS desde la posición actual (incluye diagonales).
        """
        start = (self.dun_x, self.dun_y)
        visited = {start}
        q = deque()
        q.append((start, []))

        # Incluir diagonales para mejor exploración
        all_dirs = ["l", "j", "h", "k", "u", "n", "b", "y"]

        while q:
            pos, path = q.popleft()
            if len(path) > max_dist:
                continue

            px, py = pos
            # Buscar tiles desconocidos ADYACENTES a pos
            for dk in all_dirs:
                dx, dy = DIR_VEC[dk]
                nx, ny = px + dx, py + dy
                if (nx, ny) not in self.dmap and (nx, ny) not in self.blocked_frontiers:
                    return path + [dk] if path else [dk]

            # Expandir vecinos (cardinales + diagonales)
            for dk in all_dirs:
                dx, dy = DIR_VEC[dk]
                nx, ny = px + dx, py + dy
                neighbor = (nx, ny)
                if neighbor in visited:
                    continue
                terrain = self.dmap.get(neighbor, {"type": "unknown", "char": " "})
                ch = terrain.get("char", " ")
                if self.is_walkable(terrain["type"], ch):
                    visited.add(neighbor)
                    q.append((neighbor, path + [dk]))
        return None

    # ─── Movimiento inteligente ──────────────────────────────────────

    def get_direction(self, path):
        """Toma una lista de direcciones (A*) y retorna la primera."""
        if not path:
            return None
        # Verificar que la primera dirección sea válida en surr
        return path[0]

    def next_move(self, surr):
        """Decide el siguiente movimiento con prioridades:
        1. Escaleras cercanas
        2. Seguir ruta planificada
        3. Buscar puerta si todo explorado (modo salida)
        4. Explorar frontera (zonas sin visitar)
        5. Cualquier dirección transitable
        """
        px, py = self.dun_x, self.dun_y

        # 1. Escaleras (si están cerca, ir directo)
        if self.stairs_cd <= 0:
            for pos, data in self.dmap.items():
                if data["type"] in ("stairs_down", "stairs_up"):
                    ex, ey = pos
                    dist = abs(ex - px) + abs(ey - py)
                    if dist <= 5 and dist > 0:
                        self.wander_dir = "l"  # reset wander
                        for dk, (ddx, ddy) in DIR_VEC.items():
                            if (ex - px, ey - py) == (ddx, ddy):
                                if surr and surr.get(dk, " ") in (
                                    SYMBOL_STAIRS_DOWN,
                                    SYMBOL_STAIRS_UP,
                                ):
                                    self.stairs_cd = 10
                                    return dk
                        path = self.astar((px, py), (ex, ey), max_dist=8)
                        if path:
                            self.path = path[1:]
                            self.path_target = (ex, ey)
                            self.log(f"🪜 Yendo a escalera en ({ex},{ey})")
                            return self.get_direction(path)

        # 2. Seguir ruta planificada
        if self.path:
            d = self.path.pop(0)
            if surr and surr.get(d, " ") not in SYMBOL_WALL:
                return d
            else:
                self.path = []

        # 2.5. Modo escape activo? Ir a puerta o escalera
        if self.force_exit_mode or self.steps_in_room > 25:
            self.force_exit_mode = True
            # Buscar puerta más cercana
            door_pos, door_path = self.find_nearest_door(max_dist=50)
            if door_pos and door_path:
                self.log(f"🚪 Buscando puerta en {door_pos} (escapando)")
                self.path = door_path[1:]
                self.force_exit_mode = False
                self.steps_in_room = 0
                return self.get_direction(door_path)
            # Buscar escaleras
            for pos, data in self.dmap.items():
                if data["type"] in ("stairs_down", "stairs_up"):
                    dist = abs(pos[0] - px) + abs(pos[1] - py)
                    if dist <= 50 and dist > 0:
                        path = self.astar(
                            (px, py), pos, max_dist=dist + 5, force_diag=True
                        )
                        if path:
                            self.log(f"🪜 Yendo a escalera (escapando)")
                            self.path = path[1:]
                            self.force_exit_mode = False
                            self.steps_in_room = 0
                            return self.get_direction(path)

        # 3. Explorar frontera
        frontier_path = self.find_unvisited_frontier(max_dist=30)
        if frontier_path:
            first = frontier_path[0]
            # Verificar que el primer paso sea válido
            if surr and surr.get(first, " ") in SYMBOL_WALL:
                # Falso positivo: el tile desconocido está tras una pared
                # Calcular su posición y bloquearlo
                dx, dy = DIR_VEC.get(first, (0, 0))
                blocked_tile = (px + dx, py + dy)
                # También calcular el tile desconocido objetivo
                for dk2 in ["l", "j", "h", "k"]:
                    dx2, dy2 = DIR_VEC[dk2]
                    nx, ny = px + dx2, py + dy2
                    if (nx, ny) not in self.dmap:
                        self.blocked_frontiers.add((nx, ny))
                self.blocked_frontiers.add(blocked_tile)
                self.log(f"🚫 Frontera bloqueada ({first} es pared), reintentando...")
                # Reintentar inmediatamente (con la frontera ya bloqueada)
                frontier_path = self.find_unvisited_frontier(max_dist=30)
                if frontier_path:
                    first = frontier_path[0]
            if frontier_path:
                self.wander_dir = "l"  # reset wander
                self.log(f"🗺️  Explorando frontera ({len(frontier_path)} pasos)")
                self.path = frontier_path[1:]
                self.force_exit_mode = False
                if surr and surr.get(first, " ") == SYMBOL_CLOSED_DOOR:
                    self.log(f"🚪 Abriendo puerta al {DIR_NAMES[first]}")
                    send("o")
                    time.sleep(0.2)
                    send(first)
                    time.sleep(0.3)
                return self.get_direction(frontier_path)

        # 3.5. Si todo explorado, buscar puerta
        door_pos, door_path = self.find_nearest_door(max_dist=30)
        if door_pos and door_path:
            self.wander_dir = "l"
            self.log(f"🚪 Yendo a puerta en {door_pos} ({len(door_path)} pasos)")
            self.path = door_path[1:]
            return self.get_direction(door_path)

        # 4. Navegación direccional (seguir dirección fija)
        if self.wander_steps % 10 == 0:
            self.log(f"🧭 Vagando {DIR_NAMES[self.wander_dir]} ({self.wander_steps})")
        # Primero ver si la dirección actual es válida
        ch = surr.get(self.wander_dir, " ")
        tt = self.get_terrain_type(ch)
        if self.is_walkable(tt, ch) or tt == "closed_door":
            self.wander_steps += 1
            return self.wander_dir
        # Si está bloqueada, buscar la mejor alternativa mirando paredes
        # Estrategia: seguir la pared (wall following)
        best_dir = None
        # Preferir dirección cardinal sobre diagonal
        for dk in ["l", "j", "h", "k"]:
            chk = surr.get(dk, " ")
            ttk = self.get_terrain_type(chk)
            if self.is_walkable(ttk, chk) or ttk == "closed_door":
                best_dir = dk
                break
        if not best_dir:
            for dk in ["u", "n", "b", "y"]:
                chk = surr.get(dk, " ")
                ttk = self.get_terrain_type(chk)
                if self.is_walkable(ttk, chk) or ttk == "closed_door":
                    best_dir = dk
                    break
        if best_dir:
            self.wander_dir = best_dir
            self.wander_steps += 1
            return best_dir

        return None

    # ─── Menús y submenús ──────────────────────────────────────────

    def explore_menus(self):
        """Abre todos los menús del juego y submenús para detectar inglés.
        Cada menú se abre, se captura la pantalla, y se cierra.
        """
        # (comando, nombre, descripción, submenús a navegar)
        menus = [
            (
                "?",
                "help_main",
                "Ayuda principal",
                ["a", "c", "d", "f", "i", "m", "o", "s", "t"],
            ),
            (
                "\\",
                "whatis_main",
                "Qué es (menú principal)",
                ["m", "M", "o", "O", "t", "T", "e", "E", "?"],
            ),
            ("*", "discoveries", "Descubrimientos", []),
            ("#time", "time", "Tiempo de juego", []),
            ("#version", "version", "Versión", []),
            ("#enhance", "enhance", "Habilidades", []),
        ]

        for cmd, label, desc, submenus in menus:
            answer_prompts()
            self.log(f"📋 Abriendo menú: {desc} ({cmd})")
            send(cmd)
            # Esperar con verificacion de prompts
            for _ in range(5):
                time.sleep(0.2)
                answer_prompts()
            screen = capture()
            self.save_screenshot(f"menu_{label}_{self.step:04d}", screen)
            self.process_messages(screen)

            if submenus:
                for sub in submenus:
                    answer_prompts()
                    send(sub)
                    for _ in range(4):
                        time.sleep(0.2)
                        answer_prompts()
                    sub_screen = capture()
                    self.save_screenshot(
                        f"menu_{label}_{sub}_{self.step:04d}", sub_screen
                    )
                    self.process_messages(sub_screen)
                    clear_more()
                    send("Escape")
                    time.sleep(0.3)
                    clear_more()

            # Cerrar el menú principal
            clear_more()
            send("Escape")
            time.sleep(0.3)
            clear_more()

    # ─── Búsqueda global de escaleras en dmap ──────────────────────

    def scan_for_stairs(self):
        """Busca escaleras en todo el mapa conocido y pathfind hacia ellas."""
        px, py = self.dun_x, self.dun_y
        best = None
        best_dist = 999
        for pos, data in self.dmap.items():
            if data["type"] in ("stairs_down", "stairs_up"):
                dist = abs(pos[0] - px) + abs(pos[1] - py)
                if dist < best_dist and dist > 3:
                    best_dist = dist
                    best = pos
        if best:
            path = self.astar((px, py), best, max_dist=50, force_diag=True)
            if path:
                self.log(f"🪜 Escaleras encontradas en {best} a {best_dist} pasos")
                self.path = path[1:]
                self.path_target = best
                return self.get_direction(path)
        return None

    # ─── Bucle principal ─────────────────────────────────────────────

    def play(self, max_steps=500):
        os.makedirs("/tmp/nethack_bot", exist_ok=True)
        screen = create_character()
        self.save_screenshot("000_inicio", screen)

        all_eng_set = set()
        bad = 0
        total = 0

        for self.step in range(1, max_steps + 1):
            # 1. Responder prompts
            answer_prompts()

            # 2. Capturar pantalla
            screen = capture()

            # 3. Analizar mapa
            px, py, surr, map_lines = parse_surroundings(screen)

            # 4. PROCESAR MENSAJES (en CADA paso, no cada 5)
            self.process_messages(screen)

            if px is not None and py is not None:
                self.update_map(surr)
                self.update_visible_map(screen, px, py, map_lines)

            # 5. Tracking de habitación y modo escape
            if px is not None and py is not None:
                # Contar cuántos tiles transitables conocemos alrededor
                # Si no hemos explorado nada nuevo en 30+ pasos, buscar salida
                nearby = sum(
                    1
                    for dk in ["l", "j", "h", "k"]
                    if surr.get(dk, " ") not in SYMBOL_WALL | {" "}
                )
                if surr.get("h", " ") != "?" and nearby <= 1:
                    self.steps_in_room += 1
                else:
                    self.steps_in_room = max(0, self.steps_in_room - 1)

                # Limpiar fronteras bloqueadas cada 50 pasos
                if self.step % 50 == 0 and self.blocked_frontiers:
                    self.blocked_frontiers.clear()
                    self.log(f"🧹 Fronteras bloqueadas reiniciadas")

                # Activar modo escape si está atascado mucho tiempo
                if self.steps_in_room > 35:
                    self.force_exit_mode = True
                    self.blocked_frontiers.clear()
                    if self.step % 15 == 0:
                        self.log(
                            f"🚨 Atascado {self.steps_in_room} pasos - buscando salida!"
                        )

            # 6. Inglés en pantalla completa (cada 5 pasos para stats)
            if self.step % 5 == 0:
                self.save_screenshot(f"{self.step:04d}", screen)
                total += 1
                eng = self.detect_english(screen)
                if eng:
                    bad += 1
                    all_eng_set.update(eng)

            # 6. Muerte
            if is_dead(screen):
                self.log(f"💀 Muerto en paso {self.step}")
                self.save_screenshot(f"dead_{self.step:04d}", screen)
                break

            # 7. Estado y minimapa
            hp, max_hp = get_hp(screen)
            if self.step % 10 == 0 or self.step == 1:
                pos = f"({self.dun_x},{self.dun_y})"
                viz = len([p for p in self.dmap if self.dmap[p]["type"] != "wall"])
                mm = render_minimap(surr)
                eng_count = len(self.english_messages)
                blocked = len(self.blocked_frontiers)
                rm = self.steps_in_room
                self.log(
                    f"📍 Paso {self.step} | HP:{hp}/{max_hp} | {pos} | Explor: {viz} | Eng: {eng_count} | B:{blocked} R:{rm}"
                )
                if mm:
                    for r in mm.split("\n"):
                        self.log(f"   {r}")

            # 8. Escaleras adyacentes
            if self.stairs_cd > 0:
                self.stairs_cd -= 1
            if px is not None and surr:
                for dk, ch in surr.items():
                    if (
                        ch in (SYMBOL_STAIRS_DOWN, SYMBOL_STAIRS_UP)
                        and self.stairs_cd <= 0
                    ):
                        cmd = ">" if ch == SYMBOL_STAIRS_DOWN else "<"
                        self.log(f"🪜 Escalera en {DIR_NAMES.get(dk, dk)}!")
                        send(cmd)
                        time.sleep(0.5)
                        clear_more()
                        self.stairs_cd = 20
                        ns = capture()
                        if (
                            "staircase" not in ns.lower()
                            and "escalera" not in ns.lower()
                        ):
                            self.log("  ✅ Bajada!")
                        break

            # 9. Exploración de menús (cada 70 pasos)
            if self.step % 70 == 0 and self.step > 10:
                self.explore_menus()

                # 10. Curación
                self.log(f"❤️‍🩹 Curando (HP {hp}/{max_hp})...")
                send("q")
                time.sleep(0.4)
                s2 = capture()
                if "what" in s2.lower() or "qué" in s2.lower():
                    send("a")
                    time.sleep(0.2)
                    send("Enter")
                    time.sleep(0.2)
                clear_more()
                continue

            # 10. Comida
            if px is not None:
                lines = screen.strip().split("\n")
                for line in lines[-5:]:
                    low = line.lower()
                    if any(w in low for w in ["hungry", "hambri", "weak", "débil"]):
                        self.log("🍽️  Comiendo...")
                        send("e")
                        time.sleep(0.4)
                        s2 = capture()
                        if "what" in s2.lower() or "qué" in s2.lower():
                            send("a")
                            time.sleep(0.2)
                        clear_more()
                        break

            # 11. Acciones periódicas
            if self.step % 8 == 0:
                answer_prompts()
                send("m,")
                time.sleep(0.5)
                s2 = capture()
                if "pick up" in s2.lower() or "recoger" in s2.lower() or "[yn]" in s2:
                    send("a")
                    time.sleep(0.2)
                    send("Enter")
                    time.sleep(0.2)
                clear_more()
            if self.step % 15 == 0:
                answer_prompts()
                send("s")
                time.sleep(0.5)
                clear_more()
            if self.step % 35 == 0:
                answer_prompts()
                send("i")
                time.sleep(0.5)
                self.save_screenshot(f"inv_{self.step:04d}", capture())
                clear_more()
                send("Escape")
                time.sleep(0.2)

            # 12. MOVIMIENTO INTELIGENTE
            if px is not None and surr:
                # Verificar si la posición cambió (nos movimos)
                old_x, old_y = self.dun_x, self.dun_y

                d = self.next_move(surr)

                # Detectar obstáculos alrededor
                walls_around = sum(1 for ch in surr.values() if ch in SYMBOL_WALL)
                if walls_around >= 6:
                    self.stuck += 2
                else:
                    self.stuck = max(0, self.stuck - 1)

                if d:
                    dname = DIR_NAMES.get(d, d)
                    ch = surr.get(d, " ")
                    tt = self.get_terrain_type(ch)
                    self.log(f"🚶 {dname} [{ch}:{tt}]  (stuck:{self.stuck})")

                    # Abrir puertas si es necesario
                    if ch == SYMBOL_CLOSED_DOOR:
                        self.log(f"🚪 Abriendo puerta al {dname}")
                        send("o")
                        time.sleep(0.2)
                        send(d)
                        time.sleep(0.3)

                    # Mover en RÁFAGA de 3-6 pasos (verificar cada paso)
                    import random as _random

                    burst = _random.randint(3, 6)
                    moved = 0
                    for b in range(burst):
                        send(d)
                        time.sleep(0.1)
                        # Verificar si el movimiento fue exitoso
                        b_screen = capture()
                        b_lines = b_screen.strip().split("\n")
                        b_msg = b_lines[-1].lower() if b_lines else ""
                        if (
                            "can't" in b_msg
                            or "cant" in b_msg
                            or "wall" in b_msg
                            or "block" in b_msg
                        ):
                            self.log(f"  🚫 Paso {b + 1} bloqueado, parando")
                            break
                        dx, dy = DIR_VEC.get(d, (0, 0))
                        self.dun_x += dx
                        self.dun_y += dy
                        moved += 1
                    self.last_positions.append((old_x, old_y))
                    self.recent_dirs.append(d)
                    if moved > 0:
                        self.log(f"  → {moved} pasos al {dname}")

                else:
                    self.stuck += 3
                    self.log(f"💤 Sin ruta! (stuck:{self.stuck})")

                # Modo escape: burst + search + open doors
                if self.force_exit_mode and self.step % 10 == 0:
                    self.log(f"🔥 Escape burst!")
                    # Buscar puertas secretas
                    send("s")
                    time.sleep(0.5)
                    clear_more()
                    # Abrir puertas en todas direcciones
                    for dk in ["l", "j", "h", "k"]:
                        send("o")
                        time.sleep(0.1)
                        send(dk)
                        time.sleep(0.15)
                    clear_more()

                # Burst si muy atascado: probar TODAS las direcciones
                if self.stuck > 6 or (self.force_exit_mode and self.stuck > 3):
                    self.log(f"🔥 Burst direcciones! (stuck:{self.stuck})")
                    for dk in ["l", "j", "h", "k", "u", "n", "b", "y"]:
                        send(dk)
                        time.sleep(0.06)
                    self.stuck = 2
                    if self.force_exit_mode:
                        self.stuck = 0
            else:
                send("l")
                time.sleep(0.2)

        # Guardar mensajes en inglés encontrados
        self.save_english_log()

        return all_eng_set, bad, total


# ─── Main ────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Bot NetHack-es v2")
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("  🤖  BOT NET-HACK-ES v2 (mensajes + pathfinding A*)")
    print("  Captura inglés en CADA paso - mapeo inteligente")
    print("=" * 60)
    print()
    log(f"Sesión tmux: {SESSION}")

    if args.watch:
        print()
        print("╔════════════════════════════════════════════════════════╗")
        print("║  Para VER el bot, abre OTRA TERMINAL y ejecuta:     ║")
        print(f"║    tmux attach -t {SESSION}                  ║")
        print("╚════════════════════════════════════════════════════════╝")
        print()
        log("  Esperando 5s para que te conectes...")
        time.sleep(5)

    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
    subprocess.run(["rm", "-f", f"{PLAYGROUND}/save/*"], capture_output=True)

    def cleanup():
        log(f"\n  ✅ Sesión '{SESSION}' dejada activa.")
        log(f"  Conéctate con: tmux attach -t {SESSION}")

    atexit.register(cleanup)
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(0)))

    try:
        bot = Bot(watch=args.watch)
        eng_set, bad_total, total_shots = bot.play(args.max_steps)

        print()
        print("=" * 60)
        print("  RESULTADOS")
        print("=" * 60)
        print(f"  Pasos:               {bot.step}")
        print(f"  Mapa explorado:      {len(bot.dmap)} tiles")
        print(f"  Mensajes inglés:     {len(bot.english_messages)}")
        print(f"  Palabras únicas:     {len(eng_set)}")
        if bot.english_messages:
            print()
            print("  Mensajes en inglés encontrados:")
            for item in bot.english_messages[:20]:
                print(f"    [{item['step']}] {item['message'][:100]}")
                print(f"      → {', '.join(item['english_words'])}")
            if len(bot.english_messages) > 20:
                print(f"    ... y {len(bot.english_messages) - 20} más")
        if not eng_set:
            print("  ✅ Sin inglés!")
        print()

        # Mapa explorado
        if hasattr(bot, "dmap") and bot.dmap:
            xs = [p[0] for p in bot.dmap]
            ys = [p[1] for p in bot.dmap]
            for y in range(min(ys), max(ys) + 1):
                row = ""
                for x in range(min(xs), max(xs) + 1):
                    ch = (
                        bot.dmap.get((x, y), {}).get("char", " ")
                        if isinstance(bot.dmap.get((x, y)), dict)
                        else " "
                    )
                    row += ch
                print(f"    {row}")
            print()
    except Exception as e:
        log(f"Error: {e}")
        import traceback

        traceback.print_exc()


def log(msg):
    print(msg, flush=True)


if __name__ == "__main__":
    main()
