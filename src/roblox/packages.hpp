#include <list>
#include <iostream>

namespace Cork::Roblox {
    struct base_package {
        std::string name;
        std::string target;
    };
    struct package {
        std::string name;
        std::string url;
        std::string target;
        std::string checksum;
    };

    std::list<package> GetPackages(std::string versionType, std::string version, std::string channel, std::string cdn);
    std::list<package> GetPackages(std::string versionType, std::string version, std::string channel);
}