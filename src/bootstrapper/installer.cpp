#include <vector>
#include <iostream>
#include <filesystem>
#include <cpr/cpr.h>
#include <libzippp.h>
#include <boost/log/trivial.hpp>
#include <boost/asio/post.hpp>
#include <boost/asio/thread_pool.hpp>
#include "../roblox/cdn.hpp"
#include "../roblox/packages.hpp"

namespace cr = cork::roblox;
namespace fs = std::filesystem;

std::string appSettings = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<Settings>\r\n        <ContentFolder>content</ContentFolder>\r\n        <BaseUrl>http://www.roblox.com</BaseUrl>\r\n</Settings>\r\n";

namespace cork::bootstrapper {
    void Install(std::string versionType, std::string version, std::string versionChannel, std::string versionDirectory) {
        BOOST_LOG_TRIVIAL(info) << "installing version...";

        std::list<cr::package> packages = cr::GetPackages(versionType, version, versionChannel, cr::GetCDN());

        fs::path versionPath = fs::weakly_canonical(versionDirectory);

        if (fs::is_directory(versionPath)) {
            fs::remove_all(versionPath);
        }
        fs::create_directories(versionPath);

        fs::path temporaryPath = fs::weakly_canonical(versionPath / "tmp");
        fs::create_directories(temporaryPath);

        boost::asio::thread_pool installPool;

        for (cr::package package : packages) {
            fs::path filePath = temporaryPath / package.name;
            std::ofstream zipStream = std::ofstream(filePath, std::ios::binary);

            BOOST_LOG_TRIVIAL(trace) << "downloading " << package.name << "...";
            cpr::Response response = cpr::Download(zipStream, cpr::Url{package.url});
            zipStream.close();
            BOOST_LOG_TRIVIAL(trace) << "downloaded " << package.name << "!";

            boost::asio::post(installPool,
            [filePath, versionPath, package]()
            {
                BOOST_LOG_TRIVIAL(trace) << "installing " << package.name << "...";
                libzippp::ZipArchive zipFile(filePath);
                zipFile.open(libzippp::ZipArchive::ReadOnly);

                std::vector<libzippp::ZipEntry> entries = zipFile.getEntries();
                std::vector<libzippp::ZipEntry>::iterator it;

                for (it=entries.begin() ; it!=entries.end(); ++it) {
                    libzippp::ZipEntry entry = *it;
                    std::string name = entry.getName();

                    std::replace( name.begin(), name.end(), '\\', '/');
                    
                    int numberSlashes = 0;

                    for (char c : name) {
                        if (c == '/') {
                            numberSlashes += 1;
                        } else {
                            break;
                        }
                    }

                    name.erase(0, numberSlashes);

                    fs::path targetPath = versionPath / package.target / name;
                    fs::create_directories(targetPath.parent_path());

                    std::ofstream fileStream(targetPath);
                    entry.readContent(fileStream);
                    fileStream.close();
                }

                zipFile.close();
                BOOST_LOG_TRIVIAL(info) << "installed " << package.name << "!";
            });
        }

        installPool.join();

        std::ofstream appStream = std::ofstream(versionPath / "AppSettings.xml");
        appStream << appSettings;
        appStream.close();

        fs::remove_all(temporaryPath);

        BOOST_LOG_TRIVIAL(info) << "version installed!";
    }
}