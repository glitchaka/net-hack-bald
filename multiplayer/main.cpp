// NetHack Bald: acceso cooperativo a una partida ORIGINAL de NetHack.
// 2026-11-05: módulo C++17 propio; no altera el motor de NetHack.
// Cada participante ve exactamente la misma sesión y comparte el control de
// UN personaje. No se presenta como soporte de varios personajes simultáneos.
#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <iterator>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <poll.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#ifdef __APPLE__
#include <util.h>
#else
#include <pty.h>
#endif
#include <termios.h>
#include <unistd.h>

namespace {

constexpr unsigned MAX_FRAME = 8192;
constexpr std::size_t HISTORY_CAP = 128 * 1024;
constexpr int MAX_CLIENTS = 8;

struct Frame {
    char type = 0;
    std::string payload;
};

bool writeFully(int fd, const void* ptr, std::size_t size, bool socket = true) {
    const auto* bytes = static_cast<const unsigned char*>(ptr);
    while (size) {
        ssize_t sent = socket
            ? ::send(fd, bytes, size, 0)
            : ::write(fd, bytes, size);
        if (sent < 0 && errno == EINTR) continue;
        if (sent <= 0) return false;
        bytes += static_cast<std::size_t>(sent);
        size -= static_cast<std::size_t>(sent);
    }
    return true;
}

bool readFully(int fd, void* ptr, std::size_t size) {
    auto* bytes = static_cast<unsigned char*>(ptr);
    while (size) {
        ssize_t received = ::recv(fd, bytes, size, 0);
        if (received < 0 && errno == EINTR) continue;
        if (received <= 0) return false;
        bytes += static_cast<std::size_t>(received);
        size -= static_cast<std::size_t>(received);
    }
    return true;
}

// Framing explícito: 1 byte de tipo + longitud de 32 bits en orden de red.
bool sendFrame(int fd, char type, const std::string& payload) {
    if (payload.size() > MAX_FRAME) return false;
    std::array<unsigned char, 5> header{
        static_cast<unsigned char>(type), 0, 0, 0, 0
    };
    uint32_t size = static_cast<uint32_t>(payload.size());
    header[1] = static_cast<unsigned char>((size >> 24) & 0xff);
    header[2] = static_cast<unsigned char>((size >> 16) & 0xff);
    header[3] = static_cast<unsigned char>((size >> 8) & 0xff);
    header[4] = static_cast<unsigned char>(size & 0xff);
    return writeFully(fd, header.data(), header.size()) &&
           writeFully(fd, payload.data(), payload.size());
}

bool receiveFrame(int fd, Frame& frame) {
    std::array<unsigned char, 5> header{};
    if (!readFully(fd, header.data(), header.size())) return false;
    uint32_t size = (static_cast<uint32_t>(header[1]) << 24) |
                    (static_cast<uint32_t>(header[2]) << 16) |
                    (static_cast<uint32_t>(header[3]) << 8) |
                    static_cast<uint32_t>(header[4]);
    if (size > MAX_FRAME) return false;
    frame.type = static_cast<char>(header[0]);
    frame.payload.resize(size);
    return size == 0 || readFully(fd, frame.payload.data(), size);
}

int connectSocket(const std::string& address, int port) {
    int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd == -1) throw std::runtime_error("No se pudo crear el socket TCP.");
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(port));
    if (::inet_pton(AF_INET, address.c_str(), &addr.sin_addr) != 1) {
        ::close(fd);
        throw std::runtime_error("Utiliza una dirección IPv4 válida.");
    }
    if (::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        ::close(fd);
        throw std::runtime_error("No se pudo conectar al servidor multijugador.");
    }
    int flag = 1;
    ::setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
    return fd;
}

class RawTerminal {
public:
    RawTerminal() {
        if (::isatty(STDIN_FILENO) && ::tcgetattr(STDIN_FILENO, &saved_) == 0) {
            termios next = saved_;
            next.c_lflag &= static_cast<tcflag_t>(~(ICANON | ECHO | ISIG));
            next.c_iflag &= static_cast<tcflag_t>(~(IXON | ICRNL));
            next.c_cc[VMIN] = 1;
            next.c_cc[VTIME] = 0;
            enabled_ = (::tcsetattr(STDIN_FILENO, TCSANOW, &next) == 0);
        }
        ::write(STDOUT_FILENO, "\x1b[?25l", 6);
    }
    ~RawTerminal() {
        if (enabled_) ::tcsetattr(STDIN_FILENO, TCSANOW, &saved_);
        ::write(STDOUT_FILENO, "\x1b[0m\x1b[?25h\n", 11);
    }
private:
    termios saved_{};
    bool enabled_ = false;
};

