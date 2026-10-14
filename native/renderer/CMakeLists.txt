# Temporary renderer: shadPS4's video_core + shader_recompiler, built from an external
# shadPS4 checkout (GPL-2.0-or-later) with d1-native shims for the emulator core.
# Long term this is replaced by a Rust/Vulkan renderer.
set(SHADPS4_DIR "" CACHE PATH "shadPS4 source checkout (commit e0a46675 tested)")
if(NOT EXISTS "${SHADPS4_DIR}/src/video_core/amdgpu/liverpool.cpp")
  message(FATAL_ERROR "set SHADPS4_DIR to a shadPS4 checkout with submodules vulkan-headers, vma, sirit, robin-map, xxhash, ext-boost, magic_enum, fmt, half, tracy")
endif()
set(S ${SHADPS4_DIR})
set(X ${SHADPS4_DIR}/externals)

# Vulkan is loaded at run time (vulkan-1.dll / libvulkan.so.1); only headers are needed.
if(WIN32)
  set(ABSL_PROPAGATE_CXX_STD ON CACHE BOOL "" FORCE)
  set(ABSL_BUILD_TESTING OFF CACHE BOOL "" FORCE)
  add_subdirectory(${X}/abseil-cpp ${CMAKE_CURRENT_BINARY_DIR}/abseil EXCLUDE_FROM_ALL)
else()
  find_package(Vulkan REQUIRED)
  find_package(absl REQUIRED)
endif()
find_program(GLSLANG glslangValidator REQUIRED)

