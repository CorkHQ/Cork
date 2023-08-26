include(FetchContent)

FetchContent_Declare(cpr GIT_REPOSITORY https://github.com/libcpr/cpr.git
                         GIT_TAG 2553fc41450301cd09a9271c8d2c3e0cf3546b73)
FetchContent_MakeAvailable(cpr)

FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz)
FetchContent_MakeAvailable(json)

FetchContent_Declare(libzippp URL https://github.com/ctabin/libzippp/archive/refs/tags/libzippp-v6.1-1.9.2.tar.gz)
FetchContent_MakeAvailable(libzippp)

find_package(Boost COMPONENTS system filesystem REQUIRED)

add_executable(cork main.cpp)

add_subdirectory(roblox)
add_subdirectory(runners)
add_subdirectory(bootstrapper)

target_link_libraries(cork
  PRIVATE
    cpr::cpr
    nlohmann_json::nlohmann_json
    libzippp
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    roblox
    runners
    bootstrapper
)