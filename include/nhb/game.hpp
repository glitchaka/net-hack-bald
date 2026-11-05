#pragma once

#include <array>
#include <deque>
#include <optional>
#include <random>
#include <string>
#include <vector>

namespace nhb {

constexpr int MAP_WIDTH = 76;
constexpr int MAP_HEIGHT = 22;
constexpr int FLOOR_COUNT = 10;
constexpr int PACK_LIMIT = 24;

struct Point {
    int x = 0;
    int y = 0;
    bool operator==(Point other) const { return x == other.x && y == other.y; }
};

enum class ItemKind {
    Food, Healing, Mana, MapScroll, TeleportScroll, IdentifyScroll,
    Weapon, Armor, Arrows, Gold, Amulet
};

struct Item {
    ItemKind kind = ItemKind::Food;
    std::string name;
    char glyph = '?';
    int power = 0;
    int amount = 1;
    bool identified = true;
};

struct Monster {
    Point pos;
    std::string name;
    char glyph = 'm';
    int hp = 1;
    int maxHp = 1;
    int attack = 2;
    int defense = 1;
    int xp = 1;
    bool awake = false;
};

struct GroundItem {
    Point pos;
    Item item;
};

struct Trap {
    Point pos;
    int type = 0;
    bool revealed = false;
    bool spent = false;
};

struct Floor {
    bool ready = false;
    std::array<std::string, MAP_HEIGHT> terrain{};
    std::array<std::array<bool, MAP_WIDTH>, MAP_HEIGHT> explored{};
    Point up;
    Point down;
    std::vector<Monster> monsters;
    std::vector<GroundItem> objects;
    std::vector<Trap> traps;
};

struct Hero {
    std::string name = "Aventurero";
    std::string role = "Guerrero";
    Point pos;
    int level = 1;
    int xp = 0;
    int hp = 32;
    int maxHp = 32;
    int mp = 6;
    int maxMp = 6;
    int strength = 6;
    int agility = 5;
    int intellect = 4;
    int defense = 1;
    int hunger = 950;
    int poison = 0;
    int arrows = 6;
    int gold = 0;
    int weapon = -1;
    int armor = -1;
    std::vector<Item> pack;
};

namespace terminal {
void initialize();
void shutdown();
void clear();
int readKey();
void flush();
void lineInput(std::string& output, unsigned maxLength = 22);
}

class Game {
public:
    Game();
    bool menu();
    void run();

private:
    Hero hero_;
    std::array<Floor, FLOOR_COUNT> floors_{};
    int depth_ = 1;
    int turns_ = 0;
    bool playing_ = false;
    bool victory_ = false;
    bool hasAmulet_ = false;
    std::deque<std::string> messages_;
    std::mt19937 rng_;
    std::array<std::array<bool, MAP_WIDTH>, MAP_HEIGHT> visible_{};

    Floor& floor();
    const Floor& floor() const;
    int randomInt(int low, int high);
    bool inside(int x, int y) const;
    bool passable(const Floor& f, int x, int y) const;
    bool occupied(int x, int y, int ignore = -1) const;
    bool lineOfSight(Point from, Point to) const;
    Point randomOpenTile(Floor& f, bool awayFromStairs = true);
    void generateFloor(int index);

    void newGame();
    bool loadGame();
    bool saveGame() const;
    void removeSave() const;

    void printHelp();
    void inventory();
    void draw();
    void updateVision();
    void say(const std::string& text);
    bool askDirection(int& dx, int& dy);
    int chooseItem(const std::string& prompt, std::optional<ItemKind> kind = {});
    int armorValue() const;
    int weaponValue() const;

    void advanceTurn();
    void walk(int dx, int dy);
    void attack(int monsterIndex, int bonus = 0);
    void monsterTurn();
    void activateTrap();
    void pickUp();
    void consume(int index);
    void eat();
    void drink();
    void readScroll();
    void wield();
    void wear();
    void takeOff();
    void drop();
    void openDoor();
    void shoot();
    void spell();
    void inspect();
    void changeFloor(bool down);
    void levelUp();
    void endGame(const std::string& reason, bool won);
};

} // namespace nhb
