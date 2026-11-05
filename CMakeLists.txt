cmake_minimum_required(VERSION 3.16)
project(nethack_bald VERSION 0.1.0 LANGUAGES CXX)

add_executable(nethack-bald
    src/main.cpp
    src/terminal.cpp
    src/dungeon.cpp
    src/game.cpp
    src/actions.cpp
    src/save.cpp
)

target_include_directories(nethack-bald PRIVATE include)
target_compile_features(nethack-bald PRIVATE cxx_std_17)
set_target_properties(nethack-bald PROPERTIES
    CXX_STANDARD_REQUIRED YES
    CXX_EXTENSIONS NO
)

if (MSVC)
    target_compile_options(nethack-bald PRIVATE /W4 /utf-8)
else()
    target_compile_options(nethack-bald PRIVATE -Wall -Wextra -Wpedantic)
endif()
