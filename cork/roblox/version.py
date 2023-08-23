import json
from urllib import request

def get(binary_type, channel):
    request_url = f"https://clientsettingscdn.roblox.com/v2/client-version/{binary_type}"

    if channel != "":
        request_url = f"{request_url}/channel/{channel}"

    version_response = request.urlopen(request.Request(
        request_url, headers={"User-Agent": "Cork"}))
    
    return json.loads(version_response.read().decode('utf-8'))