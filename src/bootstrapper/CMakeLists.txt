add_library(bootstrapper STATIC "")

target_sources(bootstrapper
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/environment.cpp
    ${CMAKE_CURRENT_LIST_DIR}/installer.cpp
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/environment.hpp
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
    ${Boost_LOG_LIBRARY}
    nlohmann_json::nlohmann_json
    cpr::cpr
    libzippp::libzippp
    OpenSSL::Crypto
)