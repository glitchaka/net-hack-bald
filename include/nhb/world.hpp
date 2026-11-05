#pragma once

#include <array>
#include <cstdint>
#include <deque>
#include <map>
#include <optional>
#include <random>
#include <string>
#include <vector>

namespace nhb {

constexpr int kWidth = 76;
constexpr int kHeight = 23;
constexpr int kLevels = 10;
constexpr int kMinPlayers = 2;
constexpr int kMaxPlayers = 6;
constexpr int kVision = 9;

struct Pos {
    int x = 0;
    int y = 0;
    bool operator==(Pos other) const { return x == other.x && y == other.y; }
    bool operator!=(Pos other) const { return !(*this == other); }
};

enum class Kind { Food, Potion, Mana, Sword, Armor, Scroll, Arrows, Amulet };

struct Item {
    Kind kind = Kind::Food;
    int power = 0;
    int count = 1;
    std::string name;
    char symbol = '%';
};

struct Loot {
    Pos pos;
    Item item;
};

struct Monster {
    Pos pos;
    int hp = 0;
    int maxHp = 0;
    int damage = 0;
    int defense = 0;
    int xp = 0;
    char symbol = 'r';
    std::string name;
};

struct Level {
    bool generated = false;
    std::array<std::string, kHeight> tiles{};
    Pos up;
    Pos down;
    std::vector<Loot> loot;
    std::vector<Monster> monsters;
};

struct Player {
    int id = 0;
    int depth = 1;
    Pos pos;
    std::string name;
    std::string role;
    int hp = 30, maxHp = 30;
    int mp = 8, maxMp = 8;
    int attack = 6, defense = 1;
    int level = 1, experience = 0;
    int hunger = 800;
    int poison = 0;
    int gold = 0, arrows = 4;
    int weapon = 0, armor = 0;
    bool alive = true;
    bool connected = true;
    bool hasAmulet = false;
    bool escaped = false;
    std::vector<Item> bag;
    std::array<std::array<std::array<bool, kWidth>, kHeight>, kLevels> discovered{};
    std::deque<std::string> messages;
};

struct Outcome {
    bool accepted = false;
    bool roundResolved = false;
    std::string notice;
};

class World {
public:
    World();
    std::optional<int> join(std::string name, std::string role,
                            std::string& reason);
    void disconnect(int id);
    bool started() const { return started_; }
    bool finished() const { return finished_; }
    int round() const { return round_; }
    int connectedCount() const;
    int waitingCount() const;
    Outcome submit(int id, char key);
    std::string render(int id);
    std::string roster() const;
    void chat(int id, const std::string& line);
    bool save(const std::string& filename) const;
    bool load(const std::string& filename);

private:
    std::array<Level, kLevels> levels_{};
    std::map<int, Player> players_;
    std::map<int, char> orders_;
    std::mt19937 generator_;
    int nextId_ = 1;
    int round_ = 0;
    bool started_ = false;
    bool finished_ = false;
    std::string announcement_;

    Level& level(int depth) { return levels_.at(static_cast<std::size_t>(depth - 1)); }
    const Level& level(int depth) const { return levels_.at(static_cast<std::size_t>(depth - 1)); }
    int dice(int lo, int hi);
    bool inside(Pos p) const;
    bool traversable(int depth, Pos p) const;
    bool occupiedByHero(int depth, Pos p, int except = -1) const;
    bool occupiedByMonster(int depth, Pos p) const;
    bool sees(int depth, Pos from, Pos to) const;
    Pos openSpot(int depth, bool away = true);
    void generate(int depth);

    bool perform(Player& hero, char key);
    bool move(Player& hero, int dx, int dy);
    bool collect(Player& hero);
    bool consume(Player& hero, Kind kind);
    bool equip(Player& hero, Kind kind);
    bool cast(Player& hero);
    bool shoot(Player& hero);
    bool descend(Player& hero, bool down);
    void hitMonster(Player& hero, Monster& monster, int power);
    void gainExperience(Player& hero, int amount);
    void monsterPhase();
    void advanceRound();
    void message(Player& hero, const std::string& text);
    Player* find(int id);
    const Player* find(int id) const;
    int participantsRequired() const;
    void reveal(Player& hero);
};

} // namespace nhb
