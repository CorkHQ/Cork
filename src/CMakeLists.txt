include(FetchContent)

FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz)
FetchContent_MakeAvailable(json)

FetchContent_Declare(libzippp URL https://github.com/ctabin/libzippp/archive/refs/tags/libzippp-v6.1-1.9.2.tar.gz)
FetchContent_MakeAvailable(libzippp)

FetchContent_Declare(
    tomlplusplus
    GIT_REPOSITORY https://github.com/marzer/tomlplusplus.git
    GIT_TAG        v3.3.0
)
FetchContent_MakeAvailable(tomlplusplus)

FetchContent_Declare(platform_folders URL https://github.com/sago007/PlatformFolders/archive/refs/tags/4.2.0.tar.gz)
FetchContent_MakeAvailable(platform_folders)

FetchContent_Declare(cpr GIT_REPOSITORY https://github.com/libcpr/cpr.git
                         GIT_TAG 32fd1453194c37d5136577ee55629b863a42333f)
if(NOT cpr_POPULATED)
    FetchContent_Populate(cpr)
    add_subdirectory(${cpr_SOURCE_DIR} ${cpr_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

find_package(Boost COMPONENTS system log REQUIRED)

if (WIN32)
  add_compile_definitions(NATIVE_RUNNER)
else()
  add_compile_definitions(WINE_RUNNER)
endif()

add_executable(cork main.cpp)

add_subdirectory(roblox)
add_subdirectory(runners)
add_subdirectory(bootstrapper)
add_subdirectory(settings)

target_link_libraries(cork
  PRIVATE
    cpr::cpr
    nlohmann_json::nlohmann_json
    libzippp
    tomlplusplus::tomlplusplus
    sago::platform_folders
    ${Boost_SYSTEM_LIBRARY}
    ${Boost_LOG_LIBRARY}
    roblox
    runners
    bootstrapper
    settings
)