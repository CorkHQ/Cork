#include <iostream>
#include "roblox/cdn.hpp"
#include "roblox/version.hpp"

int main(int, char**){
    std::cout << Cork::Roblox::GetVersion("WindowsPlayer", "").version;
}
