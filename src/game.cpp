#include "nhb/game.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>

namespace nhb {

Game::Game() : rng_(std::random_device{}()) {}

Floor& Game::floor() { return floors_.at(static_cast<std::size_t>(depth_ - 1)); }
const Floor& Game::floor() const { return floors_.at(static_cast<std::size_t>(depth_ - 1)); }

int Game::randomInt(int low, int high) {
    std::uniform_int_distribution<int> dice(low, high);
    return dice(rng_);
}

bool Game::inside(int x, int y) const {
    return x >= 0 && y >= 0 && x < MAP_WIDTH && y < MAP_HEIGHT;
}

bool Game::passable(const Floor& f, int x, int y) const {
    if (!inside(x, y)) return false;
    switch (f.terrain[y][x]) {
        case '.': case '#': case '<': case '>': return true;
        default: return false;
    }
}

bool Game::occupied(int x, int y, int ignore) const {
    const auto& monsters = floor().monsters;
    for (int i = 0; i < static_cast<int>(monsters.size()); ++i)
        if (i != ignore && monsters[i].hp > 0 &&
            monsters[i].pos.x == x && monsters[i].pos.y == y) return true;
    return false;
}

bool Game::lineOfSight(Point start, Point target) const {
    int x = start.x, y = start.y;
    const int dx = std::abs(target.x - x);
    const int dy = std::abs(target.y - y);
    const int sx = x < target.x ? 1 : -1;
    const int sy = y < target.y ? 1 : -1;
    int error = dx - dy;
    while (!(x == target.x && y == target.y)) {
        int doubled = 2 * error;
        if (doubled > -dy) { error -= dy; x += sx; }
        if (doubled < dx) { error += dx; y += sy; }
        if (!inside(x, y)) return false;
        if (x == target.x && y == target.y) return true;
        const char tile = floor().terrain[y][x];
        if (tile == '|' || tile == '-' || tile == '+' || tile == ' ')
            return false;
    }
    return true;
}

void Game::say(const std::string& text) {
    messages_.push_back(text);
    while (messages_.size() > 3) messages_.pop_front();
}

void Game::newGame() {
    hero_ = Hero{};
    floors_ = {};
    depth_ = 1;
    turns_ = 0;
    playing_ = true;
    victory_ = false;
    hasAmulet_ = false;
    messages_.clear();

    terminal::clear();
    std::cout <<
        "╔══════════════════════ NETHACK BALD ══════════════════════╗\n"
        "║      Una aventura por turnos completamente en español     ║\n"
        "╚══════════════════════════════════════════════════════════╝\n\n"
        "Nombre de tu aventurero (Enter = Aventurero): ";
    std::string name;
    terminal::lineInput(name);
    if (!name.empty()) hero_.name = name;

    terminal::clear();
    std::cout
        << "ELIGE TU CLASE\n\n"
        << "  1) Guerrero  — mucha vida, espada y armadura.\n"
        << "  2) Maga      — poca vida, abundante maná.\n"
        << "  3) Pícaro    — gran agilidad y precisión.\n"
        << "  4) Valquiria — resistencia y daño equilibrado.\n\n"
        << "Pulsa 1, 2, 3 o 4: " << std::flush;
    int role = terminal::readKey();
    if (role < '1' || role > '4') role = '1';

    if (role == '1') {
        hero_.role = "Guerrero";
        hero_.hp = hero_.maxHp = 38;
        hero_.mp = hero_.maxMp = 6;
        hero_.strength = 8;
        hero_.agility = 5;
        hero_.intellect = 3;
        hero_.defense = 2;
        hero_.pack.push_back({ItemKind::Weapon, "espada larga", ')', 5, 1, true});
        hero_.pack.push_back({ItemKind::Armor, "cota de malla", '[', 3, 1, true});
    } else if (role == '2') {
        hero_.role = "Maga";
        hero_.hp = hero_.maxHp = 23;
        hero_.mp = hero_.maxMp = 25;
        hero_.strength = 3;
        hero_.agility = 5;
        hero_.intellect = 9;
        hero_.defense = 0;
        hero_.pack.push_back({ItemKind::Weapon, "bastón arcano", ')', 2, 1, true});
        hero_.pack.push_back({ItemKind::Armor, "túnica reforzada", '[', 1, 1, true});
    } else if (role == '3') {
        hero_.role = "Pícaro";
        hero_.hp = hero_.maxHp = 29;
        hero_.mp = hero_.maxMp = 10;
        hero_.strength = 5;
        hero_.agility = 9;
        hero_.intellect = 5;
        hero_.defense = 1;
        hero_.arrows = 14;
        hero_.pack.push_back({ItemKind::Weapon, "daga afilada", ')', 4, 1, true});
        hero_.pack.push_back({ItemKind::Armor, "chaleco de cuero", '[', 2, 1, true});
    } else {
        hero_.role = "Valquiria";
        hero_.hp = hero_.maxHp = 35;
        hero_.mp = hero_.maxMp = 9;
        hero_.strength = 7;
        hero_.agility = 6;
        hero_.intellect = 4;
        hero_.defense = 2;
        hero_.pack.push_back({ItemKind::Weapon, "hacha de guerra", ')', 5, 1, true});
        hero_.pack.push_back({ItemKind::Armor, "escudo y coraza", '[', 3, 1, true});
    }
    hero_.weapon = 0;
    hero_.armor = 1;
    hero_.pack.push_back({ItemKind::Food, "ración de viaje", '%', 320, 2, true});
    hero_.pack.push_back({ItemKind::Healing, "poción curativa", '!', 17, 2, true});
    hero_.pack.push_back({ItemKind::Mana, "poción de maná", '!', 12, 1, true});

    generateFloor(1);
    hero_.pos = floor().up;
    say("Despiertas en la entrada del laberinto subterráneo.");
    say("Busca el Amuleto de Bald en la profundidad 10 y vuelve vivo.");
    say("Pulsa ? para consultar los controles.");
}

bool Game::menu() {
    for (;;) {
        terminal::clear();
        std::cout
            << "\x1b[1;36m"
            << "  _   _      _   _   _            _      ____        _     _\n"
            << " | \\ | | ___| |_| | | | __ _  ___| | __ | __ )  __ _| | __| |\n"
            << " |  \\| |/ _ \\ __| |_| |/ _  |/ __| |/ / |  _ \\ / _  | |/ _  |\n"
            << " | |\\  |  __/ |_|  _  | (_| | (__|   <  | |_) | (_| | | (_| |\n"
            << " |_| \\_|\\___|\\__|_| |_|\\__,_|\\___|_|\\_\\ |____/ \\__,_|_|\\__,_|\n"
            << "\x1b[0m\n"
            << "         ROGUELIKE EN C++ - TOTALMENTE EN ESPAÑOL\n\n"
            << "  [1] NUEVA PARTIDA\n"
            << "  [2] CONTINUAR PARTIDA GUARDADA\n"
            << "  [3] SALIR\n\n"
            << "  Meta: encontrar el Amuleto de Bald y regresar a la superficie.\n\n"
            << "  Selección: " << std::flush;
        int key = terminal::readKey();
        if (key == '1') { newGame(); return true; }
        if (key == '2') {
            if (loadGame()) {
                say("Has recuperado tu aventura.");
                return true;
            }
            std::cout << "\n\n  No existe partida válida. Pulsa una tecla." << std::flush;
            terminal::readKey();
        }
        if (key == '3' || key == 27 || key == 'Q') return false;
    }
}

void Game::updateVision() {
    for (auto& row : visible_) row.fill(false);
    for (int y = std::max(0, hero_.pos.y - 9);
         y <= std::min(MAP_HEIGHT - 1, hero_.pos.y + 9); ++y) {
        for (int x = std::max(0, hero_.pos.x - 9);
             x <= std::min(MAP_WIDTH - 1, hero_.pos.x + 9); ++x) {
            int dx = x - hero_.pos.x;
            int dy = y - hero_.pos.y;
            if (dx * dx + dy * dy <= 81 &&
                lineOfSight(hero_.pos, {x, y})) {
                visible_[y][x] = true;
                floor().explored[y][x] = true;
            }
        }
    }
    visible_[hero_.pos.y][hero_.pos.x] = true;
    floor().explored[hero_.pos.y][hero_.pos.x] = true;
}

int Game::armorValue() const {
    int value = hero_.defense;
    if (hero_.armor >= 0 && hero_.armor < static_cast<int>(hero_.pack.size()))
        value += hero_.pack[hero_.armor].power;
    return value;
}

int Game::weaponValue() const {
    if (hero_.weapon >= 0 && hero_.weapon < static_cast<int>(hero_.pack.size()))
        return hero_.pack[hero_.weapon].power;
    return 1;
}

void Game::draw() {
    terminal::clear();
    std::cout << "\x1b[1;36m NETHACK BALD\x1b[0m"
              << " | " << hero_.name << " / " << hero_.role
              << " | Profundidad " << depth_ << "/" << FLOOR_COUNT
              << " | Turno " << turns_ << "\n";
    std::cout << "+" << std::string(MAP_WIDTH, '-') << "+\n";
    for (int y = 0; y < MAP_HEIGHT; ++y) {
        std::cout << '|';
        for (int x = 0; x < MAP_WIDTH; ++x) {
            if (!floor().explored[y][x]) { std::cout << ' '; continue; }
            char glyph = floor().terrain[y][x];
            const char* color = "";
            if (visible_[y][x]) {
                for (const auto& obj : floor().objects)
                    if (obj.pos.x == x && obj.pos.y == y) {
                        glyph = obj.item.glyph;
                        color = "\x1b[33m";
                    }
                for (const auto& trap : floor().traps)
                    if (trap.revealed && !trap.spent &&
                        trap.pos.x == x && trap.pos.y == y) {
                        glyph = '^';
                        color = "\x1b[31m";
                    }
                for (const auto& monster : floor().monsters)
                    if (monster.hp > 0 &&
                        monster.pos.x == x && monster.pos.y == y) {
                        glyph = monster.glyph;
                        color = "\x1b[1;31m";
                    }
            }
            if (hero_.pos.x == x && hero_.pos.y == y) {
                glyph = '@';
                color = "\x1b[1;32m";
            }
            if (color[0]) std::cout << color << glyph << "\x1b[0m";
            else std::cout << glyph;
        }
        std::cout << "|\n";
    }
    std::cout << "+" << std::string(MAP_WIDTH, '-') << "+\n";
    std::cout << "PV " << hero_.hp << '/' << hero_.maxHp
              << "  PM " << hero_.mp << '/' << hero_.maxMp
              << "  NIV " << hero_.level << "  EXP " << hero_.xp
              << "  DEF " << armorValue()
              << "  ORO " << hero_.gold
              << "  FLECHAS " << hero_.arrows << '\n';

    std::string hunger = hero_.hunger > 600 ? "Saciado" :
                         hero_.hunger > 300 ? "Con apetito" :
                         hero_.hunger > 120 ? "Hambriento" : "Desfalleciendo";
    std::cout << "Estado: " << hunger;
    if (hero_.poison > 0) std::cout << " / ENVENENADO";
    std::cout << "  | Mochila " << hero_.pack.size() << '/' << PACK_LIMIT
              << "  | Amuleto: " << (hasAmulet_ ? "SÍ" : "NO") << '\n';
    for (const auto& msg : messages_) std::cout << " > " << msg << '\n';
    for (std::size_t i = messages_.size(); i < 3; ++i) std::cout << '\n';
    std::cout << "[?] Ayuda  [i] Inventario  [S] Guardar  [Q] Salir" << std::flush;
}

void Game::printHelp() {
    terminal::clear();
    std::cout <<
        "NETHACK BALD - CONTROLES Y REGLAS\n"
        "==================================\n\n"
        "MOVIMIENTO (también sirven las flechas)\n"
        "   y  k  u         7  8  9\n"
        "    \\ | /           \\ | /\n"
        "   h  @  l         4  @  6\n"
        "    / | \\           / | \\\n"
        "   b  j  n         1  2  3\n\n"
        " h,j,k,l,y,u,b,n / 1,2,3,4,6,7,8,9: moverse.\n"
        " Moverse contra un enemigo: atacarlo. .: esperar un turno.\n"
        " , / g: recoger objetos del suelo. i: consultar inventario.\n"
        " e: comer. q: beber poción. r: leer pergamino.\n"
        " w: empuñar arma. W: vestir armadura. T: quitar armadura.\n"
        " f: lanzar una flecha. z: lanzar un hechizo.\n"
        " o: abrir una puerta adyacente. d: soltar objeto.\n"
        " x: examinar una casilla cercana. >: bajar. <: subir.\n"
        " S: guardar partida. Q: abandonar. ESC: cancelar menú.\n\n"
        " SÍMBOLOS: @ tú | . sala | # pasillo | + puerta |\n"
        "           < y > escaleras | ^ trampa | ! poción |\n"
        "           ? pergamino | % comida | ) arma | [ armadura.\n"
        " Las letras rojas representan monstruos.\n\n"
        " OBJETIVO: el Amuleto de Bald se oculta en la planta 10.\n"
        " Tómalo y sube por todas las escaleras hasta la superficie.\n"
        " La muerte es permanente. Vigila el hambre y el veneno.\n\n"
        " Pulsa una tecla para volver..." << std::flush;
    terminal::readKey();
}

void Game::inventory() {
    terminal::clear();
    std::cout << "MOCHILA DE " << hero_.name << "\n\n";
    if (hero_.pack.empty()) std::cout << "(Vacía)\n";
    for (std::size_t i = 0; i < hero_.pack.size(); ++i) {
        const Item& item = hero_.pack[i];
        std::cout << " " << static_cast<char>('a' + i) << ") "
                  << item.glyph << " " << item.name;
        if (item.amount > 1) std::cout << " x" << item.amount;
        if (static_cast<int>(i) == hero_.weapon) std::cout << " [EMPUÑADA]";
        if (static_cast<int>(i) == hero_.armor) std::cout << " [PUESTA]";
        if (item.kind == ItemKind::Weapon || item.kind == ItemKind::Armor)
            std::cout << " (+" << item.power << ")";
        std::cout << '\n';
    }
    std::cout << "\nOro: " << hero_.gold << " | Flechas: " << hero_.arrows
              << "\n\nPulsa una tecla para continuar..." << std::flush;
    terminal::readKey();
}

int Game::chooseItem(const std::string& prompt, std::optional<ItemKind> kind) {
    std::vector<int> choices;
    for (int i = 0; i < static_cast<int>(hero_.pack.size()); ++i)
        if (!kind || hero_.pack[i].kind == *kind) choices.push_back(i);
    if (choices.empty()) { say("No tienes un objeto apropiado."); return -1; }

    terminal::clear();
    std::cout << prompt << "\n\n";
    for (int index : choices) {
        const Item& item = hero_.pack[index];
        std::cout << " [" << static_cast<char>('a' + index) << "] "
                  << item.name;
        if (item.amount > 1) std::cout << " x" << item.amount;
        if (hero_.weapon == index || hero_.armor == index)
            std::cout << " (equipado)";
        std::cout << '\n';
    }
    std::cout << "\nLetra del objeto o ESC para cancelar: " << std::flush;
    for (;;) {
        int key = terminal::readKey();
        if (key == 27) return -1;
        int index = key - 'a';
        if (std::find(choices.begin(), choices.end(), index) != choices.end())
            return index;
    }
}

bool Game::askDirection(int& dx, int& dy) {
    std::cout << "\nDirección (hjklyubn, 1-9, flechas o ESC): " << std::flush;
    int key = terminal::readKey();
    dx = dy = 0;
    switch (key) {
        case 'h': case '4': dx = -1; break;
        case 'l': case '6': dx = 1; break;
        case 'k': case '8': dy = -1; break;
        case 'j': case '2': dy = 1; break;
        case 'y': case '7': dx = -1; dy = -1; break;
        case 'u': case '9': dx = 1; dy = -1; break;
        case 'b': case '1': dx = -1; dy = 1; break;
        case 'n': case '3': dx = 1; dy = 1; break;
        default: return false;
    }
    return true;
}

void Game::levelUp() {
    while (hero_.xp >= 12 * hero_.level * hero_.level) {
        ++hero_.level;
        int bonus = randomInt(3, 7);
        hero_.maxHp += bonus;
        hero_.hp = std::min(hero_.maxHp, hero_.hp + bonus + 5);
        hero_.maxMp += 2 + (hero_.role == "Maga" ? 2 : 0);
        hero_.mp = hero_.maxMp;
        if (hero_.level % 2 == 0) ++hero_.strength;
        if (hero_.level % 3 == 0) ++hero_.agility;
        say("¡Subes al nivel " + std::to_string(hero_.level) + "!");
    }
}

void Game::endGame(const std::string& reason, bool won) {
    victory_ = won;
    playing_ = false;
    say(reason);
    removeSave(); // La victoria y la muerte cierran definitivamente la partida.
}

void Game::advanceTurn() {
    if (!playing_) return;
    ++turns_;
    hero_.hunger = std::max(0, hero_.hunger - 1);
    if (hero_.poison > 0) {
        --hero_.poison;
        if (turns_ % 3 == 0) {
            --hero_.hp;
            say("El veneno recorre tus venas (-1 PV).");
        }
    }
    if (hero_.hunger == 0 && turns_ % 2 == 0) {
        --hero_.hp;
        say("Te debilitas por inanición (-1 PV).");
    }
    if (turns_ % 8 == 0 && hero_.mp < hero_.maxMp) ++hero_.mp;
    if (turns_ % 15 == 0 && hero_.hunger > 300 && hero_.hp < hero_.maxHp)
        ++hero_.hp;
    if (hero_.hp <= 0) {
        endGame("Has muerto por heridas, hambre o veneno.", false);
        return;
    }
    monsterTurn();
}

void Game::monsterTurn() {
    Floor& f = floor();
    for (int i = 0; i < static_cast<int>(f.monsters.size()) && playing_; ++i) {
        Monster& enemy = f.monsters[i];
        if (enemy.hp <= 0) continue;
        int dx = hero_.pos.x - enemy.pos.x;
        int dy = hero_.pos.y - enemy.pos.y;
        int distance = std::max(std::abs(dx), std::abs(dy));

        if (distance <= 7 && lineOfSight(enemy.pos, hero_.pos))
            enemy.awake = true;
        if (!enemy.awake) continue;

        if (distance <= 1 && lineOfSight(enemy.pos, hero_.pos)) {
            int chance = std::clamp(65 + enemy.attack * 2 - hero_.agility * 4, 20, 92);
            if (randomInt(1, 100) <= chance) {
                int hit = std::max(1, randomInt(1, enemy.attack) -
                                     armorValue() / 3);
                hero_.hp -= hit;
                say("El " + enemy.name + " te golpea (-" +
                    std::to_string(hit) + " PV).");
                if (hero_.hp <= 0) {
                    endGame("El " + enemy.name + " ha acabado contigo.", false);
                    return;
                }
            } else if (distance <= 2) {
                say("Esquivas el ataque del " + enemy.name + ".");
            }
            continue;
        }

        if (distance > 12) { enemy.awake = false; continue; }
        std::vector<Point> candidates;
        for (int stepY = -1; stepY <= 1; ++stepY)
            for (int stepX = -1; stepX <= 1; ++stepX)
                if (stepX != 0 || stepY != 0)
                    candidates.push_back({enemy.pos.x + stepX, enemy.pos.y + stepY});
        std::shuffle(candidates.begin(), candidates.end(), rng_);
        std::stable_sort(candidates.begin(), candidates.end(),
            [&](Point a, Point b) {
                auto dist = [&](Point p) {
                    return std::max(std::abs(p.x - hero_.pos.x),
                                    std::abs(p.y - hero_.pos.y));
                };
                return dist(a) < dist(b);
            });

        for (Point step : candidates) {
            if (step == hero_.pos || !passable(f, step.x, step.y) ||
                occupied(step.x, step.y, i)) continue;
            int newDist = std::max(std::abs(step.x - hero_.pos.x),
                                   std::abs(step.y - hero_.pos.y));
            if (newDist < distance) {
                enemy.pos = step;
                break;
            }
        }
    }
}

void Game::run() {
    while (playing_) {
        updateVision();
        draw();
        int key = terminal::readKey();
        switch (key) {
            case 'h': case '4': walk(-1, 0); break;
            case 'j': case '2': walk(0, 1); break;
            case 'k': case '8': walk(0, -1); break;
            case 'l': case '6': walk(1, 0); break;
            case 'y': case '7': walk(-1, -1); break;
            case 'u': case '9': walk(1, -1); break;
            case 'b': case '1': walk(-1, 1); break;
            case 'n': case '3': walk(1, 1); break;
            case '.': case '5': advanceTurn(); break;
            case ',': case 'g': pickUp(); break;
            case 'i': inventory(); break;
            case 'e': eat(); break;
            case 'q': drink(); break;
            case 'r': readScroll(); break;
            case 'w': wield(); break;
            case 'W': wear(); break;
            case 'T': takeOff(); break;
            case 'f': shoot(); break;
            case 'z': spell(); break;
            case 'o': openDoor(); break;
            case 'd': drop(); break;
            case 'x': inspect(); break;
            case '>': changeFloor(true); break;
            case '<': changeFloor(false); break;
            case '?': printHelp(); break;
            case 'S':
                say(saveGame() ? "Partida guardada en partida.nhb." :
                                 "Error: no se pudo escribir partida.nhb.");
                break;
            case 'Q':
                std::cout << "\n¿Abandonar la aventura? (s/N): " << std::flush;
                if (terminal::readKey() == 's') {
                    playing_ = false;
                    say("Has interrumpido la expedición.");
                }
                break;
            default:
                if (key != 0 && key != 27)
                    say("Comando desconocido. Pulsa ? para ayuda.");
                break;
        }
    }
    terminal::clear();
    if (victory_)
        std::cout << "\x1b[1;32m¡VICTORIA! EL AMULETO HA REGRESADO A LA LUZ.\x1b[0m\n\n";
    else if (hero_.hp <= 0)
        std::cout << "\x1b[1;31mHAS MUERTO EN LAS PROFUNDIDADES.\x1b[0m\n\n";
    else
        std::cout << "EXPEDICIÓN INTERRUMPIDA\n\n";
    if (!messages_.empty()) std::cout << messages_.back() << "\n\n";
    std::cout << "Aventurero: " << hero_.name
              << " | Clase: " << hero_.role
              << " | Nivel: " << hero_.level
              << " | Profundidad: " << depth_
              << " | Turnos: " << turns_ << "\n\n";
    std::cout << "Pulsa una tecla para volver al menú principal..." << std::flush;
    terminal::readKey();
}

} // namespace nhb
