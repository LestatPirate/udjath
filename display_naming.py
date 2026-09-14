"""Persistent, system-wide renaming of a display.

macOS derives the human-readable name shown in System Settings > Displays
from the monitor's EDID, then consults an override database at
    /Library/Displays/Contents/Resources/Overrides/DisplayVendorID-<id>/DisplayProductID-<id>
for a replacement — the same mechanism used by SwitchResX and the various
"rename my external monitor" guides. That path is outside the app's normal
write access, so the actual write happens through
`osascript ... do shell script ... with administrator privileges`, which
shows macOS's own authentication dialog. This module never sees or stores
the user's password — only the OS does.

The new name only takes effect after the display reconnects (unplug/replug,
or log out and back in) — macOS reads this database when a display connects,
not continuously.
"""

from __future__ import annotations

import plistlib
import shlex
import subprocess
import tempfile
from pathlib import Path

import Quartz

OVERRIDES_ROOT = Path("/Library/Displays/Contents/Resources/Overrides")


def get_vendor_product_ids(display_id: int) -> tuple[int, int]:
    return Quartz.CGDisplayVendorNumber(display_id), Quartz.CGDisplayModelNumber(display_id)


def override_file_for(vendor_id: int, product_id: int) -> Path:
    return OVERRIDES_ROOT / f"DisplayVendorID-{vendor_id:x}" / f"DisplayProductID-{product_id:x}"


def build_override_plist(target_file: Path, new_name: str) -> bytes:
    """Merges DisplayProductName into any existing override plist for this
    display (preserving other keys another tool may have set), rather than
    clobbering it.
    """
    data: dict = {}
    if target_file.exists():
        try:
            data = plistlib.loads(target_file.read_bytes())
        except Exception:
            data = {}
    data["DisplayProductName"] = new_name
    return plistlib.dumps(data)


def rename_display_permanently(display_id: int, new_name: str) -> None:
    """Prompts for admin authorization (native macOS dialog) and installs
    the override. Raises RuntimeError if the user cancels or it fails.
    """
    vendor_id, product_id = get_vendor_product_ids(display_id)
    target_file = override_file_for(vendor_id, product_id)
    plist_bytes = build_override_plist(target_file, new_name)

    with tempfile.NamedTemporaryFile(suffix=".plist", delete=False) as tmp:
        tmp.write(plist_bytes)
        tmp_path = tmp.name

    shell_cmd = (
        f"mkdir -p {shlex.quote(str(target_file.parent))} && "
        f"cp {shlex.quote(tmp_path)} {shlex.quote(str(target_file))} && "
        f"chmod 644 {shlex.quote(str(target_file))} && "
        f"rm -f {shlex.quote(tmp_path)}"
    )
    # AppleScript string: escape backslashes and double quotes for its own quoting layer.
    escaped = shell_cmd.replace("\\", "\\\\").replace('"', '\\"')
    apple_script = f'do shell script "{escaped}" with administrator privileges'

    result = subprocess.run(
        ["osascript", "-e", apple_script],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        Path(tmp_path).unlink(missing_ok=True)
        raise RuntimeError(result.stderr.strip() or "Autorização de administrador cancelada ou falhou.")
