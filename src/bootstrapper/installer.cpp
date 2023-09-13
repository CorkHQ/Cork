#include <vector>
#include <iostream>
#include <stdexcept>
#include <filesystem>
#include <cpr/cpr.h>
#include <openssl/md5.h>
#include <openssl/evp.h>
#ifdef LOCAL_LIBZIPPP
#include <libzippp.h>
#else
#include <libzippp/libzippp.h>
#endif
#include <boost/log/trivial.hpp>
#include <boost/asio/post.hpp>
#include <boost/asio/thread_pool.hpp>
#include "../roblox/cdn.hpp"
#include "../roblox/packages.hpp"

namespace cr = cork::roblox;
namespace fs = std::filesystem;

std::string appSettings = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<Settings>\r\n        <ContentFolder>content</ContentFolder>\r\n        <BaseUrl>http://www.roblox.com</BaseUrl>\r\n</Settings>\r\n";

std::string hexToString(const uint8_t *data, int len)
{
    std::stringstream ss;
    ss << std::hex;

    for( int i(0) ; i < len; ++i )
        ss << std::setw(2) << std::setfill('0') << (int)data[i];

    return ss.str();
}

namespace cork::bootstrapper {
    void DisplayProgress(int installedPackages, int downloadedPackages, int totalPackages) {
        BOOST_LOG_TRIVIAL(trace) << "install progress: " << installedPackages << "/" << downloadedPackages << "/" << totalPackages;
    }

    void Install(std::string versionType, std::string version, std::string versionChannel, std::string versionDirectory, fs::path temporaryDirectory) {
        BOOST_LOG_TRIVIAL(info) << "installing version...";

        std::list<cr::package> packages = cr::GetPackages(versionType, version, versionChannel, cr::GetCDN());

        fs::path versionPath = fs::weakly_canonical(versionDirectory);

        if (fs::is_directory(versionPath)) {
            fs::remove_all(versionPath);
        }
        fs::create_directories(versionPath);

        fs::path temporaryPath = fs::weakly_canonical(versionPath / "tmp");
        if (temporaryDirectory != "") {
            temporaryPath = temporaryDirectory / version;
        }

        fs::create_directories(temporaryPath);

        std::atomic<int> totalPackages = packages.size();
        std::atomic<int> downloadedPackages = 0;
        std::atomic<int> installedPackages = 0;

        boost::asio::thread_pool installPool;

        for (cr::package package : packages) {
            fs::path filePath = temporaryPath / package.name;
            std::ofstream zipStream = std::ofstream(filePath, std::ios::binary);
            bool zipStreamOpen = true;

            int attempts = 0;
            bool success = false;

            while (success == false && attempts < 3) {
                try {
                    BOOST_LOG_TRIVIAL(trace) << "downloading " << package.name << "...";
                    cpr::Response response = cpr::Download(zipStream, cpr::Url{package.url});
                    
                    if (response.status_code != 200) {
                        throw std::runtime_error("Server responded with status code of not 200!");
                    }

                    zipStream.close();
                    zipStreamOpen = false;

                    std::ifstream inputStream(filePath, std::ios::binary);

                    EVP_MD_CTX* md5Context = EVP_MD_CTX_new();
                    EVP_MD_CTX_init(md5Context);
                    EVP_DigestInit_ex(md5Context, EVP_md5(), nullptr);
                    const size_t bufferSize = 4096;
                    char buffer[bufferSize];
                    while (!inputStream.eof()) {
                        inputStream.read(buffer, bufferSize);
                        EVP_DigestUpdate(md5Context, buffer, inputStream.gcount());
                    }
                    std::array<uint8_t, 16> result;
                    EVP_DigestFinal_ex(md5Context, result.data(), nullptr);
                    inputStream.close();
                    EVP_MD_CTX_free(md5Context);

                    std::string md5 = hexToString(result.data(), result.size());

                    if (md5 != package.checksum) {
                        throw std::runtime_error("Checksum incorrect!");
                    }

                    success = true;
                }
                catch (std::exception &e) {
                    BOOST_LOG_TRIVIAL(warning) << "failed to download " << package.name << ": " << e.what();

                    if (zipStreamOpen == true) {
                        zipStream.close();
                        zipStreamOpen = false;
                    }

                    zipStream = std::ofstream(filePath, std::ios::binary);
                    zipStreamOpen = true;

                    attempts++;
                }
            }

            if (success == false) {
                if (zipStreamOpen == true) {
                    zipStream.close();
                    zipStreamOpen = false;
                }

                throw std::runtime_error("Failed to download file!");
            }

            BOOST_LOG_TRIVIAL(trace) << "downloaded " << package.name << "!";

            downloadedPackages++;
            DisplayProgress(installedPackages, downloadedPackages, totalPackages);

            boost::asio::post(installPool,
            [filePath, versionPath, package, &installedPackages, &downloadedPackages, &totalPackages]()
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
                installedPackages++;
                DisplayProgress(installedPackages, downloadedPackages, totalPackages);
                
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