struct Peer {
    int socket = -1;
    int id = 0;
    std::string name;
    std::mutex output;
    std::atomic<bool> live{true};
    ~Peer() {
        if (socket >= 0) ::close(socket);
    }
    bool send(char type, const std::string& payload) {
        std::lock_guard<std::mutex> lock(output);
        if (!live) return false;
        if (!sendFrame(socket, type, payload)) {
            live = false;
            ::shutdown(socket, SHUT_RDWR);
            return false;
        }
        return true;
    }
};

class Server {
public:
    Server(std::string bind, int port, std::string game, std::string password)
        : bind_(std::move(bind)), port_(port), game_(std::move(game)),
          password_(std::move(password)) {}

    void run() {
        if (bind_ != "127.0.0.1" && password_.empty())
            throw std::runtime_error(
                "Para escuchar en la red necesitas --clave=CONTRASEÑA. "
                "El protocolo no cifra el tráfico; usa una LAN de confianza.");
        startGame();
        startListener();
        std::cout << "Sesión compartida de NetHack en " << bind_ << ':'
                  << port_ << "\nConecta usando el cliente nethack-bald-multi.\n"
                  << "Cada jugador controla al MISMO personaje por relevos.\n"
                  << "Los clientes pasan el control pulsando Ctrl+T.\n"
                  << "No se compila ni modifica el motor original.\n";
        std::thread reader([this] { readGameOutput(); });
        while (running_) {
            pollfd item{listener_, POLLIN, 0};
            int result = ::poll(&item, 1, 300);
            if (result < 0 && errno != EINTR) break;
            if (result <= 0 || !(item.revents & POLLIN)) continue;
            sockaddr_in addr{};
            socklen_t len = sizeof(addr);
            int fd = ::accept(listener_, reinterpret_cast<sockaddr*>(&addr), &len);
            if (fd < 0) continue;
            std::thread([this, fd] { handleConnection(fd); }).detach();
        }
        running_ = false;
        if (listener_ >= 0) ::close(listener_);
        if (pty_ >= 0) ::close(pty_);
        if (child_ > 0) {
            ::kill(child_, SIGHUP);
            ::waitpid(child_, nullptr, 0);
        }
        if (reader.joinable()) reader.join();
    }

private:
    void startGame() {
        winsize dimensions{};
        dimensions.ws_col = 80;
        dimensions.ws_row = 32;
        child_ = ::forkpty(&pty_, nullptr, nullptr, &dimensions);
        if (child_ < 0)
            throw std::runtime_error("forkpty() falló: no se pudo iniciar NetHack.");
        if (child_ == 0) {
            std::filesystem::path path(game_);
            std::string filename = path.filename().string();
            std::string dir = path.parent_path().empty()
                ? "." : path.parent_path().string();
            if (::chdir(dir.c_str()) != 0) ::_exit(126);
            ::setenv("LANG", "es.UTF-8", 1);
            ::setenv("TERM", "xterm-256color", 1);
            std::string executable = "./" + filename;
            ::execl(executable.c_str(), filename.c_str(), nullptr);
            ::_exit(127);
        }
    }

    void startListener() {
        listener_ = ::socket(AF_INET, SOCK_STREAM, 0);
        if (listener_ < 0)
            throw std::runtime_error("No se pudo crear socket del servidor.");
        int reuse = 1;
        ::setsockopt(listener_, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
        sockaddr_in address{};
        address.sin_family = AF_INET;
        address.sin_port = htons(static_cast<uint16_t>(port_));
        if (::inet_pton(AF_INET, bind_.c_str(), &address.sin_addr) != 1 ||
            ::bind(listener_, reinterpret_cast<sockaddr*>(&address),
                   sizeof(address)) != 0 || ::listen(listener_, 8) != 0)
            throw std::runtime_error("No se pudo escuchar en la dirección y puerto.");
    }

    void broadcast(char type, const std::string& payload) {
        std::vector<std::shared_ptr<Peer>> peers;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            peers = peers_;
        }
        for (const auto& peer : peers) peer->send(type, payload);
    }

    void notice(const std::string& message) {
        std::cout << message << '\n';
        broadcast('N', message);
    }

    void readGameOutput() {
        std::array<char, 4096> buffer{};
        while (running_) {
            ssize_t count = ::read(pty_, buffer.data(), buffer.size());
            if (count <= 0) break;
            std::string data(buffer.data(), static_cast<std::size_t>(count));
            {
                std::lock_guard<std::mutex> lock(mutex_);
                history_ += data;
                if (history_.size() > HISTORY_CAP)
                    history_.erase(0, history_.size() - HISTORY_CAP);
            }
            broadcast('D', data);
        }
        notice("La partida de NetHack ha terminado.");
        running_ = false;
    }

