import subprocess
import os
import pwd


class WineSession:
    def __init__(self, prefix, wine_home="", environment={}, wine_type="wine", wine64=False):
        self.wine_home = wine_home
        self.prefix = os.path.abspath(prefix)
        self.environment = environment
        self.wine_type = wine_type
        self.wine64 = wine64
    
    def execute(self, arguments, binary_name="", cwd="", launcher=""):
        wine_environment = os.environ.copy() | self.environment

        if cwd == "":
            cwd = self.prefix

        if self.wine_type != "proton" and self.wine_home != "":
            if binary_name == "":
                binary_name = "wine64" if self.wine64 else "wine"

            wine_binary = binary_name

            if self.wine_home != "":
                wine_binary = os.path.join(os.path.abspath(
                    self.wine_home), "bin", binary_name)
            
            wine_environment["WINEPREFIX"] = self.prefix

            return subprocess.run((launcher.split(" ") if launcher != "" else []) + [wine_binary] + arguments, env=wine_environment, cwd=cwd)
        else:
            proton_binary = os.path.join(os.path.abspath(
                    self.wine_home), "..", "proton")
            
            if binary_name != "":
                proton_binary = os.path.join(os.path.abspath(
                    self.wine_home), "bin", binary_name)
            
            wine_environment["STEAM_COMPAT_DATA_PATH"] = self.prefix
            
            return subprocess.run((launcher.split(" ") if launcher != "" else []) + [proton_binary, "run"] + arguments, env=wine_environment, cwd=cwd)


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
