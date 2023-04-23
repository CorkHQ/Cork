import subprocess
import os
import pwd


class WineSession:
    def __init__(self, prefix, wine_home="", environment={}):
        self.wine_home = wine_home
        self.prefix = os.path.abspath(prefix)
        self.environment = environment

    def execute(self, arguments, binary_name="wine", cwd="", launcher=""):
        wine_binary = binary_name

        if self.wine_home != "":
            wine_binary = os.path.join(os.path.abspath(
                self.wine_home), "bin", binary_name)

        wine_environment = os.environ.copy() | self.environment
        wine_environment["WINEPREFIX"] = self.prefix

        if cwd == "":
            cwd = self.prefix

        return subprocess.run(launcher.split(" ") if launcher != "" else [] + [wine_binary] + arguments, env=wine_environment, cwd=cwd)

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
