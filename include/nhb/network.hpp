#pragma once

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#endif

namespace nhb::net {

#ifdef _WIN32
using Socket = SOCKET;
constexpr Socket kInvalidSocket = INVALID_SOCKET;
#else
using Socket = int;
constexpr Socket kInvalidSocket = -1;
#endif

// Protocolo binario con longitud explícita. Todas las cadenas son UTF-8.
// H: login, K: orden, C: chat; S: vista individual, N: aviso, E: error.
struct Frame {
    char type = 0;
    std::string data;
};

class Runtime {
public:
    Runtime();
    ~Runtime();
    Runtime(const Runtime&) = delete;
    Runtime& operator=(const Runtime&) = delete;
};

void closeSocket(Socket socket);
void shutdownSocket(Socket socket);
bool sendFrame(Socket socket, char type, const std::string& data);
bool receiveFrame(Socket socket, Frame& frame);
Socket listen(const std::string& address, int port);
Socket connect(const std::string& address, int port);
Socket accept(Socket listener);
std::string option(const std::vector<std::string>& args,
                   const std::string& name, const std::string& fallback);
int parsePort(const std::string& value);

} // namespace nhb::net
