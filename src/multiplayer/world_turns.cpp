#include "nhb/world.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cmath>
#include <string>
#include <vector>

namespace nhb {
namespace {
int distance(Pos a, Pos b) {
    return std::max(std::abs(a.x - b.x), std::abs(a.y - b.y));
}
int sign(int value) { return (value > 0) - (value < 0); }
bool actionKey(char key) {
    return std::string("hjklyubn12346789.g,qemwWrfz<>o").find(key)
           != std::string::npos;
}
} // namespace

Outcome World::submit(int id, char key) {
    Player* hero = find(id);
    if (!hero || !hero->connected) return {false, false, "Jugador desconectado."};
    if (!started_) return {false, false, "Se necesitan al menos dos jugadores para comenzar."};
    if (finished_) return {false, false, "La aventura ya terminó."};
    if (!hero->alive || hero->escaped) return {false, false, "Tu personaje ya no puede actuar."};
    if (orders_.count(id)) return {false, false, "Ya enviaste tu acción para esta ronda."};
    if (!actionKey(key)) return {false, false, "Comando desconocido. Consulta la ayuda."};
    orders_[id] = key;
    if (waitingCount() > 0)
        return {true, false, "Acción registrada. Esperando a los demás jugadores."};
    advanceRound();
    return {true, true, "Ronda resuelta."};
}

void World::gainExperience(Player& hero, int amount) {
    hero.experience += amount;
    while (hero.experience >= hero.level * hero.level * 12) {
        ++hero.level;
        hero.maxHp += 5;
        hero.hp = std::min(hero.maxHp, hero.hp + 10);
        hero.maxMp += hero.role == "maga" ? 4 : 2;
        hero.mp = hero.maxMp;
        ++hero.attack;
        message(hero, "¡Subes al nivel " + std::to_string(hero.level) + "!");
    }
}

void World::hitMonster(Player& hero, Monster& enemy, int extra) {
    if (enemy.hp <= 0) return;
    int chance = std::clamp(75 - enemy.defense * 5, 30, 95);
    if (dice(1, 100) > chance) {
        message(hero, "Tu ataque contra " + enemy.name + " falla.");
        return;
    }
    int damage = std::max(1, dice(1, 5) + hero.attack +
                         hero.weapon + extra - enemy.defense / 2);
    enemy.hp -= damage;
    message(hero, "Golpeas al " + enemy.name + " (-" +
            std::to_string(damage) + " PV).");
    if (enemy.hp <= 0) {
        message(hero, "Has derrotado al " + enemy.name + ".");
        gainExperience(hero, enemy.xp);
        hero.gold += dice(1, 4);
    }
}

bool World::move(Player& hero, int dx, int dy) {
    Pos target{hero.pos.x + dx, hero.pos.y + dy};
    if (!inside(target)) {
        message(hero, "No puedes salir del mapa.");
        return false;
    }
    for (Monster& enemy : level(hero.depth).monsters) {
        if (enemy.hp > 0 && enemy.pos == target) {
            hitMonster(hero, enemy, 0);
            return true;
        }
    }
    if (occupiedByHero(hero.depth, target, hero.id)) {
        message(hero, "Otro aventurero ocupa esa casilla.");
        return false;
    }
    char tile = level(hero.depth).tiles[target.y][target.x];
    if (tile == '+') {
        message(hero, "Una puerta bloquea tu paso. Pulsa o para abrirla.");
        return false;
    }
    if (!traversable(hero.depth, target)) {
        message(hero, "Una pared bloquea tu paso.");
        return false;
    }
    hero.pos = target;
    return true;
}

bool World::collect(Player& hero) {
    auto& loot = level(hero.depth).loot;
    for (std::size_t i = 0; i < loot.size(); ++i) {
        if (loot[i].pos != hero.pos) continue;
        Item item = loot[i].item;
        if (item.kind == Kind::Amulet) {
            hero.hasAmulet = true;
            message(hero, "¡Recoges el Amuleto de Bald! Regresa arriba.");
        } else if (item.kind == Kind::Arrows) {
            hero.arrows += item.count;
            message(hero, "Recoges " + std::to_string(item.count) + " flechas.");
        } else {
            if (hero.bag.size() >= 22) {
                message(hero, "Tu mochila está llena.");
                return false;
            }
            hero.bag.push_back(item);
            message(hero, "Recoges " + item.name + ".");
        }
        loot.erase(loot.begin() + static_cast<std::ptrdiff_t>(i));
        return true;
    }
    message(hero, "No hay objetos en el suelo.");
    return false;
}

bool World::consume(Player& hero, Kind kind) {
    auto it = std::find_if(hero.bag.begin(), hero.bag.end(),
        [kind](const Item& item) { return item.kind == kind; });
    if (it == hero.bag.end()) {
        message(hero, "No llevas ese tipo de objeto.");
        return false;
    }
    if (kind == Kind::Food) {
        hero.hunger = std::min(1300, hero.hunger + it->power);
        message(hero, "Comes " + it->name + ". Recuperas fuerzas.");
    } else if (kind == Kind::Potion) {
        hero.hp = std::min(hero.maxHp, hero.hp + it->power);
        hero.poison = 0;
        message(hero, "Bebes una poción curativa.");
    } else if (kind == Kind::Mana) {
        hero.mp = std::min(hero.maxMp, hero.mp + it->power);
        message(hero, "Recuperas maná.");
    } else if (kind == Kind::Scroll) {
        for (int y = 0; y < kHeight; ++y)
            for (int x = 0; x < kWidth; ++x)
                if (level(hero.depth).tiles[y][x] != ' ')
                    hero.discovered[hero.depth - 1][y][x] = true;
        message(hero, "El mapa de la planta aparece en tu memoria.");
    } else return false;
    if (--it->count <= 0) hero.bag.erase(it);
    return true;
}

bool World::equip(Player& hero, Kind kind) {
    for (const Item& item : hero.bag) {
        if (item.kind != kind) continue;
        if (kind == Kind::Sword) {
            hero.weapon = item.power;
            message(hero, "Empuñas " + item.name + ".");
        } else if (kind == Kind::Armor) {
            hero.armor = item.power;
            message(hero, "Te equipas " + item.name + ".");
        }
        return true;
    }
    message(hero, "No tienes el equipo apropiado.");
    return false;
}

bool World::cast(Player& hero) {
    if (hero.mp < 5) {
        message(hero, "Necesitas al menos 5 puntos de maná.");
        return false;
    }
    hero.mp -= 5;
    Monster* target = nullptr;
    int nearest = 7;
    for (Monster& enemy : level(hero.depth).monsters) {
        int dist = distance(hero.pos, enemy.pos);
        if (enemy.hp > 0 && dist < nearest &&
            sees(hero.depth, hero.pos, enemy.pos)) {
            nearest = dist;
            target = &enemy;
        }
    }
    if (!target) {
        hero.hp = std::min(hero.maxHp, hero.hp + 6 + hero.level);
        message(hero, "Sin enemigos a la vista, concentras magia curativa.");
    } else {
        hitMonster(hero, *target, 6 + hero.level);
        message(hero, "Liberas una descarga arcana.");
    }
    return true;
}

bool World::shoot(Player& hero) {
    if (hero.arrows < 1) {
        message(hero, "Te quedaste sin flechas.");
        return false;
    }
    Monster* target = nullptr;
    int nearest = 9;
    for (Monster& enemy : level(hero.depth).monsters) {
        int dist = distance(hero.pos, enemy.pos);
        if (enemy.hp > 0 && dist < nearest &&
            sees(hero.depth, hero.pos, enemy.pos)) {
            nearest = dist;
            target = &enemy;
        }
    }
    if (!target) {
        message(hero, "No ves ningún blanco para disparar.");
        return false;
    }
    --hero.arrows;
    hitMonster(hero, *target, 3);
    return true;
}

bool World::descend(Player& hero, bool down) {
    char tile = level(hero.depth).tiles[hero.pos.y][hero.pos.x];
    if (down) {
        if (tile != '>' || hero.depth >= kLevels) {
            message(hero, "No hay escaleras hacia abajo aquí.");
            return false;
        }
        int nextDepth = hero.depth + 1;
        generate(nextDepth);
        Pos arrival = level(nextDepth).up;
        if (occupiedByHero(nextDepth, arrival))
            arrival = openSpot(nextDepth, false);
        hero.depth = nextDepth;
        hero.pos = arrival;
        message(hero, "Bajas a la profundidad " + std::to_string(nextDepth) + ".");
        return true;
    }
    if (tile != '<') {
        message(hero, "No hay escaleras hacia arriba aquí.");
        return false;
    }
    if (hero.depth == 1) {
        if (hero.hasAmulet) {
            hero.escaped = true;
            announcement_ = "¡" + hero.name + " ha escapado con el Amuleto de Bald!";
            finished_ = true;
        } else message(hero, "No puedes abandonar sin el Amuleto de Bald.");
        return hero.escaped;
    }
    int nextDepth = hero.depth - 1;
    Pos arrival = level(nextDepth).down;
    if (occupiedByHero(nextDepth, arrival))
        arrival = openSpot(nextDepth, false);
    hero.depth = nextDepth;
    hero.pos = arrival;
    message(hero, "Subes a la profundidad " + std::to_string(nextDepth) + ".");
    return true;
}

bool World::perform(Player& hero, char key) {
    switch (key) {
        case 'h': case '4': return move(hero, -1, 0);
        case 'j': case '2': return move(hero, 0, 1);
        case 'k': case '8': return move(hero, 0, -1);
        case 'l': case '6': return move(hero, 1, 0);
        case 'y': case '7': return move(hero, -1, -1);
        case 'u': case '9': return move(hero, 1, -1);
        case 'b': case '1': return move(hero, -1, 1);
        case 'n': case '3': return move(hero, 1, 1);
        case '.': return true;
        case 'g': case ',': return collect(hero);
        case 'e': return consume(hero, Kind::Food);
        case 'q': return consume(hero, Kind::Potion);
        case 'm': return consume(hero, Kind::Mana);
        case 'r': return consume(hero, Kind::Scroll);
        case 'w': return equip(hero, Kind::Sword);
        case 'W': return equip(hero, Kind::Armor);
        case 'f': return shoot(hero);
        case 'z': return cast(hero);
        case '<': return descend(hero, false);
        case '>': return descend(hero, true);
        case 'o': {
            const std::array<Pos, 8> offsets{{
                {1,0}, {-1,0}, {0,1}, {0,-1},
                {1,1}, {1,-1}, {-1,1}, {-1,-1}
            }};
            for (Pos dir : offsets) {
                Pos p{hero.pos.x + dir.x, hero.pos.y + dir.y};
                if (inside(p) && level(hero.depth).tiles[p.y][p.x] == '+') {
                    level(hero.depth).tiles[p.y][p.x] = '#';
                    message(hero, "Abres una puerta.");
                    return true;
                }
            }
            message(hero, "No hay puertas cerradas cerca.");
            return false;
        }
        default: return false;
    }
}

void World::monsterPhase() {
    for (int depth = 1; depth <= kLevels; ++depth) {
        if (!level(depth).generated) continue;
        Level& l = level(depth);
        for (std::size_t i = 0; i < l.monsters.size(); ++i) {
            Monster& m = l.monsters[i];
            if (m.hp <= 0) continue;
            Player* target = nullptr;
            int nearest = 9;
            for (auto& [_, hero] : players_) {
                int dist = distance(hero.pos, m.pos);
                if (hero.alive && !hero.escaped && hero.depth == depth &&
                    dist < nearest && sees(depth, m.pos, hero.pos)) {
                    target = &hero;
                    nearest = dist;
                }
            }
            if (!target) continue;
            if (nearest <= 1) {
                if (dice(1, 100) <= 78) {
                    int harm = std::max(1, dice(1, m.damage) -
                                         (target->defense + target->armor) / 3);
                    target->hp -= harm;
                    message(*target, "El " + m.name + " te hiere (-" +
                        std::to_string(harm) + " PV).");
                    if (target->hp <= 0) {
                        target->alive = false;
                        announcement_ = target->name + " ha muerto en la mazmorra.";
                    }
                }
                continue;
            }
            Pos next{m.pos.x + sign(target->pos.x - m.pos.x),
                     m.pos.y + sign(target->pos.y - m.pos.y)};
            if (traversable(depth, next) &&
                !occupiedByHero(depth, next) && !occupiedByMonster(depth, next))
                m.pos = next;
        }
    }
}

void World::advanceRound() {
    // Todas las órdenes corresponden al mismo estado de inicio de ronda.
    // Un orden determinista por ID resuelve contiendas por objetos/casillas.
    const auto queued = orders_;
    for (auto [id, key] : queued) {
        Player* hero = find(id);
        if (hero && hero->connected && hero->alive && !hero->escaped)
            perform(*hero, key);
        if (finished_) break;
    }
    orders_.clear();
    if (!finished_) {
        monsterPhase();
        for (auto& [_, hero] : players_) {
            if (!hero.alive || hero.escaped) continue;
            hero.hunger = std::max(0, hero.hunger - 1);
            if (hero.poison > 0) {
                --hero.poison;
                if (round_ % 3 == 0) --hero.hp;
            }
            if (hero.hunger == 0 && round_ % 2 == 0) --hero.hp;
            if (hero.hp <= 0) {
                hero.alive = false;
                announcement_ = hero.name + " ha caído.";
            }
            if (round_ % 7 == 0) hero.mp = std::min(hero.maxMp, hero.mp + 1);
            if (round_ % 18 == 0 && hero.hunger > 300)
                hero.hp = std::min(hero.maxHp, hero.hp + 1);
        }
        bool survivors = false;
        for (const auto& [_, hero] : players_)
            if (hero.alive && !hero.escaped) survivors = true;
        if (!survivors) {
            finished_ = true;
            announcement_ = "Ningún héroe sobrevivió a la expedición.";
        }
    }
    ++round_;
}

} // namespace nhb
