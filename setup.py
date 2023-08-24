import setuptools
import os

def read_file(path):
    with open(path, "r") as fp:
        return fp.read()

def install_requires():
    requirements = read_file(os.path.join(os.path.abspath(os.path.dirname(__file__)), "requirements.txt")).split("\n")
    requirements = list(filter(lambda s: not not s, map(lambda s: s.strip(), requirements)))

    return requirements

long_description = read_file("README.md")

setuptools.setup(
    name="cork-launcher",
    version="1.0.2",
    author="Bugadinho",
    description="A bootstrapper for Roblox and Roblox Studio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bugadinho/Cork",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: zlib/libpng License",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": ["cork=cork.__main__:main"]
    },
    data_files = [
        ('share/applications', ['resources/roblox-player.desktop']),
        ('share/applications', ['resources/roblox-studio.desktop']),
        ('share/icons/hicolor/scalable/apps', ['resources/cork.svg']),
        ('share/icons/hicolor/scalable/apps', ['resources/roblox-player.svg']),
        ('share/icons/hicolor/scalable/apps', ['resources/roblox-studio.svg'])
    ],
    install_requires=install_requires(),
    python_requires='>=3.10',
)