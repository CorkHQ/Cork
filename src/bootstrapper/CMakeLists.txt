add_library(bootstrapper "")

target_sources(bootstrapper
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/session.cpp
    ${CMAKE_CURRENT_LIST_DIR}/installer.cpp
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/session.hpp
    ${CMAKE_CURRENT_LIST_DIR}/installer.hpp
)

target_include_directories(bootstrapper
  PRIVATE
    ../roblox
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)
target_link_libraries(bootstrapper
  PRIVATE
    roblox
    cpr::cpr
    elzip
)