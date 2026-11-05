cmake_minimum_required(VERSION 3.16)
project(NetHackBald VERSION 0.3.0 LANGUAGES CXX)

# Juego nativo en Windows / Linux: seis personajes independientes.
# El motor original NetHack 5.0 permanece separado en upstream/nethack.
add_executable(nethack-bald
    src/multiplayer/main.cpp
    src/multiplayer/network.cpp
    src/multiplayer/terminal.cpp
    src/multiplayer/world_gen.cpp
    src/multiplayer/world_turns.cpp
    src/multiplayer/world_view.cpp
    src/multiplayer/world_save.cpp
)

target_include_directories(nethack-bald PRIVATE include)
target_compile_features(nethack-bald PRIVATE cxx_std_17)
set_target_properties(nethack-bald PROPERTIES
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)
find_package(Threads REQUIRED)
target_link_libraries(nethack-bald PRIVATE Threads::Threads)
if(WIN32)
    target_compile_definitions(nethack-bald PRIVATE
        _WIN32_WINNT=0x0601
        WIN32_LEAN_AND_MEAN
        NOMINMAX)
    target_link_libraries(nethack-bald PRIVATE ws2_32)
    if(MSVC)
        target_compile_options(nethack-bald PRIVATE /W4 /utf-8)
    endif()
else()
    target_compile_options(nethack-bald PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Solo se crea el ejecutable del modo 2-6. El antiguo nethack-bald-multi
# (una persona controlando un único héroe) ya no forma parte del build.
