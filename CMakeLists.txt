cmake_minimum_required(VERSION 3.5.0)
project(cork VERSION 2.0.0 LANGUAGES C CXX)

include(CTest)
enable_testing()

add_subdirectory(src)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
