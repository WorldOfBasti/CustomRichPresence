from setuptools import setup

# Setup:
# python3 setup_mac.py py2app

APP = ["CustomRichPresence.py"]
DATA_FILES = [("", ["files"])]
OPTIONS = {
    "iconfile": "files/icon_mac.icns",
    "argv_emulation": False
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"]
)
