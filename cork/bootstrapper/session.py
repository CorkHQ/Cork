import os
import json
import logging
import urllib.parse
from typing import Tuple
from cork.roblox import version as client_version
from cork.bootstrapper import installer

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

class RobloxSession():
    def __init__(self, runner, versions_directory, fflags={}):
        self.runner = runner
        self.fflags = fflags
        self.versions_directory = versions_directory

    def get_player(self, state_dictionary={}, channel="", version_override="") -> Tuple[str, str]:
        state_dictionary["state"] = "getting_version"
        
        version = version_override if version_override != "" else client_version.get(
            "WindowsPlayer", channel)["clientVersionUpload"]
        logging.info(f'Player Version: {version}')

        version_directory = os.path.join(self.versions_directory, version)

        if not os.path.isdir(version_directory) or not os.path.exists(os.path.join(version_directory, "RobloxPlayerBeta.exe")):
            state_dictionary["state"] = "preparing"
            state_dictionary["version"] = version
            
            installer.install(version, version_directory, channel, "WindowsPlayer", state_dictionary)

        exe_path = os.path.join(version_directory, "RobloxPlayerBeta.exe")
        
        return exe_path, version_directory

    def get_studio(self, state_dictionary={}, channel="", version_override="") -> Tuple[str, str]:
        state_dictionary["state"] = "getting_version"
        
        version = version_override if version_override != "" else client_version.get(
            "WindowsStudio64", channel)["clientVersionUpload"]
        logging.info(f'Studio Version: {version}')

        version_directory = os.path.join(self.versions_directory, version)

        if not os.path.isdir(version_directory) or not os.path.exists(os.path.join(version_directory, "RobloxStudioBeta.exe")):
            state_dictionary["state"] = "preparing"
            state_dictionary["version"] = version

            installer.install(version, version_directory, channel, "WindowsStudio64", state_dictionary)

        exe_path = os.path.join(version_directory, "RobloxStudioBeta.exe")

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
        logging.info("Executing Player")
        return self.runner.execute([player_exe] + arguments, cwd=player_directory)

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
        logging.info("Executing Studio")
        return self.runner.execute([studio_exe] + arguments, cwd=studio_directory)
