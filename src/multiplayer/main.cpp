// NetHack Bald: modo de 2 a 6 personajes independientes.
// 2026-11-05. Motor de mundo multijugador propio en C++17.
// No sustituye ni pretende reproducir el motor original de NetHack 1:1.
#include "nhb/world.hpp"
#include "nhb/network.hpp"
#include "nhb/client.hpp"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <csignal>
#include <filesystem>
#include <iostream>
#include <memory>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

namespace {
namespace net = nhb::net;

struct Peer {
    net::Socket socket = net::kInvalidSocket;
    int id = 0;
    std::string name;
    std::atomic<bool> connected{true};
    std::mutex writeMutex;

    ~Peer() { net::closeSocket(socket); }

    bool send(char kind, const std::string& payload) {
        std::lock_guard<std::mutex> guard(writeMutex);
        if (!connected.load()) return false;
        if (!net::sendFrame(socket, kind, payload)) {
            connected = false;
            net::shutdownSocket(socket);
            return false;
        }
        return true;
    }
};

bool validName(const std::string& value, std::size_t maximum) {
    if (value.empty() || value.size() > maximum) return false;
    return std::all_of(value.begin(), value.end(), [](unsigned char ch) {
        return ch >= 32 && ch != 127;
    });
}

class Server {
public:
    Server(std::string bindAddress, int port, std::string secret, std::string file)
        : bindAddress_(std::move(bindAddress)), port_(port),
          secret_(std::move(secret)), file_(std::move(file)) {
        if (bindAddress_ != "127.0.0.1" && secret_.empty())
            throw std::runtime_error(
                "Para una LAN usa --clave=SECRETO. El protocolo no cifra el tráfico.");
    }

    void run() {
        if (std::filesystem::exists(file_)) {
            if (!world_.load(file_))
                throw std::runtime_error("Archivo de campaña incompatible: " + file_);
            std::cout << "Campaña recuperada: " << file_ << "\n";
        }
        net::Socket listening = net::listen(bindAddress_, port_);
        std::cout << "NETHACK BALD - MULTIJUGADOR DE 2 A 6 PERSONAJES\n"
                  << "Escuchando: " << bindAddress_ << ":" << port_ << "\n"
                  << "Estado: motor multijugador independiente en C++17.\n"
                  << "El NetHack 5.0 original se conserva separado.\n" << std::flush;
        for (;;) {
            net::Socket socket = net::accept(listening);
            if (socket == net::kInvalidSocket) continue;
            std::thread([this, socket]() { handle(socket); }).detach();
        }
    }

private:
    std::string bindAddress_, secret_, file_;
    int port_;
    nhb::World world_;
    std::mutex worldMutex_;
    std::mutex peersMutex_;
    std::vector<std::shared_ptr<Peer>> peers_;

    std::vector<std::shared_ptr<Peer>> peersSnapshot() {
        std::lock_guard<std::mutex> guard(peersMutex_);
        return peers_;
    }

    // Separar la generación de vistas del envío de red.
    void publishViews() {
        auto peers = peersSnapshot();
        std::vector<std::string> views;
        views.reserve(peers.size());
        {
            std::lock_guard<std::mutex> guard(worldMutex_);
            for (const auto& peer : peers)
                views.push_back(world_.render(peer->id));
        }
        for (std::size_t i = 0; i < peers.size(); ++i)
            peers[i]->send('S', views[i]);
    }

    void notify(const std::string& text) {
        std::cout << text << "\n";
        for (const auto& peer : peersSnapshot())
            peer->send('N', text);
    }

    void onDisconnect(const std::shared_ptr<Peer>& peer) {
        bool wasPresent = false;
        {
            std::lock_guard<std::mutex> guard(peersMutex_);
            auto it = std::find(peers_.begin(), peers_.end(), peer);
            if (it != peers_.end()) {
                peers_.erase(it);
                wasPresent = true;
            }
        }
        peer->connected = false;
        net::shutdownSocket(peer->socket);
        if (!wasPresent) return;
        {
            std::lock_guard<std::mutex> guard(worldMutex_);
            world_.disconnect(peer->id);
            world_.save(file_);
        }
        notify(peer->name + " se ha desconectado.");
        publishViews();
    }

