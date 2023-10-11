#include "native.hpp"

namespace cork::runners {
    class WineRunner: public NativeRunner {
        private:
            std::string dist;
            std::string launchType;
            std::string prefix;
        public:
            std::string GetPrefix();
            void SetPrefix(std::string newPrefix);
            void SetType(std::string newType);
            void SetDist(std::string newDist);

            void Execute(std::list<std::string> arguments, std::string cwd) override;
            void Execute(std::list<std::string> arguments) override;
    };
}