import io
import os
from typing import BinaryIO, Collection, Dict, Optional, cast
import stat

from fs.base import FS
from fs.error_tools import convert_os_errors
from fs.info import Info
from fs.mode import Mode
from fs.osfs import OSFS

class NativeOSFS(FS):
    """
    OS filesystem implementation that sticks to native system paths.

    This implementation differs from :class:`fs.osfs.OSFS` in that the
    constructor takes no `root_path` (and thus performs no sandboxing), and
    all methods take & return *system paths* - on Windows, that means
    backslash separators and drive letters are preserved.
    
    Errata:
    
    * No fsdecode / fsencode around system paths because I'm not sure if
      that would break `os` compatibility. My gut tells me it would.
    * Only read operations are implemented as that's all I personally need.
    """
    def __init__(self):
        super().__init__()
    
    def _gettarget(self, sys_path: str) -> Optional[str]:
        if hasattr(os, "readlink"):
            try:
                return os.readlink(sys_path)
            except OSError:
                pass
        return None

    def _make_link_info(self, sys_path: str) -> Dict[str, object]:
        _target = self._gettarget(sys_path)
        return {"target": _target}

    def getinfo(
        self,
        sys_path: str,
        namespaces: Optional[Collection[str]] = None,
    ) -> Info:
        self.check()
        namespaces = namespaces or ()
        _lstat = None
        with convert_os_errors("getinfo", sys_path):
            _stat = os.stat(sys_path)
            if "lstat" in namespaces:
                _lstat = os.lstat(sys_path)

        info = {
            "basic": {"name": os.path.basename(sys_path), "is_dir": stat.S_ISDIR(_stat.st_mode)}
        }
        if "details" in namespaces:
            info["details"] = OSFS._make_details_from_stat(_stat)
        if "stat" in namespaces:
            info["stat"] = {
                k: getattr(_stat, k) for k in dir(_stat) if k.startswith("st_")
            }
        if "lstat" in namespaces:
            info["lstat"] = {
                k: getattr(_lstat, k) for k in dir(_lstat) if k.startswith("st_")
            }
        if "link" in namespaces:
            info["link"] = self._make_link_info(sys_path)
        if "access" in namespaces:
            info["access"] = OSFS._make_access_from_stat(_stat)

        return Info(info)

    def listdir(self, sys_path):
        return os.listdir(sys_path)

    def makedir(self, sys_path, permissions=None, recreate=False):
        raise NotImplementedError()
    
    def open(
        self,
        *args,
        **kwargs,
    ):
        return io.open(*args, **kwargs)

    def openbin( # type: ignore
        self,
        sys_path: str,
        mode: str = 'r',
        buffering: int = -1,
        **options
    ) -> BinaryIO:
        _mode = Mode(mode)
        _mode.validate_bin()
        self.check()
        with convert_os_errors("openbin", sys_path):
            binary_file = io.open(
                sys_path, mode=_mode.to_platform_bin(), buffering=buffering, **options
            )
        return cast(BinaryIO, binary_file)

    def remove(self, sys_path):
        raise NotImplementedError()

    def removedir(self, sys_path):
        raise NotImplementedError()

    def setinfo(self, sys_path, info):
        raise NotImplementedError()
