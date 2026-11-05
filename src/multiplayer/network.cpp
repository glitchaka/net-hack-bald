#include "nhb/network.hpp"

#include <array>
#include <cerrno>
#include <climits>
#include <cstdint>
#include <stdexcept>
#include <string>

#ifndef _WIN32
#include <arpa/inet.h>
#endif

namespace nhb::net {
namespace {
constexpr uint32_t kMaxPayload = 131072;

bool transmit(Socket fd, const char* data, std::size_t size) {
    while (size) {
        int length = static_cast<int>(std::min<std::size_t>(size, INT_MAX));
        int sent = ::send(fd, data, length, 0);
        if (sent <= 0) {
#ifndef _WIN32
            if (sent < 0 && errno == EINTR) continue;
#endif
            return false;
        }
        data += sent;
        size -= static_cast<std::size_t>(sent);
    }
    return true;
}
bool receive(Socket fd, char* data, std::size_t size) {
    while (size) {
        int length = static_cast<int>(std::min<std::size_t>(size, INT_MAX));
        int got = ::recv(fd, data, length, 0);
        if (got <= 0) {
#ifndef _WIN32
            if (got < 0 && errno == EINTR) continue;
#endif
            return false;
        }
        data += got;
        size -= static_cast<std::size_t>(got);
    }
    return true;
}
} // namespace

Runtime::Runtime() {
#ifdef _WIN32
    WSADATA info{};
    if (WSAStartup(MAKEWORD(2,2), &info) != 0)
        throw std::runtime_error("Error al iniciar Winsock.");
#endif
}
Runtime::~Runtime() {
#ifdef _WIN32
    WSACleanup();
#endif
}
void closeSocket(Socket fd) {
    if (fd == kInvalidSocket) return;
#ifdef _WIN32
    ::closesocket(fd);
#else
    ::close(fd);
#endif
}
void shutdownSocket(Socket fd) {
    if (fd == kInvalidSocket) return;
#ifdef _WIN32
    ::shutdown(fd, SD_BOTH);
#else
    ::shutdown(fd, SHUT_RDWR);
#endif
}
bool sendFrame(Socket fd, char type, const std::string& data) {
    if (data.size() > kMaxPayload) return false;
    uint32_t count = static_cast<uint32_t>(data.size());
    std::array<char, 5> header{
        type,
        static_cast<char>((count >> 24) & 255),
        static_cast<char>((count >> 16) & 255),
        static_cast<char>((count >> 8) & 255),
        static_cast<char>(count & 255)
    };
    return transmit(fd, header.data(), header.size()) &&
           transmit(fd, data.data(), data.size());
}
bool receiveFrame(Socket fd, Frame& frame) {
    std::array<char, 5> header{};
    if (!receive(fd, header.data(), header.size())) return false;
    uint32_t length =
        (static_cast<uint32_t>(static_cast<unsigned char>(header[1])) << 24) |
        (static_cast<uint32_t>(static_cast<unsigned char>(header[2])) << 16) |
        (static_cast<uint32_t>(static_cast<unsigned char>(header[3])) << 8) |
        static_cast<uint32_t>(static_cast<unsigned char>(header[4]));
    if (length > kMaxPayload) return false;
    frame.type = header[0];
    frame.data.resize(length);
    return length == 0 || receive(fd, frame.data.data(), length);
}

int parsePort(const std::string& value) {
    std::size_t parsed = 0;
    int port = 0;
    try { port = std::stoi(value, &parsed); }
    catch (...) { throw std::runtime_error("Puerto TCP incorrecto."); }
    if (parsed != value.size() || port < 1 || port > 65535)
        throw std::runtime_error("El puerto debe estar entre 1 y 65535.");
    return port;
}
std::string option(const std::vector<std::string>& args,
                   const std::string& name, const std::string& fallback) {
    const std::string prefix = "--" + name + "=";
    for (const std::string& arg : args)
        if (arg.compare(0, prefix.size(), prefix) == 0)
            return arg.substr(prefix.size());
    return fallback;
}
Socket listen(const std::string& address, int port) {
    Socket fd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (fd == kInvalidSocket)
        throw std::runtime_error("No se pudo crear el servidor TCP.");
    int reuse = 1;
#ifdef _WIN32
    ::setsockopt(fd, SOL_SOCKET, SO_REUSEADDR,
                 reinterpret_cast<const char*>(&reuse), sizeof(reuse));
#else
    ::setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#endif
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(port));
#ifdef _WIN32
    int valid = ::InetPtonA(AF_INET, address.c_str(), &addr.sin_addr);
#else
    int valid = ::inet_pton(AF_INET, address.c_str(), &addr.sin_addr);
#endif
    if (valid != 1 ||
        ::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0 ||
        ::listen(fd, 8) != 0) {
        closeSocket(fd);
        throw std::runtime_error("No se pudo iniciar la escucha en " +
                                  address + ":" + std::to_string(port));
    }
    return fd;
}
Socket connect(const std::string& address, int port) {
    Socket fd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (fd == kInvalidSocket)
        throw std::runtime_error("No se pudo crear conexión TCP.");
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(port));
#ifdef _WIN32
    int valid = ::InetPtonA(AF_INET, address.c_str(), &addr.sin_addr);
#else
    int valid = ::inet_pton(AF_INET, address.c_str(), &addr.sin_addr);
#endif
    if (valid != 1 ||
        ::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
        closeSocket(fd);
        throw std::runtime_error("No se puede conectar al servidor.");
    }
    return fd;
}
Socket accept(Socket listener) {
    return ::accept(listener, nullptr, nullptr);
}
} // namespace nhb::net
