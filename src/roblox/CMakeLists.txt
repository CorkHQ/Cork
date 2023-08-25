add_library(roblox "")

target_sources(roblox
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/cdn.cpp
    ${CMAKE_CURRENT_LIST_DIR}/version.cpp
    ${CMAKE_CURRENT_LIST_DIR}/packages.cpp
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/cdn.hpp
    ${CMAKE_CURRENT_LIST_DIR}/version.hpp
    ${CMAKE_CURRENT_LIST_DIR}/packages.hpp
)

target_include_directories(roblox
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)
target_link_libraries(roblox
  PRIVATE
    nlohmann_json::nlohmann_json
    cpr::cpr
)