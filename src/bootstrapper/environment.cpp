#include <fstream>
#include <cpr/cpr.h>
#include "installer.hpp"
#include "environment.hpp"
#include "../roblox/version.hpp"

namespace cr = cork::roblox;

std::map<std::string, std::string> playerArguments{
    {"launchmode", "--"},
    {"gameinfo", "-t "},
    {"placelauncherurl","-j "},
    {"launchtime", "--launchtime="},
    {"browsertrackerid", "-b "},
    {"robloxLocale", "--rloc "},
    {"gameLocale", "--gloc "},
    {"channel", "-channel "}
};

namespace cork::bootstrapper {
    void ApplyFFlags(std::string playerDirectory, std::string fflagJson) {
        fs::path jsonPath = fs::weakly_canonical(fs::path(playerDirectory) / "ClientSettings" / "ClientAppSettings.json");

        if (!fs::is_directory(jsonPath.parent_path())) {
            fs::create_directories(jsonPath.parent_path());
        }

        std::ofstream jsonStream = std::ofstream(jsonPath);
        jsonStream << fflagJson << std::endl;
        jsonStream.close();
    }
    void ApplyFFlags(std::string playerDirectory, nlohmann::json fflags) {
        std::ostringstream ss;
        ss << fflags.dump(4);
        ApplyFFlags(playerDirectory, ss.str());
    }

    void RobloxEnvironment::SetVersionsDirectory(std::string newVersionsDirectory) {
        versionsDirectory = fs::path(newVersionsDirectory);
    }

    std::pair<std::string, std::string> RobloxEnvironment::GetPlayer(std::string versionChannel, std::string versionOverride) {
        std::string versionType = "WindowsPlayer";
        std::string version = versionOverride;
        if (version == "") {
            version = cr::GetVersion(versionType, versionChannel).clientVersionUpload;
        }

        fs::path versionPath = fs::weakly_canonical(versionsDirectory / version);

        if (!fs::is_regular_file(versionPath / "AppSettings.xml")) {
            Install(versionType, version, versionChannel, versionPath.string());
        }

        return {versionPath, versionPath / "RobloxPlayerBeta.exe"};
    }

    std::pair<std::string, std::string> RobloxEnvironment::GetStudio(std::string versionChannel, std::string versionOverride) {
        std::string versionType = "WindowsStudio64";
        std::string version = versionOverride;
        if (version == "") {
            version = cr::GetVersion(versionType, versionChannel).clientVersionUpload;
        }

        fs::path versionPath = fs::weakly_canonical(versionsDirectory / version);

        if (!fs::is_regular_file(versionPath / "AppSettings.xml")) {
            Install(versionType, version, versionChannel, versionPath.string());
        }

        return {versionPath, versionPath / "RobloxStudioBeta.exe"};
    }

    std::list<std::string> RobloxEnvironment::ParsePlayer(std::vector<std::string> arguments) {
        if (arguments.size() == 1) {
            std::string argument = arguments.front();
            if (argument.rfind("roblox-player:1", 0) == 0) {
                std::list<std::string> newArguments;

                std::stringstream ss(argument);
                std::vector<std::string> result;

                while( ss.good() )
                {
                    std::string substr;
                    std::getline( ss, substr, '+' );
                    result.push_back( substr );
                }

                for (std::string piece : result) {
                    std::stringstream piecess(piece);
                    std::vector<std::string> pieceresult;

                    while( piecess.good() )
                    {
                        std::string piecesubstr;
                        std::getline( piecess, piecesubstr, ':' );
                        pieceresult.push_back( piecesubstr );

                        if (pieceresult.size() == 2) {
                            if ((pieceresult[0] == "launchmode") && (pieceresult[1] == "play")) {
                                pieceresult[1] = "app";
                            } else if (pieceresult[0] == "placelauncherurl") {
                                pieceresult[1] = cpr::util::urlDecode(pieceresult[1]);
                            } else if (pieceresult[0] == "channel") {
                                if (environmentChannel == "") {
                                    environmentChannel = pieceresult[1];
                                } else {
                                    pieceresult[1] = environmentChannel;
                                }
                            }

                            if (playerArguments.find(pieceresult[0]) != playerArguments.end()) {
                                newArguments.push_back(playerArguments[pieceresult[0]] + pieceresult[1]);
                            }
                        }
                    }
                }

                return newArguments;
            }
        }

        return std::list<std::string>(arguments.begin(), arguments.end());
    }
}