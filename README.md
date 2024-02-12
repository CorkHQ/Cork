<p align="center">
    <br/>
    <img src="https://github.com/Bugadinho/Cork/raw/master/resources/cork.svg" height="250"/>
    <br/>
    <h1>Cork</h1>
<p>

[![Version](https://img.shields.io/github/v/release/CorkHQ/Cork?display_name=tag)](https://github.com/CorkHQ/Cork/releases/latest)
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
Felt like trying to get Roblox to run on your Ampere Altra or your Talos II? Cork has got you covered on at least getting the launcher built. Every single part of the bootstrapper is modular and does not depend on any specific operating system or environment, compiles on any platform that supports modern versions of C++.

## Supported Platforms
| Operating System | Architecture | Runner | Support |
| --- | --- | --- | --- |
| Linux | x86_64 | Proton / Wine | Stable |
| Windows | x86_64 | Native | Stable |

## Installing from Package
RPM and DEB packages are built with GitHub Actions for every commit, you can install those but they are experimental for now. Proper releases for those are coming soon!

## Installing from Source (Linux)
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
#### Clone the Repository
```bash
git clone https://github.com/CorkHQ/Cork.git
cd Cork
```

#### Preparing to Build
```bash
mkdir build
cmake -Bbuild -H. -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DCPR_USE_SYSTEM_CURL=ON
```

#### Building
```bash
cd build
cmake --build . --target all
```

#### Installing
```bash
cmake --install . --prefix ~/.local
```

## Installing from Source (Windows)
Visual Studio wth VCPKG and CMake is enough to build this, but proper instructions are W.I.P

## Documentation
**W.I.P**

## "Why should I use this over Grapejuice or Vinegar?"
Maybe you should, maybe you shouldn't. All of the current solutions for running Roblox on Linux offer something over the other, there is no better or worse one, use whatever suits **you**.

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