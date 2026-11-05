cmake_minimum_required(VERSION 3.16)
project(nethack_bald VERSION 0.2.0 LANGUAGES CXX)

if(WIN32)
    message(FATAL_ERROR "Servidor multijugador POSIX: usar Linux o WSL.")
endif()

find_package(Threads REQUIRED)
add_executable(nethack-bald-multi multiplayer/main.cpp)
target_compile_features(nethack-bald-multi PRIVATE cxx_std_17)
set_target_properties(nethack-bald-multi PROPERTIES
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
target_link_libraries(nethack-bald-multi PRIVATE Threads::Threads)

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    find_library(UTIL_LIBRARY util)
    if(UTIL_LIBRARY)
        target_link_libraries(nethack-bald-multi PRIVATE util)
    endif()
endif()

target_compile_options(nethack-bald-multi PRIVATE -Wall -Wextra -Wpedantic)
