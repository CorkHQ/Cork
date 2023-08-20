from urllib import request

package_dictionaries = {
    "WindowsPlayer": {
        "RobloxApp.zip":                 "",
        "WebView2.zip":                  "",

        "shaders.zip":                   "shaders",
        "ssl.zip":                       "ssl",

        "content-avatar.zip":            "content/avatar",
        "content-configs.zip":           "content/configs",
        "content-fonts.zip":             "content/fonts",
        "content-sky.zip":               "content/sky",
        "content-sounds.zip":            "content/sounds",
        "content-textures2.zip":         "content/textures",
        "content-models.zip":            "content/models",

        "content-textures3.zip":         "PlatformContent/pc/textures",
        "content-terrain.zip":           "PlatformContent/pc/terrain",
        "content-platform-fonts.zip":    "PlatformContent/pc/fonts",

        "extracontent-luapackages.zip":  "ExtraContent/LuaPackages",
        "extracontent-translations.zip": "ExtraContent/translations",
        "extracontent-models.zip":       "ExtraContent/models",
        "extracontent-textures.zip":     "ExtraContent/textures",
        "extracontent-places.zip":       "ExtraContent/places"
    },

    "WindowsStudio64": {
        "ApplicationConfig.zip":           "ApplicationConfig",
        "BuiltInPlugins.zip":              "BuiltInPlugins",
        "BuiltInStandalonePlugins.zip":    "BuiltInStandalonePlugins",
        "Plugins.zip":                     "Plugins",
        "Qml.zip":                         "Qml",
        "StudioFonts.zip":                 "StudioFonts",
        "WebView2.zip":                    "",
        "RobloxStudio.zip":                "",
        "Libraries.zip":                   "",
        "LibrariesQt5.zip":                "",
        "content-avatar.zip":              "content/avatar",
        "content-configs.zip":             "content/configs",
        "content-fonts.zip":               "content/fonts",
        "content-models.zip":              "content/models",
        "content-qt_translations.zip":     "content/qt_translations",
        "content-sky.zip":                 "content/sky",
        "content-sounds.zip":              "content/sounds",
        "shaders.zip":                     "shaders",
        "ssl.zip":                         "ssl",
        "content-textures2.zip":           "content/textures",
        "content-textures3.zip":           "PlatformContent/pc/textures",
        "content-studio_svg_textures.zip": "content/studio_svg_textures",
        "content-terrain.zip":             "PlatformContent/pc/terrain",
        "content-platform-fonts.zip":      "PlatformContent/pc/fonts",
        "content-api-docs.zip":            "content/api_docs",
        "extracontent-scripts.zip":        "ExtraContent/scripts",
        "extracontent-luapackages.zip":    "ExtraContent/LuaPackages",
        "extracontent-translations.zip":   "ExtraContent/translations",
        "extracontent-models.zip":         "ExtraContent/models",
        "extracontent-textures.zip":       "ExtraContent/textures",
        "redist.zip":                      ""
    }
}

def get(version_type, version, channel, cdn):
    if channel != "":
        cdn = f"{cdn}channel/{channel}/"

    package_manifest_text = request.urlopen(request.Request(f"{cdn}{version}-rbxPkgManifest.txt", headers={
                                            "User-Agent": "Cork"})).read().decode("utf-8").split("\n", 1)[1].splitlines()
    package_manifest = {}
    line_count = 1
    last_header = ""

    for line in package_manifest_text:
        if line_count == 5:
            line_count = 1

        if line_count == 1:
            last_header = line
            package_manifest[last_header] = []
        else:
            package_manifest[last_header].append(line)
        line_count += 1
    
    corrected_packages = {}
    for package, target in package_dictionaries[version_type].items():
        corrected_packages[(package, f"{cdn}{version}-{package}")] = target
    
    return corrected_packages, package_manifest
