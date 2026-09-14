"""CoreGraphics display enumeration and resolution switching.

Uses the semi-private "kCGDisplayShowLowResolutionModes" option key for
CGDisplayCopyAllDisplayModes to surface scaled/HiDPI resolutions that
macOS hides from System Settings by default (the same technique used by
tools like SwitchResX). This is a public API called with an extra option
key, not a linked private symbol.
"""

from __future__ import annotations

from dataclasses import dataclass

import Quartz

_SHOW_HIDPI_OPTS = {"kCGDisplayShowLowResolutionModes": True}


@dataclass(frozen=True)
class DisplayInfo:
    display_id: int
    is_main: bool
    is_builtin: bool

    @property
    def name(self) -> str:
        if self.is_builtin:
            return "Ecrã interno"
        return f"Ecrã externo ({self.display_id})"


@dataclass(frozen=True)
class ResolutionMode:
    display_id: int
    width: int
    height: int
    pixel_width: int
    pixel_height: int
    refresh_rate: float
    mode_ref: object  # CGDisplayModeRef, kept alive for CGConfigureDisplayWithDisplayMode

    @property
    def label(self) -> str:
        tag = " (HiDPI)" if self.pixel_width > self.width else ""
        return f"{self.width} x {self.height}{tag}"


def list_displays() -> list[DisplayInfo]:
    err, display_ids, _count = Quartz.CGGetActiveDisplayList(16, None, None)
    if err:
        raise RuntimeError(f"CGGetActiveDisplayList falhou: {err}")
    main_id = Quartz.CGMainDisplayID()
    return [
        DisplayInfo(
            display_id=did,
            is_main=(did == main_id),
            is_builtin=bool(Quartz.CGDisplayIsBuiltin(did)),
        )
        for did in display_ids
    ]


def get_current_mode(display_id: int) -> ResolutionMode:
    mode = Quartz.CGDisplayCopyDisplayMode(display_id)
    return _to_resolution_mode(display_id, mode)


def list_modes(display_id: int) -> list[ResolutionMode]:
    """All usable modes for a display, including hidden HiDPI/scaled ones,
    deduplicated by (point width, point height) keeping the sharpest/
    highest-refresh variant of each.
    """
    raw_modes = Quartz.CGDisplayCopyAllDisplayModes(display_id, _SHOW_HIDPI_OPTS) or []
    best_by_size: dict[tuple[int, int], ResolutionMode] = {}
    for mode in raw_modes:
        if not Quartz.CGDisplayModeIsUsableForDesktopGUI(mode):
            continue
        candidate = _to_resolution_mode(display_id, mode)
        key = (candidate.width, candidate.height)
        current = best_by_size.get(key)
        if current is None or (candidate.pixel_width, candidate.refresh_rate) > (
            current.pixel_width,
            current.refresh_rate,
        ):
            best_by_size[key] = candidate
    return sorted(best_by_size.values(), key=lambda m: (m.width, m.height))


def find_mode(display_id: int, width: int, height: int) -> ResolutionMode | None:
    for mode in list_modes(display_id):
        if mode.width == width and mode.height == height:
            return mode
    return None


def set_mode(mode: ResolutionMode) -> None:
    err, config = Quartz.CGBeginDisplayConfiguration(None)
    if err:
        raise RuntimeError(f"CGBeginDisplayConfiguration falhou: {err}")
    err = Quartz.CGConfigureDisplayWithDisplayMode(config, mode.display_id, mode.mode_ref, None)
    if err:
        Quartz.CGCancelDisplayConfiguration(config)
        raise RuntimeError(f"CGConfigureDisplayWithDisplayMode falhou: {err}")
    err = Quartz.CGCompleteDisplayConfiguration(config, Quartz.kCGConfigurePermanently)
    if err:
        raise RuntimeError(f"CGCompleteDisplayConfiguration falhou: {err}")


def _to_resolution_mode(display_id: int, mode) -> ResolutionMode:
    return ResolutionMode(
        display_id=display_id,
        width=Quartz.CGDisplayModeGetWidth(mode),
        height=Quartz.CGDisplayModeGetHeight(mode),
        pixel_width=Quartz.CGDisplayModeGetPixelWidth(mode),
        pixel_height=Quartz.CGDisplayModeGetPixelHeight(mode),
        refresh_rate=Quartz.CGDisplayModeGetRefreshRate(mode),
        mode_ref=mode,
    )
