#include <iostream>
#include "roblox/cdn.hpp"
#include "roblox/version.hpp"
#include "roblox/packages.hpp"

int main(int, char**){
    cork::roblox::GetPackages("WindowsPlayer", cork::roblox::GetVersion("WindowsPlayer", "").clientVersionUpload, "");
}
