add_library(runners STATIC "")
target_compile_features(runners PUBLIC cxx_std_20)

target_sources(runners
  PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/native.cpp
    ${CMAKE_CURRENT_LIST_DIR}/wine.cpp
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/native.hpp
    ${CMAKE_CURRENT_LIST_DIR}/wine.hpp
)

target_include_directories(runners
  PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}
)
target_link_libraries(runners
  PRIVATE
    ${Boost_SYSTEM_LIBRARY}
    ${Boost_LOG_LIBRARY}
)