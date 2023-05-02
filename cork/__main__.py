import argparse
import json
import os
import shutil
import threading
import time
from urllib import request
from platformdirs import user_config_dir, user_data_dir, user_cache_dir
from cork import splash
from cork.roblox import RobloxSession
from cork.utils import deep_merge


def main():
    parser = argparse.ArgumentParser(
        prog='Cork',
        description='A Roblox Wine Wrapper')
    parser.add_argument("mode", type=str, choices=[
                        "player", "studio", "wine", "install", "cleanup", "kill"])
    parser.add_argument("args", nargs='*')
    arguments = parser.parse_args()

    if not os.path.isdir(user_config_dir("cork")):
        os.makedirs(user_config_dir("cork"))
    if not os.path.isdir(user_data_dir("cork")):
        os.makedirs(user_data_dir("cork"))
    if not os.path.isdir(user_cache_dir("cork")):
        os.makedirs(user_cache_dir("cork"))

    if not os.path.isdir(os.path.join(user_data_dir("cork"), "pfx")):
        os.makedirs(os.path.join(user_data_dir("cork"), "pfx"))
    if not os.path.isdir(os.path.join(user_cache_dir("cork"), "logs")):
        os.makedirs(os.path.join(user_cache_dir("cork"), "logs"))

    settings = {
        "wine": {
            "dist": "",
            "type": "wine",
            "wine64": False,
            "launcher": "",
            "environment": {
                "WINEDLLOVERRIDES": "winemenubuilder.exe=d"
            }
        },
        "roblox": {
            "channel": "live",
            "player": {
                "launcher": "",
                "version": "",
                "environment": {},
                "remotefflags": "",
                "fflags": {}
            },
            "studio": {
                "launcher": "",
                "version": "",
                "environment": {}
            }
        }
    }

    data_settings = ""
    if os.path.exists(os.path.join(user_config_dir("cork"), "settings.json")):
        with open(os.path.join(user_config_dir("cork"), "settings.json"), "r") as file:
            data_settings = file.read()
            data = json.loads(data_settings)
            settings = deep_merge(data, settings)

    new_data_settings = json.dumps(settings, indent=4)
    if data_settings != new_data_settings:
        with open(os.path.join(user_config_dir("cork"), "settings.json"), "w") as file:
            file.write(json.dumps(settings, indent=4))
    
    session = RobloxSession(
        os.path.join(user_data_dir("cork"), "pfx"),
        dist=settings["wine"]["dist"],
        environment=settings["wine"]["environment"],
        wine64=settings["wine"]["wine64"],
        launcher= [x for x in settings["wine"]["launcher"].split(" ") if x],
        launch_type=settings["wine"]["type"],
        log_directory=os.path.join(user_cache_dir("cork"), "logs"))

    match arguments.mode:
        case "player":
            session.launcher += [x for x in settings["roblox"]["player"]["launcher"].split(" ") if x]

            this_splash = splash.CorkSplash()
            this_splash.show("roblox-player")

            remote_fflags = {}
            if settings["roblox"]["player"]["remotefflags"] != "":
                try:
                    this_splash.set_text("Acquiring Remote FFlags...")
                    this_splash.set_progress_mode(True)
                    fflag_request = request.urlopen(request.Request(
                        settings["roblox"]["player"]["remotefflags"], headers={"User-Agent": "Cork"}))
                    remote_fflags = json.loads(
                        fflag_request.read().decode('utf-8'))
                except:
                    pass
            
            this_splash.set_text("Initializing prefix...")
            this_splash.set_progress_mode(True)
            session.fflags = remote_fflags | settings["roblox"]["player"]["fflags"]
            session.environment = session.environment | settings["roblox"]["player"]["environment"]
            session.initialize_prefix()

            state_dictionary = {"state": "none"}

            def run_thread():
                if len(arguments.args) > 0:
                    session.execute_player(
                        arguments.args, state_dictionary=state_dictionary, channel=settings["roblox"]["channel"], version=settings["roblox"]["player"]["version"])
                else:
                    session.execute_player(
                        ["--app"], state_dictionary=state_dictionary, channel=settings["roblox"]["channel"], version=settings["roblox"]["player"]["version"])
                return

            thread = threading.Thread(target=run_thread)
            thread.start()

            while thread.is_alive() and this_splash.is_showing:
                match state_dictionary["state"]:
                    case "none":
                        pass
                    case "getting_version":
                        this_splash.set_progress_mode(True)
                        this_splash.set_text("Getting version...")
                    case "installing":
                        this_splash.set_text(f"Installing {state_dictionary['version']}...")
                        if "packages_total" in state_dictionary:
                            this_splash.set_progress_mode(False)
                            progress = (state_dictionary["packages_downloaded"] + state_dictionary["packages_installed"]) / (state_dictionary["packages_total"] * 2)
                            this_splash.set_progress(progress)
                        else:
                            this_splash.set_progress_mode(True)
                    case "done":
                        this_splash.close()
                time.sleep(0.1)
                
            thread.join()
        case "studio":
            session.launcher += [x for x in settings["roblox"]["studio"]["launcher"].split(" ") if x]

            this_splash = splash.CorkSplash()
            this_splash.show("roblox-studio")

            this_splash.set_text("Starting Roblox Studio...")
            session.environment = session.environment | settings["roblox"]["studio"]["environment"]
            session.initialize_prefix()

            state_dictionary = {"state": "none"}

            def run_thread():
                if len(arguments.args) > 0:
                    session.execute_studio(
                        arguments.args, state_dictionary=state_dictionary, channel=settings["roblox"]["channel"], version=settings["roblox"]["studio"]["version"])
                else:
                    session.execute_studio(
                        ["-ide"], state_dictionary=state_dictionary, channel=settings["roblox"]["channel"], version=settings["roblox"]["studio"]["version"])

            thread = threading.Thread(target=run_thread)
            thread.start()

            while thread.is_alive() and this_splash.is_showing:
                match state_dictionary["state"]:
                    case "none":
                        pass
                    case "getting_version":
                        this_splash.set_progress_mode(True)
                        this_splash.set_text("Getting version...")
                    case "installing":
                        this_splash.set_text(f"Installing {state_dictionary['version']}...")
                        if "packages_total" in state_dictionary:
                            this_splash.set_progress_mode(False)
                            progress = (state_dictionary["packages_downloaded"] + state_dictionary["packages_installed"]) / (state_dictionary["packages_total"] * 2)
                            this_splash.set_progress(progress)
                        else:
                            this_splash.set_progress_mode(True)
                    case "done":
                        this_splash.close()
                time.sleep(0.1)
                
            thread.join()
        case "wine":
            session.initialize_prefix()
            session.execute(arguments.args)
        case "install":
            session.initialize_prefix()

            session.get_player()
            session.get_studio()
        case "cleanup":
            session.initialize_prefix()

            versions_directory = os.path.join(
                session.get_drive(), "Roblox", "Versions")

            for version in [f for f in os.listdir(versions_directory) if not os.path.isfile(os.path.join(versions_directory, f))]:
                print(f"Removing {version}...")
                shutil.rmtree(os.path.join(versions_directory, version))
        case "kill":
            session.shutdown_prefix()


if __name__ == "__main__":
    main()
