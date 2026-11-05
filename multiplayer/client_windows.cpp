// NetHack Bald, cliente multijugador nativo Windows.
// 2026-11-05: cliente Win32/Winsock para el servidor POSIX.
// Conserva una única partida y personaje compartidos. No ejecuta el motor.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <conio.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <iostream>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {
constexpr unsigned MAX_FRAME = 8192;
std::mutex outputMutex;

struct Session {
    WSADATA winsock{};
    Session() {
        if (WSAStartup(MAKEWORD(2,2), &winsock) != 0)
            throw std::runtime_error("No se pudo iniciar Winsock.");
    }
    ~Session() { WSACleanup(); }
};

struct Console {
    HANDLE output = INVALID_HANDLE_VALUE;
    DWORD saved = 0;
    bool restore = false;
    Console() {
        SetConsoleOutputCP(CP_UTF8);
        SetConsoleCP(CP_UTF8);
        output = GetStdHandle(STD_OUTPUT_HANDLE);
        DWORD mode = 0;
        if (output != INVALID_HANDLE_VALUE && GetConsoleMode(output, &mode)) {
            saved = mode;
            restore = SetConsoleMode(
                output, mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING) != 0;
        }
        std::cout << "\x1b[2J\x1b[H\x1b[?25l" << std::flush;
    }
    ~Console() {
        std::cout << "\x1b[0m\x1b[?25h\n" << std::flush;
        if (restore) SetConsoleMode(output, saved);
    }
};

bool sendAll(SOCKET fd, const void* data, std::size_t size) {
    const char* buffer = static_cast<const char*>(data);
    while (size > 0) {
        int n = send(fd, buffer, static_cast<int>(size), 0);
        if (n == SOCKET_ERROR || n <= 0) return false;
        buffer += n;
        size -= static_cast<std::size_t>(n);
    }
    return true;
}

bool readAll(SOCKET fd, void* data, std::size_t size) {
    char* buffer = static_cast<char*>(data);
    while (size > 0) {
        int n = recv(fd, buffer, static_cast<int>(size), 0);
        if (n == SOCKET_ERROR || n <= 0) return false;
        buffer += n;
        size -= static_cast<std::size_t>(n);
    }
    return true;
}

bool sendFrame(SOCKET fd, char type, const std::string& payload) {
    if (payload.size() > MAX_FRAME) return false;
    uint32_t n = static_cast<uint32_t>(payload.size());
    std::array<unsigned char, 5> hdr{
        static_cast<unsigned char>(type),
        static_cast<unsigned char>((n >> 24) & 255),
        static_cast<unsigned char>((n >> 16) & 255),
        static_cast<unsigned char>((n >> 8) & 255),
        static_cast<unsigned char>(n & 255)
    };
    return sendAll(fd, hdr.data(), hdr.size()) &&
           sendAll(fd, payload.data(), payload.size());
}

bool readFrame(SOCKET fd, char& type, std::string& payload) {
    std::array<unsigned char, 5> hdr{};
    if (!readAll(fd, hdr.data(), hdr.size())) return false;
    uint32_t n = (static_cast<uint32_t>(hdr[1]) << 24) |
                 (static_cast<uint32_t>(hdr[2]) << 16) |
                 (static_cast<uint32_t>(hdr[3]) << 8) |
                 static_cast<uint32_t>(hdr[4]);
    if (n > MAX_FRAME) return false;
    type = static_cast<char>(hdr[0]);
    payload.resize(n);
    return n == 0 || readAll(fd, payload.data(), n);
}

void printNote(const std::string& message) {
    std::lock_guard<std::mutex> lock(outputMutex);
    std::cout << "\x1b" "7\x1b[35;1H\x1b[2K\x1b[1;36m"
              << message.substr(0, 120) << "\x1b[0m\x1b" "8" << std::flush;
}

std::string argument(const std::vector<std::string>& args,
                     const std::string& name,
                     const std::string& defaultValue) {
    for (const auto& value : args) {
        const std::string prefix = "--" + name + "=";
        if (value.compare(0, prefix.size(), prefix) == 0)
            return value.substr(prefix.size());
    }
    return defaultValue;
}

