#include <iostream>
#include "bootstrapper/environment.hpp"

#if defined(NATIVE_RUNNER)
#include "runners/native.hpp"
#elif defined(WINE_RUNNER)
#include "runners/wine.hpp"
#endif

namespace cb = cork::bootstrapper;
namespace cr = cork::runners;

int main(int argc, char *argv[]){
    std::vector<std::string> arguments(argv + 1, argv + argc);

    cb::RobloxEnvironment environment;
    environment.SetVersionsDirectory("versions");
    std::pair<std::string, std::string> playerData = environment.GetPlayer("");
    
    std::list<std::string> playerArguments;
    playerArguments.push_back(playerData.second);

    if (arguments.size() > 0) {
        for (std::string argument: environment.ParsePlayer(arguments)) {
            playerArguments.push_back(argument);
        }
    } else {
        playerArguments.push_back("--app");
    }

#if defined(NATIVE_RUNNER)
    cr::NativeRunner runner;
#elif defined(WINE_RUNNER)
    cr::WineRunner runner;
    runner.SetType("wine");
#endif

    runner.Execute(playerArguments, playerData.first);
}
