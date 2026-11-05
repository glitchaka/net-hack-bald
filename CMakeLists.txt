cmake_minimum_required(VERSION 3.16)
project(nethack_bald VERSION 0.2.0 LANGUAGES CXX)

add_executable(nethack-bald-multi)
target_compile_features(nethack-bald-multi PRIVATE cxx_std_17)
set_target_properties(nethack-bald-multi PROPERTIES
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

if(WIN32)
    # Cliente Windows nativo: servidor original disponible en Linux/WSL.
    target_sources(nethack-bald-multi PRIVATE multiplayer/client_windows.cpp)
    target_compile_definitions(nethack-bald-multi PRIVATE _WIN32_WINNT=0x0601)
    target_link_libraries(nethack-bald-multi PRIVATE ws2_32)
    if(MSVC)
        target_compile_options(nethack-bald-multi PRIVATE /W4 /utf-8)
    endif()
else()
    # En Linux/macOS este ejecutable admite servidor y cliente.
    find_package(Threads REQUIRED)
    target_sources(nethack-bald-multi PRIVATE multiplayer/main.cpp)
    target_link_libraries(nethack-bald-multi PRIVATE Threads::Threads)
    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        find_library(UTIL_LIBRARY util)
        if(UTIL_LIBRARY)
            target_link_libraries(nethack-bald-multi PRIVATE util)
        endif()
    endif()
    target_compile_options(nethack-bald-multi PRIVATE -Wall -Wextra -Wpedantic)
endif()
