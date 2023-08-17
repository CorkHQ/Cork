import os
import pwd
import logging
from subprocess import Popen, PIPE, STDOUT

class WineSession:
    def __init__(self, prefix, dist="", launcher=[], environment={}, launch_type="wine", wine64=False):
        self.dist = dist
        self.prefix = os.path.abspath(prefix)
        self.environment = environment
        self.launch_type = launch_type
        self.launcher = launcher
        self.wine64 = wine64
    
    def execute(self, arguments, binary_name="", cwd=""):
        wine_environment = os.environ.copy() | self.environment

        if cwd == "":
            cwd = self.prefix

        if self.launch_type != "proton" or self.dist == "":
            if binary_name == "":
                binary_name = "wine64" if self.wine64 else "wine"

            wine_binary = binary_name

            if self.dist != "":
                wine_binary = os.path.join(os.path.abspath(
                    self.dist), "bin", binary_name)
            
            wine_environment["WINEPREFIX"] = self.prefix

            command = self.launcher + [wine_binary] + arguments
            logging.debug(f'Executing "{command}"')

            return Popen(command, env=wine_environment, cwd=cwd, stdout=PIPE, stderr=STDOUT, stdin=PIPE)
        else:
            proton_binary = os.path.join(os.path.abspath(
                    self.dist), "..", "proton")
            
            if binary_name != "":
                proton_binary = os.path.join(os.path.abspath(
                    self.dist), "bin", binary_name)
            
            wine_environment["STEAM_COMPAT_DATA_PATH"] = os.path.join(self.prefix, "..")

            command = self.launcher + [proton_binary, "run"] + arguments
            logging.debug(f'Executing "{command}"')
            
            return Popen(command, env=wine_environment, cwd=cwd, stdout=PIPE, stderr=STDOUT, stdin=PIPE)


    def initialize_prefix(self):
        return self.execute(["wineboot"])

    def shutdown_prefix(self):
        return self.execute(["-k"], binary_name="wineserver")

    def wait_prefix(self):
        return self.execute(["-wk"], binary_name="wineserver")

    def get_drive(self) -> str:
        return os.path.join(self.prefix, "drive_c")

    def get_user(self) -> str:
        return pwd.getpwuid(os.getuid())[0]
