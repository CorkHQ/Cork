<p align="center">
    <br/>
    <img src="https://github.com/Bugadinho/Cork/raw/master/resources/cork.svg" height="250"/>
    <br/>
    <h1>Cork</h1>
<p>

[![Version](https://img.shields.io/github/v/release/CorkHQ/Cork?display_name=tag)](https://github.com/CorkHQ/Cork/releases/latest)
[![Windows Build (amd64)](https://img.shields.io/github/actions/workflow/status/CorkHQ/Cork/build-windows-amd64.yml?logo=windows&label=build+(amd64))](https://github.com/CorkHQ/Cork/actions/workflows/build-windows-amd64.yml)
[![Fedora Package (amd64)](https://img.shields.io/github/actions/workflow/status/CorkHQ/Cork/package-fedora-amd64.yml?logo=fedora&label=package+(amd64))](https://github.com/CorkHQ/Cork/actions/workflows/package-fedora-amd64.yml)
[![Ubuntu Package (amd64)](https://img.shields.io/github/actions/workflow/status/CorkHQ/Cork/package-ubuntu-amd64.yml?logo=ubuntu&label=package+(amd64))](https://github.com/CorkHQ/Cork/actions/workflows/package-ubuntu-amd64.yml)
[![License](https://img.shields.io/github/license/CorkHQ/Cork)](https://github.com/CorkHQ/Cork/blob/master/LICENSE)

A fast, platform-agnostic and minimal bootstrapper for Roblox and Roblox Studio

## Features
### Fast & Lightweight
Cork was rewritten from the ground up to be as fast and as lightweight as possible, by opting for a compiled language and by dropping components such as the splash screen from the main program.
### Mirror Selection
Whenever a version of Roblox starts being downloaded, Cork auto-selects the fastest mirror by running a small benchmark to attempt to get the fastest possible download speeds.
### Extensible
Cork ships with a built-in Lua interpreter for plugins, allowing great portions of the launcher to be changed and allowing features like automatic DXVK installation to be added relatively easily.
### Customizable
Want to run Roblox with [gamescope](https://github.com/ValveSoftware/gamescope), inside of [distrobox](https://github.com/89luca89/distrobox) or [Box64](https://github.com/ptitSeb/box64) for some non-x86 action? Feel like changing some FFlags to mess about? Just do it, the settings are there, it's up to you to tinker.
### Portable
Felt like trying to get Roblox to run on your Ampere Altra or your Talos II? Good luck with that, but Cork has got you covered on at least getting the launcher built. Every single part of the bootstrapper is modular and does not depend on any specific operating system or environment, compiles on any platform that supports modern versions of C++.

## Supported Platforms
| Operating System | Architecture | Runner | Support |
| --- | --- | --- | --- |
| Windows | x86_64 | Native | Full |
| Linux | x86_64 | Proton / Wine | Bootstrapper-only |

## Documentation
**W.I.P**

## Building from Source (Windows)
### Requirements
- Visual Studio 2022
- CMake
- Git
- vcpkg

### Building
#### Cloning the Repository
```bat
git clone https://github.com/CorkHQ/Cork.git
cd Cork
```

#### Preparing to Build
```bat
mkdir build
cmake -Bbuild --preset release-vcpkg
```

#### Building
```bat
cmake --build build/ --preset release-vcpkg --config Release
```

Resulting binaries will be located in the `build/src/Release` directory on the Cork source folder.

## Installing from Package (Linux)
RPM and DEB packages are built with GitHub Actions for every commit, you can install those but they are experimental for now. Proper releases for those are coming soon!

## Building from Source (Linux)
### Dependencies
- Boost
- libzip
    - zlib
    - bzip2
    - xz
- OpenSSL
- cURL
- Lua *(optional, required for plugin support)*

#### Installing dependencies and build tools on Fedora
```bash
sudo dnf install git cmake make automake gcc gcc-c++ rpm-build
sudo dnf install boost-devel libzip-devel zlib-devel bzip2-devel xz-devel openssl-devel curl-devel lua-devel
```

#### Installing dependencies and build tools on Ubuntu
```bash
sudo apt install git build-essential cmake
sudo apt install libboost-all-dev libzip-dev zlib1g-dev libbz2-dev liblzma-dev libssl-dev curl libcurl4-openssl-dev liblua5.4-dev
```

### Building and Installing
#### Cloning the Repository
```bash
git clone https://github.com/CorkHQ/Cork.git
cd Cork
```

#### Preparing to Build
```bash
mkdir build
cmake -Bbuild --preset release
```

#### Building
```bash
cmake --build build/ --preset release --target all
```

#### Installing
```bash
cmake --install build/ --prefix ~/.local
```

## Libraries
Cork makes use of the following libraries:
* [Boost](https://www.boost.org/)
* [toml++](https://github.com/marzer/tomlplusplus)
* [Nlohmann JSON](https://github.com/nlohmann/json)
* [PlatformFolders](https://github.com/sago007/PlatformFolders)
* [libcpr](https://github.com/libcpr/cpr)
* [libzippp]( https://github.com/ctabin/libzippp)
* [sol2](https://github.com/ThePhD/sol2)

## Acknowledgements
Heavily inspired and based on:
* [Vinegar](https://github.com/vinegarhq/vinegar)
* [Grapejuice](https://gitlab.com/brinkervii/grapejuice)
* [Bloxstrap](https://github.com/pizzaboxer/bloxstrap)
* [Roblox Studio Mod Manager](https://github.com/MaximumADHD/Roblox-Studio-Mod-Manager)
