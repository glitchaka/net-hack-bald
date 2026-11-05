#include "nhb/world.hpp"

#include <algorithm>
#include <cmath>
#include <sstream>
#include <string>

namespace nhb {
namespace {
constexpr const char* kReset = "\x1b[0m";
std::string className(const std::string& role) {
    if (role == "picaro") return "Pícaro";
    if (role == "maga") return "Maga";
    if (role == "guerrero") return "Guerrero";
    return "Valquiria";
}
} // namespace

void World::reveal(Player& hero) {
    for (int y = std::max(0, hero.pos.y - kVision);
         y <= std::min(kHeight - 1, hero.pos.y + kVision); ++y) {
        for (int x = std::max(0, hero.pos.x - kVision);
             x <= std::min(kWidth - 1, hero.pos.x + kVision); ++x) {
            int dx = x - hero.pos.x, dy = y - hero.pos.y;
            if (dx * dx + dy * dy <= kVision * kVision &&
                sees(hero.depth, hero.pos, {x,y}))
                hero.discovered[hero.depth - 1][y][x] = true;
        }
    }
}

std::string World::roster() const {
    std::ostringstream out;
    out << "JUGADORES (" << connectedCount() << '/' << kMaxPlayers << "): ";
    bool first = true;
    for (const auto& [id, hero] : players_) {
        if (!first) out << " | ";
        first = false;
        out << id << ':' << hero.name << " [" << className(hero.role)
            << "; " << (hero.escaped ? "escapó" :
                         !hero.alive ? "muerto" :
                         !hero.connected ? "desconectado" :
                         "P" + std::to_string(hero.depth)) << ']';
    }
    return out.str();
}

std::string World::render(int id) {
    Player* hero = find(id);
    if (!hero) return "Identificación de personaje desconocida.\n";
    reveal(*hero);

    std::ostringstream out;
    out << "\x1b[0m\x1b[2J\x1b[H"
        << "\x1b[1;36mNET-HACK BALD / EXPEDICIÓN MULTIJUGADOR\x1b[0m"
        << "  |  Ronda " << round_ << "  |  " << connectedCount()
        << "/" << kMaxPlayers << " jugadores\n"
        << roster() << "\n";
    if (!started_) {
        out << "\n   SALA DE ESPERA\n\n"
            << "   Se necesitan al menos dos jugadores para empezar.\n"
            << "   Se pueden conectar entre dos y seis personajes.\n\n"
            << "   Cada jugador conserva sus propias estadísticas,\n"
            << "   inventario, posición y línea de visión.\n\n"
            << "   Esperando al segundo participante...\n\n";
    } else {
        const Level& l = level(hero->depth);
        out << " Profundidad " << hero->depth << '/' << kLevels
            << "  |  " << className(hero->role)
            << "  |  " << hero->name << " (@" << id << ")\n";
        out << '+' << std::string(kWidth, '-') << "+\n";
        for (int y = 0; y < kHeight; ++y) {
            out << '|';
            for (int x = 0; x < kWidth; ++x) {
                if (!hero->discovered[hero->depth - 1][y][x]) {
                    out << ' ';
                    continue;
                }
                const Pos pos{x,y};
                bool visible = std::abs(hero->pos.x - x) <= kVision &&
                    std::abs(hero->pos.y - y) <= kVision &&
                    ((x - hero->pos.x) * (x - hero->pos.x) +
                     (y - hero->pos.y) * (y - hero->pos.y) <=
                     kVision * kVision) &&
                    sees(hero->depth, hero->pos, pos);
                char symbol = l.tiles[y][x];
                const char* color = visible ? "" : "\x1b[2m";
                if (visible) {
                    for (const Loot& item : l.loot)
                        if (item.pos == pos) {
                            symbol = item.item.symbol;
                            color = "\x1b[33m";
                        }
                    for (const Monster& monster : l.monsters)
                        if (monster.hp > 0 && monster.pos == pos) {
                            symbol = monster.symbol;
                            color = "\x1b[1;31m";
                        }
                    // Otros jugadores no comparten automáticamente sus mapas.
                    for (const auto& [otherId, other] : players_)
                        if (otherId != id && other.alive && !other.escaped &&
                            other.depth == hero->depth && other.pos == pos) {
                            symbol = static_cast<char>('0' + otherId);
                            color = "\x1b[1;35m";
                        }
                }
                if (hero->pos == pos) {
                    symbol = '@';
                    color = "\x1b[1;32m";
                }
                out << color << symbol << kReset;
            }
            out << "|\n";
        }
        out << '+' << std::string(kWidth, '-') << "+\n"
            << "PV " << hero->hp << '/' << hero->maxHp
            << " | PM " << hero->mp << '/' << hero->maxMp
            << " | NIV " << hero->level
            << " | EXP " << hero->experience
            << " | HAMBRE " << hero->hunger
            << " | ORO " << hero->gold
            << " | FLECHAS " << hero->arrows
            << " | AMULETO " << (hero->hasAmulet ? "SÍ" : "NO") << '\n'
            << "ARMA +" << hero->weapon << " | ARMADURA +" << hero->armor
            << " | " << (hero->poison > 0 ? "ENVENENADO" :
                         !hero->alive ? "MUERTO" : "EN PIE") << '\n';

        out << "MOCHILA: ";
        if (hero->bag.empty()) out << "(vacía)";
        for (std::size_t i = 0; i < hero->bag.size(); ++i) {
            if (i) out << ", ";
            out << hero->bag[i].name;
            if (hero->bag[i].count > 1) out << " x" << hero->bag[i].count;
        }
        out << "\n";
        for (const auto& msg : hero->messages) out << " > " << msg << '\n';
        if (finished_)
            out << "\x1b[1;33m" << announcement_ << kReset << '\n';
        else if (!hero->alive)
            out << "\x1b[1;31mTu personaje ha muerto.\x1b[0m\n";
        else if (orders_.count(id))
            out << "Tu acción está enviada. Esperando " << waitingCount()
                << " jugador(es) antes de resolver la ronda.\n";
        else
            out << "TU TURNO: elige una acción. Faltan "
                << waitingCount() << " jugador(es) por actuar.\n";
    }
    out << "Mover: hjklyubn / teclado numérico | . esperar | g recoger | "
        << "e comer | q poción\n"
        << "m maná | r leer | w arma | W armadura | f flecha | z magia | "
        << "o puerta | < > escaleras\n"
        << "Ctrl+G chat | Ctrl+] salir | ? ayuda. "
        << "Todas las acciones se resuelven por rondas.\n";
    return out.str();
}

void World::chat(int id, const std::string& line) {
    const Player* sender = find(id);
    if (!sender || line.empty()) return;
    std::string text = "[CHAT] " + sender->name + ": " + line.substr(0, 180);
    for (auto& [_, hero] : players_)
        message(hero, text);
}

} // namespace nhb
