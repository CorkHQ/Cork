import time
import logging
from urllib import request

urls = [
    "https://setup.rbxcdn.com/",
	"https://setup-ak.rbxcdn.com/",
	"https://setup-cfly.rbxcdn.com/",
	"https://s3.amazonaws.com/setup.roblox.com/"
]

def get():
    logging.debug("Trying to find fastest mirror")
    working_urls = {}
    for url in urls:
        start_time = time.time()
        try:
            request.urlopen(f"{url}version", timeout=5)
        except:
            logging.warning(f"Failed to access {url}")
        else:
            working_urls[url] = (time.time() - start_time) * 1000
    
    sorted_urls = sorted(working_urls.items(), key=lambda x: (x[1],x[0]))
    if len(sorted_urls) <= 0:
        raise ConnectionError("No mirror was found")
    
    fast_url = sorted_urls[0][0]
    logging.debug(f"Fastest mirror is {fast_url}")
    
    return fast_url