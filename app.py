"""Menu bar app: switch monitor resolution (internal or external),
with a countdown confirmation that auto-reverts on timeout, like macOS's
own display-change dialog.
"""

from __future__ import annotations

import rumps

import display_manager as dm
from confirm_dialog import confirm_resolution
from known_resolutions import KNOWN_RESOLUTIONS


class ResolutionSwitcherApp(rumps.App):

    def __init__(self):
        super().__init__("⧉", quit_button="Sair")
        self.menu.clear()
        self.rebuild_menu()

    def rebuild_menu(self):
        self.menu.clear()
        try:
            displays = dm.list_displays()
        except Exception as exc:
            self.menu.add(rumps.MenuItem(f"Erro ao listar ecrãs: {exc}"))
            self.menu.add(None)
            self.menu.add(rumps.MenuItem("Sair", callback=rumps.quit_application))
            return

        for display in displays:
            try:
                current = dm.get_current_mode(display.display_id)
            except Exception:
                current = None

            title = display.name
            if current is not None:
                title += f" — atual: {current.label}"
            header = rumps.MenuItem(title)
            header.set_callback(None)
            self.menu.add(header)

            available = {(m.width, m.height) for m in dm.list_modes(display.display_id)}
            for width, height in KNOWN_RESOLUTIONS:
                label = f"    {width} x {height}"
                if (width, height) not in available:
                    label += "  (não disponível)"
                item = rumps.MenuItem(
                    label,
                    callback=self._make_switch_handler(display.display_id, width, height),
                )
                if (width, height) not in available:
                    item.set_callback(None)
                if current is not None and (width, height) == (current.width, current.height):
                    item.state = 1
                self.menu.add(item)
            self.menu.add(None)

        self.menu.add(rumps.MenuItem("Atualizar lista de ecrãs", callback=lambda _: self.rebuild_menu()))
        self.menu.add(None)
        self.menu.add(rumps.MenuItem("Sair", callback=rumps.quit_application))

    def _make_switch_handler(self, display_id: int, width: int, height: int):
        def handler(_sender):
            self.switch_resolution(display_id, width, height)

        return handler

    def switch_resolution(self, display_id: int, width: int, height: int):
        previous_mode = dm.get_current_mode(display_id)
        target_mode = dm.find_mode(display_id, width, height)
        if target_mode is None:
            rumps.alert(
                title="Resolução indisponível",
                message=f"{width} x {height} não está disponível para este ecrã.",
            )
            return

        try:
            dm.set_mode(target_mode)
        except Exception as exc:
            rumps.alert(title="Falha ao aplicar resolução", message=str(exc))
            return

        kept = confirm_resolution(width, height)

        if kept:
            self._notify("Resolução confirmada", f"{width} x {height}", "A nova resolução foi mantida.")
        else:
            try:
                dm.set_mode(dm.find_mode(display_id, previous_mode.width, previous_mode.height) or previous_mode)
            except Exception as exc:
                rumps.alert(title="Falha ao reverter", message=str(exc))
            else:
                self._notify("Resolução revertida", previous_mode.label, "Voltou à resolução anterior.")

        self.rebuild_menu()

    @staticmethod
    def _notify(title: str, subtitle: str, message: str):
        try:
            rumps.notification(title=title, subtitle=subtitle, message=message)
        except Exception:
            pass  # notifications need a proper app bundle; harmless when running unpackaged


if __name__ == "__main__":
    ResolutionSwitcherApp().run()
