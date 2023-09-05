cmake_minimum_required(VERSION 3.5.0)
project(cork VERSION 2.0.0 LANGUAGES C CXX)
set (CMAKE_CXX_STANDARD 20)

include(CTest)
enable_testing()

add_compile_definitions(CORK_VERSION="${PROJECT_VERSION}")
add_compile_definitions(CORK_CODENAME="Cape Canaveral")

add_subdirectory(src)

install(TARGETS cork)
if(UNIX AND NOT APPLE)
    install(FILES resources/cork.svg DESTINATION share/icons/hicolor/scalable/apps)
    install(FILES resources/roblox-player.svg DESTINATION share/icons/hicolor/scalable/apps)
    install(FILES resources/roblox-studio.svg DESTINATION share/icons/hicolor/scalable/apps)
    install(FILES distribution/roblox-player.desktop DESTINATION share/applications)
    install(FILES distribution/roblox-studio.desktop DESTINATION share/applications)
endif()

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
