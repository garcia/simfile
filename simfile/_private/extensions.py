from typing import Optional


SIMFILE = ('.sm', '.ssc')

IMAGE = ('.bmp', '.gif', '.jpeg', '.jpg', '.png')
"""
Image formats. Incidentally in *ascending* order of preference
(SimfilePack.banner relies on this).
"""

AUDIO = ('.mp3', '.oga', '.ogg', '.wav')


def match(path: str, *extensions: str) -> Optional[str]:
    assert extensions

    lower_path = path.lower()
    for extension in extensions:
        if lower_path.endswith(extension):
            return extension
    
    return None
