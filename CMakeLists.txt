cmake_minimum_required(VERSION 3.10)
project(Wordsploit VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(OpenSSL REQUIRED)
find_package(CURL REQUIRED)
find_package(SQLite3 REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${OPENSSL_INCLUDE_DIR})
include_directories(${CURL_INCLUDE_DIR})

# Core library
add_library(wordsploit_core
    src/core/engine.cpp
    src/core/plugin_manager.cpp
    src/core/config_manager.cpp
    src/core/logger.cpp
    src/core/database.cpp
)

target_link_libraries(wordsploit_core
    ${OPENSSL_LIBRARIES}
    ${CURL_LIBRARIES}
    ${SQLITE3_LIBRARIES}
)

# Modules
add_subdirectory(src/modules/reconnaissance)
add_subdirectory(src/modules/scanning)
add_subdirectory(src/modules/exploitation)
add_subdirectory(src/modules/payload_generation)
add_subdirectory(src/modules/post_exploitation)
add_subdirectory(src/modules/reporting)
add_subdirectory(src/modules/metasploit_integration)
add_subdirectory(src/modules/wordlist_management)
add_subdirectory(src/modules/network_analysis)
add_subdirectory(src/modules/forensics)

# Main executable
add_executable(wordsploit src/main.cpp)
target_link_libraries(wordsploit
    wordsploit_core
    reconnaissance_module
    scanning_module
    exploitation_module
    payload_module
    post_exploit_module
    reporting_module
    metasploit_module
    wordlist_module
    network_module
    forensics_module
)

# Tests
add_subdirectory(tests)

install(TARGETS wordsploit DESTINATION bin)
