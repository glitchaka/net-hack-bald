#include "nhb/client.hpp"

#include <iostream>

#ifdef _WIN32
#include <conio.h>
#include <windows.h>
#else
#include <sys/select.h>
#include <termios.h>
#include <unistd.h>
#endif

namespace nhb::client {
#ifndef _WIN32
struct Terminal::TermiosBackup {
    termios previous{};
    bool saved = false;
};
#endif

Terminal::Terminal() {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    HANDLE console = GetStdHandle(STD_OUTPUT_HANDLE);
    handle_ = console;
    DWORD mode = 0;
    if (console != INVALID_HANDLE_VALUE && GetConsoleMode(console, &mode)) {
        oldMode_ = mode;
        active_ = SetConsoleMode(console, mode |
            ENABLE_VIRTUAL_TERMINAL_PROCESSING) != 0;
    }
#else
    saved_ = new TermiosBackup{};
    if (::isatty(STDIN_FILENO) &&
        ::tcgetattr(STDIN_FILENO, &saved_->previous) == 0) {
        termios raw = saved_->previous;
        raw.c_lflag &= static_cast<tcflag_t>(~(ICANON | ECHO | ISIG));
        raw.c_iflag &= static_cast<tcflag_t>(~(IXON | ICRNL));
        raw.c_cc[VMIN] = 1;
        raw.c_cc[VTIME] = 0;
        saved_->saved = (::tcsetattr(STDIN_FILENO, TCSANOW, &raw) == 0);
    }
#endif
    std::cout << "\x1b[?25l" << std::flush;
}
Terminal::~Terminal() {
#ifdef _WIN32
    if (active_)
        SetConsoleMode(static_cast<HANDLE>(handle_), oldMode_);
#else
    if (saved_) {
        if (saved_->saved)
            ::tcsetattr(STDIN_FILENO, TCSANOW, &saved_->previous);
        delete saved_;
        saved_ = nullptr;
    }
#endif
    std::cout << "\x1b[0m\x1b[?25h" << std::flush;
}
int Terminal::pollKey() {
#ifdef _WIN32
    if (!_kbhit()) return 0;
    int key = _getch();
    if (key == 0 || key == 224) {
        switch (_getch()) {
            case 72: return 'k';
            case 80: return 'j';
            case 75: return 'h';
            case 77: return 'l';
            default: return 0;
        }
    }
    return key;
#else
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(STDIN_FILENO, &fds);
    timeval tv{};
    if (::select(STDIN_FILENO + 1, &fds, nullptr, nullptr, &tv) <= 0)
        return 0;
    unsigned char key = 0;
    if (::read(STDIN_FILENO, &key, 1) != 1) return 0;
    if (key != 27) return key;
    timeval shortTimeout{0, 20000};
    FD_ZERO(&fds);
    FD_SET(STDIN_FILENO, &fds);
    if (::select(STDIN_FILENO + 1, &fds, nullptr, nullptr, &shortTimeout) <= 0)
        return 27;
    unsigned char first = 0, second = 0;
    if (::read(STDIN_FILENO, &first, 1) != 1) return 27;
    if (first != '[' && first != 'O') return 27;
    shortTimeout = {0, 20000};
    FD_ZERO(&fds);
    FD_SET(STDIN_FILENO, &fds);
    if (::select(STDIN_FILENO + 1, &fds, nullptr, nullptr, &shortTimeout) <= 0)
        return 27;
    if (::read(STDIN_FILENO, &second, 1) != 1) return 27;
    switch (second) {
        case 'A': return 'k';
        case 'B': return 'j';
        case 'C': return 'l';
        case 'D': return 'h';
        default: return 27;
    }
#endif
}
void Terminal::draw(const std::string& value) {
    std::cout << value << std::flush;
}
} // namespace nhb::client
