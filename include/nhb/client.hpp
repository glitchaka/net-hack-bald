#pragma once

#include <string>

namespace nhb::client {

class Terminal {
public:
    Terminal();
    ~Terminal();
    Terminal(const Terminal&) = delete;
    Terminal& operator=(const Terminal&) = delete;

    // Devuelve 0 cuando no hay ninguna tecla disponible.
    int pollKey();
    void draw(const std::string& value);

private:
    bool active_ = false;
#ifdef _WIN32
    void* handle_ = nullptr;
    unsigned long oldMode_ = 0;
#else
    // No incluir encabezados POSIX en la interfaz pública.
    struct TermiosBackup;
    TermiosBackup* saved_ = nullptr;
#endif
};

} // namespace nhb::client
