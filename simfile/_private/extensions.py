from typing import Optional


SIMFILE = (".ssc", ".sm")

IMAGE = (".png", ".jpg", ".jpeg", ".gif", ".bmp")
"""
Incidentally in descending order of preference
(SimfilePack.banner relies on this).
"""

AUDIO = (".mp3", ".oga", ".ogg", ".wav")


def match(path: str, *extensions: str) -> Optional[str]:
    assert extensions

    lower_path = path.lower()
    for extension in extensions:
        if lower_path.endswith(extension):
            return extension

    return None
