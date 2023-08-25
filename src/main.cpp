#include <iostream>
#include "roblox/cdn.hpp"
#include "roblox/version.hpp"
#include "roblox/packages.hpp"

int main(int, char**){
    Cork::Roblox::GetPackages("WindowsPlayer", Cork::Roblox::GetVersion("WindowsPlayer", "").clientVersionUpload, "");
}