# third-party pieces
set(SIRIT_USE_SYSTEM_SPIRV_HEADERS OFF CACHE BOOL "" FORCE)
add_subdirectory(${X}/sirit ${CMAKE_CURRENT_BINARY_DIR}/sirit EXCLUDE_FROM_ALL)
set(FMT_INSTALL OFF CACHE BOOL "" FORCE)
add_subdirectory(${X}/fmt ${CMAKE_CURRENT_BINARY_DIR}/fmt EXCLUDE_FROM_ALL)
set(ZYDIS_BUILD_TOOLS OFF CACHE BOOL "" FORCE)
set(ZYDIS_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
add_subdirectory(${X}/zydis ${CMAKE_CURRENT_BINARY_DIR}/zydis EXCLUDE_FROM_ALL)
add_library(d1_xxhash STATIC ${X}/xxhash/xxhash.c)
target_include_directories(d1_xxhash PUBLIC ${X}/xxhash)

# host shaders -> SPIR-V headers
set(HS_OUT ${CMAKE_CURRENT_BINARY_DIR}/hs/video_core/host_shaders)
set(HS_HEADERS "")
function(host_shader FILE NAME)
  string(TOUPPER ${NAME} SYM)
  set(DEFS ${ARGN})
  list(TRANSFORM DEFS PREPEND "-D")
  set(OUT ${HS_OUT}/${NAME}.h)
  add_custom_command(OUTPUT ${OUT}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${HS_OUT}
    COMMAND ${GLSLANG} --target-env vulkan1.3 -o ${OUT} --vn ${SYM} ${DEFS} ${S}/src/video_core/host_shaders/${FILE}
    COMMAND ${CMAKE_COMMAND} "-DHEADER_FILE=${OUT}" -P ${S}/src/video_core/host_shaders/AddShaderHeaderInclude.cmake
    DEPENDS ${S}/src/video_core/host_shaders/${FILE} VERBATIM)
  set(HS_HEADERS ${HS_HEADERS} ${OUT} PARENT_SCOPE)
endfunction()
host_shader(color_to_ms_depth.frag color_to_ms_depth_frag)
host_shader(ms_image_blit.frag ms_image_blit_frag)
host_shader(ms_image_blit.frag ms_image_blit_msaa_frag SRC_MSAA=1)
host_shader(fault_buffer_process.comp fault_buffer_process_comp)
host_shader(fs_tri.vert fs_tri_vert)
host_shader(fsr.comp fsr_easu_comp SAMPLE_EASU=1)
host_shader(fsr.comp fsr_rcas_comp SAMPLE_RCAS=1)
host_shader(post_process.frag post_process_frag)
foreach(BPP 8 16 32 64 96 128)
  host_shader(tiling.comp tiling_micro_${BPP}_comp BITS_PER_PIXEL=${BPP} IS_MACRO_TILED=0)
  host_shader(tiling.comp tiling_macro_${BPP}_comp BITS_PER_PIXEL=${BPP} IS_MACRO_TILED=1)
endforeach()
add_custom_target(d1_host_shaders DEPENDS ${HS_HEADERS})

file(STRINGS ${CMAKE_CURRENT_SOURCE_DIR}/sources.txt REL_SOURCES)
# Fixes to shadPS4 sources live in patches/*.patch (unified diffs against the checkout). Each
# patched file is copied into the build tree, patched there and compiled instead of the
# original, so the checkout itself is never modified.
find_program(PATCH_EXE patch REQUIRED)
file(GLOB D1_SHAD_PATCHES ${CMAKE_CURRENT_SOURCE_DIR}/patches/*.patch)
list(SORT D1_SHAD_PATCHES)
set(D1_PATCHED ${CMAKE_CURRENT_BINARY_DIR}/shad_patched)
set(D1_PATCHED_FILES "")
foreach(P ${D1_SHAD_PATCHES})
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${P})
  file(STRINGS ${P} PLINES REGEX "^\\+\\+\\+ b/")
  foreach(L ${PLINES})
    string(REGEX REPLACE "^\\+\\+\\+ b/([^\t ]+).*" "\\1" F "${L}")
    if(NOT F IN_LIST D1_PATCHED_FILES)
      list(APPEND D1_PATCHED_FILES ${F})
      get_filename_component(FD ${D1_PATCHED}/${F} DIRECTORY)
      file(MAKE_DIRECTORY ${FD})
      file(COPY_FILE ${S}/${F} ${D1_PATCHED}/${F})
    endif()
  endforeach()
endforeach()
foreach(P ${D1_SHAD_PATCHES})
  execute_process(COMMAND ${PATCH_EXE} -p1 --forward --batch -i ${P}
                  WORKING_DIRECTORY ${D1_PATCHED} RESULT_VARIABLE PR OUTPUT_VARIABLE PO ERROR_VARIABLE PO)
  if(NOT PR EQUAL 0)
    message(FATAL_ERROR "applying ${P} failed:\n${PO}")
  endif()
endforeach()
set(ABS_SOURCES "")
foreach(F ${REL_SOURCES})
  if(F IN_LIST D1_PATCHED_FILES)
    list(APPEND ABS_SOURCES ${D1_PATCHED}/${F})
  else()
    list(APPEND ABS_SOURCES ${S}/${F})
  endif()
endforeach()
set(REL_SOURCES ${ABS_SOURCES})
find_package(SDL2 REQUIRED)
add_library(d1_shad_video STATIC ${REL_SOURCES}
  ${CMAKE_CURRENT_SOURCE_DIR}/glue/glue_common.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/glue/core_glue.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/glue/d1_renderer.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/glue/d1_window.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/glue/d1_present.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/glue/gpu_profiler.cpp)
add_dependencies(d1_shad_video d1_host_shaders)
target_compile_features(d1_shad_video PRIVATE cxx_std_23)
# shims first so they override emulator-core headers
target_include_directories(d1_shad_video PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/shim ${S}/src ${S} ${CMAKE_CURRENT_BINARY_DIR}/hs
  ${X}/vulkan-headers/include ${X}/vma/include ${X}/robin-map/include ${X}/magic_enum/include
  ${X}/half/include ${X}/ext-boost ${X}/tracy/public ${X}/stb)
target_compile_definitions(d1_shad_video PRIVATE BOOST_ASIO_STANDALONE)
target_compile_options(d1_shad_video PRIVATE -w -fno-strict-aliasing)
target_link_libraries(d1_shad_video PUBLIC sirit fmt::fmt d1_xxhash Zydis absl::flat_hash_map)
if(WIN32)
  # MinGW cross build: header case aliases, xbyak, Windows 10 1809 APIs (CreateFileMapping2).
  target_include_directories(d1_shad_video PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/shim/win ${X}/xbyak ${SDL2_INCLUDE_DIRS})
  target_compile_definitions(d1_shad_video PRIVATE _WIN32_WINNT=0x0A00 NTDDI_VERSION=0x0A000006 NOMINMAX)
  target_link_libraries(d1_shad_video PUBLIC SDL2::SDL2-static onecore ntdll)  # no SDL2.dll next to the exe
else()
  target_link_libraries(d1_shad_video PUBLIC Vulkan::Vulkan SDL2::SDL2)
endif()
