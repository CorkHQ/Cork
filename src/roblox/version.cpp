#include <stdexcept>
#include <cpr/cpr.h>
#include <nlohmann/json.hpp>
#include "version.hpp"
    
using json = nlohmann::json;

namespace cork::roblox {
    version GetVersion(std::string binaryType, std::string channel) {
        std::string requestUrl = "https://clientsettingscdn.roblox.com/v2/client-version/" + binaryType;

        if (channel != "") {
            requestUrl += "/channel/" + channel;
        }

        cpr::Response r = cpr::Get(cpr::Url{requestUrl}, cpr::Timeout{10000});

        if (r.status_code == 200) {
            json versionJson = json::parse(r.text);
            version responseVersion = {versionJson["version"], versionJson["clientVersionUpload"], versionJson["bootstrapperVersion"]};

            return responseVersion;
        }

        throw std::runtime_error("Failed to get version!");
    }
}