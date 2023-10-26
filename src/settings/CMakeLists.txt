add_library(settings STATIC "")
target_compile_features(settings PUBLIC cxx_std_20)

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