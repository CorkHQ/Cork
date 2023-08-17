import os
import json
import urllib.parse
from typing import Tuple
from cork import rbxcdn
from cork.wine import WineSession

player_arguments = {
    "launchmode":       "--",
    "gameinfo":         "-t ",
    "placelauncherurl": "-j ",
    "launchtime":       "--launchtime=",
    "browsertrackerid": "-b ",
    "robloxLocale":     "--rloc ",
    "gameLocale":       "--gloc ",
    "channel":          "-channel "
}

class RobloxSession(WineSession):
    def __init__(self, prefix, dist="", launcher=[], environment={}, fflags={}, launch_type="wine", wine64=False, log_directory=""):
        WineSession.__init__(self, prefix, dist, launcher,
                             environment, launch_type, wine64, log_directory)
        self.fflags = fflags

    def get_player(self, state_dictionary={}, channel="", version_override="") -> Tuple[str, str]:
        state_dictionary["state"] = "getting_version"
        
        version = version_override if version_override != "" else rbxcdn.get_version(
            "WindowsPlayer", channel)["clientVersionUpload"]

        version_directory = os.path.join(
            self.get_drive(), "Roblox", "Versions", version)

        if not os.path.isdir(version_directory) or not os.path.exists(os.path.join(version_directory, "RobloxPlayerBeta.exe")):
            state_dictionary["state"] = "installing"
            state_dictionary["version"] = version
            
            rbxcdn.install_version(
                version, version_directory, channel, rbxcdn.package_dictionaries["Player"], state_dictionary=state_dictionary)

        exe_path = os.path.join("C:/", os.path.relpath(os.path.join(
            version_directory, "RobloxPlayerBeta.exe"), self.get_drive()))
        
        return exe_path, version_directory

    def get_studio(self, state_dictionary={}, channel="", version_override="") -> Tuple[str, str]:
        state_dictionary["state"] = "getting_version"
        
        version = version_override if version_override != "" else rbxcdn.get_version(
            "WindowsStudio64", channel)["clientVersionUpload"]

        version_directory = os.path.join(
            self.get_drive(), "Roblox", "Versions", version)

        if not os.path.isdir(version_directory) or not os.path.exists(os.path.join(version_directory, "RobloxStudioBeta.exe")):
            state_dictionary["state"] = "installing"
            state_dictionary["version"] = version

            rbxcdn.install_version(
                version, version_directory, channel, rbxcdn.package_dictionaries["Studio"], state_dictionary=state_dictionary)

        exe_path = os.path.join("C:/", os.path.relpath(os.path.join(
            version_directory, "RobloxStudioBeta.exe"), self.get_drive()))

        return exe_path, version_directory

    def apply_fflags(self, player_directory):
        if not os.path.isdir(os.path.join(player_directory, "ClientSettings")):
            os.makedirs(os.path.join(player_directory, "ClientSettings"))

        with open(os.path.join(player_directory, "ClientSettings", "ClientAppSettings.json"), "w") as file:
            file.write(json.dumps(self.fflags, indent=4))

    def execute_player(self, arguments, state_dictionary={}, channel="live", version=""):
        if len(arguments) > 0 and arguments[0].startswith("roblox-player:1+launchmode:"):
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

                if argument_parts[0] in player_arguments:
                    arguments.append(
                        player_arguments[argument_parts[0]] + argument_parts[1])

        if channel == "live":
            channel = ""
        
        player_exe, player_directory = self.get_player(
            state_dictionary=state_dictionary, channel=channel, version_override=version)

        self.apply_fflags(player_directory)
        
        state_dictionary["state"] = "done"
        return self.execute([player_exe] + arguments, cwd=player_directory)

    def execute_studio(self, arguments, state_dictionary={}, channel="live", version=""):
        if len(arguments) > 0 and arguments[0].startswith("roblox-studio:"):
            startup_argument = arguments[0]

            argument_map = {}
            arguments = []
            for argument_piece in startup_argument.split("+"):
                argument_parts = argument_piece.split(":")
                
                if argument_parts[0] == "channel":
                    if channel == "live":
                        channel = argument_parts[1].lower()
                    else:
                        argument_parts[1] = channel
                
                if argument_parts[0] == "gameinfo":
                    arguments.append("-url https://www.roblox.com/Login/Negotiate.ashx")
                    arguments.append(f"-ticket {argument_parts[1]}")
                else:
                    if len(argument_parts) > 1:
                        arguments.append(f"-{argument_parts[0]} {argument_parts[1]}")
                    else:
                        arguments.append(f"-{argument_parts[0]}")
                
                if len(argument_parts) > 1:
                    argument_map[argument_parts[0]] = argument_parts[1]
                else:
                    argument_map[argument_parts[0]] = True
            
            if "launchmode" in argument_map and "task" not in argument_map:
                if argument_map["launchmode"] == "plugin":
                    arguments.append(f"-task InstallPlugin -pluginId {argument_map['pluginid']}")
                elif argument_map["launchmode"] == "edit":
                    arguments.append("-task EditPlace")
                elif argument_map["launchmode"] == "asset":
                    arguments.append(f"-task TryAsset -assetId {argument_map['assetid']}")
        
        if channel == "live":
            channel = ""
        
        studio_exe, studio_directory = self.get_studio(
            state_dictionary=state_dictionary, channel=channel, version_override=version)
        
        state_dictionary["state"] = "done"
        return self.execute([studio_exe] + arguments, cwd=studio_directory)
