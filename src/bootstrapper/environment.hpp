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
        public:
            std::string environmentChannel;
            
            void SetVersionsDirectory(std::string newVersionsDirectory);

            std::pair<std::string, std::string> GetPlayer(std::string versionChannel, std::string versionOverride = "");
            std::pair<std::string, std::string> GetStudio(std::string versionChannel, std::string versionOverride = "");

            std::list<std::string> ParsePlayer(std::vector<std::string> arguments);
            std::list<std::string> ParseStudio(std::vector<std::string> arguments);
    };
}