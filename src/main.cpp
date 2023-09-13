#include <iostream>
#include <boost/log/core.hpp> 
#include <boost/log/trivial.hpp> 
#include <boost/log/expressions.hpp>
#include <boost/log/utility/setup/file.hpp>
#include <boost/log/utility/setup/console.hpp>
#include "bootstrapper/environment.hpp"
#include "settings/settings.hpp"

#if defined(NATIVE_RUNNER)
#include "runners/native.hpp"
#elif defined(WINE_RUNNER)
#include "runners/wine.hpp"
#endif

namespace cb = cork::bootstrapper;
namespace cr = cork::runners;
namespace cs = cork::settings;

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
        boost::log::keywords::file_name = "cork-%Y-%m-%d_%H-%M-%S.%N.log",
        boost::log::keywords::rotation_size = 10 * 1024 * 1024,
        boost::log::keywords::min_free_space = 30 * 1024 * 1024,
        boost::log::keywords::open_mode = std::ios_base::app,
        boost::log::keywords::target = cs::GetLogsPath());
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

    if (arguments.size() > 0) {
        std::string operationMode = arguments.front();
        arguments.pop_front();

        BOOST_LOG_TRIVIAL(info) << "mode: " << operationMode;
        if (operationMode == "player") {
            BOOST_LOG_TRIVIAL(trace) << "getting player...";
            std::string versionOverride = cs::GetString("player.version");
            std::pair<std::string, std::string> playerData = environment.GetPlayer(cs::GetString("player.channel"), versionOverride);
            BOOST_LOG_TRIVIAL(trace) << "got player!";

            BOOST_LOG_TRIVIAL(trace) << "parsing arguments...";
            std::list<std::string> playerArguments;
            playerArguments.push_back(playerData.second);
            if (arguments.size() > 0) {
                for (std::string argument: arguments) {
                    playerArguments.push_back(argument);
                }
            } else {
                playerArguments.push_back("--app");
            }
            BOOST_LOG_TRIVIAL(trace) << "arguments parsed!";

            runner.SetEnvironment(cs::GetStringMap("player.env"));

            runner.AddLaunchers(cs::GetString("player.launcher.pre"));
            runner.AddLaunchers(cs::GetString("cork.launcher"));
            runner.AddLaunchers(cs::GetString("player.launcher.post"));

            cb::ApplyFFlags(playerData.first, cs::GetJson("player.fflags"));
            runner.Execute(playerArguments, playerData.first);
        } else if (operationMode == "studio") {
            BOOST_LOG_TRIVIAL(trace) << "getting studio...";
            std::string versionOverride = cs::GetString("studio.version");
            std::pair<std::string, std::string> studioData = environment.GetStudio(cs::GetString("studio.channel"), versionOverride);
            BOOST_LOG_TRIVIAL(trace) << "got studio!";

            BOOST_LOG_TRIVIAL(trace) << "parsing arguments...";
            std::list<std::string> studioArguments;
            studioArguments.push_back(studioData.second);
            if (arguments.size() > 0) {
                for (std::string argument: arguments) {
                    if (argument.rfind("roblox-studio:", 0) == 0) {
                        studioArguments.push_back("-protocolString");
                    }
                    studioArguments.push_back(argument);
                }
            } else {
                studioArguments.push_back("-ide");
            }
            BOOST_LOG_TRIVIAL(trace) << "arguments parsed!";

            runner.SetEnvironment(cs::GetStringMap("studio.env"));

            runner.AddLaunchers(cs::GetString("studio.launcher.pre"));
            runner.AddLaunchers(cs::GetString("cork.launcher"));
            runner.AddLaunchers(cs::GetString("studio.launcher.post"));

            runner.Execute(studioArguments, studioData.first);
        } else if (operationMode == "runner") {
            runner.Execute(arguments);
        } else if (operationMode == "clear") {
            if (arguments.size() > 0) {
                std::string target = arguments.front();

                BOOST_LOG_TRIVIAL(info) << "clear target: " << target;
                if (target == "versions") {
                    environment.CleanVersions();
                } else if (target == "downloads") {
                    fs::remove_all(fs::path(cs::GetDownloadsPath()));
                } else if (target == "settings") {
                    cs::LoadDefaults();
                    cs::SaveSettings();
                } else {
                    BOOST_LOG_TRIVIAL(error) << "invalid clear target";
                }
            } else {
                BOOST_LOG_TRIVIAL(error) << "no target to clear";
            }
        } else if (operationMode == "version") {
            std::cout << CORK_VERSION << " (" << CORK_CODENAME << ")" << std::endl;
        } else {
            BOOST_LOG_TRIVIAL(error) << "invalid mode given";
        }
    } else {
        BOOST_LOG_TRIVIAL(error) << "no mode given";
    }

    BOOST_LOG_TRIVIAL(debug) << "end";
}
