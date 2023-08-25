#include <iostream>

namespace cork::roblox {
    struct version {
        std::string version;
        std::string clientVersionUpload;
        std::string bootstrapperVersion;
    };

    version GetVersion(std::string binaryType, std::string channel);
}