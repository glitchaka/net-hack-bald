#include "nhb/world.hpp"

#include <algorithm>
#include <cmath>
#include <sstream>
#include <utility>

namespace nhb {
namespace {
struct Room {
    int x, y, w, h;
    Pos center() const { return {x + w / 2, y + h / 2}; }
    bool apart(const Room& b) const {
        return x + w + 1 < b.x || b.x + b.w + 1 < x ||
               y + h + 1 < b.y || b.y + b.h + 1 < y;
    }
};
Monster monsterFor(int depth, int roll) {
    if (depth > 8 && roll > 7)
        return {{}, 50, 50, 12, 6, 80, 'D', "dragón"};
    if (depth > 6 && roll > 6)
        return {{}, 32, 32, 10, 5, 45, '&', "demonio"};
    if (depth > 4 && roll > 5)
        return {{}, 24, 24, 8, 4, 28, 'T', "trol"};
    if (depth > 2 && roll > 4)
        return {{}, 16, 16, 6, 3, 16, 'o', "orco"};
    if (depth > 1 && roll > 3)
        return {{}, 10, 10, 5, 2, 9, 's', "esqueleto"};
    return (roll > 5)
        ? Monster{{}, 7, 7, 4, 1, 6, 'g', "duende"}
        : Monster{{}, 5, 5, 3, 1, 4, 'r', "rata gigante"};
}
Item itemFor(int depth, int roll) {
    switch (roll) {
        case 0: case 1: return {Kind::Food, 350, 1, "ración de viaje", '%'};
        case 2: case 3: return {Kind::Potion, 12 + depth, 1, "poción curativa", '!'};
        case 4: return {Kind::Mana, 10 + depth, 1, "poción de maná", '!'};
        case 5: return {Kind::Sword, 3 + depth / 2, 1, "espada encantada", ')'};
        case 6: return {Kind::Armor, 2 + depth / 3, 1, "armadura", '['};
        case 7: return {Kind::Scroll, 0, 1, "pergamino cartográfico", '?'};
        case 8: return {Kind::Arrows, 0, 5, "flechas", ')'};
        default: return {Kind::Food, 220, 1, "manzana", '%'};
    }
}
} // namespace

World::World() : generator_(std::random_device{}()) {}
int World::dice(int low, int high) {
    return std::uniform_int_distribution<int>(low, high)(generator_);
}
bool World::inside(Pos p) const {
    return p.x >= 0 && p.x < kWidth && p.y >= 0 && p.y < kHeight;
}
bool World::traversable(int depth, Pos p) const {
    if (depth < 1 || depth > kLevels || !inside(p)) return false;
    char tile = level(depth).tiles[p.y][p.x];
    return tile == '.' || tile == '#' || tile == '<' || tile == '>';
}
bool World::occupiedByHero(int depth, Pos p, int except) const {
    for (const auto& pair : players_) {
        const Player& hero = pair.second;
        if (pair.first != except && hero.alive && !hero.escaped &&
            hero.depth == depth && hero.pos == p) return true;
    }
    return false;
}
bool World::occupiedByMonster(int depth, Pos p) const {
    for (const Monster& monster : level(depth).monsters)
        if (monster.hp > 0 && monster.pos == p) return true;
    return false;
}
bool World::sees(int depth, Pos from, Pos to) const {
    if (depth < 1 || depth > kLevels || !inside(from) || !inside(to)) return false;
    int x = from.x, y = from.y;
    int dx = std::abs(to.x - x), dy = std::abs(to.y - y);
    int sx = x < to.x ? 1 : -1, sy = y < to.y ? 1 : -1;
    int err = dx - dy;
    while (x != to.x || y != to.y) {
        int twice = err * 2;
        if (twice > -dy) { err -= dy; x += sx; }
        if (twice < dx) { err += dx; y += sy; }
        if (!inside({x,y})) return false;
        if (x == to.x && y == to.y) return true;
        char tile = level(depth).tiles[y][x];
        if (tile == ' ' || tile == '-' || tile == '|' || tile == '+')
            return false;
    }
    return true;
}
Pos World::openSpot(int depth, bool away) {
    const Level& l = level(depth);
    for (int attempt = 0; attempt < 2500; ++attempt) {
        Pos p{dice(2, kWidth - 3), dice(2, kHeight - 3)};
        if (l.tiles[p.y][p.x] != '.') continue;
        if (away && std::abs(p.x - l.up.x) + std::abs(p.y - l.up.y) < 8)
            continue;
        if (!occupiedByMonster(depth, p) && !occupiedByHero(depth, p))
            return p;
    }
    return l.up;
}
void World::generate(int depth) {
    Level& l = level(depth);
    if (l.generated) return;
    for (std::string& row : l.tiles) row.assign(kWidth, ' ');
    l.loot.clear();
    l.monsters.clear();
    std::vector<Room> rooms;
    for (int tries = 0; tries < 450 && rooms.size() < 15; ++tries) {
        Room r{dice(2, kWidth - 17), dice(2, kHeight - 10),
               dice(7, 14), dice(5, 8)};
        if (r.x + r.w >= kWidth - 2 || r.y + r.h >= kHeight - 2) continue;
        bool suitable = true;
        for (const Room& old : rooms)
            if (!r.apart(old)) { suitable = false; break; }
        if (!suitable) continue;
        rooms.push_back(r);
        for (int y = r.y; y < r.y + r.h; ++y)
            for (int x = r.x; x < r.x + r.w; ++x)
                l.tiles[y][x] = (y == r.y || y == r.y + r.h - 1) ? '-'
                    : ((x == r.x || x == r.x + r.w - 1) ? '|' : '.');
    }
    if (rooms.size() < 2) {
        for (std::string& row : l.tiles) row.assign(kWidth, ' ');
        rooms = {{4,4,12,7},{kWidth - 19,kHeight - 11,12,7}};
        for (const Room& r : rooms)
            for (int y = r.y; y < r.y + r.h; ++y)
                for (int x = r.x; x < r.x + r.w; ++x)
                    l.tiles[y][x] = (y == r.y || y == r.y + r.h - 1) ? '-'
                        : ((x == r.x || x == r.x + r.w - 1) ? '|' : '.');
    }
    const auto carve = [&](Pos p) {
        if (!inside(p)) return;
        char& t = l.tiles[p.y][p.x];
        if (t == '-' || t == '|') t = '+';
        else if (t == ' ') t = '#';
    };
    for (std::size_t i = 1; i < rooms.size(); ++i) {
        Pos a = rooms[i - 1].center();
        Pos b = rooms[i].center();
        const bool horizontalFirst = dice(0, 1) == 0;
        auto dx = [&]() {
            while (a.x != b.x) {
                a.x += a.x < b.x ? 1 : -1;
                carve(a);
            }
        };
        auto dy = [&]() {
            while (a.y != b.y) {
                a.y += a.y < b.y ? 1 : -1;
                carve(a);
            }
        };
        if (horizontalFirst) { dx(); dy(); }
        else { dy(); dx(); }
    }
    l.up = rooms.front().center();
    l.down = rooms.back().center();
    l.tiles[l.up.y][l.up.x] = '<';
    if (depth != kLevels) l.tiles[l.down.y][l.down.x] = '>';
    // Se marca antes de poblar para evitar regeneración accidental.
    l.generated = true;
    for (int i = 0; i < 6 + depth * 2; ++i) {
        Monster m = monsterFor(depth, dice(0,9));
        m.pos = openSpot(depth);
        if (m.pos == l.up) continue;
        l.monsters.push_back(std::move(m));
    }
    for (int i = 0; i < 9 + depth; ++i) {
        Pos p = openSpot(depth);
        if (p != l.up) l.loot.push_back({p, itemFor(depth, dice(0,9))});
    }
    if (depth == kLevels) {
        Pos p = openSpot(depth);
        if (p == l.up) p = l.down;
        l.loot.push_back({p, {Kind::Amulet, 0, 1, "Amuleto de Bald", '"'}});
    }
}
Player* World::find(int id) {
    auto it = players_.find(id);
    return it == players_.end() ? nullptr : &it->second;
}
const Player* World::find(int id) const {
    auto it = players_.find(id);
    return it == players_.end() ? nullptr : &it->second;
}
void World::message(Player& hero, const std::string& text) {
    hero.messages.push_back(text);
    while (hero.messages.size() > 4) hero.messages.pop_front();
}
int World::connectedCount() const {
    int count = 0;
    for (const auto& [_, hero] : players_)
        if (hero.connected) ++count;
    return count;
}
int World::waitingCount() const {
    int count = 0;
    for (const auto& [id, hero] : players_)
        if (hero.connected && hero.alive && !hero.escaped &&
            orders_.find(id) == orders_.end()) ++count;
    return count;
}
int World::participantsRequired() const {
    int count = 0;
    for (const auto& [_, hero] : players_)
        if (hero.connected && hero.alive && !hero.escaped) ++count;
    return count;
}
std::optional<int> World::join(std::string name, std::string role,
                                std::string& reason) {
    if (name.empty() || name.size() > 24) {
        reason = "El nombre debe tener de 1 a 24 caracteres.";
        return {};
    }
    for (unsigned char c : name)
        if (c < 32 || c == 127 || c == '\\') {
            reason = "El nombre contiene caracteres no permitidos.";
            return {};
        }
    if (role != "guerrero" && role != "maga" &&
        role != "picaro" && role != "valquiria") {
        reason = "Clases válidas: guerrero, maga, picaro, valquiria.";
        return {};
    }
    for (auto& [id, hero] : players_) {
        if (hero.name != name) continue;
        if (hero.connected) {
            reason = "Ya hay un jugador conectado con ese nombre.";
            return {};
        }
        hero.connected = true;
        // La clase original se conserva al recuperar el personaje.
        reason = "Personaje recuperado, bienvenido.";
        orders_.erase(id);
        return id;
    }
    if (players_.size() >= kMaxPlayers) {
        reason = "La partida ya tiene seis personajes.";
        return {};
    }
    if (finished_) {
        reason = "La expedición ya terminó.";
        return {};
    }
    if (!level(1).generated) generate(1);
    Player hero;
    hero.id = nextId_++;
    hero.name = std::move(name);
    hero.role = std::move(role);
    hero.depth = 1;
    hero.pos = level(1).up;
    if (occupiedByHero(1, hero.pos))
        hero.pos = openSpot(1, false);
    if (hero.role == "guerrero") {
        hero.maxHp = hero.hp = 42;
        hero.attack = 9;
        hero.defense = 4;
        hero.mp = hero.maxMp = 5;
    } else if (hero.role == "maga") {
        hero.maxHp = hero.hp = 26;
        hero.attack = 4;
        hero.defense = 1;
        hero.mp = hero.maxMp = 24;
    } else if (hero.role == "picaro") {
        hero.maxHp = hero.hp = 32;
        hero.attack = 7;
        hero.defense = 2;
        hero.mp = hero.maxMp = 10;
        hero.arrows = 18;
    } else {
        hero.maxHp = hero.hp = 38;
        hero.attack = 8;
        hero.defense = 3;
        hero.mp = hero.maxMp = 9;
    }
    hero.bag.push_back({Kind::Food, 350, 2, "ración de viaje", '%'});
    hero.bag.push_back({Kind::Potion, 18, 2, "poción curativa", '!'});
    message(hero, "Eres " + hero.name + ", " + hero.role + ".");
    message(hero, "Tu personaje y tu inventario son independientes.");
    int id = hero.id;
    players_.emplace(id, std::move(hero));
    if (connectedCount() >= kMinPlayers) started_ = true;
    announcement_ = "Se ha unido " + players_.at(id).name +
        ". Participantes: " + std::to_string(connectedCount()) +
        "/" + std::to_string(kMaxPlayers) + ".";
    reason = "Personaje creado.";
    return id;
}
void World::disconnect(int id) {
    Player* hero = find(id);
    if (!hero) return;
    hero->connected = false;
    orders_.erase(id);
    announcement_ = hero->name + " se ha desconectado.";
    if (started_ && waitingCount() == 0 && participantsRequired() > 0)
        advanceRound();
}
} // namespace nhb
