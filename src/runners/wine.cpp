#include <boost/process.hpp>
#include <filesystem>
#include "wine.hpp"

namespace fs = std::filesystem;

namespace cork::runners {
    void WineRunner::SetPrefix(std::string newPrefix) {
        prefix = newPrefix;
    }
    void WineRunner::SetType(std::string newType) {
        launchType = newType;
    }
    void WineRunner::SetDist(std::string newDist) {
        dist = newDist;
    }

    void WineRunner::Execute(std::list<std::string> arguments, std::string cwd) {
        std::list<std::string> wineArguments;

        if (launchType != "proton") {
            std::string wineBinary = "wine64";

            if (dist != "") {
                wineBinary = fs::canonical(fs::path(dist) / fs::path("bin") / fs::path(wineBinary)).string();
            }
            SetEnvironment("WINEPREFIX", fs::canonical(fs::path(prefix)).string());

            wineArguments.push_back(wineBinary);
        } else {
            std::string protonBinary = "proton";

            if (dist != "") {
                protonBinary = fs::canonical(fs::path(dist) / fs::path(protonBinary)).string();
            }
            SetEnvironment("STEAM_COMPAT_CLIENT_INSTALL_PATH", "");
            SetEnvironment("STEAM_COMPAT_DATA_PATH", fs::canonical(fs::path(prefix)).parent_path().string());

            wineArguments.push_back(protonBinary);
            wineArguments.push_back("run");
        }

        for (std::string argument : arguments) {
            wineArguments.push_back(argument);
        }

        NativeRunner::Execute(wineArguments, cwd);
    }
    void WineRunner::Execute(std::list<std::string> arguments) {
        Execute(arguments, fs::current_path().string());
    }
}