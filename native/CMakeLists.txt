cmake_minimum_required(VERSION 3.16)
project(d1_native CXX)

if(NOT CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
  message(FATAL_ERROR "d1-native runs the game's x86-64 code directly; it needs an x86-64 host")
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE RelWithDebInfo)
endif()

find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_package(Threads REQUIRED)

# NID -> name table for imports we have not implemented (log readability only).
set(IMPORT_SURFACE ${CMAKE_CURRENT_SOURCE_DIR}/../evidence/generated/d1_import_surface.json)
set(IMPORT_NAMES ${CMAKE_CURRENT_BINARY_DIR}/import_names.inc)
add_custom_command(
  OUTPUT ${IMPORT_NAMES}
  COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/gen_import_names.py ${IMPORT_SURFACE} ${IMPORT_NAMES}
  DEPENDS ${IMPORT_SURFACE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/gen_import_names.py)

add_executable(d1-native
  src/main.cpp
  src/loader.cpp
  src/runtime.cpp
  src/hle_kernel.cpp
  src/hle_pthread.cpp
  src/hle_services.cpp
  src/hle_input.cpp
  src/hle_gpu.cpp
  src/hle_audio.cpp
  src/hle_net.cpp
  src/hle_http.cpp
  src/hooks.cpp
  ${IMPORT_NAMES})
target_include_directories(d1-native PRIVATE src ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(d1-native PRIVATE Threads::Threads)
target_compile_options(d1-native PRIVATE -Wall -Wno-unused-function -fno-omit-frame-pointer)
