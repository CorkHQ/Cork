#include <iostream>
#include <boost/log/core.hpp> 
#include <boost/log/trivial.hpp> 
#include <boost/log/expressions.hpp>
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

void setupLogger() {
    auto formatSeverity = boost::log::expressions::
        attr<boost::log::trivial::severity_level>("Severity");
    
    boost::log::formatter logFmt =
        boost::log::expressions::format("%1%: %2%")
        % formatSeverity
        % boost::log::expressions::smessage;
    
    auto consoleSink = boost::log::add_console_log(std::clog);
    consoleSink->set_formatter(logFmt);
}

int main(int argc, char *argv[]){
    std::list<std::string> arguments(argv + 1, argv + argc);

    cs::LoadDefaults();
    cs::LoadSettings();
    cs::SaveSettings();

    setupLogger();

    std::string logLevel = cs::GetString("cork.loglevel");
    if (logLevel == "trace") {
        boost::log::core::get()->set_filter(        
            boost::log::trivial::severity >= boost::log::trivial::trace    
        ); 
    } else if (logLevel == "debug") {
        boost::log::core::get()->set_filter(        
            boost::log::trivial::severity >= boost::log::trivial::debug   
        ); 
    } else if (logLevel == "info") {
        boost::log::core::get()->set_filter(        
            boost::log::trivial::severity >= boost::log::trivial::info    
        ); 
    } else {
        boost::log::core::get()->set_filter(        
            boost::log::trivial::severity >= boost::log::trivial::warning    
        ); 
    }
    
    BOOST_LOG_TRIVIAL(info) << "Cork " << CORK_VERSION << " (" << CORK_CODENAME << ")";
    
    cb::RobloxEnvironment environment;
    environment.SetVersionsDirectory(cs::GetVersionsPath());

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
                for (std::string argument: environment.ParsePlayer(std::vector<std::string>{std::begin(arguments), std::end(arguments)})) {
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
                for (std::string argument: environment.ParseStudio(std::vector<std::string>{std::begin(arguments), std::end(arguments)})) {
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
        } else if (operationMode == "cleanup") {
            environment.CleanVersions();
        } else if (operationMode == "reset") {
            cs::LoadDefaults();
            cs::SaveSettings();
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
