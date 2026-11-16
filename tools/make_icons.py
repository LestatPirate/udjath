"""Gera os ícones a partir dos SVG em icons/src (só é preciso correr quando os SVG mudam):

    ./venv/bin/python3 tools/make_icons.py

Produz icons/AppIcon-*.png (512 px, escolhidos no menu "Ícone"), icons/menubar-*.png
(barra de menu, "template images") e icons/Udjath.icns (ícone do .app, o Clássico).
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from Cocoa import (
    NSBitmapImageRep,
    NSCompositingOperationSourceOver,
    NSDeviceRGBColorSpace,
    NSGraphicsContext,
    NSImage,
    NSMakeRect,
    NSPNGFileType,
    NSZeroRect,
)

ICONS = Path(__file__).resolve().parent.parent / "icons"
APP_ICON_PX = 512
MENUBAR_PX = 60  # 20 pt @3x
ICNS_SOURCE = "AppIcon-Classico"
ICNS_SIZES = [16, 32, 128, 256, 512]


def render(svg: Path, png: Path, pixels: int) -> None:
    image = NSImage.alloc().initWithContentsOfFile_(str(svg))
    if image is None:
        raise RuntimeError(f"não foi possível ler {svg}")
    rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
        None, pixels, pixels, 8, 4, True, False, NSDeviceRGBColorSpace, 0, 0
    )
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.setCurrentContext_(NSGraphicsContext.graphicsContextWithBitmapImageRep_(rep))
    image.drawInRect_fromRect_operation_fraction_(
        NSMakeRect(0, 0, pixels, pixels), NSZeroRect, NSCompositingOperationSourceOver, 1.0
    )
    NSGraphicsContext.restoreGraphicsState()
    rep.representationUsingType_properties_(NSPNGFileType, {}).writeToFile_atomically_(str(png), True)


def make_icns(svg: Path, icns: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "Udjath.iconset"
        iconset.mkdir()
        for size in ICNS_SIZES:
            render(svg, iconset / f"icon_{size}x{size}.png", size)
            render(svg, iconset / f"icon_{size}x{size}@2x.png", size * 2)
        subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns)], check=True)


def main() -> None:
    for svg in sorted((ICONS / "src").glob("*.svg")):
        pixels = MENUBAR_PX if svg.stem.startswith("menubar-") else APP_ICON_PX
        render(svg, ICONS / f"{svg.stem}.png", pixels)
        print(f"{svg.stem}.png ({pixels} px)")
    make_icns(ICONS / "src" / f"{ICNS_SOURCE}.svg", ICONS / "Udjath.icns")
    print("Udjath.icns")


if __name__ == "__main__":
    main()
