#include <fstream>
#include <cpr/cpr.h>
#include <boost/log/trivial.hpp>
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
        BOOST_LOG_TRIVIAL(trace) << "Applying FFlags..."; 
        fs::path jsonPath = fs::weakly_canonical(fs::path(playerDirectory) / "ClientSettings" / "ClientAppSettings.json");

        if (!fs::is_directory(jsonPath.parent_path())) {
            fs::create_directories(jsonPath.parent_path());
        }

        std::ofstream jsonStream = std::ofstream(jsonPath);
        jsonStream << fflagJson << std::endl;
        jsonStream.close();
        BOOST_LOG_TRIVIAL(trace) << "Applied!"; 
    }
    void ApplyFFlags(std::string playerDirectory, nlohmann::json fflags) {
        std::ostringstream ss;
        ss << fflags.dump(4);
        ApplyFFlags(playerDirectory, ss.str());
    }

    void RobloxEnvironment::SetVersionsDirectory(std::string newVersionsDirectory) {
        versionsDirectory = fs::path(newVersionsDirectory);
        BOOST_LOG_TRIVIAL(debug) << "Versions Directory: " << versionsDirectory; 
    }

    std::pair<std::string, std::string> RobloxEnvironment::GetPlayer(std::string versionChannel, std::string versionOverride) {
        std::string versionType = "WindowsPlayer";
        std::string version = versionOverride;
        if (version == "") {
            version = cr::GetVersion(versionType, versionChannel).clientVersionUpload;
        }
        BOOST_LOG_TRIVIAL(info) << "Player Version: " << version; 

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
        BOOST_LOG_TRIVIAL(info) << "Studio Version: " << version; 

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

    std::list<std::string> RobloxEnvironment::ParseStudio(std::vector<std::string> arguments) {
        if (arguments.size() == 1) {
            std::string argument = arguments.front();
            if (argument.rfind("roblox-studio:", 0) == 0) {
                std::list<std::string> newArguments;
                std::map<std::string, std::string> argumentMap;

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

                        if (pieceresult.size() >= 1) {
                            if (pieceresult[0] == "channel" && pieceresult.size() > 1) {
                                if (environmentChannel == "") {
                                    environmentChannel = pieceresult[1];
                                } else {
                                    pieceresult[1] = environmentChannel;
                                }
                            }

                            if (pieceresult[0] == "gameinfo" && pieceresult.size() > 1) {
                                newArguments.push_back("-url https://www.roblox.com/Login/Negotiate.ashx");
                                newArguments.push_back("-ticket " + pieceresult[1]);
                            } else {
                                if (pieceresult.size() > 1) {
                                    newArguments.push_back("-" + pieceresult[0] + " " + pieceresult[1]);
                                } else {
                                    newArguments.push_back("-" + pieceresult[0]);
                                }
                            }

                            if (pieceresult.size() > 1) {
                                argumentMap[pieceresult[0]] = pieceresult[1];
                            } else {
                                argumentMap[pieceresult[0]] = "";
                            }
                        }
                    }
                }

                if (argumentMap.count("launchmode") > 0 && argumentMap.count("task") == 0 ) {
                    if (argumentMap["launchmode"] == "plugin") {
                        newArguments.push_back("-task InstallPlugin");
                        newArguments.push_back("-pluginId " + argumentMap["pluginid"]);
                    } else if (argumentMap["launchmode"] == "edit") {
                        newArguments.push_back("-task EditPlace");
                    } else if (argumentMap["launchmode"] == "asset") {
                        newArguments.push_back("-task TryAsset");
                        newArguments.push_back("-assetId " + argumentMap["assetid"]);
                    }
                }

                return newArguments;
            }
        }

        return std::list<std::string>(arguments.begin(), arguments.end());
    }

    void RobloxEnvironment::CleanVersions() {
        fs::remove_all(fs::path(versionsDirectory));
    }
}