import argparse
import json
import os
import shutil
import threading
import time
import logging
from urllib import request
from datetime import datetime
from platformdirs import user_config_dir, user_data_dir, user_cache_dir
from cork import splash, __version__, __codename__, __file__
from cork.utils import deep_merge
from cork.runners.native import NativeRunner
from cork.runners.wine import WineRunner
from cork.bootstrapper.session import RobloxSession

def main():
    parser = argparse.ArgumentParser(
        prog='Cork',
        description='A bootstrapper for Roblox and Roblox Studio')
    parser.add_argument("mode", type=str, choices=[
                        "player", "studio", "runner", "install", "cleanup", "kill"])
    parser.add_argument("args", nargs='*')
    arguments = parser.parse_args()

    data_directory = user_data_dir("cork")
    config_directory = user_config_dir("cork")
    cache_directory = user_cache_dir("cork")

    log_directory = os.path.join(cache_directory, "logs")
    prefix_directory = os.path.join(data_directory, "pfx")
    versions_directory = os.path.join(data_directory, "versions")

    if not os.path.isdir(config_directory):
        os.makedirs(config_directory)
    if not os.path.isdir(data_directory):
        os.makedirs(data_directory)
    if not os.path.isdir(cache_directory):
        os.makedirs(cache_directory)
    
    if not os.path.isdir(log_directory):
        os.makedirs(log_directory)

    settings = {
        "cork": {
            "splash": True,
            "downloadthreads": 2,
            "installthreads": -1,
            "loglevel": "info",
            "launcher": "",
            "environment": {}
        },
        "wine": {
            "dist": "",
            "type": "wine",
            "environment": {
                "WINEDLLOVERRIDES": "winemenubuilder.exe=d"
            }
        },
        "roblox": {
            "channel": "live",
            "player": {
                "prelauncher": "",
                "postlauncher": "",
                "version": "",
                "environment": {},
                "remotefflags": "",
                "fflags": {}
            },
            "studio": {
                "prelauncher": "",
                "postlauncher": "",
                "version": "",
                "environment": {}
            }
        }
    }

    defaults_path = os.path.join(os.path.dirname(__file__), "default.json")
    if os.path.exists(defaults_path):
        with open(defaults_path, "r") as file:
            default_settings = file.read()
            default = json.loads(default_settings)
            settings = deep_merge(default, settings)
    
    data_settings = ""
    settings_path = os.path.join(config_directory, "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r") as file:
            data_settings = file.read()
            data = json.loads(data_settings)
            settings = deep_merge(data, settings)

    new_data_settings = json.dumps(settings, indent=4)
    if data_settings != new_data_settings:
        with open(settings_path, "w") as file:
            file.write(json.dumps(settings, indent=4))
    
    log_level = logging.INFO
    match settings["cork"]["loglevel"]:
        case "debug":
            log_level = logging.DEBUG
        case "info":
            log_level = logging.INFO
        case "error":
            log_level = logging.ERROR
    
    start_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_directory, f"cork-{start_time}.log")),
            logging.StreamHandler()
        ])
    logging.info(f"Cork {__version__} ({__codename__})")

    runner = NativeRunner(
        environment=settings["cork"]["environment"],
        launcher=[x for x in settings["cork"]["launcher"].split(" ") if x]
    )
    if os.name != "nt":
        logging.info(f"Using Wine ({settings['wine']['type']})")
        
        if settings['wine']['dist'] != "":
            logging.info(f"Wine Distribution: {settings['wine']['dist']}")

        if not os.path.isdir(prefix_directory):
            os.makedirs(prefix_directory)
        
        runner = WineRunner(
            prefix = prefix_directory,
            dist=settings["wine"]["dist"],
            launch_type=settings["wine"]["type"],
            environment=settings["cork"]["environment"] | settings["wine"]["environment"],
            launcher=[x for x in settings["cork"]["launcher"].split(" ") if x]
        )

    session = RobloxSession(
        runner,
        versions_directory,
        settings["cork"]["downloadthreads"],
        settings["cork"]["installthreads"]
    )

    match arguments.mode:
        case "player":
            if settings["cork"]["splash"] == True:
                this_splash = splash.CorkSplash()
                this_splash.show("roblox-player")

            remote_fflags = {}
            if settings["roblox"]["player"]["remotefflags"] != "":
                try:
                    if settings["cork"]["splash"] == True:
                        this_splash.set_text("Acquiring Remote FFlags...")
                        this_splash.set_progress_mode(True)
                    
                    fflag_request = request.urlopen(request.Request(
                        settings["roblox"]["player"]["remotefflags"], headers={"User-Agent": "Cork"}))
                    remote_fflags = json.loads(
                        fflag_request.read().decode('utf-8'))
                except:
                    pass
            
            session.fflags = remote_fflags | settings["roblox"]["player"]["fflags"]
            session.runner.environment = session.runner.environment | settings["roblox"]["player"]["environment"]

            session.runner.launcher = [x for x in settings["roblox"]["player"]["prelauncher"].split(" ") if x] + session.runner.launcher + [x for x in settings["roblox"]["player"]["postlauncher"].split(" ") if x]
            
            state_dictionary = {"state": "none"}

            if settings["cork"]["splash"] == True:
                this_splash.set_text("Starting Roblox...")
                this_splash.set_progress_mode(True)
                def splash_function():
                    while this_splash.is_showing:
                        match state_dictionary["state"]:
                            case "none":
                                pass
                            case "getting_version":
                                this_splash.set_progress_mode(True)
                                this_splash.set_text("Getting version...")
                            case "preparing":
                                this_splash.set_progress_mode(True)
                                this_splash.set_text("Preparing...")
                            case "downloading":
                                this_splash.set_text(f"Downloading {state_dictionary['version']}...")
                                if "packages_total" in state_dictionary:
                                    this_splash.set_progress_mode(False)
                                    progress = state_dictionary["packages_downloaded"] / state_dictionary["packages_total"]
                                    this_splash.set_progress(progress)
                                else:
                                    this_splash.set_progress_mode(True)
                            case "installing":
                                this_splash.set_text(f"Installing {state_dictionary['version']}...")
                                if "packages_total" in state_dictionary:
                                    this_splash.set_progress_mode(False)
                                    progress = state_dictionary["packages_installed"] / state_dictionary["packages_total"]
                                    this_splash.set_progress(progress)
                                else:
                                    this_splash.set_progress_mode(True)
                            case "done":
                                this_splash.close()
                        time.sleep(0.1)
                    return

                splash_thread = threading.Thread(target=splash_function)
                splash_thread.start()

            if len(arguments.args) > 0:
                process = session.execute_player(
                    arguments.args, state_dictionary=state_dictionary, channel=settings["roblox"]["channel"], version=settings["roblox"]["player"]["version"])
            else:
                process = session.execute_player(
                    ["--app"], state_dictionary=state_dictionary, channel=settings["roblox"]["channel"], version=settings["roblox"]["player"]["version"])
            
            with process.stdout:
                for line in iter(process.stdout.readline, b''):
                    logging.warning(line.decode("utf-8").strip())
            process.wait()

            if settings["cork"]["splash"] == True:
                splash_thread.join()
        case "studio":
            if settings["cork"]["splash"] == True:
                this_splash = splash.CorkSplash()
                this_splash.show("roblox-studio")

                this_splash.set_text("Starting Roblox Studio...")
            
            session.runner.environment = session.runner.environment | settings["roblox"]["studio"]["environment"]

            session.runner.launcher = [x for x in settings["roblox"]["studio"]["prelauncher"].split(" ") if x] + session.runner.launcher + [x for x in settings["roblox"]["studio"]["postlauncher"].split(" ") if x]

            state_dictionary = {"state": "none"}

            if settings["cork"]["splash"] == True:
                def splash_function():
                    while this_splash.is_showing:
                        match state_dictionary["state"]:
                            case "none":
                                pass
                            case "getting_version":
                                this_splash.set_progress_mode(True)
                                this_splash.set_text("Getting version...")
                            case "preparing":
                                this_splash.set_progress_mode(True)
                                this_splash.set_text("Preparing...")
                            case "downloading":
                                this_splash.set_text(f"Downloading {state_dictionary['version']}...")
                                if "packages_total" in state_dictionary:
                                    this_splash.set_progress_mode(False)
                                    progress = state_dictionary["packages_downloaded"] / state_dictionary["packages_total"]
                                    this_splash.set_progress(progress)
                                else:
                                    this_splash.set_progress_mode(True)
                            case "installing":
                                this_splash.set_text(f"Installing {state_dictionary['version']}...")
                                if "packages_total" in state_dictionary:
                                    this_splash.set_progress_mode(False)
                                    progress = state_dictionary["packages_installed"] / state_dictionary["packages_total"]
                                    this_splash.set_progress(progress)
                                else:
                                    this_splash.set_progress_mode(True)
                            case "done":
                                this_splash.close()
                        time.sleep(0.1)
                    return

                splash_thread = threading.Thread(target=splash_function)
                splash_thread.start()

            if len(arguments.args) > 0:
                process = session.execute_studio(
                    arguments.args, state_dictionary=state_dictionary, channel=settings["roblox"]["channel"], version=settings["roblox"]["studio"]["version"])
            else:
                process = session.execute_studio(
                    ["-ide"], state_dictionary=state_dictionary, channel=settings["roblox"]["channel"], version=settings["roblox"]["studio"]["version"])
            
            with process.stdout:
                for line in iter(process.stdout.readline, b''):
                    logging.warning(line.decode("utf-8").strip())
            process.wait()

            if settings["cork"]["splash"] == True:
                splash_thread.join()
        case "runner":
            process = session.runner.execute(arguments.args, cwd=os.getcwd())
            with process.stdout:
                for line in iter(process.stdout.readline, b''):
                    logging.warning(line.decode("utf-8").strip())
        case "install":
            session.get_player()
            session.get_studio()
        case "cleanup":
            for version in [f for f in os.listdir(versions_directory) if not os.path.isfile(os.path.join(versions_directory, f))]:
                logging.info(f"Removing {version}...")
                shutil.rmtree(os.path.join(versions_directory, version))
        case "kill":
            pass
    
    logging.info("End")


if __name__ == "__main__":
    main()
