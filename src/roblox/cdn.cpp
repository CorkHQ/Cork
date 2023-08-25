#include <chrono>
#include <iostream>
#include <stdexcept>
#include <cpr/cpr.h>

std::string urls[] = {
    "https://setup.rbxcdn.com/",
    "https://setup-ak.rbxcdn.com/",
    "https://setup-cfly.rbxcdn.com/",
    "https://s3.amazonaws.com/setup.roblox.com/"
};

namespace cork::roblox {
    std::string GetCDN() {
        std::string fastestUrl = "";
        int fastestTime = 10000;

        for (std::string url : urls) {
            auto start = std::chrono::high_resolution_clock::now();

            cpr::Response r = cpr::Get(cpr::Url{url + "version"}, cpr::Timeout{fastestTime});

            auto stop = std::chrono::high_resolution_clock::now();

            if (r.status_code == 200) {
                int duration = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start).count();
                if (duration < fastestTime) {
                    fastestTime = duration;
                    fastestUrl = url;
                }
            }
        }

        if (fastestUrl == "") {
            throw std::runtime_error("No CDN URL has responded!");
        }
        
        return fastestUrl;
    }
}