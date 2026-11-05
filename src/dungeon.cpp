#include "nhb/game.hpp"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <utility>

namespace nhb {
namespace {

struct Room {
    int x, y, width, height;
    Point center() const { return {x + width / 2, y + height / 2}; }
};

bool separated(const Room& a, const Room& b) {
    return a.x + a.width + 1 < b.x ||
           b.x + b.width + 1 < a.x ||
           a.y + a.height + 1 < b.y ||
           b.y + b.height + 1 < a.y;
}

Item createTreasure(int depth, int roll) {
    switch (roll) {
        case 0:
        case 1: return {ItemKind::Food, "ración de viaje", '%', 310, 1, true};
        case 2: return {ItemKind::Healing, "poción curativa", '!', 12 + depth * 2, 1, true};
        case 3: return {ItemKind::Mana, "poción de maná", '!', 10 + depth, 1, true};
        case 4: return {ItemKind::MapScroll, "pergamino cartográfico", '?', 0, 1, true};
        case 5: return {ItemKind::TeleportScroll, "pergamino de teletransporte", '?', 0, 1, true};
        case 6: return {ItemKind::IdentifyScroll, "pergamino de conocimiento", '?', 0, 1, true};
        case 7: return {ItemKind::Arrows, "flechas", ')', 0, 3 + depth / 2, true};
        case 8: return {ItemKind::Weapon, depth < 4 ? "espada corta" : "espada rúnica",
                         ')', depth < 4 ? 3 : 4 + depth / 3, 1, true};
        case 9: return {ItemKind::Armor, depth < 5 ? "coraza de cuero" : "coraza de acero",
                         '[', depth < 5 ? 2 : 3 + depth / 4, 1, true};
        default: return {ItemKind::Gold, "monedas de oro", '$', 0, 8 + depth * 4, true};
    }
}

Monster createMonster(int depth, int roll) {
    if (depth >= 9 && roll >= 7)
        return {{}, "dragón antiguo", 'D', 36 + depth * 2, 36 + depth * 2, 11, 6, 65, false};
    if (depth >= 7 && roll >= 5)
        return {{}, "demonio de las simas", '&', 26 + depth, 26 + depth, 9, 5, 43, false};
    if (depth >= 5 && roll >= 5)
        return {{}, "trol", 'T', 20 + depth, 20 + depth, 8, 4, 32, false};
    if (depth >= 4 && roll >= 3)
        return {{}, "orco", 'o', 13 + depth, 13 + depth, 6, 3, 19, false};
    if (depth >= 3 && roll >= 3)
        return {{}, "esqueleto", 's', 10 + depth, 10 + depth, 5, 2, 12, false};
    if (depth >= 2 && roll >= 2)
        return {{}, "kobold", 'k', 7 + depth, 7 + depth, 4, 2, 8, false};
    if (roll >= 3)
        return {{}, "duende", 'g', 7 + depth, 7 + depth, 3, 1, 6, false};
    return {{}, "rata gigante", 'r', 4 + depth, 4 + depth, 2 + depth / 4, 1, 4, false};
}

} // namespace

Point Game::randomOpenTile(Floor& f, bool awayFromStairs) {
    for (int attempt = 0; attempt < 1200; ++attempt) {
        Point p{randomInt(2, MAP_WIDTH - 3), randomInt(2, MAP_HEIGHT - 3)};
        if (f.terrain[p.y][p.x] != '.') continue;
        if (awayFromStairs &&
            (std::abs(p.x - f.up.x) + std::abs(p.y - f.up.y) < 5 ||
             p == f.down)) continue;
        bool inUse = false;
        for (const auto& monster : f.monsters)
            if (monster.hp > 0 && monster.pos == p) inUse = true;
        if (!inUse) return p;
    }
    // Cada planta contiene al menos dos salas transitables.
    return f.up;
}

void Game::generateFloor(int index) {
    Floor& f = floors_.at(static_cast<std::size_t>(index - 1));
    if (f.ready) return;
    for (auto& row : f.terrain) row.assign(MAP_WIDTH, ' ');
    for (auto& row : f.explored) row.fill(false);
    f.monsters.clear();
    f.objects.clear();
    f.traps.clear();

    std::vector<Room> rooms;
    for (int attempt = 0; attempt < 280 && rooms.size() < 13; ++attempt) {
        Room candidate{
            randomInt(2, MAP_WIDTH - 16),
            randomInt(2, MAP_HEIGHT - 9),
            randomInt(6, 13),
            randomInt(4, 7)
        };
        if (candidate.x + candidate.width >= MAP_WIDTH - 2 ||
            candidate.y + candidate.height >= MAP_HEIGHT - 2) continue;
        bool free = true;
        for (const Room& room : rooms)
            if (!separated(candidate, room)) { free = false; break; }
        if (!free) continue;

        rooms.push_back(candidate);
        for (int y = candidate.y; y < candidate.y + candidate.height; ++y) {
            for (int x = candidate.x; x < candidate.x + candidate.width; ++x) {
                const bool topOrBottom =
                    y == candidate.y || y == candidate.y + candidate.height - 1;
                const bool leftOrRight =
                    x == candidate.x || x == candidate.x + candidate.width - 1;
                f.terrain[y][x] = topOrBottom ? '-' : (leftOrRight ? '|' : '.');
            }
        }
    }

    // Respaldo extremadamente infrecuente cuando la elección aleatoria no da salas.
    if (rooms.size() < 2) {
        f.terrain = {};
        for (auto& row : f.terrain) row.assign(MAP_WIDTH, ' ');
        rooms = {{3, 3, 12, 7}, {MAP_WIDTH - 18, MAP_HEIGHT - 10, 13, 7}};
        for (const Room& room : rooms)
            for (int y = room.y; y < room.y + room.height; ++y)
                for (int x = room.x; x < room.x + room.width; ++x)
                    f.terrain[y][x] =
                        (y == room.y || y == room.y + room.height - 1) ? '-' :
                        (x == room.x || x == room.x + room.width - 1) ? '|' : '.';
    }

    const auto carve = [&](int x, int y) {
        if (!inside(x, y)) return;
        char& tile = f.terrain[y][x];
        if (tile == '|' || tile == '-') tile = '+';
        else if (tile == ' ') tile = '#';
    };
    const auto corridor = [&](Point a, Point b) {
        const bool horizontalFirst = randomInt(0, 1) != 0;
        Point p = a;
        auto alongX = [&]() {
            while (p.x != b.x) {
                p.x += (b.x > p.x) ? 1 : -1;
                carve(p.x, p.y);
            }
        };
        auto alongY = [&]() {
            while (p.y != b.y) {
                p.y += (b.y > p.y) ? 1 : -1;
                carve(p.x, p.y);
            }
        };
        if (horizontalFirst) { alongX(); alongY(); }
        else { alongY(); alongX(); }
    };

    for (std::size_t i = 1; i < rooms.size(); ++i)
        corridor(rooms[i - 1].center(), rooms[i].center());

    f.up = rooms.front().center();
    f.down = rooms.back().center();
    f.terrain[f.up.y][f.up.x] = '<';
    if (index < FLOOR_COUNT)
        f.terrain[f.down.y][f.down.x] = '>';

    const int totalMonsters = 5 + index * 2;
    for (int i = 0; i < totalMonsters; ++i) {
        Monster monster = createMonster(index, randomInt(0, 9));
        monster.pos = randomOpenTile(f);
        if (monster.pos == f.up) continue;
        f.monsters.push_back(std::move(monster));
    }

    for (int i = 0; i < 6 + index; ++i) {
        GroundItem object{randomOpenTile(f), createTreasure(index, randomInt(0, 10))};
        if (object.pos != f.up) f.objects.push_back(std::move(object));
    }

    for (int i = 0; i < 2 + index / 2; ++i) {
        Point p = randomOpenTile(f);
        if (p != f.up)
            f.traps.push_back({p, randomInt(0, 2), false, false});
    }

    if (index == FLOOR_COUNT) {
        Point p = randomOpenTile(f);
        if (p == f.up) p = f.down;
        f.objects.push_back({p, {ItemKind::Amulet, "Amuleto de Bald", '"', 0, 1, true}});
    }
    f.ready = true;
}

} // namespace nhb
