from zipfile import ZipFile
from urllib import request
from joblib import Parallel, delayed
from io import BytesIO
import logging
import hashlib
import shutil
import time
import json
import os

package_dictionaries = {
    "Player": {
        "RobloxApp.zip":                 "",
        "WebView2.zip":                  "",

        "shaders.zip":                   "shaders",
        "ssl.zip":                       "ssl",

        "content-avatar.zip":            "content/avatar",
        "content-configs.zip":           "content/configs",
        "content-fonts.zip":             "content/fonts",
        "content-sky.zip":               "content/sky",
        "content-sounds.zip":            "content/sounds",
        "content-textures2.zip":         "content/textures",
        "content-models.zip":            "content/models",

        "content-textures3.zip":         "PlatformContent/pc/textures",
        "content-terrain.zip":           "PlatformContent/pc/terrain",
        "content-platform-fonts.zip":    "PlatformContent/pc/fonts",

        "extracontent-luapackages.zip":  "ExtraContent/LuaPackages",
        "extracontent-translations.zip": "ExtraContent/translations",
        "extracontent-models.zip":       "ExtraContent/models",
        "extracontent-textures.zip":     "ExtraContent/textures",
        "extracontent-places.zip":       "ExtraContent/places"
    },

    "Studio": {
        "ApplicationConfig.zip":           "ApplicationConfig",
        "BuiltInPlugins.zip":              "BuiltInPlugins",
        "BuiltInStandalonePlugins.zip":    "BuiltInStandalonePlugins",
        "Plugins.zip":                     "Plugins",
        "Qml.zip":                         "Qml",
        "StudioFonts.zip":                 "StudioFonts",
        "WebView2.zip":                    "",
        "RobloxStudio.zip":                "",
        "Libraries.zip":                   "",
        "LibrariesQt5.zip":                "",
        "content-avatar.zip":              "content/avatar",
        "content-configs.zip":             "content/configs",
        "content-fonts.zip":               "content/fonts",
        "content-models.zip":              "content/models",
        "content-qt_translations.zip":     "content/qt_translations",
        "content-sky.zip":                 "content/sky",
        "content-sounds.zip":              "content/sounds",
        "shaders.zip":                     "shaders",
        "ssl.zip":                         "ssl",
        "content-textures2.zip":           "content/textures",
        "content-textures3.zip":           "PlatformContent/pc/textures",
        "content-studio_svg_textures.zip": "content/studio_svg_textures",
        "content-terrain.zip":             "PlatformContent/pc/terrain",
        "content-platform-fonts.zip":      "PlatformContent/pc/fonts",
        "content-api-docs.zip":            "content/api_docs",
        "extracontent-scripts.zip":        "ExtraContent/scripts",
        "extracontent-luapackages.zip":    "ExtraContent/LuaPackages",
        "extracontent-translations.zip":   "ExtraContent/translations",
        "extracontent-models.zip":         "ExtraContent/models",
        "extracontent-textures.zip":       "ExtraContent/textures",
        "redist.zip":                      ""
    }
}

cdn_urls = [
    "https://setup.rbxcdn.com/",
	"https://setup-ak.rbxcdn.com/",
	"https://setup-cfly.rbxcdn.com/",
	"https://s3.amazonaws.com/setup.roblox.com/"
]

def get_version(binary_type, channel):
    request_url = f"https://clientsettings.roblox.com/v2/client-version/{binary_type}"

    if channel != "":
        request_url = f"{request_url}/channel/{channel}"

    version_response = request.urlopen(request.Request(
        request_url, headers={"User-Agent": "Cork"}))
    return json.loads(version_response.read().decode('utf-8'))


def install_version(version, version_directory, version_channel, package_dictionary, state_dictionary={}):
    if os.path.isdir(version_directory):
        shutil.rmtree(version_directory)

    os.makedirs(version_directory)

    logging.debug("Trying to find fastest mirror")
    working_urls = {}
    for url in cdn_urls:
        start_time = time.time()
        try:
            request.urlopen(f"{url}version")
        except:
            logging.warning(f"Failed to access {url}")
        else:
            working_urls[url] = time.time() - start_time
    
    sorted_urls = sorted(working_urls)
    if len(sorted_urls) <= 0:
        raise ConnectionError("No mirror was found")
    
    url_base = sorted_urls[0]
    logging.debug(f"Fastest mirror is {url_base}")
    
    if version_channel != "":
        url_base = f"{url_base}channel/{version_channel}/"

    package_manifest_text = request.urlopen(request.Request(f"{url_base}{version}-rbxPkgManifest.txt", headers={
                                            "User-Agent": "Cork"})).read().decode("utf-8").split("\n", 1)[1].splitlines()
    package_manifest = {}
    line_count = 1
    last_header = ""

    for line in package_manifest_text:
        if line_count == 5:
            line_count = 1

        if line_count == 1:
            last_header = line
            package_manifest[last_header] = []
        else:
            package_manifest[last_header].append(line)
        line_count += 1

    package_zips = {}

    def download(package, target):
        logging.info(f"Downloading package {package}...")

        response = request.urlopen(request.Request(
            f"{url_base}{version}-{package}", headers={"User-Agent": "Cork"}))
        response_bytes = response.read()
        while package_manifest[package][0] != hashlib.md5(response_bytes).hexdigest():
            logging.error(f"Checksum failed for {package}, retrying...")
            response = request.urlopen(request.Request(
                f"{url_base}{version}-{package}", headers={"User-Agent": "Cork"}))
            response_bytes = response.read()

        zip = ZipFile(BytesIO(response_bytes))
        package_zips[(package, target)] = zip

        state_dictionary["packages_downloaded"] += 1

    state_dictionary["packages_downloaded"] = 0
    state_dictionary["packages_installed"] = 0
    state_dictionary["packages_total"] = len(package_dictionary)

    Parallel(n_jobs=len(package_dictionary), require='sharedmem')(
        delayed(download)(package, target) for package, target in package_dictionary.items())

    def install(package, target, zip):
        logging.info(f"Installing package {package}...")

        target_directory = os.path.join(version_directory, target)
        if not os.path.isdir(target_directory):
            os.makedirs(target_directory)

        for zipinfo in zip.infolist():
            zipinfo.filename = zipinfo.filename.replace("\\", "/")
            zip.extract(zipinfo, target_directory)
        
        state_dictionary["packages_installed"] += 1

    Parallel(n_jobs=len(package_zips), require='sharedmem')(delayed(install)(
        package, target, zip) for (package, target), zip in package_zips.items())

    with open(os.path.join(version_directory, "AppSettings.xml"), "w") as file:
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n" +
                   "<Settings>\r\n" +
                   "        <ContentFolder>content</ContentFolder>\r\n" +
                   "        <BaseUrl>http://www.roblox.com</BaseUrl>\r\n" +
                   "</Settings>\r\n"
                   )
