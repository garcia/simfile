from dataclasses import replace
from typing import Literal

from simfile.types import Simfile
from .behaviors import (
    Preset,
    Whitespace,
    LineEndings,
    ChangeComments,
    CreateMissingProperties,
    DestructivelyRemoveProperties,
    SortProperties,
)


__all__ = [
    "tidy",
    "Preset",
    "Whitespace",
    "LineEndings",
    "ChangeComments",
    "CreateMissingProperties",
    "DestructivelyRemoveProperties",
    "SortProperties",
]


def tidy(
    sim: Simfile,
    preset: Preset | None = None,
    *,
    whitespace: Whitespace | Literal[False] | None = None,
    line_endings: LineEndings | Literal[False] | None = None,
    change_comments: ChangeComments | Literal[False] | None = None,
    create_missing_properties: CreateMissingProperties | Literal[False] | None = None,
    destructively_remove_properties: DestructivelyRemoveProperties
    | Literal[False]
    | None = None,
    sort_properties: SortProperties | Literal[False] | None = None,
):
    """
    Tidy up a simfile for future serialization, mutating it in-memory.

    This function has many optional parameters that toggle various
    tidying **behaviors**. The simplest way to call it is to pass a preset
    as the second argument::

        import tidy, Preset from simfile.tidy
        tidy(sim, Preset.RECOMMENDED)  # or Preset.SM5

    Without a preset, all behaviors default to off. If you don't specify
    a preset, you must set at least one behavior to a non-empty value, or
    specify the :data:`~Preset.NO_OP` preset to allow no behaviors.

    Each optional behavior has an associated enum. Some behaviors' enums
    are flags that can be combined using bitwise operators, for example::

        import tidy, ChangeComments from simfile.tidy
        tidy(
            sim,
            change_comments=ChangeComments.REMOVE_PREAMBLE | ChangeComments.REMOVE_CHART_PREAMBLE,
        )

    Returns `True` only if changes were made to the simfile.
    Raises `ValueError` if no preset or behaviors are specified.
    """
    if not any(
        (
            preset,
            whitespace,
            line_endings,
            change_comments,
            create_missing_properties,
            destructively_remove_properties,
            sort_properties,
        )
    ):
        raise ValueError(
            "Must specify a preset or at least one behavior"
            + " (pass `Preset.NO_OP` as the second argument to silence this error)"
        )

    changed = False

    # Override preset behaviors with manually specified behaviors
    behaviors = preset.behaviors() if preset else Preset.NO_OP.behaviors()
    if whitespace is not None:
        behaviors.whitespace = whitespace or None
    if line_endings is not None:
        behaviors.line_endings = line_endings or None
    if change_comments is not None:
        behaviors.change_comments = change_comments or None
    if create_missing_properties is not None:
        behaviors.create_missing_properties = create_missing_properties or None
    if destructively_remove_properties is not None:
        behaviors.destructively_remove_properties = (
            destructively_remove_properties or None
        )
    if sort_properties is not None:
        behaviors.sort_properties = sort_properties or None

    if behaviors.create_missing_properties:
        changed |= behaviors.create_missing_properties.run(sim)
    if behaviors.destructively_remove_properties:
        changed |= behaviors.destructively_remove_properties.run(sim)
    if behaviors.sort_properties:
        changed |= behaviors.sort_properties.run(sim)
    if behaviors.change_comments:
        changed |= behaviors.change_comments.run(sim)
    if behaviors.whitespace:
        changed |= behaviors.whitespace.run(sim)
    if behaviors.line_endings:
        changed |= behaviors.line_endings.run(sim)

    new_contents = str(sim)

    return changed


def set_preamble_comment(sim: Simfile, text: str):
    first_property = next(iter(sim._properties.values()))
    first_property.msd_parameter = replace(
        first_property.msd_parameter,
        preamble="".join(
            f"// {line}\n" if not line.startswith("//") else line
            for line in text.splitlines()
        ),
    )