SOCKET connectTo(const std::string& address, int port) {
    SOCKET socket = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (socket == INVALID_SOCKET)
        throw std::runtime_error("No se pudo crear un socket TCP.");
    sockaddr_in server{};
    server.sin_family = AF_INET;
    server.sin_port = htons(static_cast<u_short>(port));
    if (InetPtonA(AF_INET, address.c_str(), &server.sin_addr) != 1 ||
        connect(socket, reinterpret_cast<sockaddr*>(&server),
                sizeof(server)) == SOCKET_ERROR) {
        closesocket(socket);
        throw std::runtime_error("No fue posible conectar con el servidor.");
    }
    BOOL noDelay = TRUE;
    setsockopt(socket, IPPROTO_TCP, TCP_NODELAY,
               reinterpret_cast<const char*>(&noDelay), sizeof(noDelay));
    return socket;
}

void run(const std::vector<std::string>& args) {
    int port = std::stoi(argument(args, "puerto", "7777"));
    if (port < 1 || port > 65535)
        throw std::runtime_error("Puerto TCP fuera de rango.");
    Session session;
    Console console;
    SOCKET sock = connectTo(argument(args, "ip", "127.0.0.1"), port);
    const std::string name = argument(args, "nombre", "Aventurero");
    const std::string password = argument(args, "clave", "");
    if (!sendFrame(sock, 'H', name + "\n" + password)) {
        closesocket(sock);
        throw std::runtime_error("Falló la identificación inicial.");
    }

    std::atomic<bool> running{true};
    std::thread receiver([&] {
        char type = 0;
        std::string payload;
        while (running && readFrame(sock, type, payload)) {
            if (type == 'D') {
                std::lock_guard<std::mutex> lock(outputMutex);
                std::cout.write(payload.data(),
                                static_cast<std::streamsize>(payload.size()));
                std::cout.flush();
            } else if (type == 'N' || type == 'E') {
                printNote(payload);
                if (type == 'E') break;
            }
        }
        running = false;
    });

    printNote("Ctrl+T: pasar control | Ctrl+G: chat | Ctrl+]: salir");
    bool chat = false;
    std::string typed;
    while (running) {
        if (!_kbhit()) { Sleep(25); continue; }
        int key = _getch();
        if (key == 0 || key == 224) {
            switch (_getch()) {
                case 72: key = 'k'; break;
                case 80: key = 'j'; break;
                case 75: key = 'h'; break;
                case 77: key = 'l'; break;
                default: key = 0;
            }
        }
        if (key == 29 || key == 3) break;
        if (chat) {
            if (key == 13 || key == 10) {
                if (!typed.empty()) sendFrame(sock, 'C', typed);
                chat = false;
                typed.clear();
                printNote("Mensaje enviado.");
            } else if (key == 27) {
                typed.clear();
                chat = false;
                printNote("Chat cancelado.");
            } else if (key == 8) {
                if (!typed.empty()) typed.pop_back();
                printNote("Chat: " + typed);
            } else if (key >= 32 && key <= 255 && typed.size() < 200) {
                typed.push_back(static_cast<char>(key));
                printNote("Chat: " + typed);
            }
        } else if (key == 20) {
            sendFrame(sock, 'P', "");
        } else if (key == 7) {
            chat = true;
            typed.clear();
            printNote("Chat: escribe, Enter envía, ESC cancela.");
        } else if (key >= 1 && key <= 255) {
            sendFrame(sock, 'K', std::string(1, static_cast<char>(key)));
        }
    }
    running = false;
    shutdown(sock, SD_BOTH);
    closesocket(sock);
    receiver.join();
}

} // namespace

int main(int argc, char** argv) {
    try {
        std::vector<std::string> args;
        for (int i = 1; i < argc; ++i) args.emplace_back(argv[i]);
        if (args.empty() || args[0] != "cliente") {
            std::cout << "Cliente NetHack Bald (Windows nativo)\n"
                      << "Uso: nethack-bald-multi cliente --ip=127.0.0.1 "
                         "[--puerto=7777] [--nombre=Jugador] [--clave=CLAVE]\n"
                      << "El servidor de NetHack funciona en Linux/WSL.\n";
            return args.empty() ? 0 : 2;
        }
        run(args);
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Error del cliente: " << e.what() << '\n';
        return 1;
    }
}
