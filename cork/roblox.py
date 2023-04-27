import os
import json
import shutil
import urllib.parse
import asyncio
import hashlib
from zipfile import ZipFile
from urllib import request
from io import BytesIO
from typing import Tuple
from desktop_notifier.base import Urgency
from cork.wine import WineSession
from desktop_notifier import DesktopNotifier
from joblib import Parallel, delayed

class RobloxSession(WineSession):
    def __init__(self, prefix, dist="", environment={}, fflags={}, launch_type="wine", wine64=False):
        WineSession.__init__(self, prefix, dist, environment, launch_type, wine64)
        self.fflags = fflags

    def get_version(self, version_type, channel="live"):
        if channel == "live":
            channel = ""

        base_url = "https://setup.rbxcdn.com/"

        if channel != "":
            base_url = f"{base_url}channel/{channel}/"

        version_response = request.urlopen(request.Request(f"{base_url}{version_type}", headers={"User-Agent": "Cork"}))
        return version_response.read().decode('utf-8')

    def install_version(self, version, studio=False):
        notifier = DesktopNotifier()

        packages = {
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
        }

        if studio:
            packages = {
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

        loop = asyncio.new_event_loop()
        notification = loop.run_until_complete(notifier.send(
            title="Cork", icon="roblox-studio" if studio else "roblox-player", message=f"Installing {version}...", urgency=Urgency.Critical))

        version_directory = os.path.join(
            self.get_drive(), "Roblox", "Versions", version)

        if os.path.isdir(version_directory):
            shutil.rmtree(version_directory)

        os.makedirs(version_directory)

        package_manifest_text = request.urlopen(request.Request(f"https://setup.rbxcdn.com/{version}-rbxPkgManifest.txt", headers={"User-Agent": "Cork"})).read().decode("utf-8").split("\n", 1)[1].splitlines()
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
            print(f"Downloading package {package}...")

            response = request.urlopen(request.Request(
                f"https://setup.rbxcdn.com/{version}-{package}", headers={"User-Agent": "Cork"}))
            response_bytes = response.read()
            while package_manifest[package][0] != hashlib.md5(response_bytes).hexdigest():
                print(f"Checksum failed for {package}, retrying...")
                response = request.urlopen(request.Request(
                    f"https://setup.rbxcdn.com/{version}-{package}", headers={"User-Agent": "Cork"}))
                response_bytes = response.read()

            zip = ZipFile(BytesIO(response_bytes))
            package_zips[(package, target)] = zip
        
        Parallel(n_jobs=len(packages), require='sharedmem')(delayed(download)(package, target) for package, target in packages.items())
        print("Packages downloaded!")
        
        def install(package, target, zip):
            print(f"Installing package {package}...")

            target_directory = os.path.join(version_directory, target)
            if not os.path.isdir(target_directory):
                os.makedirs(target_directory)
            
            for zipinfo in zip.infolist():
                zipinfo.filename = zipinfo.filename.replace("\\", "/")
                zip.extract(zipinfo, target_directory)
        
        Parallel(n_jobs=len(package_zips), require='sharedmem')(delayed(install)(package, target, zip) for (package, target), zip in package_zips.items())
        print("Packages installed!")

        with open(os.path.join(version_directory, "AppSettings.xml"), "w") as file:
            file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n" +
                       "<Settings>\r\n" +
                       "        <ContentFolder>content</ContentFolder>\r\n" +
                       "        <BaseUrl>http://www.roblox.com</BaseUrl>\r\n" +
                       "</Settings>\r\n"
                       )

        print(f"{version} has been installed!")

        loop.run_until_complete(notifier.clear(notification))
        loop.run_until_complete(notifier.send(title="Cork", icon="roblox-studio" if studio else "roblox-player",
                                message=f"{version} has been installed!", urgency=Urgency.Normal))

        loop.close()

    def get_player(self, channel="live", version_override="") -> Tuple[str, str]:
        version = version_override if version_override != "" else self.get_version("version", channel=channel)

        version_directory = os.path.join(
            self.get_drive(), "Roblox", "Versions", version)

        if not os.path.isdir(version_directory) or not os.path.exists(os.path.join(version_directory, "RobloxPlayerBeta.exe")):
            self.install_version(version)

        exe_path = os.path.join("C:/", os.path.relpath(os.path.join(
            version_directory, "RobloxPlayerBeta.exe"), self.get_drive()))

        return exe_path, version_directory

    def get_studio(self, channel="live", version_override="") -> Tuple[str, str]:
        version = version_override if version_override != "" else self.get_version("versionQTStudio", channel=channel)

        version_directory = os.path.join(
            self.get_drive(), "Roblox", "Versions", version)

        if not os.path.isdir(version_directory) or not os.path.exists(os.path.join(version_directory, "RobloxStudioBeta.exe")):
            self.install_version(version, studio=True)

        exe_path = os.path.join("C:/", os.path.relpath(os.path.join(
            version_directory, "RobloxStudioBeta.exe"), self.get_drive()))

        return exe_path, version_directory

    def apply_fflags(self, player_directory):
        if not os.path.isdir(os.path.join(player_directory, "ClientSettings")):
            os.makedirs(os.path.join(player_directory, "ClientSettings"))

        with open(os.path.join(player_directory, "ClientSettings", "ClientAppSettings.json"), "w") as file:
            file.write(json.dumps(self.fflags, indent=4))

    def execute_player(self, arguments, launcher="", channel="live", version=""):
        if len(arguments) > 0 and arguments[0].startswith("roblox-player:1+launchmode:"):
            argument_dictionary = {
                "launchmode":       "--",
                "gameinfo":         "-t ",
                "placelauncherurl": "-j ",
                "launchtime":       "--launchtime=",
                "browsertrackerid": "-b ",
                "robloxLocale":     "--rloc ",
                "gameLocale":       "--gloc ",
                "channel":          "-channel "
            }
            startup_argument = arguments[0]

            arguments = []
            for argument_piece in startup_argument.split("+"):
                argument_parts = argument_piece.split(":")

                if argument_parts[0] == "launchmode" and argument_parts[1] == "play":
                    argument_parts[1] = "app"
                if argument_parts[0] == "placelauncherurl":
                    argument_parts[1] = urllib.parse.unquote(argument_parts[1])
                if argument_parts[0] == "channel":
                    if channel == "live":
                        channel = argument_parts[1].lower()
                    else:
                        argument_parts[1] = channel

                if argument_parts[0] in argument_dictionary:
                    arguments.append(
                        argument_dictionary[argument_parts[0]] + argument_parts[1])

        player_exe, player_directory = self.get_player(channel=channel, version_override=version)

        self.apply_fflags(player_directory)

        return self.execute([player_exe] + arguments, cwd=player_directory, launcher=launcher)

    def execute_studio(self, arguments, launcher="", channel="live", version=""):
        studio_exe, studio_directory = self.get_studio(channel=channel, version_override=version)

        return self.execute([studio_exe] + arguments, cwd=studio_directory, launcher=launcher)
