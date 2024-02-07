#include <boost/process.hpp>
#include <boost/log/trivial.hpp>
#include <boost/program_options/parsers.hpp>
#include <filesystem>
#include <iostream>
#include "native.hpp"

namespace bp = boost::process;
namespace bo = boost::program_options;
namespace fs = std::filesystem;

namespace cork::runners {
    NativeRunner::NativeRunner() {}
    
    void NativeRunner::AddLauncher(std:: string launcher) {
        launcherList.push_back(launcher);
    }

    void NativeRunner::AddLaunchers(std::list<std::string> list) {
        for (std::string launcher : list) {
            AddLauncher(launcher);
        }
    }
    void NativeRunner::AddLaunchers(std:: string launchers) {
        for (std::string launcher : bo::split_unix(launchers)) {
            AddLauncher(launcher);
        }
    }

    bool NativeRunner::HasEnvironment(std:: string key) {
        return (environmentMap.count(key) > 0);
    }
    void NativeRunner::SetEnvironment(std:: string var, std:: string value, bool preserveIfExists) {
        if (preserveIfExists && HasEnvironment(var)) {
            return;
        }
        environmentMap[var] = value;
    }
    void NativeRunner::SetEnvironment(std::map<std::string, std::string> map, bool preserveIfExists) {
        for (std::pair<std::string, std::string> const& pair : map) {
            SetEnvironment(pair.first, pair.second, preserveIfExists);
        }
    }
    std::string NativeRunner::GetEnvironment(std::string var) {
        if (HasEnvironment(var)) {
            return environmentMap[var];
        }
        return "";
    }

    void NativeRunner::Execute(std::list<std::string> arguments, std::string cwd) {
        auto systemEnvironment = boost::this_process::environment();

        bp::environment env = systemEnvironment;
        for (std::pair<std::string, std::string> const& pair : environmentMap) {
            env[pair.first] = pair.second;
        }

        std::list<std::string> newArguments;
        for (std::string launcher : launcherList) {
            newArguments.push_back(launcher);
        }
        for (std::string argument : arguments) {
            newArguments.push_back(argument);
            std::cout << argument << std::endl;
        }

        bp::ipstream output;
        std::string line;

        bp::child childProcess(bp::args(newArguments), env, bp::start_dir(cwd), (bp::std_out & bp::std_err) > output);
        while (std::getline(output, line)) {
            BOOST_LOG_TRIVIAL(info) << line;
        }
    }
    void NativeRunner::Execute(std::list<std::string> arguments) {
        Execute(arguments, fs::current_path().string());
    }
}