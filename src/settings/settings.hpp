#include <iostream>
#include <toml++/toml.h>

namespace cork::settings {
    std::string GetDataPath();
    std::string GetConfigPath();

    std::string GetSettingsPath();
    std::string GetVersionsPath();
#if defined(WINE_RUNNER)
    std::string GetPrefixPath();
#endif

    void LoadSettings();
    void SaveSettings();
    
    bool GetBool(std::string category, std::string setting);
    int GetInt(std::string category, std::string setting);
    float GetFloat(std::string category, std::string setting);
    std::string GetString(std::string category, std::string setting);
    toml::table GetTable();
}