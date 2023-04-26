# Cork
Yet another Wine wrapper for Roblox

## Features
* Custom Roblox Launcher
* Transparent
* Can be used via a terminal
* Multi-Threaded installation of Roblox
* Highly customizable:
    * Custom Wine versions are fully supported
    * Proton support
    * Roblox version channels can be customized
    * FFlags can be changed in the settings file
    * FFlags can be merged from an external remote source such as [RCO](https://github.com/L8X/Roblox-Client-Optimizer)
    * Third-party software integrations, such as DXVK, are not handled by the wrapper by design

## Installation
### *To use Cork, one must have a fully functional install of Wine 7.0+, Python 3.10+ and the appropriate graphics drivers!*

Begin the installation by cloning this repository and entering it's folder:
```sh
git clone https://github.com/Bugadinho/Cork.git
cd Cork
```

After that, use `pip` to install the repository to your user:
```sh
pip install --user .
```

Cork should be installed and you can go to Roblox's website or open the app!

If you want to make sure it's functional, install the Player and Studio with the following command:
```sh
cork install
```
To alter any settings, edit the `~/.config/cork/settings.json` file, and the prefix is located in the `~/.local/share/cork/pfx` folder. Have fun tinkering!

## Acknowledgements
Heavily inspired by:
* [Grapejuice](https://gitlab.com/brinkervii/grapejuice)
* [Vinegar](https://github.com/vinegarhq/vinegar)
* [Bloxstrap](https://github.com/pizzaboxer/bloxstrap)

## License
- [zlib License](https://choosealicense.com/licenses/zlib/)