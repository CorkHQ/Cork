#include <iostream>
#include <filesystem>

namespace fs = std::filesystem;

namespace cork::bootstrapper {
    void Install(std::string versionType, std::string version, std::string versionChannel, std::string versionDirectory, fs::path temporaryDirectory = "");
}