    void announceOwner() {
        std::string name = "(ninguno)";
        {
            std::lock_guard<std::mutex> lock(mutex_);
            for (const auto& peer : peers_)
                if (peer->id == activeId_) name = peer->name;
        }
        notice("Control activo: " + name + ". Ctrl+T para cederlo.");
    }

    void rotateOwner(int who) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (activeId_ != who || peers_.empty()) return;
            auto it = std::find_if(peers_.begin(), peers_.end(),
                [who](const std::shared_ptr<Peer>& p) { return p->id == who; });
            if (it == peers_.end()) return;
            auto next = std::next(it);
            if (next == peers_.end()) next = peers_.begin();
            activeId_ = (*next)->id;
        }
        announceOwner();
    }

    void removePeer(const std::shared_ptr<Peer>& peer) {
        bool wasActive = false;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            wasActive = activeId_ == peer->id;
            peers_.erase(std::remove(peers_.begin(), peers_.end(), peer),
                         peers_.end());
            if (wasActive)
                activeId_ = peers_.empty() ? 0 : peers_.front()->id;
        }
        peer->live = false;
        ::shutdown(peer->socket, SHUT_RDWR);
        notice(peer->name + " abandonó la sesión.");
        if (wasActive) announceOwner();
    }

    void handleConnection(int fd) {
        timeval deadline{};
        deadline.tv_sec = 12;
        ::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &deadline, sizeof(deadline));
        Frame hello;
        if (!receiveFrame(fd, hello) || hello.type != 'H') {
            ::close(fd);
            return;
        }
        auto split = hello.payload.find('\n');
        std::string name = hello.payload.substr(0, split);
        std::string key = split == std::string::npos
            ? "" : hello.payload.substr(split + 1);
        if (name.empty() || name.size() > 28 || key != password_ ||
            !std::all_of(name.begin(), name.end(), [](unsigned char c) {
                return c >= 32 && c != 127;
            })) {
            sendFrame(fd, 'E', "Identificación rechazada.");
            ::close(fd);
            return;
        }
        deadline.tv_sec = 0;
        ::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &deadline, sizeof(deadline));

        auto peer = std::make_shared<Peer>();
        peer->socket = fd;
        peer->name = name;
        std::string history;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (peers_.size() >= MAX_CLIENTS || !running_) {
                sendFrame(fd, 'E', "La sala está llena o terminó la partida.");
                peer->socket = -1;
                ::close(fd);
                return;
            }
            peer->id = nextId_++;
            peers_.push_back(peer);
            if (activeId_ == 0) activeId_ = peer->id;
            history = history_;
        }
        // Los fragmentos son independientes: cada frame <= 8192 bytes.
        for (std::size_t i = 0; i < history.size(); i += MAX_FRAME)
            if (!peer->send('D', history.substr(i, MAX_FRAME))) break;
        notice(peer->name + " se ha unido a la expedición.");
        announceOwner();

        Frame frame;
        while (peer->live && running_ && receiveFrame(fd, frame)) {
            if (frame.type == 'P') {
                rotateOwner(peer->id);
            } else if (frame.type == 'C') {
                if (frame.payload.size() <= 200 &&
                    std::all_of(frame.payload.begin(), frame.payload.end(),
                        [](unsigned char c) { return c >= 32 && c != 127; }))
                    notice("[CHAT] " + peer->name + ": " + frame.payload);
            } else if (frame.type == 'K' && !frame.payload.empty() &&
                       frame.payload.size() <= 16) {
                bool allowed = false;
                {
                    std::lock_guard<std::mutex> lock(mutex_);
                    allowed = (peer->id == activeId_);
                }
                if (allowed) writeFully(pty_, frame.payload.data(),
                                        frame.payload.size(), false);
                else peer->send('N', "Espera tu turno de control.");
            }
        }
        removePeer(peer);
    }

    std::string bind_, game_, password_;
    int port_;
    int listener_ = -1;
    int pty_ = -1;
    pid_t child_ = -1;
    std::atomic<bool> running_{true};
    std::mutex mutex_;
    std::vector<std::shared_ptr<Peer>> peers_;
    int nextId_ = 1;
    int activeId_ = 0;
    std::string history_;
};

void showClientNotice(const std::string& note) {
    // Pantalla NetHack: 80x32. Fila 35 reservada para avisos cooperativos.
    std::string message = note.substr(0, 120);
    std::string ansi = "\x1b" "7\x1b[35;1H\x1b[2K\x1b[1;36m" +
                       message + "\x1b[0m\x1b" "8";
    writeFully(STDOUT_FILENO, ansi.data(), ansi.size(), false);
}

