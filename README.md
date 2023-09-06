<p align="center">
    <br/>
    <img src="https://github.com/Bugadinho/Cork/raw/master/resources/cork.svg" height="250"/>
    <br/>
    <h1>Cork 2 (Cape Canaveral)</h1>
<p>

[![License](https://img.shields.io/github/license/Bugadinho/Cork)](https://github.com/Bugadinho/Cork/blob/master/LICENSE)

> **⚠️ Work in Progress**<br>
> This version of Cork is a full rewrite of the original in an entirely different language, and as such, is not 100% stable yet.

A fast, platform-agnostic and minimal bootstrapper for Roblox and Roblox Studio

## Features
### Fast & Lightweight
Cork was rewritten from the ground up to be as fast and as lightweight as possible, by opting for a compiled language and by dropping components such as the splash screen from the main program.
### Mirror Selection
Whenever a version of Roblox starts being downloaded, Cork auto-selects the fastest mirror by running a small benchmark to attempt to get the fastest possible download speeds.
### Customizable
Want to run Roblox with `gamescope` or inside of `distrobox`? Feel like changing some FFlags to mess about? Just do it, the settings are there, it's up to you to tinker.
### Portable
Felt like trying to get Roblox to run on your Ampere Altra or your Talos II? Cork aims to make that easier for you. Every single part of the bootstrapper is modular and does not depend on any specific operating system or environment, compiles on any platform that supports modern versions of C++.

## Supported Platforms
| Operating System | Architecture | Runner | Support |
| --- | --- | --- | --- |
| Linux | x86_64 | Proton / Wine | Stable |
| Windows | x86_64 | Native | Experimental |

## Installing from Package
RPM and DEB packages are built with GitHub Actions for every commit, you can install those but they are experimental for now. Proper releases for those are coming soon!

## Installing from Source
### Dependencies
- Boost
- libzip
    - zlib
    - bzip2
    - xz
- OpenSSL
- cURL

#### Installing dependencies and build tools on Fedora
```bash
sudo dnf install git cmake make automake gcc gcc-c++ rpm-build
sudo dnf install boost-devel libzip-devel zlib-devel bzip2-devel xz-devel openssl-devel curl-devel
```

#### Installing dependencies and build tools on Ubuntu
```bash
sudo apt install git build-essential cmake
sudo apt install libboost-all-dev libzip-dev zlib1g-dev libbz2-dev liblzma-dev libssl-dev curl libcurl4-openssl-dev
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
cmake -Bbuild -H.
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

## Documentation
**W.I.P**

## "Why should I use this over Grapejuice or Vinegar?"
Maybe you should, maybe you shouldn't. All of the current solutions for running Roblox on Linux offer something over the other, there is no better or worse one, use whatever suits **you**.

## Acknowledgements
Heavily inspired and based on:
* [Grapejuice](https://gitlab.com/brinkervii/grapejuice)
* [Vinegar](https://github.com/vinegarhq/vinegar)
* [Bloxstrap](https://github.com/pizzaboxer/bloxstrap)
* [Roblox Studio Mod Manager](https://github.com/MaximumADHD/Roblox-Studio-Mod-Manager)