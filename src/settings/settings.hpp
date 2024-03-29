#include <map>
#include <list>
#include <iostream>
#include <toml++/toml.h>

namespace cork::settings {
    bool HasVendorPath();
    std::string GetVendorPath();

    std::string GetDataPath();
    std::string GetConfigPath();

    std::string GetSettingsPath();
    std::string GetVersionsPath();
    std::string GetDownloadsPath();
    std::string GetLogsPath();
#if defined(WINE_RUNNER)
    std::string GetPrefixPath();
#endif
    std::list<std::string> GetPlugins();

    void LoadDefaults();
    void LoadSettings();
    void SaveSettings();
    
    toml::v3::node_view<toml::v3::node> GetElement(std::string path);
    
    bool GetBool(std::string path);
    int GetInt(std::string path);
    float GetFloat(std::string path);
    std::string GetString(std::string path);

    std::map<std::string, std::string> GetStringMap(std::string path);
    std::string GetJson(std::string path);

    toml::table GetTomlTable();
}