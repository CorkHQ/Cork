#include <map>
#include <sstream>
#include <string>
#include <cpr/cpr.h>
#include "cdn.hpp"
#include "packages.hpp"

std::map<std::string, std::list<cork::roblox::base_package>> packageDictionary{
    {"WindowsPlayer", {
        {"RobloxApp.zip", ""},
        {"WebView2.zip", ""},

        {"shaders.zip", "shaders"},
        {"ssl.zip", "ssl"},

        {"content-avatar.zip", "content/avatar"},
        {"content-configs.zip", "content/configs"},
        {"content-fonts.zip", "content/fonts"},
        {"content-sky.zip", "content/sky"},
        {"content-sounds.zip", "content/sounds"},
        {"content-textures2.zip", "content/textures"},
        {"content-models.zip", "content/models"},

        {"content-textures3.zip", "PlatformContent/pc/textures"},
        {"content-terrain.zip", "PlatformContent/pc/terrain"},
        {"content-platform-fonts.zip", "PlatformContent/pc/fonts"},

        {"extracontent-luapackages.zip", "ExtraContent/LuaPackages"},
        {"extracontent-translations.zip", "ExtraContent/translations"},
        {"extracontent-models.zip", "ExtraContent/models"},
        {"extracontent-textures.zip", "ExtraContent/textures"},
        {"extracontent-places.zip", "ExtraContent/places"}
    }},

    {"WindowsStudio64", {
        {"ApplicationConfig.zip", "ApplicationConfig"},
        {"BuiltInPlugins.zip", "BuiltInPlugins"},
        {"BuiltInStandalonePlugins.zip", "BuiltInStandalonePlugins"},
        {"Plugins.zip", "Plugins"},
        {"Qml.zip", "Qml"},
        {"StudioFonts.zip", "StudioFonts"},
        {"WebView2.zip", ""},
        {"RobloxStudio.zip", ""},
        {"Libraries.zip", ""},
        {"LibrariesQt5.zip", ""},
        {"content-avatar.zip", "content/avatar"},
        {"content-configs.zip", "content/configs"},
        {"content-fonts.zip", "content/fonts"},
        {"content-models.zip", "content/models"},
        {"content-qt_translations.zip", "content/qt_translations"},
        {"content-sky.zip", "content/sky"},
        {"content-sounds.zip", "content/sounds"},
        {"shaders.zip", "shaders"},
        {"ssl.zip", "ssl"},
        {"content-textures2.zip", "content/textures"},
        {"content-textures3.zip", "PlatformContent/pc/textures"},
        {"content-studio_svg_textures.zip", "content/studio_svg_textures"},
        {"content-terrain.zip", "PlatformContent/pc/terrain"},
        {"content-platform-fonts.zip", "PlatformContent/pc/fonts"},
        {"content-api-docs.zip", "content/api_docs"},
        {"extracontent-scripts.zip", "ExtraContent/scripts"},
        {"extracontent-luapackages.zip", "ExtraContent/LuaPackages"},
        {"extracontent-translations.zip", "ExtraContent/translations"},
        {"extracontent-models.zip", "ExtraContent/models"},
        {"extracontent-textures.zip", "ExtraContent/textures"},
        {"redist.zip", ""}
    }}
};

namespace cork::roblox {
    std::list<package> GetPackages(std::string versionType, std::string version, std::string channel, std::string cdn) {
        std::string baseUrl = cdn;
        
        if (channel != "") {
            baseUrl += "channel/" + channel + "/";
        }

        cpr::Response r = cpr::Get(cpr::Url{baseUrl + version + "-rbxPkgManifest.txt"}, cpr::Timeout{10000});

        if(r.status_code == 200) {
            std::map<std::string, std::string> packageHashes;

            int lineCount = 0;
            std::string lastHeader = "";
            std::string lastLine = "";

            for(char c : r.text) {
                if (c == '\n') {
                    if (lineCount >= 5) {
                        lineCount = 1;
                    }
                    
                    if (lineCount == 1) {
                        lastHeader = lastLine;
                    } else if (lineCount == 2) {
                        packageHashes[lastHeader] = lastLine;
                    }

                    lineCount += 1;
                    lastLine = "";
                } else {
                    if (c != '\r') {
                        lastLine += c;
                    }
                }
            }

            std::list<package> packageList;
            for (base_package thisPackage : packageDictionary[versionType]) {
                package newPackage = package{
                    thisPackage.name,
                    baseUrl + version + "-" + thisPackage.name,
                    thisPackage.target,
                    packageHashes[thisPackage.name]
                };

                packageList.push_back(newPackage);
            }

            return packageList;
        }

        throw std::runtime_error("Failed to get package manifest!");
    }

    std::list<package> GetPackages(std::string versionType, std::string version, std::string channel) {
        return GetPackages(versionType, version, channel, GetCDN());
    };
}