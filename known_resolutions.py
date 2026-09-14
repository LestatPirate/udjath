"""Curated list of commonly used resolutions, offered in the menu even
when a display doesn't currently expose them as a "hidden" HiDPI mode.
"""

KNOWN_RESOLUTIONS: list[tuple[int, int]] = [
    (1024, 768),
    (1280, 800),
    (1280, 1024),
    (1366, 768),
    (1440, 900),
    (1600, 900),
    (1680, 1050),
    (1920, 1080),
    (1920, 1200),
    (2560, 1080),   # Ultrawide FHD
    (2560, 1440),   # QHD
    (2560, 1600),
    (2880, 1800),
    (3440, 1440),   # Ultrawide QHD — o pedido específico
    (3840, 1600),   # Ultrawide 4K
    (3840, 2160),   # 4K UHD
    (5120, 1440),   # Super ultrawide
    (5120, 2880),   # 5K
]
