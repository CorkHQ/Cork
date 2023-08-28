#include <iostream>
#include <filesystem>
#include <toml++/toml.h>
#include <platform_folders.h>
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
#if defined(WINE_RUNNER)
    std::string GetPrefixPath() {
        fs::path prefixPath = fs::path(GetDataPath()) / "pfx";
        return prefixPath;
    }
#endif

    void LoadSettings() {
        settingsTable = toml::parse(defaultSettings);

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
    
    bool GetBool(std::string category, std::string setting) {
        return settingsTable[category][setting].value<bool>().value_or(false);
    }
    int GetInt(std::string category, std::string setting) {
        return settingsTable[category][setting].value<int>().value_or(0);
    }
    float GetFloat(std::string category, std::string setting) {
        return settingsTable[category][setting].value<float>().value_or(0.0f);
    }
    std::string GetString(std::string category, std::string setting) {
        return settingsTable[category][setting].value<std::string>().value_or("");
    }
    std::map<std::string, std::string> GetStringMap(std::string category, std::string setting) {
        std::map<std::string, std::string> newMap;

        for (auto element : *settingsTable[category][setting].as_table()) {
            newMap.insert_or_assign(std::string(element.first.str()), element.second.value<std::string>().value_or(""));
        }

        return newMap;
    }
    toml::table GetTomlTable() {
        return settingsTable;
    }
}