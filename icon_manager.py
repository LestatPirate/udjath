"""Ícones à escolha: o ícone da app (Finder, diálogos, notificações) e o da
barra de menu. A escolha fica nas preferências (NSUserDefaults).

O ícone da app é aplicado de duas maneiras, como no Toth: à app a correr
(`NSApp.applicationIconImage`) e ao pacote `.app` no disco, como ícone
personalizado do Finder (`NSWorkspace.setIcon`). Este último fica ao lado
do conteúdo do pacote (ficheiro `Icon\\r`), e um build novo leva-o:
`apply_app_icon()` repõe-no no arranque seguinte.
"""

from __future__ import annotations

import os

from Cocoa import NSApplication, NSBundle, NSImage, NSUserDefaults, NSWorkspace

# (id, título no menu); o primeiro é o original (o .icns do pacote).
APP_ICONS: list[tuple[str, str]] = [
    ("Classico", "Clássico"),
    ("Ultrawide", "Ultrawide"),
    ("Turquesa", "Turquesa"),
]
MENUBAR_ICONS: list[tuple[str, str]] = [
    ("olho", "Olho de Hórus"),
    ("ecra", "Olho com ecrã"),
]

_APP_ICON_KEY = "appIcon"
_MENUBAR_ICON_KEY = "menubarIcon"


def _icons_dir() -> str:
    # py2app põe os recursos em Contents/Resources (RESOURCEPATH); em desenvolvimento, ao lado do código.
    base = os.environ.get("RESOURCEPATH") or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "icons")


def _chosen(key: str, options: list[tuple[str, str]]) -> str:
    value = NSUserDefaults.standardUserDefaults().stringForKey_(key)
    return value if value in {option_id for option_id, _ in options} else options[0][0]


def current_app_icon() -> str:
    return _chosen(_APP_ICON_KEY, APP_ICONS)


def current_menubar_icon() -> str:
    return _chosen(_MENUBAR_ICON_KEY, MENUBAR_ICONS)


def menubar_icon_path(icon_id: str | None = None) -> str:
    return os.path.join(_icons_dir(), f"menubar-{icon_id or current_menubar_icon()}.png")


def select_menubar_icon(icon_id: str) -> None:
    NSUserDefaults.standardUserDefaults().setObject_forKey_(icon_id, _MENUBAR_ICON_KEY)


def _app_icon_image(icon_id: str):
    return NSImage.alloc().initWithContentsOfFile_(os.path.join(_icons_dir(), f"AppIcon-{icon_id}.png"))


def _bundle_path() -> str | None:
    """O pacote `.app` de onde a app corre (None em desenvolvimento)."""
    path = str(NSBundle.mainBundle().bundlePath())
    return path if path.endswith(".app") else None


def _apply_to_bundle(image) -> None:
    """Põe (ou tira, com None) o ícone personalizado do pacote. Falha em
    silêncio se o pacote não for gravável: fica só o ícone da app a correr.
    """
    path = _bundle_path()
    if path is None:
        return
    workspace = NSWorkspace.sharedWorkspace()
    if workspace.setIcon_forFile_options_(image, path, 0):
        workspace.noteFileSystemChanged_(path)


def apply_app_icon() -> None:
    """No arranque: põe o ícone escolhido na app a correr e, só se for
    preciso, no pacote (falta depois de um build novo, ou sobra).
    """
    icon_id = current_app_icon()
    image = _app_icon_image(icon_id)
    if image is None:
        return
    NSApplication.sharedApplication().setApplicationIconImage_(image)
    path = _bundle_path()
    if path is None:
        return
    wants_custom = icon_id != APP_ICONS[0][0]
    if wants_custom != os.path.exists(os.path.join(path, "Icon\r")):
        _apply_to_bundle(image if wants_custom else None)


def select_app_icon(icon_id: str) -> None:
    image = _app_icon_image(icon_id)
    if image is None:
        return
    NSUserDefaults.standardUserDefaults().setObject_forKey_(icon_id, _APP_ICON_KEY)
    NSApplication.sharedApplication().setApplicationIconImage_(image)
    _apply_to_bundle(None if icon_id == APP_ICONS[0][0] else image)
