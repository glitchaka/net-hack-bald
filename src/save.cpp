#include "nhb/game.hpp"

#include <cstdio>
#include <fstream>
#include <iomanip>
#include <limits>
#include <string>
#include <utility>

namespace nhb {
namespace {

constexpr const char* SAVE_FILE = "partida.nhb";
constexpr const char* SAVE_VERSION = "NHB2";

void writeItem(std::ostream& out, const Item& item) {
    out << static_cast<int>(item.kind) << ' '
        << std::quoted(item.name) << ' '
        << static_cast<int>(static_cast<unsigned char>(item.glyph)) << ' '
        << item.power << ' ' << item.amount << ' ' << item.identified << '\n';
}

bool readItem(std::istream& in, Item& item) {
    int kind = -1, glyph = 0;
    if (!(in >> kind >> std::quoted(item.name) >> glyph
          >> item.power >> item.amount >> item.identified)) return false;
    if (kind < 0 || kind > static_cast<int>(ItemKind::Amulet) ||
        glyph < 32 || glyph > 126 || item.amount < 1 ||
        item.amount > 100000 || item.name.size() > 120) return false;
    item.kind = static_cast<ItemKind>(kind);
    item.glyph = static_cast<char>(glyph);
    return true;
}

bool readCount(std::istream& in, std::size_t& count, std::size_t limit) {
    if (!(in >> count)) return false;
    return count <= limit;
}

bool validPosition(Point p) {
    return p.x >= 0 && p.x < MAP_WIDTH && p.y >= 0 && p.y < MAP_HEIGHT;
}

} // namespace

bool Game::saveGame() const {
    std::ofstream out(SAVE_FILE, std::ios::binary | std::ios::trunc);
    if (!out) return false;
    out << SAVE_VERSION << '\n';
    out << depth_ << ' ' << turns_ << ' ' << hasAmulet_ << '\n';
    out << std::quoted(hero_.name) << ' ' << std::quoted(hero_.role) << '\n';
    out << hero_.pos.x << ' ' << hero_.pos.y << ' '
        << hero_.level << ' ' << hero_.xp << ' '
        << hero_.hp << ' ' << hero_.maxHp << ' '
        << hero_.mp << ' ' << hero_.maxMp << ' '
        << hero_.strength << ' ' << hero_.agility << ' '
        << hero_.intellect << ' ' << hero_.defense << ' '
        << hero_.hunger << ' ' << hero_.poison << ' '
        << hero_.arrows << ' ' << hero_.gold << ' '
        << hero_.weapon << ' ' << hero_.armor << '\n';
    out << hero_.pack.size() << '\n';
    for (const auto& item : hero_.pack) writeItem(out, item);

    for (const Floor& f : floors_) {
        out << f.ready << '\n';
        if (!f.ready) continue;
        out << f.up.x << ' ' << f.up.y << ' '
            << f.down.x << ' ' << f.down.y << '\n';
        for (const std::string& row : f.terrain)
            out << std::quoted(row) << '\n';
        for (const auto& row : f.explored) {
            for (bool explored : row) out << (explored ? '1' : '0');
            out << '\n';
        }
        out << f.monsters.size() << '\n';
        for (const auto& monster : f.monsters) {
            out << monster.pos.x << ' ' << monster.pos.y << ' '
                << std::quoted(monster.name) << ' '
                << static_cast<int>(static_cast<unsigned char>(monster.glyph)) << ' '
                << monster.hp << ' ' << monster.maxHp << ' '
                << monster.attack << ' ' << monster.defense << ' '
                << monster.xp << ' ' << monster.awake << '\n';
        }
        out << f.objects.size() << '\n';
        for (const auto& object : f.objects) {
            out << object.pos.x << ' ' << object.pos.y << ' ';
            writeItem(out, object.item);
        }
        out << f.traps.size() << '\n';
        for (const auto& trap : f.traps) {
            out << trap.pos.x << ' ' << trap.pos.y << ' '
                << trap.type << ' ' << trap.revealed << ' ' << trap.spent << '\n';
        }
    }
    out.flush();
    return out.good();
}

bool Game::loadGame() {
    std::ifstream in(SAVE_FILE, std::ios::binary);
    if (!in) return false;
    std::string version;
    if (!(in >> version) || version != SAVE_VERSION) return false;

    int depth = 0, turns = 0;
    bool amulet = false;
    if (!(in >> depth >> turns >> amulet) ||
        depth < 1 || depth > FLOOR_COUNT || turns < 0) return false;

    Hero loadedHero;
    if (!(in >> std::quoted(loadedHero.name) >>
          std::quoted(loadedHero.role))) return false;
    if (!(in >> loadedHero.pos.x >> loadedHero.pos.y
          >> loadedHero.level >> loadedHero.xp
          >> loadedHero.hp >> loadedHero.maxHp
          >> loadedHero.mp >> loadedHero.maxMp
          >> loadedHero.strength >> loadedHero.agility
          >> loadedHero.intellect >> loadedHero.defense
          >> loadedHero.hunger >> loadedHero.poison
          >> loadedHero.arrows >> loadedHero.gold
          >> loadedHero.weapon >> loadedHero.armor)) return false;

    if (loadedHero.name.size() > 120 || loadedHero.role.size() > 120 ||
        !validPosition(loadedHero.pos) ||
        loadedHero.level < 1 || loadedHero.level > 100 ||
        loadedHero.hp <= 0 || loadedHero.hp > loadedHero.maxHp ||
        loadedHero.maxHp > 10000 ||
        loadedHero.mp < 0 || loadedHero.mp > loadedHero.maxMp ||
        loadedHero.maxMp > 10000 || loadedHero.hunger < 0 ||
        loadedHero.poison < 0 || loadedHero.arrows < 0 ||
        loadedHero.gold < 0) return false;

    std::size_t count = 0;
    if (!readCount(in, count, PACK_LIMIT)) return false;
    for (std::size_t i = 0; i < count; ++i) {
        Item item;
        if (!readItem(in, item)) return false;
        loadedHero.pack.push_back(std::move(item));
    }
    if (loadedHero.weapon < -1 ||
        loadedHero.weapon >= static_cast<int>(loadedHero.pack.size()) ||
        loadedHero.armor < -1 ||
        loadedHero.armor >= static_cast<int>(loadedHero.pack.size()))
        return false;
    if (loadedHero.weapon >= 0 &&
        loadedHero.pack[loadedHero.weapon].kind != ItemKind::Weapon) return false;
    if (loadedHero.armor >= 0 &&
        loadedHero.pack[loadedHero.armor].kind != ItemKind::Armor) return false;

    std::array<Floor, FLOOR_COUNT> loadedFloors{};
    for (Floor& f : loadedFloors) {
        if (!(in >> f.ready)) return false;
        if (!f.ready) continue;
        if (!(in >> f.up.x >> f.up.y >> f.down.x >> f.down.y) ||
            !validPosition(f.up) || !validPosition(f.down)) return false;
        for (std::string& row : f.terrain) {
            if (!(in >> std::quoted(row)) || row.size() != MAP_WIDTH)
                return false;
            for (char tile : row) {
                if (std::string(" .#-|+<>").find(tile) == std::string::npos)
                    return false;
            }
        }
        for (auto& row : f.explored) {
            std::string bits;
            if (!(in >> bits) || bits.size() != MAP_WIDTH) return false;
            for (int x = 0; x < MAP_WIDTH; ++x) {
                if (bits[x] != '0' && bits[x] != '1') return false;
                row[x] = bits[x] == '1';
            }
        }

        if (!readCount(in, count, 500)) return false;
        for (std::size_t i = 0; i < count; ++i) {
            Monster enemy;
            int glyph = 0;
            if (!(in >> enemy.pos.x >> enemy.pos.y
                  >> std::quoted(enemy.name) >> glyph
                  >> enemy.hp >> enemy.maxHp >> enemy.attack
                  >> enemy.defense >> enemy.xp >> enemy.awake) ||
                !validPosition(enemy.pos) || enemy.name.size() > 120 ||
                glyph < 32 || glyph > 126 ||
                enemy.hp > enemy.maxHp || enemy.maxHp > 10000 ||
                enemy.attack < 1 || enemy.xp < 0) return false;
            enemy.glyph = static_cast<char>(glyph);
            f.monsters.push_back(std::move(enemy));
        }

        if (!readCount(in, count, 800)) return false;
        for (std::size_t i = 0; i < count; ++i) {
            GroundItem object;
            if (!(in >> object.pos.x >> object.pos.y) ||
                !validPosition(object.pos) || !readItem(in, object.item))
                return false;
            f.objects.push_back(std::move(object));
        }

        if (!readCount(in, count, 250)) return false;
        for (std::size_t i = 0; i < count; ++i) {
            Trap trap;
            if (!(in >> trap.pos.x >> trap.pos.y >> trap.type
                  >> trap.revealed >> trap.spent) ||
                !validPosition(trap.pos) || trap.type < 0 || trap.type > 2)
                return false;
            f.traps.push_back(trap);
        }
    }

    if (!loadedFloors[static_cast<std::size_t>(depth - 1)].ready ||
        !passable(loadedFloors[static_cast<std::size_t>(depth - 1)],
                  loadedHero.pos.x, loadedHero.pos.y))
        return false;

    hero_ = std::move(loadedHero);
    floors_ = std::move(loadedFloors);
    depth_ = depth;
    turns_ = turns;
    hasAmulet_ = amulet;
    playing_ = true;
    victory_ = false;
    messages_.clear();
    return true;
}

void Game::removeSave() const {
    std::remove(SAVE_FILE);
}

} // namespace nhb