void runClient(const std::string& address, int port,
               const std::string& name, const std::string& key) {
    int fd = connectSocket(address, port);
    if (!sendFrame(fd, 'H', name + '\n' + key)) {
        ::close(fd);
        throw std::runtime_error("Error al enviar credenciales.");
    }
    RawTerminal terminal;
    std::cout << "\x1b[2J\x1b[H" << std::flush;
    showClientNotice("Ctrl+T = pasar el control | Ctrl+G = chat | Ctrl+] = salir");
    bool chatting = false;
    std::string chatLine;
    bool active = true;
    while (active) {
        pollfd pending[2]{{fd, POLLIN, 0}, {STDIN_FILENO, POLLIN, 0}};
        int count = ::poll(pending, 2, -1);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) break;
        if (pending[0].revents & (POLLERR | POLLHUP | POLLNVAL)) break;
        if (pending[0].revents & POLLIN) {
            Frame frame;
            if (!receiveFrame(fd, frame)) break;
            if (frame.type == 'D') {
                writeFully(STDOUT_FILENO, frame.payload.data(),
                           frame.payload.size(), false);
            } else if (frame.type == 'N' || frame.type == 'E') {
                showClientNotice(frame.payload);
                if (frame.type == 'E') break;
            }
        }
        if (pending[1].revents & POLLIN) {
            char input{};
            if (::read(STDIN_FILENO, &input, 1) != 1) break;
            if (input == 29 || input == 3) break; // Ctrl+] o Ctrl+C
            if (chatting) {
                if (input == '\r' || input == '\n') {
                    if (!chatLine.empty()) sendFrame(fd, 'C', chatLine);
                    chatLine.clear();
                    chatting = false;
                } else if (input == 27) {
                    chatLine.clear();
                    chatting = false;
                } else if (input == 8 || input == 127) {
                    if (!chatLine.empty()) chatLine.pop_back();
                } else if (static_cast<unsigned char>(input) >= 32 &&
                           chatLine.size() < 200) {
                    chatLine.push_back(input);
                }
                if (chatting) showClientNotice("Chat: " + chatLine);
                else showClientNotice("Chat enviado / cancelado.");
            } else if (input == 20) { // Ctrl+T
                sendFrame(fd, 'P', "");
            } else if (input == 7) { // Ctrl+G
                chatting = true;
                chatLine.clear();
                showClientNotice("Chat: (Enter para enviar, ESC para cancelar)");
            } else {
                sendFrame(fd, 'K', std::string(1, input));
            }
        }
    }
    ::shutdown(fd, SHUT_RDWR);
    ::close(fd);
}

void usage() {
    std::cout <<
        "NetHack Bald - servidor y cliente cooperativo (C++17)\n\n"
        "Uso:\n"
        "  nethack-bald-multi servidor [--bind=127.0.0.1] [--puerto=7777]\n"
        "      [--juego=upstream/nethack/playground/nethack] [--clave=CLAVE]\n"
        "  nethack-bald-multi cliente --ip=127.0.0.1 [--puerto=7777]\n"
        "      [--nombre=Jugador] [--clave=CLAVE]\n\n"
        "Cooperativo de UNA aventura y UN personaje, por relevos.\n"
        "Ctrl+T: pasar turno; Ctrl+G: escribir en el chat;\n"
        "Ctrl+]: desconectarse. Hasta ocho participantes.\n"
        "El servidor escucha solo en localhost de forma predeterminada.\n"
        "Para LAN usa --bind=0.0.0.0 --clave=CLAVE. Sin TLS: LAN confiable.\n"
        "El ejecutable de NetHack en español debe compilarse por separado.\n";
}

std::string arg(const std::vector<std::string>& args,
                const std::string& name, const std::string& fallback) {
    for (const auto& s : args) {
        const std::string prefix = "--" + name + "=";
        if (s.compare(0, prefix.size(), prefix) == 0)
            return s.substr(prefix.size());
    }
    return fallback;
}

} // namespace

int main(int argc, char** argv) {
    ::signal(SIGPIPE, SIG_IGN);
    try {
        std::vector<std::string> args;
        for (int i = 1; i < argc; ++i) args.emplace_back(argv[i]);
        if (args.empty() || (args[0] != "servidor" && args[0] != "cliente")) {
            usage();
            return args.empty() ? 0 : 2;
        }
        int port = std::stoi(arg(args, "puerto", "7777"));
        if (port <= 0 || port > 65535)
            throw std::runtime_error("Puerto TCP no válido.");
        if (args[0] == "servidor") {
            Server server(arg(args, "bind", "127.0.0.1"), port,
                          arg(args, "juego",
                              "upstream/nethack/playground/nethack"),
                          arg(args, "clave", ""));
            server.run();
        } else {
            runClient(arg(args, "ip", "127.0.0.1"), port,
                      arg(args, "nombre", "Aventurero"),
                      arg(args, "clave", ""));
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
