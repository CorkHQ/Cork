import os
import json
import shutil
import urllib.parse
from zipfile import ZipFile
from urllib.request import urlopen
from io import BytesIO
from typing import Tuple
from wine import WineSession


class RobloxSession(WineSession):
    def __init__(self, prefix, wine_home="", environment={}, fflags={}, wine64=False):
        WineSession.__init__(self, prefix, wine_home, environment, wine64)
        self.fflags = fflags

    def get_version(self, version_type, channel=""):
        base_url = "https://setup.rbxcdn.com/"
        if channel != "":
            base_url = f"{base_url}channel/{channel}/"

        version_response = urlopen(f"{base_url}{version_type}")
        return version_response.read().decode('utf-8')

    def install_version(self, version, studio=False):
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

            print(f"Installing Studio {version}...")
        else:
            print(f"Installing Player {version}...")

        version_directory = os.path.join(
            self.get_drive(), "Roblox", "Versions", version)

        if os.path.isdir(version_directory):
            shutil.rmtree(version_directory)

        os.makedirs(version_directory)

        for package, target in packages.items():
            target_directory = os.path.join(version_directory, target)
            if not os.path.isdir(target_directory):
                os.makedirs(target_directory)

            response = urlopen(
                f"https://setup.rbxcdn.com/{version}-{package}")
            zip = ZipFile(BytesIO(response.read()))
            for zipinfo in zip.infolist():
                zipinfo.filename = zipinfo.filename.replace("\\", "/")
                zip.extract(zipinfo, target_directory)

        with open(os.path.join(version_directory, "AppSettings.xml"), "w") as file:
            file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n" +
                       "<Settings>\r\n" +
                       "        <ContentFolder>content</ContentFolder>\r\n" +
                       "        <BaseUrl>http://www.roblox.com</BaseUrl>\r\n" +
                       "</Settings>\r\n"
                       )

        print(f"{version} has been installed!")

    def get_player(self) -> Tuple[str, str]:
        version = self.get_version("version")

        version_directory = os.path.join(
            self.get_drive(), "Roblox", "Versions", version)

        if not os.path.isdir(version_directory) or not os.path.exists(os.path.join(version_directory, "RobloxPlayerBeta.exe")):
            self.install_version(version)

        exe_path = os.path.join("C:/", os.path.relpath(os.path.join(
            version_directory, "RobloxPlayerBeta.exe"), self.get_drive()))

        return exe_path, version_directory

    def get_studio(self) -> Tuple[str, str]:
        version = self.get_version("versionQTStudio")

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

    def execute_player(self, arguments, launcher=""):
        player_exe, player_directory = self.get_player()

        self.apply_fflags(player_directory)
        if len(arguments) > 0 and arguments[0].startswith("roblox-player:1+launchmode:"):
            argument_dictionary = {
                "launchmode":       "--",
                "gameinfo":         "-t ",
                "placelauncherurl": "-j ",
                "launchtime":       "--launchtime=",
                "browsertrackerid": "-b ",
                "robloxLocale":     "--rloc ",
                "gameLocale":       "--gloc ",
            }
            startup_argument = arguments[0]

            arguments = []
            for argument_piece in startup_argument.split("+"):
                argument_parts = argument_piece.split(":")

                if argument_parts[0] == "launchmode" and argument_parts[1] == "play":
                    argument_parts[1] = "app"
                if argument_parts[0] == "placelauncherurl":
                    argument_parts[1] = urllib.parse.unquote(argument_parts[1])

                if argument_parts[0] in argument_dictionary:
                    arguments.append(
                        argument_dictionary[argument_parts[0]] + argument_parts[1])

        return self.execute([player_exe] + arguments, cwd=player_directory, launcher=launcher)

    def execute_studio(self, arguments, launcher=""):
        studio_exe, studio_directory = self.get_studio()

        return self.execute([studio_exe] + arguments, cwd=studio_directory, launcher=launcher)
