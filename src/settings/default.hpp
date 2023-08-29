#include <iostream>

static const std::string defaultSettings =
    "[cork]\n"
    "loglevel = \"info\"\n"
    "launcher = \"\"\n"
    "[cork.env]\n"
    "\n"
    "\n"
#if defined(WINE_RUNNER)
    "[wine]\n"
    "dist = \"\"\n"
    "type = \"wine\"\n"
    "\n"
    "[wine.env]\n"
    "\"WINEDLLOVERRIDES\" = \"winemenubuilder.exe=d\"\n"
    "\n"
#endif
    "[player]\n"
    "channel = \"\"\n"
    "version = \"\"\n"
    "[player.launcher]\n"
    "pre = \"\"\n"
    "post = \"\"\n"
    "[player.fflags]\n"
    "\n"
    "[player.env]\n"
    "\n"
    "\n"
    "[studio]\n"
    "channel = \"\"\n"
    "version = \"\"\n"
    "[studio.launcher]\n"
    "pre = \"\"\n"
    "post = \"\"\n"
    "[studio.env]\n"
    "\n";