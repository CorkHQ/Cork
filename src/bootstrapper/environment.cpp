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
        BOOST_LOG_TRIVIAL(trace) << "applying fflags..."; 
        fs::path jsonPath = fs::weakly_canonical(fs::path(playerDirectory) / "ClientSettings" / "ClientAppSettings.json");

        if (!fs::is_directory(jsonPath.parent_path())) {
            fs::create_directories(jsonPath.parent_path());
        }

        std::ofstream jsonStream = std::ofstream(jsonPath);
        jsonStream << fflagJson << std::endl;
        jsonStream.close();
        BOOST_LOG_TRIVIAL(trace) << "applied!"; 
    }
    void ApplyFFlags(std::string playerDirectory, nlohmann::json fflags) {
        std::ostringstream ss;
        ss << fflags.dump(4);
        ApplyFFlags(playerDirectory, ss.str());
    }

    void RobloxEnvironment::SetVersionsDirectory(std::string newVersionsDirectory) {
        versionsDirectory = fs::path(newVersionsDirectory);
        BOOST_LOG_TRIVIAL(debug) << "versions directory: " << versionsDirectory; 
    }
    void RobloxEnvironment::SetTemporaryDirectory(std::string newTemporaryDirectory) {
        temporaryDirectory = fs::path(newTemporaryDirectory);
        BOOST_LOG_TRIVIAL(debug) << "temporary directory: " << temporaryDirectory; 
    }

    std::pair<std::string, std::string> RobloxEnvironment::GetPlayer(std::string versionChannel, std::string versionOverride) {
        std::string versionType = "WindowsPlayer";
        std::string version = versionOverride;
        if (version == "") {
            version = cr::GetVersion(versionType, versionChannel).clientVersionUpload;
        }
        BOOST_LOG_TRIVIAL(info) << "player version: " << version; 

        fs::path versionPath = fs::weakly_canonical(versionsDirectory / version);

        if (!fs::is_regular_file(versionPath / "AppSettings.xml")) {
            Install(versionType, version, versionChannel, versionPath.string(), temporaryDirectory);
        }

        return {versionPath, versionPath / "RobloxPlayerBeta.exe"};
    }

    std::pair<std::string, std::string> RobloxEnvironment::GetStudio(std::string versionChannel, std::string versionOverride) {
        std::string versionType = "WindowsStudio64";
        std::string version = versionOverride;
        if (version == "") {
            version = cr::GetVersion(versionType, versionChannel).clientVersionUpload;
        }
        BOOST_LOG_TRIVIAL(info) << "studio version: " << version; 

        fs::path versionPath = fs::weakly_canonical(versionsDirectory / version);

        if (!fs::is_regular_file(versionPath / "AppSettings.xml")) {
            Install(versionType, version, versionChannel, versionPath.string(), temporaryDirectory);
        }

        return {versionPath, versionPath / "RobloxStudioBeta.exe"};
    }

    void RobloxEnvironment::CleanVersions() {
        fs::remove_all(fs::path(versionsDirectory));
    }
}