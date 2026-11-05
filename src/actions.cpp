#include "nhb/game.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>

namespace nhb {

void Game::attack(int monsterIndex, int bonus) {
    Monster& enemy = floor().monsters.at(static_cast<std::size_t>(monsterIndex));
    if (enemy.hp <= 0) return;
    const int accuracy = std::clamp(
        67 + hero_.agility * 3 - enemy.defense * 5 + (bonus > 0 ? 5 : 0), 25, 96);
    if (randomInt(1, 100) > accuracy) {
        say("Fallaste tu ataque contra " + enemy.name + ".");
        advanceTurn();
        return;
    }

    const int damage = std::max(
        1, randomInt(1, 4) + hero_.strength / 2 + weaponValue() +
           bonus - enemy.defense / 2);
    enemy.hp -= damage;
    say("Golpeas a " + enemy.name + " (-" + std::to_string(damage) + " PV).");
    if (enemy.hp <= 0) {
        hero_.xp += enemy.xp;
        say("Has derrotado a " + enemy.name +
            " (+" + std::to_string(enemy.xp) + " EXP).");
        if (randomInt(1, 100) <= 16) {
            int coins = randomInt(3, 9) + depth_ * 2;
            floor().objects.push_back({
                enemy.pos, {ItemKind::Gold, "monedas de oro", '$', 0, coins, true}
            });
        }
        levelUp();
    }
    advanceTurn();
}

void Game::walk(int dx, int dy) {
    const int x = hero_.pos.x + dx;
    const int y = hero_.pos.y + dy;
    if (!inside(x, y)) return;
    for (int i = 0; i < static_cast<int>(floor().monsters.size()); ++i) {
        const Monster& enemy = floor().monsters[i];
        if (enemy.hp > 0 && enemy.pos.x == x && enemy.pos.y == y) {
            attack(i);
            return;
        }
    }
    if (floor().terrain[y][x] == '+') {
        say("Hay una puerta cerrada. Pulsa o para abrirla.");
        return;
    }
    if (!passable(floor(), x, y)) {
        say("Una pared bloquea tu paso.");
        return;
    }
    hero_.pos = {x, y};
    activateTrap();
    if (!playing_) return;
    for (const auto& object : floor().objects) {
        if (object.pos == hero_.pos) {
            say("En el suelo: " + object.item.name + ". Pulsa , para recoger.");
            break;
        }
    }
    advanceTurn();
}

void Game::activateTrap() {
    Floor& f = floor();
    for (auto& trap : f.traps) {
        if (trap.spent || !(trap.pos == hero_.pos)) continue;
        trap.spent = true;
        trap.revealed = true;
        if (trap.type == 0) {
            int damage = randomInt(3, 8) + depth_ / 2;
            hero_.hp -= damage;
            say("¡Una trampa de pinchos! -" + std::to_string(damage) + " PV.");
        } else if (trap.type == 1) {
            int damage = randomInt(1, 4);
            hero_.hp -= damage;
            hero_.poison = std::max(hero_.poison, 9 + depth_);
            say("¡Un dardo envenenado te atraviesa! Estás envenenado.");
        } else {
            hero_.pos = randomOpenTile(f, false);
            say("¡Un sello mágico te teletransporta!");
        }
        if (hero_.hp <= 0) {
            endGame("Una trampa ha acabado con tu aventura.", false);
        }
        return;
    }
}

void Game::pickUp() {
    Floor& f = floor();
    bool picked = false;
    for (std::size_t i = 0; i < f.objects.size();) {
        GroundItem& object = f.objects[i];
        if (!(object.pos == hero_.pos)) { ++i; continue; }
        const Item item = object.item;
        if (item.kind == ItemKind::Gold) {
            hero_.gold += item.amount;
            say("Recoges " + std::to_string(item.amount) + " monedas de oro.");
        } else if (item.kind == ItemKind::Arrows) {
            hero_.arrows += item.amount;
            say("Guardas " + std::to_string(item.amount) + " flechas.");
        } else if (item.kind == ItemKind::Amulet) {
            hasAmulet_ = true;
            say("¡TIENES EL AMULETO DE BALD! Regresa a la superficie.");
        } else {
            int stack = -1;
            if (item.kind != ItemKind::Weapon && item.kind != ItemKind::Armor) {
                for (int j = 0; j < static_cast<int>(hero_.pack.size()); ++j) {
                    if (hero_.pack[j].kind == item.kind &&
                        hero_.pack[j].name == item.name &&
                        hero_.pack[j].power == item.power) {
                        stack = j;
                        break;
                    }
                }
            }
            if (stack >= 0) {
                hero_.pack[stack].amount += item.amount;
            } else if (hero_.pack.size() < PACK_LIMIT) {
                hero_.pack.push_back(item);
            } else {
                say("Tu mochila está llena. Suelta algo antes.");
                ++i;
                continue;
            }
            say("Recoges: " + item.name + ".");
        }
        f.objects.erase(f.objects.begin() + static_cast<std::ptrdiff_t>(i));
        picked = true;
    }
    if (picked) advanceTurn();
    else say("No hay nada que puedas recoger aquí.");
}

void Game::consume(int index) {
    if (index < 0 || index >= static_cast<int>(hero_.pack.size())) return;
    if (--hero_.pack[index].amount > 0) return;
    hero_.pack.erase(hero_.pack.begin() + index);
    if (hero_.weapon == index) hero_.weapon = -1;
    else if (hero_.weapon > index) --hero_.weapon;
    if (hero_.armor == index) hero_.armor = -1;
    else if (hero_.armor > index) --hero_.armor;
}

void Game::eat() {
    int index = chooseItem("¿Qué quieres comer?", ItemKind::Food);
    if (index < 0) return;
    hero_.hunger = std::min(1600, hero_.hunger + hero_.pack[index].power);
    say("Comes " + hero_.pack[index].name + ". Recuperas fuerzas.");
    consume(index);
    advanceTurn();
}

void Game::drink() {
    int index = chooseItem("¿Qué poción quieres beber?");
    if (index < 0) return;
    ItemKind kind = hero_.pack[index].kind;
    if (kind == ItemKind::Healing) {
        int before = hero_.hp;
        hero_.hp = std::min(hero_.maxHp, hero_.hp + hero_.pack[index].power);
        hero_.poison = 0;
        say("La poción te devuelve " + std::to_string(hero_.hp - before) +
            " PV y limpia el veneno.");
    } else if (kind == ItemKind::Mana) {
        int before = hero_.mp;
        hero_.mp = std::min(hero_.maxMp, hero_.mp + hero_.pack[index].power);
        say("Recuperas " + std::to_string(hero_.mp - before) + " PM.");
    } else {
        say("Eso no es una poción.");
        return;
    }
    consume(index);
    advanceTurn();
}

void Game::readScroll() {
    int index = chooseItem("¿Qué pergamino deseas leer?");
    if (index < 0) return;
    ItemKind kind = hero_.pack[index].kind;
    if (kind == ItemKind::MapScroll) {
        for (int y = 0; y < MAP_HEIGHT; ++y)
            for (int x = 0; x < MAP_WIDTH; ++x)
                if (floor().terrain[y][x] != ' ')
                    floor().explored[y][x] = true;
        say("El plano de esta planta aparece ante tus ojos.");
    } else if (kind == ItemKind::TeleportScroll) {
        hero_.pos = randomOpenTile(floor(), false);
        say("El pergamino te transporta a otra sala.");
    } else if (kind == ItemKind::IdentifyScroll) {
        for (auto& item : hero_.pack) item.identified = true;
        for (auto& trap : floor().traps) trap.revealed = true;
        say("Comprendes tus pertenencias y detectas trampas ocultas.");
    } else {
        say("Ese objeto no es un pergamino.");
        return;
    }
    consume(index);
    advanceTurn();
}

void Game::wield() {
    int index = chooseItem("¿Qué arma quieres empuñar?", ItemKind::Weapon);
    if (index < 0) return;
    if (hero_.weapon == index) { say("Ya empuñas esa arma."); return; }
    hero_.weapon = index;
    say("Empuñas " + hero_.pack[index].name + ".");
    advanceTurn();
}

void Game::wear() {
    int index = chooseItem("¿Qué armadura quieres ponerte?", ItemKind::Armor);
    if (index < 0) return;
    if (hero_.armor == index) { say("Ya llevas esa armadura."); return; }
    hero_.armor = index;
    say("Te colocas " + hero_.pack[index].name + ".");
    advanceTurn();
}

void Game::takeOff() {
    if (hero_.armor < 0) { say("No llevas armadura."); return; }
    say("Te quitas " + hero_.pack[hero_.armor].name + ".");
    hero_.armor = -1;
    advanceTurn();
}

void Game::drop() {
    int index = chooseItem("¿Qué objeto quieres soltar?");
    if (index < 0) return;
    Item item = hero_.pack[index];
    if (item.amount > 1) {
        item.amount = 1;
        --hero_.pack[index].amount;
    } else {
        if (hero_.weapon == index) hero_.weapon = -1;
        else if (hero_.weapon > index) --hero_.weapon;
        if (hero_.armor == index) hero_.armor = -1;
        else if (hero_.armor > index) --hero_.armor;
        hero_.pack.erase(hero_.pack.begin() + index);
    }
    floor().objects.push_back({hero_.pos, item});
    say("Dejas en el suelo: " + item.name + ".");
    advanceTurn();
}

void Game::openDoor() {
    int dx = 0, dy = 0;
    if (!askDirection(dx, dy)) return;
    Point target{hero_.pos.x + dx, hero_.pos.y + dy};
    if (!inside(target.x, target.y) || floor().terrain[target.y][target.x] != '+') {
        say("No hay ninguna puerta cerrada en esa dirección.");
        return;
    }
    floor().terrain[target.y][target.x] = '#';
    say("Abres la puerta.");
    advanceTurn();
}

void Game::shoot() {
    if (hero_.arrows <= 0) { say("No te quedan flechas."); return; }
    int dx = 0, dy = 0;
    if (!askDirection(dx, dy)) return;
    --hero_.arrows;
    Point ray = hero_.pos;
    for (int step = 0; step < 9; ++step) {
        ray.x += dx;
        ray.y += dy;
        if (!passable(floor(), ray.x, ray.y)) break;
        for (int i = 0; i < static_cast<int>(floor().monsters.size()); ++i) {
            if (floor().monsters[i].hp > 0 &&
                floor().monsters[i].pos == ray) {
                say("Disparas una flecha.");
                attack(i, 2 + hero_.agility / 3);
                return;
            }
        }
    }
    say("La flecha se pierde en la oscuridad.");
    advanceTurn();
}

void Game::spell() {
    terminal::clear();
    std::cout <<
        "GRIMORIO - HECHIZOS\n\n"
        " [1] Proyectil arcano   - 4 PM, objetivo en línea recta.\n"
        " [2] Sanación           - 6 PM, recuperar puntos de vida.\n"
        " [3] Explosión mística  - 8 PM, enemigos próximos.\n\n"
        " Maná actual: " << hero_.mp <<
        "\n\n Elige 1-3 o ESC para cancelar: " << std::flush;
    int key = terminal::readKey();
    int cost = key == '1' ? 4 : key == '2' ? 6 : key == '3' ? 8 : 0;
    if (cost == 0) return;
    if (hero_.mp < cost) { say("No tienes suficiente maná."); return; }

    if (key == '1') {
        int dx = 0, dy = 0;
        if (!askDirection(dx, dy)) return;
        hero_.mp -= cost;
        Point ray = hero_.pos;
        for (int step = 0; step < 8; ++step) {
            ray.x += dx;
            ray.y += dy;
            if (!passable(floor(), ray.x, ray.y)) break;
            bool hit = false;
            for (auto& enemy : floor().monsters) {
                if (enemy.hp <= 0 || !(enemy.pos == ray)) continue;
                int damage = randomInt(5, 10) + hero_.intellect;
                enemy.hp -= damage;
                say("¡Proyectil arcano contra " + enemy.name + "! -" +
                    std::to_string(damage) + " PV.");
                if (enemy.hp <= 0) {
                    hero_.xp += enemy.xp;
                    say("Has abatido a " + enemy.name + " mediante magia.");
                    levelUp();
                }
                hit = true;
                break;
            }
            if (hit) { advanceTurn(); return; }
        }
        say("El proyectil se desvanece sin encontrar blanco.");
    } else if (key == '2') {
        hero_.mp -= cost;
        int healing = randomInt(8, 14) + hero_.intellect;
        int before = hero_.hp;
        hero_.hp = std::min(hero_.maxHp, hero_.hp + healing);
        say("La magia cura " + std::to_string(hero_.hp - before) + " PV.");
    } else {
        hero_.mp -= cost;
        int hits = 0;
        for (auto& enemy : floor().monsters) {
            if (enemy.hp <= 0) continue;
            int dist = std::max(std::abs(enemy.pos.x - hero_.pos.x),
                                std::abs(enemy.pos.y - hero_.pos.y));
            if (dist > 2 || !lineOfSight(hero_.pos, enemy.pos)) continue;
            int damage = randomInt(5, 10) + hero_.intellect / 2;
            enemy.hp -= damage;
            ++hits;
            if (enemy.hp <= 0) hero_.xp += enemy.xp;
        }
        say("La explosión mística alcanza " + std::to_string(hits) + " enemigos.");
        levelUp();
    }
    advanceTurn();
}

void Game::inspect() {
    int dx = 0, dy = 0;
    if (!askDirection(dx, dy)) return;
    Point p{hero_.pos.x + dx, hero_.pos.y + dy};
    if (!inside(p.x, p.y) || !visible_[p.y][p.x]) {
        say("No distingues qué hay en ese lugar.");
        return;
    }
    for (const auto& enemy : floor().monsters) {
        if (enemy.hp > 0 && enemy.pos == p) {
            say("Ves un " + enemy.name + " (PV " +
                std::to_string(enemy.hp) + "/" +
                std::to_string(enemy.maxHp) + ").");
            return;
        }
    }
    for (const auto& obj : floor().objects) {
        if (obj.pos == p) { say("Encuentras: " + obj.item.name + "."); return; }
    }
    for (const auto& trap : floor().traps) {
        if (trap.pos == p && trap.revealed && !trap.spent) {
            say("Hay una trampa activable en el suelo.");
            return;
        }
    }
    switch (floor().terrain[p.y][p.x]) {
        case '.': say("Suelo de piedra de una sala."); break;
        case '#': say("Un pasillo excavado en la roca."); break;
        case '|': case '-': say("Pared de piedra."); break;
        case '+': say("Una puerta cerrada."); break;
        case '<': say("Una escalera hacia arriba."); break;
        case '>': say("Una escalera hacia abajo."); break;
        default: say("Oscuridad y roca sólida.");
    }
}

void Game::changeFloor(bool down) {
    const char underfoot = floor().terrain[hero_.pos.y][hero_.pos.x];
    if (down) {
        if (underfoot != '>' || depth_ >= FLOOR_COUNT) {
            say("Aquí no hay una escalera que baje.");
            return;
        }
        ++depth_;
        generateFloor(depth_);
        hero_.pos = floor().up;
        say("Desciendes a la profundidad " + std::to_string(depth_) + ".");
    } else {
        if (underfoot != '<') {
            say("Aquí no hay una escalera que suba.");
            return;
        }
        if (depth_ == 1) {
            if (hasAmulet_) {
                endGame("Escapas del laberinto con el Amuleto de Bald.", true);
            } else {
                say("Debes encontrar el Amuleto de Bald antes de escapar.");
            }
            return;
        }
        --depth_;
        hero_.pos = floor().down;
        say("Asciendes a la profundidad " + std::to_string(depth_) + ".");
    }
    advanceTurn();
}

} // namespace nhb
