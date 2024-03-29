#include <fstream>
#include <iostream>
#if defined(PLUGINS_ENABLED)
#include <sol/sol.hpp>
#endif
#include <nlohmann/json.hpp>
#include <boost/interprocess/sync/named_mutex.hpp>
#include <boost/log/core.hpp> 
#include <boost/log/trivial.hpp> 
#include <boost/log/expressions.hpp>
#include <boost/log/utility/setup/file.hpp>
#include <boost/log/utility/setup/console.hpp>
#include "bootstrapper/environment.hpp"
#include "settings/settings.hpp"
#include "roblox/version.hpp"

#if defined(NATIVE_RUNNER)
#include "runners/native.hpp"
#elif defined(WINE_RUNNER)
#include "runners/wine.hpp"
#endif

namespace cb = cork::bootstrapper;
namespace cr = cork::runners;
namespace cs = cork::settings;
namespace cro = cork::roblox;

void setupLogger(std::string logLevel) {
    auto formatSeverity = boost::log::expressions::
        attr<boost::log::trivial::severity_level>("Severity");
    
    boost::log::formatter logFmt =
        boost::log::expressions::format("%1%: %2%")
        % formatSeverity
        % boost::log::expressions::smessage;
    
    auto consoleSink = boost::log::add_console_log(std::clog);
    consoleSink->set_formatter(logFmt);
    consoleSink->set_filter(boost::log::trivial::severity >= boost::log::trivial::trace);

    auto fsSink = boost::log::add_file_log(
        boost::log::keywords::file_name = (fs::path(cs::GetLogsPath()) / "cork-%Y-%m-%d_%H-%M-%S.%N.log").string(),
        boost::log::keywords::rotation_size = 10 * 1024 * 1024,
        boost::log::keywords::min_free_space = 30 * 1024 * 1024,
        boost::log::keywords::open_mode = std::ios_base::app);
    fsSink->set_formatter(logFmt);
    fsSink->locked_backend()->auto_flush(true);

    if (logLevel == "trace") {
        fsSink->set_filter(        
            boost::log::trivial::severity >= boost::log::trivial::trace    
        ); 
    } else if (logLevel == "debug") {
        fsSink->set_filter(        
            boost::log::trivial::severity >= boost::log::trivial::debug   
        ); 
    } else if (logLevel == "info") {
        fsSink->set_filter(        
            boost::log::trivial::severity >= boost::log::trivial::info    
        ); 
    } else {
        fsSink->set_filter(        
            boost::log::trivial::severity >= boost::log::trivial::warning    
        ); 
    }
}

