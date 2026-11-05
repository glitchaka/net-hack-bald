#include "nhb/world.hpp"

#include <fstream>
#include <iomanip>
#include <limits>
#include <string>
#include <utility>

namespace nhb {
namespace {
constexpr const char* kFormat = "NET-HACK-BALD-HEROES-2";

void itemOut(std::ostream& os, const Item& item) {
    os << static_cast<int>(item.kind) << ' ' << item.power << ' '
       << item.count << ' ' << static_cast<int>(item.symbol) << ' '
       << std::quoted(item.name) << '\n';
}
bool itemIn(std::istream& is, Item& item) {
    int kind = -1, symbol = 0;
    if (!(is >> kind >> item.power >> item.count >> symbol >>
          std::quoted(item.name))) return false;
    if (kind < 0 || kind > static_cast<int>(Kind::Amulet) ||
        item.count < 1 || item.count > 100000 ||
        symbol < 32 || symbol > 126 || item.name.size() > 150) return false;
    item.kind = static_cast<Kind>(kind);
    item.symbol = static_cast<char>(symbol);
    return true;
}
bool posOk(Pos pos) {
    return pos.x >= 0 && pos.x < kWidth && pos.y >= 0 && pos.y < kHeight;
}
bool boundedCount(std::istream& stream, std::size_t& value, std::size_t limit) {
    return (stream >> value) && value <= limit;
}
} // namespace

bool World::save(const std::string& filename) const {
    std::ofstream out(filename, std::ios::binary | std::ios::trunc);
    if (!out) return false;
    out << kFormat << '\n' << nextId_ << ' ' << round_ << ' '
        << started_ << ' ' << finished_ << ' '
        << std::quoted(announcement_) << '\n';
    out << players_.size() << '\n';
    for (const auto& [id, hero] : players_) {
        out << id << ' ' << std::quoted(hero.name) << ' '
            << std::quoted(hero.role) << ' '
            << hero.depth << ' ' << hero.pos.x << ' ' << hero.pos.y << ' '
            << hero.hp << ' ' << hero.maxHp << ' '
            << hero.mp << ' ' << hero.maxMp << ' '
            << hero.attack << ' ' << hero.defense << ' '
            << hero.level << ' ' << hero.experience << ' '
            << hero.hunger << ' ' << hero.poison << ' ' << hero.gold << ' '
            << hero.arrows << ' ' << hero.weapon << ' ' << hero.armor << ' '
            << hero.alive << ' ' << hero.hasAmulet << ' ' << hero.escaped << '\n';
        out << hero.bag.size() << '\n';
        for (const Item& item : hero.bag) itemOut(out, item);
        out << hero.messages.size() << '\n';
        for (const std::string& msg : hero.messages)
            out << std::quoted(msg) << '\n';
        for (int floor = 0; floor < kLevels; ++floor)
            for (int y = 0; y < kHeight; ++y) {
                for (int x = 0; x < kWidth; ++x)
                    out << (hero.discovered[floor][y][x] ? '1' : '0');
                out << '\n';
            }
    }
    for (const Level& l : levels_) {
        out << l.generated << '\n';
        if (!l.generated) continue;
        out << l.up.x << ' ' << l.up.y << ' '
            << l.down.x << ' ' << l.down.y << '\n';
        for (const std::string& tile : l.tiles)
            out << std::quoted(tile) << '\n';
        out << l.loot.size() << '\n';
        for (const Loot& loot : l.loot) {
            out << loot.pos.x << ' ' << loot.pos.y << ' ';
            itemOut(out, loot.item);
        }
        out << l.monsters.size() << '\n';
        for (const Monster& m : l.monsters)
            out << m.pos.x << ' ' << m.pos.y << ' '
                << m.hp << ' ' << m.maxHp << ' '
                << m.damage << ' ' << m.defense << ' '
                << m.xp << ' ' << static_cast<int>(m.symbol) << ' '
                << std::quoted(m.name) << '\n';
    }
    out.flush();
    return out.good();
}

bool World::load(const std::string& filename) {
    std::ifstream in(filename, std::ios::binary);
    if (!in) return false;
    std::string format;
    if (!(in >> format) || format != kFormat) return false;
    int next = 0, round = 0;
    bool started = false, finished = false;
    std::string announcement;
    if (!(in >> next >> round >> started >> finished >>
          std::quoted(announcement)) ||
        next < 1 || next > 100000 || round < 0 ||
        announcement.size() > 500) return false;

    std::map<int, Player> players;
    std::size_t count = 0;
    if (!boundedCount(in, count, kMaxPlayers)) return false;
    for (std::size_t i = 0; i < count; ++i) {
        Player hero;
        if (!(in >> hero.id >> std::quoted(hero.name) >>
              std::quoted(hero.role) >> hero.depth >>
              hero.pos.x >> hero.pos.y >>
              hero.hp >> hero.maxHp >> hero.mp >> hero.maxMp >>
              hero.attack >> hero.defense >>
              hero.level >> hero.experience >> hero.hunger >>
              hero.poison >> hero.gold >> hero.arrows >>
              hero.weapon >> hero.armor >>
              hero.alive >> hero.hasAmulet >> hero.escaped)) return false;
        if (hero.id < 1 || hero.id >= next || hero.name.empty() ||
            hero.name.size() > 24 || hero.role.size() > 24 ||
            hero.depth < 1 || hero.depth > kLevels ||
            !posOk(hero.pos) || hero.maxHp < 1 ||
            hero.maxHp > 10000 || hero.hp > hero.maxHp ||
            hero.maxMp < 0 || hero.maxMp > 10000 ||
            hero.mp < 0 || hero.mp > hero.maxMp ||
            hero.level < 1 || hero.level > 999 ||
            hero.hunger < 0 || hero.poison < 0 ||
            hero.gold < 0 || hero.arrows < 0) return false;
        hero.connected = false; // Los clientes deben volver a identificarse.
        if (!boundedCount(in, count, 22)) return false;
        for (std::size_t j = 0; j < count; ++j) {
            Item item;
            if (!itemIn(in, item)) return false;
            hero.bag.push_back(std::move(item));
        }
        if (!boundedCount(in, count, 4)) return false;
        for (std::size_t j = 0; j < count; ++j) {
            std::string msg;
            if (!(in >> std::quoted(msg)) || msg.size() > 500) return false;
            hero.messages.push_back(std::move(msg));
        }
        for (int floor = 0; floor < kLevels; ++floor) {
            for (int y = 0; y < kHeight; ++y) {
                std::string explored;
                if (!(in >> explored) || explored.size() != kWidth) return false;
                for (int x = 0; x < kWidth; ++x) {
                    if (explored[x] != '0' && explored[x] != '1') return false;
                    hero.discovered[floor][y][x] = explored[x] == '1';
                }
            }
        }
        if (!players.emplace(hero.id, std::move(hero)).second)
            return false;
    }

    std::array<Level, kLevels> floors{};
    for (Level& l : floors) {
        if (!(in >> l.generated)) return false;
        if (!l.generated) continue;
        if (!(in >> l.up.x >> l.up.y >> l.down.x >> l.down.y) ||
            !posOk(l.up) || !posOk(l.down)) return false;
        for (std::string& row : l.tiles) {
            if (!(in >> std::quoted(row)) || row.size() != kWidth) return false;
            for (char tile : row)
                if (std::string(" .#-|+<>").find(tile) == std::string::npos)
                    return false;
        }
        if (!boundedCount(in, count, 1000)) return false;
        for (std::size_t j = 0; j < count; ++j) {
            Loot loot;
            if (!(in >> loot.pos.x >> loot.pos.y) ||
                !posOk(loot.pos) || !itemIn(in, loot.item)) return false;
            l.loot.push_back(std::move(loot));
        }
        if (!boundedCount(in, count, 700)) return false;
        for (std::size_t j = 0; j < count; ++j) {
            Monster m;
            int symbol = 0;
            if (!(in >> m.pos.x >> m.pos.y >>
                  m.hp >> m.maxHp >> m.damage >> m.defense >>
                  m.xp >> symbol >> std::quoted(m.name)) ||
                !posOk(m.pos) || m.maxHp < 1 || m.maxHp > 10000 ||
                m.hp > m.maxHp || m.damage < 1 || symbol < 32 ||
                symbol > 126 || m.name.size() > 120) return false;
            m.symbol = static_cast<char>(symbol);
            l.monsters.push_back(std::move(m));
        }
    }
    for (const auto& [_, hero] : players) {
        if (!floors[hero.depth - 1].generated) return false;
    }
    players_ = std::move(players);
    levels_ = std::move(floors);
    nextId_ = next;
    round_ = round;
    started_ = started;
    finished_ = finished;
    announcement_ = std::move(announcement);
    orders_.clear();
    return true;
}

} // namespace nhb
