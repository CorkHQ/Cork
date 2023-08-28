#include <map>
#include <list>
#include <string>

namespace cork::runners {
    class NativeRunner {
        private:
            std::list<std::string> launcherList;
            std::map<std::string, std::string> environmentMap;
        public:
            NativeRunner();

            void AddLauncher(std:: string launcher);
            void AddLaunchers(std::list<std::string> list);
            void AddLaunchers(std:: string launchers);

            void SetEnvironment(std:: string var, std:: string value);
            void SetEnvironment(std::map<std::string, std::string> map);

            virtual void Execute(std::list<std::string> arguments, std::string cwd);
            virtual void Execute(std::list<std::string> arguments);
    };
}