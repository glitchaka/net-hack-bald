cmake_minimum_required(VERSION 3.20)

# El objetivo predeterminado es el NET-HACK ORIGINAL en modo grafico nativo.
# No se compila el prototipo de consola en este proyecto.
if(NOT WIN32)
    message(FATAL_ERROR "NetHack Bald se compila exclusivamente en Windows.")
endif()

project(NetHackBald VERSION 0.4.0 LANGUAGES NONE)

find_program(NHB_POWERSHELL powershell.exe REQUIRED)
add_custom_target(nethack-original ALL
    COMMAND "${NHB_POWERSHELL}"
        -NoProfile -ExecutionPolicy Bypass
        -File "${CMAKE_SOURCE_DIR}/scripts/compilar-nethack-original.ps1"
        -Root "${CMAKE_SOURCE_DIR}"
        -Configuration "$<CONFIG>"
        -Platform x64
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    COMMENT "Construyendo el motor original NetHack 5.0 para Windows (NetHackW.exe)"
    VERBATIM
    USES_TERMINAL
)

# El experimento src/multiplayer/ no es fiel 1:1 y no forma parte del
# ejecutable original. La extension de 2-6 personajes sigue pendiente.
