try:
    import fs
    from fs.base import FS
    from .fs_installed import NativeOSFS
except ImportError:
    from .fs_not_installed import NativeOSFS

    FS = NativeOSFS

__all__ = ["FS", "NativeOSFS"]
