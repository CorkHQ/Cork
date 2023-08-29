include(FetchContent)

FetchContent_Declare(cpr GIT_REPOSITORY https://github.com/libcpr/cpr.git
                         GIT_TAG 2553fc41450301cd09a9271c8d2c3e0cf3546b73)
FetchContent_MakeAvailable(cpr)

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

find_package(Boost COMPONENTS system filesystem log REQUIRED)

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
    tomlplusplus
    sago::platform_folders
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${Boost_LOG_LIBRARY}
    roblox
    runners
    bootstrapper
    settings
)