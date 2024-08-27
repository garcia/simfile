import io
import os


class NativeOSFS:
    """
    OS filesystem shim that mimics the PyFilesystem2 API
    without having it installed.
    """

    def open(
        self,
        *args,
        **kwargs,
    ):
        return io.open(*args, **kwargs)

    def exists(self, sys_path):
        return os.path.exists(sys_path)

    def isdir(self, sys_path):
        return os.path.isdir(sys_path)

    def listdir(self, sys_path):
        return os.listdir(sys_path)
