cmake_minimum_required(VERSION 3.5.0)
project(cork VERSION 2.0.0 LANGUAGES C CXX)
set (CMAKE_CXX_STANDARD 20)

include(CTest)
enable_testing()

add_compile_definitions(CORK_VERSION="${PROJECT_VERSION}")
add_compile_definitions(CORK_CODENAME="Cape Canaveral")

add_subdirectory(src)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
