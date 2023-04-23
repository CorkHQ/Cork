import os
import requests
import glob
import json
from typing import Optional, Tuple
from wine import WineSession


class RobloxSession(WineSession):
    def __init__(self, prefix, wine_home="", environment={}, fflags={}, wine64=False):
        WineSession.__init__(self, prefix, wine_home, environment, wine64)
        self.fflags = fflags

    def install_roblox(self):
        url = "https://www.roblox.com/download/client"
        request = requests.get(url, allow_redirects=True)

        open(os.path.join(self.get_drive(), "RobloxPlayerLauncher.exe"),
             "wb").write(request.content)
        return self.execute(["C:/RobloxPlayerLauncher.exe"])

    def get_player(self) -> Tuple[Optional[str], Optional[str]]:
        installation_directories = [
            "Program Files",
            "Program Files (x86)",
            os.path.join("users", self.get_user(), "AppData", "Local")
        ]

        for directory in installation_directories:
            full_directory = os.path.join(
                self.get_drive(), directory, "Roblox", "Versions")
            if os.path.exists(full_directory):
                for binary in glob.glob(os.path.join(full_directory, "version-*/RobloxPlayerLauncher.exe")):
                    exe_path = os.path.join(
                        "C:/", os.path.relpath(binary, self.get_drive()))
                    return exe_path, os.path.dirname(binary)

        return None, None

    def apply_fflags(self, player_directory):
        if not os.path.isdir(os.path.join(player_directory, "ClientSettings")):
            os.makedirs(os.path.join(player_directory, "ClientSettings"))

        with open(os.path.join(player_directory, "ClientSettings", "ClientAppSettings.json"), "w") as file:
            file.write(json.dumps(self.fflags, indent=4))

    def execute_player(self, arguments, launcher=""):
        player_exe, player_directory = self.get_player()
        if not player_exe:
            self.install_roblox()
            player_exe, player_directory = self.get_player()

        if player_exe and player_directory:
            self.apply_fflags(player_directory)

            return self.execute([player_exe] + arguments, cwd=player_directory, launcher=launcher)

        raise Exception("Roblox could not be installed!")
