include(FetchContent)

find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
  FetchContent_Declare(nlohmann_json URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz)
  FetchContent_MakeAvailable(nlohmann_json)
endif()

find_package(libzippp QUIET)
if(NOT libzippp_FOUND)
  FetchContent_Declare(libzippp URL https://github.com/ctabin/libzippp/archive/refs/tags/libzippp-v6.1-1.9.2.tar.gz)
  FetchContent_MakeAvailable(libzippp)

  add_compile_definitions(LOCAL_LIBZIPPP)
endif()

find_package(platform_folders QUIET)
if(NOT platform_folders_FOUND)
  FetchContent_Declare(platform_folders URL https://github.com/sago007/PlatformFolders/archive/refs/tags/4.2.0.tar.gz)
  FetchContent_MakeAvailable(platform_folders)

  add_compile_definitions(LOCAL_PLATFORM_FOLDERS)
endif()

find_package(tomlplusplus QUIET)
if(NOT tomlplusplus_FOUND)
  FetchContent_Declare(
      tomlplusplus
      GIT_REPOSITORY https://github.com/marzer/tomlplusplus.git
      GIT_TAG        v3.3.0
  )
  FetchContent_MakeAvailable(tomlplusplus)
endif()

find_package(cpr QUIET)
if(NOT cpr_FOUND)
  FetchContent_Declare(cpr GIT_REPOSITORY https://github.com/libcpr/cpr.git
                          GIT_TAG 32fd1453194c37d5136577ee55629b863a42333f)
  if(NOT cpr_POPULATED)
      FetchContent_Populate(cpr)
      add_subdirectory(${cpr_SOURCE_DIR} ${cpr_BINARY_DIR} EXCLUDE_FROM_ALL)
  endif()
endif()

if(CORK_PLUGINS)
  set(SOL2_BUILD_LUA OFF)
  find_package(sol2 QUIET)
  if(NOT sol2_FOUND)
    FetchContent_Declare(sol2 GIT_REPOSITORY https://github.com/ThePhD/sol2.git
    GIT_TAG 9c882a28fdb6f4ad79a53a4191b43ce48a661175)
    FetchContent_MakeAvailable(sol2)
  endif()
  find_package(Lua REQUIRED)
endif()

find_package(OpenSSL REQUIRED)
find_package(Boost COMPONENTS system log REQUIRED)

if (WIN32)
  add_compile_definitions(NATIVE_RUNNER)
else()
  add_compile_definitions(WINE_RUNNER)
endif()

if(CORK_PLUGINS)
  add_compile_definitions(PLUGINS_ENABLED)
endif()

add_compile_definitions(CORK_VERSION="${PROJECT_VERSION}")
add_compile_definitions(CORK_CODENAME="Cape Canaveral")

add_executable(cork main.cpp)

add_subdirectory(roblox)
add_subdirectory(runners)
add_subdirectory(bootstrapper)
add_subdirectory(settings)

target_link_libraries(cork
  PRIVATE
    cpr::cpr
    nlohmann_json::nlohmann_json
    libzippp::libzippp
    tomlplusplus::tomlplusplus
    sago::platform_folders
    ${Boost_SYSTEM_LIBRARY}
    ${Boost_LOG_LIBRARY}
    OpenSSL::Crypto
    roblox
    runners
    bootstrapper
    settings
)

if(CORK_PLUGINS)
  target_link_libraries(cork
    PRIVATE
      sol2::sol2
      ${LUA_LIBRARIES}
  )
endif()