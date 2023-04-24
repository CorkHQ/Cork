import argparse
import requests
import json
import os
from platformdirs import user_config_dir, user_data_dir
from roblox import RobloxSession

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Cork',
        description='A Roblox Wine Wrapper')
    parser.add_argument("mode", type=str, choices=["player", "studio", "wine"])
    parser.add_argument("args", nargs='*')
    arguments = parser.parse_args()

    if not os.path.isdir(user_config_dir("cork")):
        os.makedirs(user_config_dir("cork"))
    if not os.path.isdir(user_data_dir("cork")):
        os.makedirs(user_data_dir("cork"))

    settings = {
        "WineHome": "",
        "Wine64": False,
        "Channel": "live",
        "Launcher": "",
        "RemoteFFlags": "",
        "FFlags": {},
        "Environment": {
            "WINEDLLOVERRIDES": "winemenubuilder.exe=d"
        },
    }

    if os.path.exists(os.path.join(user_config_dir("cork"), "settings.json")):
        with open(os.path.join(user_config_dir("cork"), "settings.json"), "r") as file:
            data = json.loads(file.read())
            settings = settings | data

    with open(os.path.join(user_config_dir("cork"), "settings.json"), "w") as file:
        file.write(json.dumps(settings, indent=4))

    session = RobloxSession(
        os.path.join(user_data_dir("cork"), "prefix"),
        wine_home=settings["WineHome"],
        environment=settings["Environment"],
        wine64=settings["Wine64"])

    match arguments.mode:
        case "player":
            remote_fflags = {}
            if settings["RemoteFFlags"] != "":
                try:
                    fflag_request = requests.get(settings["RemoteFFlags"])
                    remote_fflags = fflag_request.json()
                except:
                    pass

            session.fflags = remote_fflags | settings["FFlags"]
            session.initialize_prefix()

            if len(arguments.args) > 0:
                session.execute_player(
                    arguments.args, launcher=settings["Launcher"], channel=settings["Channel"])
            else:
                session.execute_player(
                    ["--app"], launcher=settings["Launcher"], channel=settings["Channel"])

            session.wait_prefix()
        case "studio":
            session.initialize_prefix()

            if len(arguments.args) > 0:
                session.execute_studio(
                    arguments.args, launcher=settings["Launcher"], channel=settings["Channel"])
            else:
                session.execute_studio(
                    ["-ide"], launcher=settings["Launcher"], channel=settings["Channel"])

            session.wait_prefix()
        case "wine":
            session.initialize_prefix()
            session.execute(arguments.args)
            session.wait_prefix()
