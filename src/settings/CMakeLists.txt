add_library(settings STATIC "")

set(CORK_VENDOR_PATH "" CACHE STRING "Path to look for defaults")
add_compile_definitions(CORK_VENDOR_PATH="${CORK_VENDOR_PATH}")

target_sources(settings
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/settings.cpp
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/settings.hpp
)

target_include_directories(settings
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)
target_link_libraries(settings
  PRIVATE
    tomlplusplus::tomlplusplus
    sago::platform_folders
)