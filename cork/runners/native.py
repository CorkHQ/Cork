import os
import logging
from subprocess import Popen, PIPE, STDOUT

class NativeRunner:
    def __init__(self, launcher="", environment={}):
        self.environment = environment
        self.launcher = launcher
    
    def execute(self, arguments, cwd=""):
        target_environment = os.environ.copy() | self.environment

        command = self.launcher + arguments
        logging.debug(f'Executing "{command}"')

        return Popen(command, env=target_environment, cwd=cwd, stdout=PIPE, stderr=STDOUT, stdin=PIPE)