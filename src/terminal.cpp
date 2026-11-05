#include "nhb/game.hpp"

#include <clocale>
#include <iostream>
#include <string>

#ifdef _WIN32
#define NOMINMAX
#include <conio.h>
#include <windows.h>
#else
#include <sys/select.h>
#include <termios.h>
#include <unistd.h>
#endif

namespace nhb::terminal {
namespace {
#ifdef _WIN32
DWORD originalMode = 0;
HANDLE outputHandle = INVALID_HANDLE_VALUE;
bool consoleModeSaved = false;
#else
termios originalMode{};
bool modeSaved = false;
#endif
bool initialized = false;
}

void initialize() {
    if (initialized) return;
    std::setlocale(LC_ALL, "");
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    outputHandle = GetStdHandle(STD_OUTPUT_HANDLE);
    if (outputHandle != INVALID_HANDLE_VALUE &&
        GetConsoleMode(outputHandle, &originalMode)) {
        consoleModeSaved = SetConsoleMode(
            outputHandle, originalMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING) != 0;
    }
#else
    if (isatty(STDIN_FILENO) && tcgetattr(STDIN_FILENO, &originalMode) == 0) {
        termios raw = originalMode;
        raw.c_lflag &= static_cast<tcflag_t>(~(ICANON | ECHO));
        raw.c_iflag &= static_cast<tcflag_t>(~(IXON | ICRNL));
        raw.c_cc[VMIN] = 1;
        raw.c_cc[VTIME] = 0;
        modeSaved = (tcsetattr(STDIN_FILENO, TCSANOW, &raw) == 0);
    }
#endif
    initialized = true;
    std::cout << "\x1b[?25l" << std::flush;
}

void shutdown() {
    if (!initialized) return;
#ifdef _WIN32
    if (consoleModeSaved && outputHandle != INVALID_HANDLE_VALUE)
        SetConsoleMode(outputHandle, originalMode);
#else
    if (modeSaved) tcsetattr(STDIN_FILENO, TCSANOW, &originalMode);
#endif
    std::cout << "\x1b[0m\x1b[?25h\n" << std::flush;
    initialized = false;
}

void clear() {
    std::cout << "\x1b[0m\x1b[H\x1b[2J";
}

void flush() { std::cout << std::flush; }

int readKey() {
#ifdef _WIN32
    int ch = _getch();
    if (ch == 0 || ch == 224) {
        switch (_getch()) {
            case 72: return 'k';
            case 80: return 'j';
            case 75: return 'h';
            case 77: return 'l';
            default: return 0;
        }
    }
    return ch;
#else
    unsigned char ch = 0;
    if (::read(STDIN_FILENO, &ch, 1) != 1) return 0;
    if (ch == 27) {
        // Distinguir flechas ANSI de ESC mediante lectura sin bloqueo breve.
        fd_set fds;
        FD_ZERO(&fds);
        FD_SET(STDIN_FILENO, &fds);
        timeval timeout{0, 25000};
        if (select(STDIN_FILENO + 1, &fds, nullptr, nullptr, &timeout) <= 0)
            return 27;
        unsigned char seq[2]{};
        if (::read(STDIN_FILENO, &seq[0], 1) != 1) return 27;
        if (seq[0] != '[' && seq[0] != 'O') return 27;
        if (::read(STDIN_FILENO, &seq[1], 1) != 1) return 27;
        switch (seq[1]) {
            case 'A': return 'k';
            case 'B': return 'j';
            case 'C': return 'l';
            case 'D': return 'h';
            default: return 27;
        }
    }
    return ch;
#endif
}

void lineInput(std::string& output, unsigned maxLength) {
    output.clear();
    std::cout << "\x1b[?25h" << std::flush;
    for (;;) {
        int key = readKey();
        if (key == '\r' || key == '\n') break;
        if (key == 27) { output.clear(); break; }
        if (key == 8 || key == 127) {
            if (!output.empty()) {
                output.pop_back();
                std::cout << "\b \b" << std::flush;
            }
        } else if (key >= 32 && key <= 126 && output.size() < maxLength) {
            output.push_back(static_cast<char>(key));
            std::cout << static_cast<char>(key) << std::flush;
        }
    }
    std::cout << "\x1b[?25l" << std::flush;
}

} // namespace nhb::terminal