    void handle(net::Socket socket) {
        net::Frame frame;
        if (!net::receiveFrame(socket, frame) || frame.type != 'H') {
            net::closeSocket(socket);
            return;
        }

        // H = nombre + '\n' + clase + '\n' + clave
        auto a = frame.data.find('\n');
        auto b = (a == std::string::npos) ? std::string::npos :
            frame.data.find('\n', a + 1);
        if (b == std::string::npos) {
            net::sendFrame(socket, 'E', "Identificación incompleta.");
            net::closeSocket(socket);
            return;
        }
        std::string name = frame.data.substr(0, a);
        std::string role = frame.data.substr(a + 1, b - a - 1);
        std::string key = frame.data.substr(b + 1);
        if (!validName(name, 24) || !validName(role, 20) || key != secret_) {
            net::sendFrame(socket, 'E', "Nombre, clase o clave incorrectos.");
            net::closeSocket(socket);
            return;
        }

        std::optional<int> id;
        std::string reason;
        {
            std::lock_guard<std::mutex> guard(worldMutex_);
            id = world_.join(name, role, reason);
            if (id) world_.save(file_);
        }
        if (!id) {
            net::sendFrame(socket, 'E', reason);
            net::closeSocket(socket);
            return;
        }

        auto peer = std::make_shared<Peer>();
        peer->socket = socket;
        peer->id = *id;
        peer->name = name;
        {
            std::lock_guard<std::mutex> guard(peersMutex_);
            peers_.push_back(peer);
        }
        peer->send('N', reason);
        notify(name + " se ha unido a la expedición.");
        publishViews();

        while (peer->connected && net::receiveFrame(socket, frame)) {
            if (frame.type == 'K' && frame.data.size() == 1) {
                nhb::Outcome outcome;
                {
                    std::lock_guard<std::mutex> guard(worldMutex_);
                    outcome = world_.submit(peer->id, frame.data[0]);
                    if (outcome.roundResolved) world_.save(file_);
                }
                if (!outcome.accepted) peer->send('N', outcome.notice);
                publishViews();
            } else if (frame.type == 'C' &&
                       validName(frame.data, 180)) {
                {
                    std::lock_guard<std::mutex> guard(worldMutex_);
                    world_.chat(peer->id, frame.data);
                }
                publishViews();
            } else if (frame.type == 'R') {
                std::string view;
                {
                    std::lock_guard<std::mutex> guard(worldMutex_);
                    view = world_.render(peer->id);
                }
                peer->send('S', view);
            } else {
                peer->send('N', "Comando de red desconocido.");
            }
        }
        onDisconnect(peer);
    }
};

void guide() {
    std::cout
        << "\x1b[2J\x1b[HAYUDA - NETHACK BALD MULTIJUGADOR\n\n"
        << "Cada participante controla un personaje propio.\n"
        << "De 2 a 6 jugadores; cada ronda se resuelve tras recibir órdenes.\n\n"
        << "   y  k  u       7  8  9\n"
        << "    \\ | /         \\ | /\n"
        << "   h  @  l       4  @  6\n"
        << "    / | \\         / | \\\n"
        << "   b  j  n       1  2  3\n\n"
        << " . esperar, g recoger, e comer, q poción curativa,\n"
        << " m poción de maná, r leer, w empuñar, W armadura,\n"
        << " f disparar, z magia, o abrir puerta, < subir, > bajar.\n"
        << " Ctrl+G chat; Ctrl+] desconectarse.\n\n"
        << "Pulsa cualquier tecla para regresar...\n" << std::flush;
}

void runClient(const std::vector<std::string>& args) {
    const int port = net::parsePort(net::option(args, "puerto", "7777"));
    const std::string name = net::option(args, "nombre", "Aventurero");
    const std::string role = net::option(args, "clase", "guerrero");
    const std::string password = net::option(args, "clave", "");

    if (!validName(name, 24) || !validName(role, 20))
        throw std::runtime_error("Nombre o clase incorrectos.");

    net::Socket socket = net::connect(net::option(args, "ip", "127.0.0.1"), port);
    if (!net::sendFrame(socket, 'H', name + '\n' + role + '\n' + password)) {
        net::closeSocket(socket);
        throw std::runtime_error("No se pudo enviar el registro.");
    }

    nhb::client::Terminal terminal;
    std::mutex screenMutex;
    std::atomic<bool> active{true};
    std::thread incoming([&]() {
        net::Frame frame;
        while (active && net::receiveFrame(socket, frame)) {
            if (frame.type == 'S') {
                std::lock_guard<std::mutex> guard(screenMutex);
                terminal.draw(frame.data);
            } else if (frame.type == 'E') {
                {
                    std::lock_guard<std::mutex> guard(screenMutex);
                    terminal.draw("\x1b[2J\x1b[HERROR: " + frame.data + "\n");
                }
                active = false;
                break;
            } else if (frame.type == 'N') {
                // Los avisos individuales se muestran en la próxima actualización.
            }
        }
        active = false;
    });

    bool chatting = false;
    std::string typed;
    while (active) {
        int key = terminal.pollKey();
        if (key == 0) {
            std::this_thread::sleep_for(std::chrono::milliseconds(25));
            continue;
        }
        if (key == 29 || key == 3) break; // Ctrl+] o Ctrl+C
        if (chatting) {
            if (key == '\r' || key == '\n') {
                if (!typed.empty()) net::sendFrame(socket, 'C', typed);
                chatting = false;
                typed.clear();
                net::sendFrame(socket, 'R', "");
            } else if (key == 27) {
                chatting = false;
                typed.clear();
                net::sendFrame(socket, 'R', "");
            } else if (key == 8 || key == 127) {
                if (!typed.empty()) typed.pop_back();
            } else if (key >= 32 && key <= 126 && typed.size() < 180) {
                typed.push_back(static_cast<char>(key));
            }
            if (chatting) {
                std::lock_guard<std::mutex> guard(screenMutex);
                terminal.draw("\x1b[34;1H\x1b[2KChat: " + typed);
            }
        } else if (key == '?') {
            {
                std::lock_guard<std::mutex> guard(screenMutex);
                guide();
            }
            while (active && terminal.pollKey() == 0)
                std::this_thread::sleep_for(std::chrono::milliseconds(25));
            net::sendFrame(socket, 'R', "");
        } else if (key == 7) {
            chatting = true;
            typed.clear();
            std::lock_guard<std::mutex> guard(screenMutex);
            terminal.draw("\x1b[34;1H\x1b[2KChat: ");
        } else if (key > 0 && key <= 126) {
            net::sendFrame(socket, 'K',
                           std::string(1, static_cast<char>(key)));
        }
    }
    active = false;
    net::shutdownSocket(socket);
    if (incoming.joinable()) incoming.join();
    net::closeSocket(socket);
}

std::string prompt(const std::string& label, const std::string& fallback) {
    std::cout << label << " [" << fallback << "]: " << std::flush;
    std::string value;
    if (!std::getline(std::cin, value))
        throw std::runtime_error("No se pudo leer la entrada de teclado.");
    return value.empty() ? fallback : value;
}

std::string chooseRole() {
    for (;;) {
        std::cout << "\nClase de personaje:\n"
                  << "  1. Guerrero\n  2. Maga\n  3. Pícaro\n  4. Valquiria\n";
        std::string chosen = prompt("Selecciona una clase", "1");
        if (chosen == "1") return "guerrero";
        if (chosen == "2") return "maga";
        if (chosen == "3") return "picaro";
        if (chosen == "4") return "valquiria";
        std::cout << "Opción no válida.\n";
    }
}

int interactiveMenu() {
    std::shared_ptr<Server> localServer;
    for (;;) {
        std::cout << "\x1b[0m\x1b[2J\x1b[H"
                  << "=====================================================\n"
                  << "             NET-HACK BALD - MULTIJUGADOR\n"
                  << "=====================================================\n"
                  << "  1. CREAR PARTIDA Y JUGAR (en este equipo)\n"
                  << "  2. UNIRSE A UNA PARTIDA\n"
                  << "  3. INICIAR SERVIDOR DEDICADO\n"
                  << "  4. AYUDA\n"
                  << "  5. SALIR\n\n"
                  << "  Cada jugador es un personaje distinto (de 2 a 6).\n"
                  << "  Modo C++ propio, aún no equivale a NetHack 1:1.\n\n";
        std::string selected = prompt("Opción", "1");
        if (selected == "5") return 0;
        if (selected == "4") {
            guide();
            std::string ignored;
            std::getline(std::cin, ignored);
            continue;
        }
        try {
            if (selected == "1") {
                if (!localServer) {
                    localServer = std::make_shared<Server>(
                        "127.0.0.1", 7777, "", "partida-multi.nhb");
                    auto background = localServer;
                    std::thread([background] {
                        try { background->run(); }
                        catch (const std::exception& error) {
                            std::cerr << "\nError del servidor: " << error.what()
                                      << "\n" << std::flush;
                        }
                    }).detach();
                    // El servidor abre su socket en el hilo anterior.
                    std::this_thread::sleep_for(std::chrono::milliseconds(350));
                }
                std::string name = prompt("Nombre de tu personaje", "Jugador1");
                std::string role = chooseRole();
                runClient({"cliente", "--ip=127.0.0.1",
                           "--nombre=" + name, "--clase=" + role});
            } else if (selected == "2") {
                std::string address = prompt("IP del servidor", "127.0.0.1");
                std::string port = prompt("Puerto TCP", "7777");
                std::string name = prompt("Nombre de tu personaje", "Jugador2");
                std::string role = chooseRole();
                std::string key = prompt("Contraseña (vacía si es local)", "");
                runClient({"cliente", "--ip=" + address, "--puerto=" + port,
                           "--nombre=" + name, "--clase=" + role,
                           "--clave=" + key});
            } else if (selected == "3") {
                std::string address = prompt("IP donde escuchar", "127.0.0.1");
                std::string port = prompt("Puerto TCP", "7777");
                std::string key = prompt("Contraseña (obligatoria en LAN)", "");
                Server server(address, net::parsePort(port), key,
                              "partida-multi.nhb");
                server.run();
            } else {
                std::cout << "Opción desconocida.\n";
            }
        } catch (const std::exception& error) {
            std::cerr << "\nNo se pudo iniciar la opción: " << error.what()
                      << "\nEl programa permanecerá abierto.\n";
        }
        std::cout << "\nPulsa Intro para regresar al menú..."
                  << std::flush;
        std::string ignored;
        if (!std::getline(std::cin, ignored)) return 1;
    }
}

void usage() {
    std::cout
        << "NET-HACK BALD - C++17, Windows/Linux\n"
        << "Modo propio de 2-6 personajes independientes.\n\n"
        << "Servidor:\n"
        << "  nethack-bald servidor --bind=127.0.0.1 --puerto=7777\n"
        << "  nethack-bald servidor --bind=0.0.0.0 --clave=SECRETO\n\n"
        << "Clientes:\n"
        << "  nethack-bald cliente --ip=127.0.0.1 --nombre=Ada --clase=maga\n"
        << "  nethack-bald cliente --ip=127.0.0.1 --nombre=Bran --clase=guerrero\n"
        << "Clases: guerrero, maga, picaro, valquiria.\n\n"
        << "El código del NetHack original se encuentra en upstream/nethack.\n"
        << "Este modo todavía no reproduce íntegramente el NetHack original.\n";
}
} // namespace

int main(int argc, char* argv[]) {
#ifndef _WIN32
    std::signal(SIGPIPE, SIG_IGN);
#endif
    try {
        net::Runtime runtime;
        std::vector<std::string> args;
        for (int i = 1; i < argc; ++i) args.emplace_back(argv[i]);
        if (args.empty()) return interactiveMenu();
        const int port = net::parsePort(net::option(args, "puerto", "7777"));
        if (args[0] == "servidor") {
            Server server(net::option(args, "bind", "127.0.0.1"),
                          port, net::option(args, "clave", ""),
                          net::option(args, "guardar", "partida-multi.nhb"));
            server.run();
        } else if (args[0] == "cliente") {
            runClient(args);
        } else {
            usage();
            return 2;
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
#ifdef _WIN32
        // Conserva el mensaje de error al iniciar mediante doble clic.
        std::cerr << "Pulsa Intro para cerrar..." << std::flush;
        std::string ignored;
        std::getline(std::cin, ignored);
#endif
        return 1;
    }
}
