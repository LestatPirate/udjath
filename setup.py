"""py2app build script.

Build with:
    ./scripts/build-app.sh        (versão, .app e zip para a release)
or directly:
    ./venv/bin/python3 setup.py py2app

Produces dist/Udjath.app — a standalone menu bar app (no Dock icon).
"""

import os
from glob import glob

from setuptools import setup

# A versão vem de scripts/build-app.sh.
VERSION = os.environ.get("VERSION", "0.0.0")

APP = ["app.py"]
DATA_FILES = [("icons", glob("icons/*.png"))]
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "icons/Udjath.icns",
    "plist": {
        "LSUIElement": True,
        "CFBundleName": "Udjath",
        "CFBundleDisplayName": "Udjath",
        "CFBundleIdentifier": "io.github.lestatpirate.udjath",
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        "NSHumanReadableCopyright": "© 2026 Alex Felizardo. Licença MIT.",
    },
    "packages": ["rumps"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
