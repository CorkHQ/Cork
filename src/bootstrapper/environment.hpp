#include <map>
#include <list>
#include <iostream>
#include <filesystem>
#include <nlohmann/json.hpp>

namespace fs = std::filesystem;

namespace cork::bootstrapper {
    void ApplyFFlags(std::string playerDirectory, std::string fflagJson);
    void ApplyFFlags(std::string playerDirectory, nlohmann::json fflags);
    
    class RobloxEnvironment {
        private:
            fs::path versionsDirectory;
            fs::path temporaryDirectory;
        public:
            std::string environmentChannel;
            
            void SetVersionsDirectory(std::string newVersionsDirectory);
            void SetTemporaryDirectory(std::string newTemporaryDirectory);

            std::pair<std::string, std::string> GetPlayer(std::string versionChannel, std::string versionOverride = "");
            std::pair<std::string, std::string> GetStudio(std::string versionChannel, std::string versionOverride = "");

            void CleanVersions();
    };
}