from typing import Optional

from simfile.types import Simfile
from .enums import *


__all__ = [
    "tidy",
    "Preset",
    "Whitespace",
    "LineEndings",
    "RemoveComments",
    "CreateComments",
    "CreateDefaultProperties",
    "DestructivelyRemoveProperties",
    "SortProperties",
]


def tidy(
    sim: Simfile,
    preset: Optional[Preset] = None,
    *,
    whitespace: bool | Whitespace = False,
    line_endings: bool | LineEndings = False,
    remove_comments: bool | RemoveComments = False,
    create_comments: bool | CreateComments = False,
    create_default_properties: bool | CreateDefaultProperties = False,
    destructively_remove_properties: bool | DestructivelyRemoveProperties = False,
    sort_properties: bool | SortProperties = False,
):
    """
    Tidy up a simfile for serialization to disk, mutating it in-memory.

    This function has many optional parameters that toggle various
    tidying **behaviors**. The simplest way to call it is to pass a preset
    as the second argument::

        import tidy, Preset from simfile.tidy
        tidy(sim, Preset.SM5)

    Without a preset, all behaviors default to `False`. You must set at
    least one behavior to a non-`False` value, or specify the
    :data:`~.NO_OP` preset to allow no behaviors.

    Each optional behavior has an associated enum. Some enums are flags
    that can be combined using bitwise operators, like so::

        tidy(
            sim,
            filter_comments=FilterComments.PREAMBLE | FilterComments.CHART_PREAMBLE,
        )

    Optional behaviors also take the shorthand `True` to opt into a default
    behavior. For non-flag enums, this is equivalent to passing the first
    enum value. For flag enums, it's equivalent to combining all options.
    Refer to each enum class's documentation for more details.

    Returns `True` only if changes were made to the simfile.
    """
    if not any(
        (
            preset,
            whitespace,
            line_endings,
            remove_comments,
            create_comments,
            create_default_properties,
            destructively_remove_properties,
            sort_properties,
        )
    ):
        raise ValueError(
            "Must specify a preset or at least one behavior"
            " (specify `Preset.NO_OP` to silence this error)"
        )

    changed = False

    if whitespace:
        changed |= Whitespace.run_outer(sim, whitespace)
    if line_endings:
        changed |= LineEndings.run_outer(sim, line_endings)
    if remove_comments:
        changed |= RemoveComments.run_outer(sim, remove_comments)
    if create_comments:
        changed |= CreateComments.run_outer(sim, create_comments)
    if create_default_properties:
        changed |= CreateDefaultProperties.run_outer(sim, create_default_properties)
    if destructively_remove_properties:
        changed |= DestructivelyRemoveProperties.run_outer(
            sim, destructively_remove_properties
        )
    if sort_properties:
        changed |= SortProperties.run_outer(sim, sort_properties)

    return changed
