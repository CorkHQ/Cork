import argparse
import json
import os
import shutil
from urllib import request
from platformdirs import user_config_dir, user_data_dir
from cork.roblox import RobloxSession
from cork.utils import deep_merge


def main():
    parser = argparse.ArgumentParser(
        prog='Cork',
        description='A Roblox Wine Wrapper')
    parser.add_argument("mode", type=str, choices=[
                        "player", "studio", "wine", "install", "cleanup"])
    parser.add_argument("args", nargs='*')
    arguments = parser.parse_args()

    if not os.path.isdir(user_config_dir("cork")):
        os.makedirs(user_config_dir("cork"))
    if not os.path.isdir(user_data_dir("cork")):
        os.makedirs(user_data_dir("cork"))
    if not os.path.isdir(os.path.join(user_data_dir("cork"), "pfx")):
        os.makedirs(os.path.join(user_data_dir("cork"), "pfx"))

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
                "version": "",
                "environment": {},
                "remotefflags": "",
                "fflags": {}
            },
            "studio": {
                "version": "",
                "environment": {}
            }
        }
    }

    if os.path.exists(os.path.join(user_config_dir("cork"), "settings.json")):
        with open(os.path.join(user_config_dir("cork"), "settings.json"), "r") as file:
            data = json.loads(file.read())
            settings = deep_merge(data, settings)

    with open(os.path.join(user_config_dir("cork"), "settings.json"), "w") as file:
        file.write(json.dumps(settings, indent=4))

    session = RobloxSession(
        os.path.join(user_data_dir("cork"), "pfx"),
        dist=settings["wine"]["dist"],
        environment=settings["wine"]["environment"],
        wine64=settings["wine"]["wine64"],
        launch_type=settings["wine"]["type"])

    match arguments.mode:
        case "player":
            remote_fflags = {}
            if settings["roblox"]["player"]["remotefflags"] != "":
                try:
                    fflag_request = request.urlopen(request.Request(
                        settings["roblox"]["player"]["remotefflags"], headers={"User-Agent": "Cork"}))
                    remote_fflags = json.loads(
                        fflag_request.read().decode('utf-8'))
                except:
                    pass

            session.fflags = remote_fflags | settings["roblox"]["player"]["fflags"]
            session.environment = session.environment | settings["roblox"]["player"]["environment"]
            session.initialize_prefix()

            if len(arguments.args) > 0:
                session.execute_player(
                    arguments.args, launcher=settings["wine"]["launcher"], channel=settings["roblox"]["channel"], version=settings["roblox"]["player"]["version"])
            else:
                session.execute_player(
                    ["--app"], launcher=settings["wine"]["launcher"], channel=settings["roblox"]["channel"], version=settings["roblox"]["player"]["version"])

            session.shutdown_prefix()
        case "studio":
            session.environment = session.environment | settings["roblox"]["studio"]["environment"]
            session.initialize_prefix()

            if len(arguments.args) > 0:
                session.execute_studio(
                    arguments.args, launcher=settings["wine"]["launcher"], channel=settings["roblox"]["channel"], version=settings["roblox"]["studio"]["version"])
            else:
                session.execute_studio(
                    ["-ide"], launcher=settings["wine"]["launcher"], channel=settings["roblox"]["channel"], version=settings["roblox"]["studio"]["version"])

            session.wait_prefix()
        case "wine":
            session.initialize_prefix()
            session.execute(arguments.args, launcher=settings["wine"]["launcher"])
            session.shutdown_prefix()
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


if __name__ == "__main__":
    main()
