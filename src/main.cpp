#include <iostream>
#include "bootstrapper/environment.hpp"
#include "settings/settings.hpp"

#if defined(NATIVE_RUNNER)
#include "runners/native.hpp"
#elif defined(WINE_RUNNER)
#include "runners/wine.hpp"
#endif

namespace cb = cork::bootstrapper;
namespace cr = cork::runners;
namespace cs = cork::settings;

int main(int argc, char *argv[]){
    std::list<std::string> arguments(argv + 1, argv + argc);

    cs::LoadSettings();
    cs::SaveSettings();
    
    cb::RobloxEnvironment environment;
    environment.SetVersionsDirectory(cs::GetVersionsPath());

#if defined(NATIVE_RUNNER)
    cr::NativeRunner runner;
    runner.SetEnvironment(cs::GetStringMap("cork.env"));
#elif defined(WINE_RUNNER)
    cr::WineRunner runner;
    runner.SetDist(cs::GetString("wine.dist"));
    runner.SetType(cs::GetString("wine.type"));
    runner.SetPrefix(cs::GetPrefixPath());
    runner.SetEnvironment(cs::GetStringMap("cork.env"));
    runner.SetEnvironment(cs::GetStringMap("wine.env"));
#endif

    if (arguments.size() > 0) {
        std::string operationMode = arguments.front();
        arguments.pop_front();
        
        if (operationMode == "player") {
            std::string versionOverride = cs::GetString("player.version");
            std::pair<std::string, std::string> playerData = environment.GetPlayer(cs::GetString("player.channel"), versionOverride);

            std::list<std::string> playerArguments;
            playerArguments.push_back(playerData.second);
            if (arguments.size() > 0) {
                for (std::string argument: environment.ParsePlayer(std::vector<std::string>{std::begin(arguments), std::end(arguments)})) {
                    playerArguments.push_back(argument);
                }
            } else {
                playerArguments.push_back("--app");
            }

            runner.SetEnvironment(cs::GetStringMap("player.env"));

            runner.AddLaunchers(cs::GetString("player.launcher.pre"));
            runner.AddLaunchers(cs::GetString("cork.launcher"));
            runner.AddLaunchers(cs::GetString("player.launcher.post"));

            cb::ApplyFFlags(playerData.first, cs::GetJson("player.fflags"));
            runner.Execute(playerArguments, playerData.first);
        }
    }
}
