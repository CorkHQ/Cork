#include <iostream>

static const std::string defaultSettings =
#if defined(WINE_RUNNER)
    "[wine]\n"
    "dist = \"\"\n"
    "type = \"wine\"\n"
#endif
    "[roblox]\n"
    "channel = \"\"\n";