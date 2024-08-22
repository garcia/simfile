import os
import re
from typing import Mapping, MutableMapping, NamedTuple, Optional, Sequence, Tuple

import simfile
from .types import Simfile
from ._private import extensions
from ._private.fs import FS, NativeOSFS
from ._private.path import FSPath


__all__ = ["Assets"]


class AssetDefinition(NamedTuple):
    presets: Sequence[str] = ()
    extensions: Sequence[str] = ()
    match_by_extension: bool = False

    def matches(self, path: str) -> bool:
        root, _ = os.path.splitext(path)
        if any(re.search(preset, root.lower()) for preset in self.presets):
            return True
        if self.match_by_extension and extensions.match(path, *self.extensions):
            return True
        return False


ASSET_DEFINITIONS: Mapping[str, AssetDefinition] = {
    "BANNER": AssetDefinition(
        extensions=extensions.IMAGE,
        # NOTE: according to StepMania's source code, the end pattern should be
        # " bn" with a space, not "bn". But it matches "bn.png" and I don't
        # know why, so I'm changing it to reflect the observed behavior.
        presets=["banner", "bn$"],
    ),
    "BACKGROUND": AssetDefinition(
        extensions=extensions.IMAGE,
        presets=["background", "bg$"],
    ),
    "CDTITLE": AssetDefinition(
        extensions=extensions.IMAGE,
        presets=["cdtitle"],
    ),
    "JACKET": AssetDefinition(
        extensions=extensions.IMAGE,
        presets=["^jk_", "jacket", "albumart"],
    ),
    "CDIMAGE": AssetDefinition(
        extensions=extensions.IMAGE,
        presets=["-cd$"],
    ),
    "DISC": AssetDefinition(
        extensions=extensions.IMAGE,
        presets=[" disc$", " title$"],
    ),
    "MUSIC": AssetDefinition(
        extensions=extensions.AUDIO,
        match_by_extension=True,
    ),
}


class Assets:
    """
    Asset loader for a simfile directory.

    This loader uses the same heuristics as StepMania to determine a
    default path for assets not specified in the simfile. For example, if
    the BACKGROUND property is missing or blank, StepMania will look for an
    image whose filename contains "background" or ends with "bg".

    The simfile will be loaded from the :code:`simfile_dir` unless an
    explicit :code:`simfile` argument is supplied. This is intended mostly
    as an optimization for when the simfile has already been loaded from
    disk.

    All asset paths are absolute and normalized. Keyword arguments are
    passed down to :func:`simfile.open` (and are only valid if
    :code:`simfile` is not provided).
    """

    @property
    def music(self):
        return self._asset_property("MUSIC")

    @property
    def banner(self):
        return self._asset_property("BANNER")

    @property
    def background(self):
        return self._asset_property("BACKGROUND")

    @property
    def cdtitle(self):
        return self._asset_property("CDTITLE")

    @property
    def jacket(self):
        return self._asset_property("JACKET")

    @property
    def cdimage(self):
        return self._asset_property("CDIMAGE")

    @property
    def disc(self):
        return self._asset_property("DISC")

    def __init__(
        self,
        simfile_dir: str,
        *,
        simfile: Optional[Simfile] = None,
        filesystem: FS = NativeOSFS(),
        **kwargs,
    ):
        if simfile and kwargs:
            raise TypeError(
                "Assets can't take both a simfile and kwargs (kwargs are only "
                "useful if no explicit simfile is provided)"
            )
        self.simfile_dir = simfile_dir
        self.filesystem = filesystem
        self._dirlist = self.filesystem.listdir(simfile_dir)
        self._cache: MutableMapping[str, Optional[str]] = {}
        self._path = FSPath(filesystem)

        if simfile:
            self.simfile = simfile
        else:
            from simfile.dir import SimfileDirectory

            self.simfile = SimfileDirectory(
                simfile_dir,
                filesystem=filesystem,
            ).open(**kwargs)

    def _get_case_insensitive_path(self, path: str) -> Optional[str]:
        containing_dir, filename = self._path.split(path)
        filename_lower = filename.lower()

        if self.filesystem.isdir(containing_dir):
            for item in self.filesystem.listdir(containing_dir):
                if item.lower() == filename_lower:
                    return self._path.join(containing_dir, item)

    def _asset_property(self: "Assets", prop: str) -> Optional[str]:
        if prop in self._cache:
            return self._cache[prop]

        specified_path = self.simfile.get(prop)
        if specified_path:
            full_path = self._path.join(self.simfile_dir, specified_path)
            case_insensitive_path = self._get_case_insensitive_path(full_path)
            if case_insensitive_path:
                return self._cache_path(prop, case_insensitive_path, absolute=True)

        asset_definition = ASSET_DEFINITIONS[prop]
        for file_in_simfile_dir in self._dirlist:
            if asset_definition.matches(file_in_simfile_dir):
                return self._cache_path(prop, file_in_simfile_dir)

        return self._cache_path(prop, None)

    def _cache_path(
        self, key: str, value: Optional[str], *, absolute: bool = False
    ) -> Optional[str]:
        if value is not None:
            if absolute:
                self._cache[key] = self._path.normpath(value)
            else:
                self._cache[key] = self._path.normpath(
                    self._path.join(self.simfile_dir, value),
                )
        else:
            self._cache[key] = None
        return self._cache[key]
