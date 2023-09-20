#include <iostream>
#include <filesystem>
#include <toml++/toml.h>
#ifdef LOCAL_PLATFORM_FOLDERS
#include <platform_folders.h>
#else
#include <sago/platform_folders.h>
#endif
#include "default.hpp"

namespace fs = std::filesystem;

toml::table settingsTable;

void mergeTable(toml::table* target, toml::table* source) {
    for (auto element : *source) {
        if (element.second.is_table() && (*target).contains(element.first) && (*target)[element.first].is_table()) {
            mergeTable((*target)[element.first].as_table(), element.second.as_table());
        } else {
            (*target).insert_or_assign(element.first, element.second);
        }
    }
}

namespace cork::settings {
    bool HasVendorPath() {
        return CORK_VENDOR_PATH != "";
    }
    std::string GetVendorPath(){
        return CORK_VENDOR_PATH;
    }

    std::string GetDataPath() {
        fs::path dataPath = fs::path(sago::getDataHome()) / "cork";
        fs::create_directories(dataPath);

        return dataPath;
    }
    std::string GetConfigPath() {
        fs::path configPath = fs::path(sago::getConfigHome()) / "cork";
        fs::create_directories(configPath);

        return configPath;
    }
    
    std::string GetSettingsPath() {
        fs::path filePath = fs::path(GetConfigPath()) / "settings.toml";
        return filePath;
    }
    std::string GetVersionsPath() {
        fs::path versionsPath = fs::path(GetDataPath()) / "versions";
        return versionsPath;
    }
    std::string GetDownloadsPath() {
        fs::path downloadsPath = fs::path(sago::getCacheDir()) / "cork" / "downloads";
        fs::create_directories(downloadsPath);
        
        return downloadsPath;
    }
    std::string GetLogsPath() {
        fs::path logsPath = fs::path(sago::getCacheDir()) / "cork" / "logs";
        fs::create_directories(logsPath);
        
        return logsPath;
    }
#if defined(WINE_RUNNER)
    std::string GetPrefixPath() {
        fs::path prefixPath = fs::path(GetDataPath()) / "pfx";
        return prefixPath;
    }
#endif

    void LoadDefaults() {
        settingsTable = toml::parse(defaultSettings);
    }
    void LoadSettings() {
        std::string filePath = GetSettingsPath();
        if (fs::exists(filePath)) {
            toml::table storedTable = toml::parse_file(filePath);
            mergeTable(&settingsTable, &storedTable);
        }
    }
    void SaveSettings() {
        std::ofstream fileStream = std::ofstream(GetSettingsPath());
        fileStream << settingsTable;
        fileStream.close();
    }
    
    toml::v3::node_view<toml::v3::node> GetElement(std::string path) {
        toml::v3::node_view<toml::v3::node> element;
        bool firstElement = true;

        std::string lastPiece = "";
        for(char c : path) {
            if (c == '.') {
                if (firstElement) {
                    element = settingsTable[lastPiece];
                    firstElement = false;
                } else {
                    element = element[lastPiece];
                }

                lastPiece = "";
            } else {
                lastPiece += c;
            }
        }
        if (firstElement) {
            element = settingsTable[lastPiece];
            firstElement = false;
        } else {
            element = element[lastPiece];
        }

        return element;
    }

    bool GetBool(std::string path) {
        return GetElement(path).value<bool>().value_or(false);
    }
    int GetInt(std::string path) {
        return GetElement(path).value<int>().value_or(0);
    }
    float GetFloat(std::string path) {
        return GetElement(path).value<float>().value_or(0.0f);
    }
    std::string GetString(std::string path) {
        return GetElement(path).value<std::string>().value_or("");
    }

    std::map<std::string, std::string> GetStringMap(std::string path) {
        std::map<std::string, std::string> newMap;

        for (auto element : *GetElement(path).as_table()) {
            newMap.insert_or_assign(std::string(element.first.str()), element.second.value<std::string>().value_or(""));
        }

        return newMap;
    }
    std::string GetJson(std::string path) {
        std::ostringstream ss;
        ss << toml::json_formatter{*GetElement(path).as_table()};
        return ss.str();
    }

    toml::table GetTomlTable() {
        return settingsTable;
    }
}