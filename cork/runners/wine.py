import os
from cork.runners.native import NativeRunner

class WineRunner(NativeRunner):
    def __init__(self, prefix, dist="", launch_type="wine", launcher="", environment={}):
        self.dist = dist
        self.launch_type = launch_type
        self.prefix = os.path.abspath(prefix)

        super().__init__(launcher, environment)
    
    def execute(self, arguments, cwd=""):
        if cwd == "":
            cwd = self.prefix
        
        wine_arguments = arguments
        if self.launch_type != "proton" or self.dist == "":
            wine_binary = "wine64"

            if self.dist != "":
                wine_binary = os.path.join(os.path.abspath(
                    self.dist), "bin", wine_binary)
            
            self.environment["WINEPREFIX"] = self.prefix

            wine_arguments = [wine_binary] + arguments
        else:
            proton_binary = os.path.join(os.path.abspath(
                    self.dist), "..", "proton")
            
            self.environment["STEAM_COMPAT_DATA_PATH"] = os.path.join(self.prefix, "..")

            wine_arguments = [proton_binary, "run"] + arguments

        return super().execute(wine_arguments, cwd)
        