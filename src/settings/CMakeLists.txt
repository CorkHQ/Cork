add_library(settings "")

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
    tomlplusplus
    sago::platform_folders
)