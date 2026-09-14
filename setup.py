"""py2app build script.

Build with:
    ./venv/bin/python3 setup.py py2app

Produces dist/MonitorRes.app — a standalone menu bar app (no Dock icon).
"""

from setuptools import setup

APP = ["app.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "LSUIElement": True,
        "CFBundleName": "MonitorRes",
        "CFBundleDisplayName": "MonitorRes",
        "CFBundleIdentifier": "local.monitorres.switcher",
        "CFBundleShortVersionString": "1.0.0",
        "NSHumanReadableCopyright": "",
    },
    "packages": ["rumps"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
