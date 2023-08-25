#include <boost/process.hpp>
#include <filesystem>
#include "native.hpp"

namespace bp = boost::process;
namespace fs = std::filesystem;

namespace cork::runners {
    NativeRunner::NativeRunner() {}
    
    void NativeRunner::AddLauncher(std:: string launcher) {
        launcherList.push_back(launcher);
    }
    void NativeRunner::AddLauncher(std::list<std::string> list) {
        for (std::string launcher : list) {
            AddLauncher(launcher);
        }
    }

    void NativeRunner::SetEnvironment(std:: string var, std:: string value) {
        environmentMap[var] = value;
    }
    void NativeRunner::SetEnvironment(std::map<std::string, std::string> map) {
        for (std::pair<std::string, std::string> const& pair : map) {
            SetEnvironment(pair.first, pair.second);
        }
    }

    void NativeRunner::Execute(std::list<std::string> arguments, std::string cwd) {
        auto system_env = boost::this_process::environment();

        bp::environment env = system_env;
        for (std::pair<std::string, std::string> const& pair : environmentMap) {
            env[pair.first] = pair.second;
        }

        std::list<std::string> newArguments;
        for (std::string launcher : launcherList) {
            newArguments.push_back(launcher);
        }
        for (std::string argument : arguments) {
            newArguments.push_back(argument);
        }

        bp::system(bp::args(newArguments), env, bp::start_dir(cwd));
    }
    void NativeRunner::Execute(std::list<std::string> arguments) {
        Execute(arguments, fs::current_path().string());
    }
}