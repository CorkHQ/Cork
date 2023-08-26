#include <iostream>
#include "roblox/version.hpp"
#include "bootstrapper/installer.hpp"

int main(int, char**){
    std::string versionType = "WindowsPlayer";
    std::string versionChannel = "";
    std::string versionDirectory = "versiontest";
    std::string version = cork::roblox::GetVersion(versionType, versionChannel).clientVersionUpload;

    cork::bootstrapper::Install(versionType, version, versionChannel, versionDirectory);
}
