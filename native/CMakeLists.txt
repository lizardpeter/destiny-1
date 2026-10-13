cmake_minimum_required(VERSION 3.16)
project(d1_native C CXX)
if(WIN32)
  enable_language(RC)  # application manifest (UTF-8 code page)
endif()

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
  src/hle_npwebapi.cpp
  src/hooks.cpp
  src/settings.cpp
  src/discord.cpp
  ${IMPORT_NAMES})
if(WIN32)
  target_sources(d1-native PRIVATE src/os_win.cpp win/d1-native.rc)
  # One self-contained .exe: C/C++ runtime and winpthreads linked in statically.
  target_link_libraries(d1-native PRIVATE ws2_32 winmm -static)
  target_compile_definitions(d1-native PRIVATE _FILE_OFFSET_BITS=64 _WIN32_WINNT=0x0A00 WINVER=0x0A00)
else()
  target_sources(d1-native PRIVATE src/os_posix.cpp)
endif()
target_include_directories(d1-native PRIVATE src ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(d1-native PRIVATE Threads::Threads)
target_compile_options(d1-native PRIVATE -Wall -Wno-unused-function -fno-omit-frame-pointer)
if(NOT WIN32)
  # Logs print 64-bit values with %llx (correct on both systems; uint64_t is unsigned long here).
  target_compile_options(d1-native PRIVATE -Wno-format)
endif()

option(D1_RENDERER_SHADPS4 "Build the temporary shadPS4-based renderer (needs SHADPS4_DIR)" OFF)
if(D1_RENDERER_SHADPS4)
  add_subdirectory(renderer)
  target_link_libraries(d1-native PRIVATE d1_shad_video)
  target_compile_definitions(d1-native PRIVATE D1_RENDERER_SHADPS4=1)
else()
  target_sources(d1-native PRIVATE src/render_null.cpp)
endif()
