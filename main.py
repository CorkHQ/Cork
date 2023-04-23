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

    remote_fflags = {}
    if settings["RemoteFFlags"] != "":
        try:
            fflag_request = requests.get(settings["RemoteFFlags"])
            remote_fflags = fflag_request.json()
        except:
            pass

    session = RobloxSession(
        os.path.join(user_data_dir("cork"), "prefix"),
        wine_home=settings["WineHome"],
        environment=settings["Environment"],
        fflags=remote_fflags | settings["FFlags"])

    match arguments.mode:
        case "player":
            session.initialize_prefix()

            if len(arguments.args) > 0:
                session.execute_player(
                    arguments.args, launcher=settings["Launcher"])
            else:
                session.execute_player(["-app"], launcher=settings["Launcher"])

            session.wait_prefix()
        case "studio":
            raise Exception("Studio support not implemented!")
        case "wine":
            session.initialize_prefix()
            session.execute(arguments.args)
            session.wait_prefix()