int main(int argc, char *argv[]){
    std::list<std::string> arguments(argv + 1, argv + argc);

    cs::LoadDefaults();
    cs::LoadSettings();
    cs::SaveSettings();

    std::string logLevel = cs::GetString("cork.loglevel");
    setupLogger(logLevel);
    
    BOOST_LOG_TRIVIAL(info) << "Cork " << CORK_VERSION << " (" << CORK_CODENAME << ")";
    
    cb::RobloxEnvironment environment;
    environment.SetVersionsDirectory(cs::GetVersionsPath());
    environment.SetTemporaryDirectory(cs::GetDownloadsPath());

#if defined(NATIVE_RUNNER)
    BOOST_LOG_TRIVIAL(info) << "runner: native";

    cr::NativeRunner runner;
    runner.SetEnvironment(cs::GetStringMap("cork.env"));
#elif defined(WINE_RUNNER)
    BOOST_LOG_TRIVIAL(info) << "runner: wine";

    cr::WineRunner runner;
    runner.SetDist(cs::GetString("wine.dist"));
    runner.SetType(cs::GetString("wine.type"));
    runner.SetPrefix(cs::GetPrefixPath());
    runner.SetEnvironment(cs::GetStringMap("cork.env"));
    runner.SetEnvironment(cs::GetStringMap("wine.env"));
#endif

#if defined(PLUGINS_ENABLED)
    std::list<std::unique_ptr<sol::state>> pluginStates;
    std::list<std::string> pluginFolders = cs::GetPlugins();

    for (std::string pluginFolder: pluginFolders) {
        fs::path pluginFile = fs::path(pluginFolder) / "plugin.lua";
        if (fs::exists(pluginFile) && fs::is_regular_file(pluginFile)) {
            std::string pluginName = fs::path(pluginFolder).filename().generic_string();
            BOOST_LOG_TRIVIAL(info) << "initializing plugin '" << pluginName << "'...";

            std::ifstream pluginStream(pluginFile);
            std::ostringstream stringStream;
            stringStream << pluginStream.rdbuf();

            std::string pluginString = stringStream.str();

            pluginStates.push_back(std::make_unique<sol::state>());

            (*pluginStates.back()).open_libraries(sol::lib::base,
                sol::lib::package,
                sol::lib::coroutine,
                sol::lib::string,
                sol::lib::os,
                sol::lib::math,
                sol::lib::table,
                sol::lib::io,
                sol::lib::debug);
            
            (*pluginStates.back())["NAME"] = pluginName;

    #if defined(NATIVE_RUNNER)
            (*pluginStates.back())["RUNNER"] = "native";
    #elif defined(WINE_RUNNER)
            (*pluginStates.back())["RUNNER"] = "wine";
            (*pluginStates.back())["PATH_PREFIX"] = runner.GetPrefix();
    #endif
            (*pluginStates.back())["PATH_PLUGIN"] = pluginFolder;
            (*pluginStates.back())["PATH_DATA"] = cs::GetDataPath();
            (*pluginStates.back())["PATH_LOGS"] = cs::GetLogsPath();
            (*pluginStates.back())["PATH_CONFIG"] = cs::GetConfigPath();
            (*pluginStates.back())["PATH_VERSIONS"] = cs::GetVersionsPath();
            (*pluginStates.back())["PATH_DOWNLOADS"] = cs::GetDownloadsPath();

            (*pluginStates.back()).set_function("RunnerExecute", [&runner, pluginFolder](std::list<std::string> runnerArguments) {
                runner.Execute(runnerArguments, pluginFolder);
            });
            (*pluginStates.back()).set_function("SetEnvironment", [&runner](std::string key, std::string value) {
                runner.SetEnvironment(key, value);
            });
            (*pluginStates.back()).set_function("GetEnvironment", [&runner](std::string key) -> std::string {
                return runner.GetEnvironment(key);
            });
            (*pluginStates.back()).set_function("Log", [pluginName](std::string text, std::string logLevel) {
                if (logLevel == "trace") {
                    BOOST_LOG_TRIVIAL(trace) << pluginName + ": " << text;
                } else if (logLevel == "debug") {
                    BOOST_LOG_TRIVIAL(debug) << pluginName + ": " << text;
                } else if (logLevel == "info") {
                    BOOST_LOG_TRIVIAL(info) << pluginName + ": " << text;
                }
            });
            (*pluginStates.back()).set_function("Throw", [pluginName](std::string text) {
                throw std::runtime_error(pluginName + ": " + text);
            });

            (*pluginStates.back()).script(pluginString);
            BOOST_LOG_TRIVIAL(info) << "plugin '" << pluginName << "' initialized!";
        }
    }
#endif

    boost::interprocess::named_mutex lockVersion(boost::interprocess::open_or_create, "CORK_version");

    int returnCode = 0;
    if (arguments.size() > 0) {
        std::string operationMode = arguments.front();
        arguments.pop_front();

#if defined(PLUGINS_ENABLED)
        for (std::unique_ptr<sol::state>& state: pluginStates) {
            (*state)["MODE"] = operationMode;
        }
#endif

        BOOST_LOG_TRIVIAL(info) << "mode: " << operationMode;
        try {
            if (operationMode == "player" || operationMode == "studio") {
                BOOST_LOG_TRIVIAL(trace) << "getting " + operationMode + "...";
                std::string versionOverride = cs::GetString(operationMode + ".version");
                std::string versionChannel = cs::GetString(operationMode + ".channel");

                std::string fflagJsonString = cs::GetJson(operationMode + ".fflags");
                nlohmann::json fflagsJson = nlohmann::json::parse(fflagJsonString);

#if defined(PLUGINS_ENABLED)
                for (std::unique_ptr<sol::state>& state: pluginStates) {
                    (*state)["VERSION_OVERRIDE"] = versionOverride;
                    (*state)["VERSION_CHANNEL"] = versionChannel;

                    (*state).set_function("GetFFlag", [&fflagsJson](std::string key) -> std::string {
                        return fflagsJson[key].dump();
                    });
                    (*state).set_function("SetFFlag", [&fflagsJson](std::string key, std::string value) {
                        fflagsJson[key] = nlohmann::json::parse(value);
                    });

                    if ((*state)["PluginPreVersion"].valid()) {
                        (*state)["PluginPreVersion"]();
                        versionOverride = (*state)["VERSION_OVERRIDE"];
                        versionChannel = (*state)["VERSION_CHANNEL"];
                    }
                }
#endif

                std::pair<std::string, std::string> versionData;
                std::string version = versionOverride;

                if (operationMode == "player") {
                    if (version == "") {
                        version = cro::GetVersion("WindowsPlayer", versionChannel).clientVersionUpload;
                    }

                    lockVersion.lock();
                    versionData = environment.GetPlayer(versionChannel, version);
                } else if (operationMode == "studio") {
                    if (version == "") {
                        version = cro::GetVersion("WindowsStudio64", versionChannel).clientVersionUpload;
                    }

                    lockVersion.lock();
                    versionData = environment.GetStudio(versionChannel, version);
                }
                lockVersion.unlock();

                BOOST_LOG_TRIVIAL(trace) << "got " + operationMode + "!";

#if defined(PLUGINS_ENABLED)
                for (std::unique_ptr<sol::state>& state: pluginStates) {
                    (*state)["VERSION_PATH"] = versionData.first;
                    (*state)["VERSION_EXECUTABLE"] = versionData.second;
                    if ((*state)["PluginVersion"].valid()) {
                        (*state)["PluginVersion"]();
                        versionData.first = (*state)["VERSION_PATH"];
                        versionData.second = (*state)["VERSION_EXECUTABLE"];
                    }
                }
#endif

                BOOST_LOG_TRIVIAL(trace) << "parsing arguments...";
                std::list<std::string> versionArguments;
                if (operationMode == "player") {
                    versionArguments.push_back((fs::path(versionData.first).make_preferred() / versionData.second).string());
                    if (arguments.size() > 0) {
                        for (std::string argument: arguments) {
                            versionArguments.push_back(argument);
                        }
                    } else {
                        versionArguments.push_back("--app");
                    }
                } else if (operationMode == "studio") {
                    versionArguments.push_back((fs::path(versionData.first).make_preferred() / versionData.second).string());
                    if (arguments.size() > 0) {
                        for (std::string argument: arguments) {
                            if (argument.rfind("roblox-studio:", 0) == 0) {
                                versionArguments.push_back("-protocolString");
                            }
                            versionArguments.push_back(argument);
                        }
                    } else {
                        versionArguments.push_back("-ide");
                    }
                }

                BOOST_LOG_TRIVIAL(trace) << "arguments parsed!";

                runner.SetEnvironment(cs::GetStringMap(operationMode + ".env"));

                runner.AddLaunchers(cs::GetString(operationMode + ".launcher.pre"));
                runner.AddLaunchers(cs::GetString("cork.launcher"));
                runner.AddLaunchers(cs::GetString(operationMode + ".launcher.post"));

#if defined(PLUGINS_ENABLED)
                for (std::unique_ptr<sol::state>& state: pluginStates) {
                    if ((*state)["PluginExecute"].valid()) {
                        (*state)["PluginExecute"]();
                    }
                }
#endif

                cb::ApplyFFlags(versionData.first, fflagsJson);
                runner.Execute(versionArguments, fs::path(versionData.first).make_preferred().string()) ;
            } else if (operationMode == "runner") {
                runner.AddLaunchers(cs::GetString("cork.launcher"));
                runner.Execute(arguments);
            } else if (operationMode == "clear") {
                if (arguments.size() > 0) {
                    std::string target = arguments.front();

                    BOOST_LOG_TRIVIAL(info) << "clear target: " << target;
                    if (target == "versions") {
                        lockVersion.lock();
                        environment.CleanVersions();
                        lockVersion.unlock();
                    } else if (target == "downloads") {
                        lockVersion.lock();
                        fs::remove_all(fs::path(cs::GetDownloadsPath()));
                        lockVersion.unlock();
                    } else if (target == "logs") {
                        fs::remove_all(fs::path(cs::GetLogsPath()));
                    } else if (target == "settings") {
                        cs::LoadDefaults();
                        cs::SaveSettings();
                    } else {
                        BOOST_LOG_TRIVIAL(error) << "invalid clear target";
                        returnCode = 1;
                    }
                } else {
                    BOOST_LOG_TRIVIAL(error) << "no target to clear";
                    returnCode = 1;
                }
            } else if (operationMode == "version") {
                std::cout << CORK_VERSION << " (" << CORK_CODENAME << ")" << std::endl;
            } else {
                BOOST_LOG_TRIVIAL(error) << "invalid mode given";
                returnCode = 1;
            }
        }
        catch (std::exception &e) {
            BOOST_LOG_TRIVIAL(fatal) << "exception: " << e.what();
            returnCode = 2;
        }
    } else {
        BOOST_LOG_TRIVIAL(error) << "no mode given";
        returnCode = 1;
    }

#if defined(PLUGINS_ENABLED)
    for (std::unique_ptr<sol::state>& state: pluginStates) {
        (*state)["RETURN_CODE"] = returnCode;
        if ((*state)["PluginShutdown"].valid()) {
            (*state)["PluginShutdown"]();
        }
    }
#endif

    BOOST_LOG_TRIVIAL(debug) << "end";

    return returnCode;
}
