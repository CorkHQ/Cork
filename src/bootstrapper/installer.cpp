#include <iostream>
#include <filesystem>
#include <cpr/cpr.h>
#include <elzip/elzip.hpp>
#include "../roblox/cdn.hpp"
#include "../roblox/packages.hpp"

namespace cr = cork::roblox;
namespace fs = std::filesystem;

std::string appSettings = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<Settings>\r\n        <ContentFolder>content</ContentFolder>\r\n        <BaseUrl>http://www.roblox.com</BaseUrl>\r\n</Settings>\r\n";

namespace cork::bootstrapper {
    void Install(std::string versionType, std::string version, std::string versionChannel, std::string versionDirectory) {
        std::list<cr::package> packages = cr::GetPackages(versionType, version, versionChannel, cr::GetCDN());

        fs::path versionPath = fs::weakly_canonical(versionDirectory);

        if (fs::is_directory(versionPath)) {
            fs::remove_all(versionPath);
        }
        fs::create_directories(versionPath);

        fs::path temporaryPath = fs::weakly_canonical(versionPath / "tmp");
        fs::create_directories(temporaryPath);

        for (cr::package package : packages) {
            std::cout << package.name << std::endl;

            fs::path filePath = temporaryPath / package.name;
            std::ofstream ofstream = std::ofstream(filePath, std::ios::binary);

            cpr::Response response = cpr::Download(ofstream, cpr::Url{package.url});
            ofstream.close();

            elz::extractZip(filePath, versionPath / package.target);

            std::cout << "Done!" << std::endl;
        }

        std::ofstream ofstream = std::ofstream(versionPath / "AppSettings.xml");
        ofstream << appSettings;
        ofstream.close();

        fs::remove_all(temporaryPath);
    }
}