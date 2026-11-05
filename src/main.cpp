#include "nhb/game.hpp"

#include <exception>
#include <iostream>

int main() {
    try {
        nhb::terminal::initialize();
        nhb::Game game;
        while (game.menu()) game.run();
        nhb::terminal::shutdown();
        return 0;
    } catch (const std::exception& error) {
        nhb::terminal::shutdown();
        std::cerr << "Error de NetHack Bald: " << error.what() << "\n";
        return 1;
    }
}
