from dataclasses import dataclass, replace
import enum
import re
from typing import Iterator, Mapping, Optional
from typing_extensions import assert_never

from msdparser import MSDParameter, parse_msd

import simfile
from simfile._private.msd_serializable import MSDSerializable
from simfile._private.ordered_dict_forwarder import Property
from simfile.sm import SMChart, SMSimfile
from simfile.ssc import SSCChart, SSCSimfile
from simfile.timing._private.timingsource import timing_source, CHART_TIMING_DEFAULTS
from simfile.types import Chart, Simfile


__all__ = [
    "Preset",
    "Whitespace",
    "LineEndings",
    "RemoveComments",
    "CreateComments",
    "CreateMissingProperties",
    "DestructivelyRemoveProperties",
    "SortProperties",
]


def reencode_msd(
    msd: MSDParameter | MSDSerializable | str, clear_preamble: bool = False
):
    if isinstance(msd, MSDParameter):
        msd_string = msd.stringify(exact=True)
    elif isinstance(msd, MSDSerializable):
        msd_string = str(msd)
    elif isinstance(msd, str):
        msd_string = msd
    else:
        assert_never(msd)

    reencoded = next(parse_msd(string=msd_string))

    if clear_preamble:
        reencoded = replace(reencoded, preamble=None)

    return reencoded


class Preset(enum.Enum):
    """
    A predefined set of behaviors for use with :func:`~.tidy`.
    """

    NO_OP = enum.auto()
    """
    Leave all optional behaviors off by default.
    
    This is equivalent to not specifying a preset, except it allows you to
    leave all optional behaviors ``False``.
    """

    SM5 = enum.auto()
    """
    Emulate the StepMania 5 editor's output (nondestructively).
    """

    SM5_DESTRUCTIVE = enum.auto()
    """
    Emulate the StepMania 5 editor's output (including removing unknown
    properties).
    """

    RECOMMENDED = enum.auto()
    """
    Same as SM5, but keep the preamble & add or update the library version.
    """

    def behaviors(self) -> "DefaultBehaviors":
        if self is Preset.NO_OP:
            return DefaultBehaviors()

        elif self is Preset.SM5:
            return replace(
                DefaultBehaviors(),
                whitespace=Whitespace.SM5,
                line_endings=LineEndings.LF,
                remove_comments=RemoveComments.ALL,
                create_comments=CreateComments.CHART_PREAMBLE
                | CreateComments.CHART_MEASURES,
                create_missing_properties=CreateMissingProperties.SM5,
                sort_properties=SortProperties.SM5,
            )

        elif self is Preset.SM5_DESTRUCTIVE:
            return replace(
                Preset.SM5.behaviors(),
                destructively_remove_properties=DestructivelyRemoveProperties.SM5,
            )

        elif self is Preset.RECOMMENDED:
            sm5 = Preset.SM5.behaviors()
            assert sm5.remove_comments
            assert sm5.create_comments
            return replace(
                sm5,
                remove_comments=sm5.remove_comments ^ RemoveComments.PREAMBLE,
                create_comments=sm5.create_comments
                | CreateComments.LIBRARY_VERSION_PREAMBLE,
            )

        else:
            assert False


class Whitespace(enum.Enum):
    """
    Normalize all whitespace in the file.
    """

    SM5 = enum.auto()
    """
    Normalize whitespace to match StepMania 5's output:

    * Properties are separated by a newline.
    * Each chart is prefixed by a blank line.
    * Each SM chart property (before note data) is prefixed by 5 spaces.

    Currently, this option removes comments inside of SM charts
    if their whitespace is adjusted. Combine with :class:`.CreateComments`
    to regenerate measure comments if desired.
    """

    def run(self, sim: Simfile) -> bool:
        changed = False

        if self is Whitespace.SM5:
            # Extract newline from heursitic-determined suffix
            nl = "\r\n" if "\r\n" in sim._default_parameter.suffix else "\n"

            # Normalize suffix & (optionally) preamble whitespace
            def normalize_ws(param: MSDParameter, preamble=False) -> MSDParameter:
                if preamble:
                    # Blank / empty -> single newline
                    if not param.preamble or param.preamble.isspace():
                        new_preamble = nl
                    # Non-empty -> strip & pad with newline on each side
                    else:
                        new_preamble = f"{nl}{param.preamble.strip()}{nl}"
                else:
                    new_preamble = param.preamble

                suffix_no_semicolon = param.suffix.removeprefix(";")
                # Blank / empty -> semicolon followed by newline
                if suffix_no_semicolon == "" or suffix_no_semicolon.isspace():
                    new_suffix = f";{nl}"
                # Non-empty -> ensure semicolon & one trailing newline
                else:
                    new_suffix = f";{suffix_no_semicolon.rstrip()}{nl}"

                return replace(param, preamble=new_preamble, suffix=new_suffix)

            if sim._default_parameter.suffix != f";{nl}":
                sim._default_parameter = replace(
                    sim._default_parameter, suffix=f";{nl}"
                )
                changed = True

            for property in sim._properties.values():
                normalized_ws = normalize_ws(property.msd_parameter)
                if property.msd_parameter != normalized_ws:
                    property.msd_parameter = normalized_ws
                    changed = True

            for chart in sim.charts:

                # This is tricky to get right on SMChart
                # because of the way it abuses the _properties dict.
                if isinstance(chart, SMChart):
                    # Normalize whitespace before the (real) chart property
                    normalized_ws = normalize_ws(chart._real_parameter, preamble=True)
                    if chart._real_parameter != normalized_ws:
                        chart._real_parameter = normalized_ws
                        changed = True

                    # Normalize whitespace between each (pseudo) property
                    # TODO: check how this interacts with escape & comment MSD data
                    for key, property in chart._properties.items():
                        sm_chart_changed = False
                        if key == "NOTES":
                            updated_parameter = replace(
                                property.msd_parameter, suffix=nl
                            )
                            if property.msd_parameter != updated_parameter:
                                property.msd_parameter = updated_parameter
                                sm_chart_changed = True
                        else:
                            updated_parameter = replace(
                                property.msd_parameter, preamble=f"{nl}     "
                            )
                            if property.msd_parameter != updated_parameter:
                                property.msd_parameter = updated_parameter
                                sm_chart_changed = True

                        # Adjusting whitespace *inside* of an MSD parameter
                        # invalidates the escape & comment positions;
                        # we could try to keep track of the positions,
                        # but for now, just reset it and let msdparser
                        # regenerate any necessary escapes.
                        if sm_chart_changed:
                            chart._real_parameter = replace(
                                chart._real_parameter,
                                escape_positions=None,
                                comments=None,
                            )

                        changed |= sm_chart_changed

                elif isinstance(chart, SSCChart):
                    # Normalize whitespace before the chart
                    notedata = chart._properties["NOTEDATA"]
                    normalized_ws = normalize_ws(notedata.msd_parameter, preamble=True)
                    if notedata.msd_parameter != normalized_ws:
                        notedata.msd_parameter = normalized_ws
                        changed = True

                    # Normalize whitespace between each property
                    for property in chart._properties.values():
                        normalized_ws = normalize_ws(property.msd_parameter)
                        if property.msd_parameter != normalized_ws:
                            property.msd_parameter = normalized_ws
                            changed = True
                else:
                    assert_never(chart)

            return changed

        else:
            assert_never(self)


class LineEndings(enum.Enum):
    """
    Normalize all line endings in the file.
    """

    LF = enum.auto()
    """
    Normalize all line endings to '\\n'.
    """

    CRLF = enum.auto()
    """
    Normalize all line endings to '\\r\\n'.
    """

    HEURISTIC = enum.auto()
    """
    Use the heuristic-determined line ending.

    This typically matches the first line ending seen in the file.
    """

    def run(self, sim: Simfile) -> bool:
        if self in (LineEndings.LF, LineEndings.CRLF):
            changed = False
            nl = "\n" if self is LineEndings.LF else "\r\n"

            sim._default_parameter = replace(
                sim._default_parameter,
                suffix=sim._default_parameter.suffix.rstrip("\r\n") + nl,
            )

            for property in sim._properties.values():
                changed |= self._normalize_property(nl, property)

            for chart in sim.charts:

                # _normalize_property doesn't work well with fake SMChart
                # properties, so instead serialize the whole chart into a
                # fresh MSDParameter, then update the chart in-place.
                if isinstance(chart, SMChart):
                    parameter = reencode_msd(chart)
                    fake_property = Property("", parameter)
                    self._normalize_property(nl, fake_property)
                    normalized_chart = SMChart.from_msd_parameter(
                        fake_property.msd_parameter
                    )
                    chart._real_parameter = normalized_chart._real_parameter
                    chart._properties = normalized_chart._properties

                elif isinstance(chart, SSCChart):
                    for property in chart._properties.values():
                        changed |= self._normalize_property(nl, property)

                else:
                    assert_never(chart)

            return changed

        elif self is LineEndings.HEURISTIC:
            crlf = "\r\n" in sim._default_parameter.suffix
            if crlf:
                return LineEndings.CRLF.run(sim)
            else:
                return LineEndings.LF.run(sim)

        else:
            assert_never(self)

    def _normalize_property(self, nl, property: Property) -> bool:
        # Serialize using msdparser so that we can perform the newline swap
        # on everything (preamble, key, value(s), suffix) at once.
        # This also means we get correct escape_positions for free.
        stringified = property.msd_parameter.stringify(exact=True)
        changed = False

        # Short-circuit if no newlines to change
        if "\r" not in stringified and "\n" not in stringified:
            return False

        split = stringified.splitlines(keepends=True)
        normalized = []
        for line in split:
            if line.endswith("\n") or line.endswith("\r"):
                normalized.append(line.rstrip("\r\n") + nl)
            else:
                normalized.append(line)

        normalized_string = "".join(normalized)
        normalized_param = reencode_msd(
            normalized_string,
            # parse_msd always outputs a (possibly empty) preamble for the
            # first parameter, which will mess up the equality comparison
            # if it's None in the original parameter.
            clear_preamble=property.msd_parameter.preamble is None,
        )

        if normalized_param != property.msd_parameter:
            property.msd_parameter = normalized_param
            # TODO: handle multi-value properties
            property.value = normalized_param.value
            changed = True

        return changed


# Scaffolding for RemoveComments:


class MsdFieldForComments(enum.Flag):
    PREAMBLE = enum.auto()
    COMMENTS = enum.auto()
    SUFFIX = enum.auto()


class PropertyForComments(enum.Enum):
    SIMFILE_FIRST_PROP = enum.auto()
    SIMFILE_OTHER_PROPS = enum.auto()
    SSCCHART_FIRST_PROP = enum.auto()
    SSCCHART_OTHER_PROPS = enum.auto()
    SMCHART_REAL_PARAM = enum.auto()

    def iter_props(self, sim: Simfile) -> Iterator[Property]:
        if self is PropertyForComments.SIMFILE_FIRST_PROP:
            yield next(iter(sim._properties.values()))
        elif self is PropertyForComments.SIMFILE_OTHER_PROPS:
            iterator = iter(sim._properties.values())
            next(iterator)
            yield from iterator
        elif self is PropertyForComments.SMCHART_REAL_PARAM:
            for chart in sim.charts:
                if isinstance(chart, SMChart):
                    # HACK(update-real-param): fake property must be updated
                    # in the simfile *manually* by the caller
                    fake_prop = Property(value="", msd_parameter=chart._real_parameter)
                    yield fake_prop
        elif self is PropertyForComments.SSCCHART_FIRST_PROP:
            for chart in sim.charts:
                if isinstance(chart, SSCChart):
                    yield next(iter(chart._properties.values()))
        elif self is PropertyForComments.SSCCHART_OTHER_PROPS:
            for chart in sim.charts:
                if isinstance(chart, SSCChart):
                    iterator = iter(chart._properties.values())
                    next(iterator)
                    yield from iterator
        else:
            assert_never(self)

    def change_msd_fields(
        self, remove_comments: "RemoveComments"
    ) -> MsdFieldForComments:
        fields = MsdFieldForComments(0)

        if self is PropertyForComments.SIMFILE_FIRST_PROP:
            if RemoveComments.PREAMBLE in remove_comments:
                fields |= MsdFieldForComments.PREAMBLE
            if RemoveComments.OTHER in remove_comments:
                fields |= MsdFieldForComments.COMMENTS | MsdFieldForComments.SUFFIX

        elif self is PropertyForComments.SIMFILE_OTHER_PROPS:
            if RemoveComments.OTHER in remove_comments:
                fields |= (
                    MsdFieldForComments.PREAMBLE
                    | MsdFieldForComments.COMMENTS
                    | MsdFieldForComments.SUFFIX
                )

        elif self in (
            PropertyForComments.SSCCHART_FIRST_PROP,
            PropertyForComments.SMCHART_REAL_PARAM,
        ):
            if RemoveComments.CHART_PREAMBLE in remove_comments:
                fields |= MsdFieldForComments.PREAMBLE
            if RemoveComments.CHART_INNER in remove_comments:
                fields |= MsdFieldForComments.COMMENTS
            if RemoveComments.OTHER in remove_comments:
                fields |= MsdFieldForComments.SUFFIX

        elif self is PropertyForComments.SSCCHART_OTHER_PROPS:
            if RemoveComments.CHART_INNER in remove_comments:
                fields |= MsdFieldForComments.COMMENTS
            if RemoveComments.OTHER in remove_comments:
                fields |= MsdFieldForComments.PREAMBLE | MsdFieldForComments.SUFFIX

        else:
            assert_never(self)

        return fields


class RemoveComments(enum.Flag):
    """
    Remove comments from various (or all) parts of the simfile.
    """

    PREAMBLE = enum.auto()
    """
    Remove any preamble (comment at the start of the file).
    """

    CHART_PREAMBLE = enum.auto()
    """
    Remove any chart preamble (comment before the first property signaling
    a chart, i.e. ``NOTES`` for SM and ``NOTEDATA`` for SSC).
    """

    CHART_INNER = enum.auto()
    """
    Remove any comments inside a chart, such as (but not limited to)
    measure indicators.
    """

    OTHER = enum.auto()
    """
    Remove any other comments that don't match the above definitions.
    """

    ALL = PREAMBLE | CHART_PREAMBLE | CHART_INNER | OTHER
    """
    Remove all comments.
    """

    @staticmethod
    def _remove_comments(string: str) -> str:
        output_lines = []
        for line in string.splitlines(keepends=True):
            # Completely drop the line if it only contains a comment
            if not line.lstrip().startswith("//"):
                output_lines.append(re.sub(r"(?<!\\)//.*", "", line))
        return "".join(output_lines)

    def run(self, sim: Simfile) -> bool:
        changed = False

        for prop_type in PropertyForComments:
            # Iterate over all properties of a given type
            for prop in prop_type.iter_props(sim):

                original_msd_parameter = prop.msd_parameter
                change_msd_fields = prop_type.change_msd_fields(self)
                msd_field_names = {
                    MsdFieldForComments.PREAMBLE: "preamble",
                    MsdFieldForComments.COMMENTS: "comments",
                    MsdFieldForComments.SUFFIX: "suffix",
                }

                for field, field_name in msd_field_names.items():
                    if field in change_msd_fields:
                        if field in (
                            MsdFieldForComments.PREAMBLE | MsdFieldForComments.SUFFIX
                        ):
                            field_value: Optional[str] = getattr(
                                prop.msd_parameter, field_name
                            )
                            if field_value and "//" in field_value:
                                field_value_no_comments = (
                                    RemoveComments._remove_comments(field_value)
                                )
                                if field_value_no_comments != field_value:
                                    prop.msd_parameter = replace(
                                        prop.msd_parameter,
                                        **{field_name: field_value_no_comments},
                                    )
                                    changed = True

                        elif field is MsdFieldForComments.COMMENTS:
                            if prop.msd_parameter.comments:
                                prop.msd_parameter = replace(
                                    prop.msd_parameter, comments={}
                                )
                                changed = True

                # HACK(update-real-param): update chart._real_parameter
                # manually here (because it isn't contained in a Property)
                if prop_type is PropertyForComments.SMCHART_REAL_PARAM:
                    if isinstance(sim, SMSimfile):
                        for chart in sim.charts:
                            if chart._real_parameter == original_msd_parameter:
                                chart._real_parameter = prop.msd_parameter

        return changed


class CreateComments(enum.Flag):
    """
    Create or update pre-fabricated comments in the simfile.
    """

    LIBRARY_VERSION_PREAMBLE = enum.auto()
    """
    Create a comment at the start of the file with the following string::

        // Generated by simfile {VERSION} for Python
    
    :code:`{VERSION}` is replaced with :data:`simfile.__version__`.
    """

    CHART_PREAMBLE = enum.auto()
    """
    Create a comment before each chart with the following string::

        //---------------{STEPSTYPE} - {DESCRIPTION}----------------
    
    :code:`{STEPSTYPE}` is replaced by :attr:`Chart.stepstype` and
    :code:`{DESCRIPTION}` is replaced by :attr:`Chart.description`.
    """

    CHART_MEASURES = enum.auto()
    """
    Create comments before each measure to indicate the measure number::

        #NOTES:
        // measure 0
        0000
        0000
        0000
        0000
        ,  // measure 1
        (etc.)
    """

    @staticmethod
    def _update_or_create_preamble_line(
        prop: Property, comment_pattern: str, comment_text: str
    ) -> bool:
        changed = False

        if prop.msd_parameter.preamble:
            updated_preamble_lines = []
            match_found = False

            for line in prop.msd_parameter.preamble.splitlines(keepends=True):
                if re.match(comment_pattern, line):
                    updated_preamble_lines.append(comment_text)
                    match_found = True
                else:
                    updated_preamble_lines.append(line)

            if not match_found:
                updated_preamble_lines.append(comment_text)

            updated_preamble = "".join(updated_preamble_lines)

        else:
            updated_preamble = comment_text

        if updated_preamble != prop.msd_parameter.preamble:
            prop.msd_parameter = replace(prop.msd_parameter, preamble=updated_preamble)
            changed = True

        return changed

    @staticmethod
    def _generate_measure_comments(chart: Chart, *, line_offset=0):
        comments: dict[int, str] = {}
        notes_with_preamble = (
            chart._properties["NOTES"].msd_parameter.preamble or ""
        ) + (chart.notes or "")
        lines = notes_with_preamble.splitlines()

        # Find where the measure 0 comment should go
        first_nonblank_line = next(
            (ln for ln, line in enumerate(lines) if line.strip()), 0
        )
        last_blank_line = max(0, first_nonblank_line - 1)
        # If it lands on line 0, add a newline before it
        maybe_nl = "\n" if last_blank_line == 0 else ""
        comments[last_blank_line + line_offset] = f"{maybe_nl}// measure 0"

        # Add the rest of the measure comments
        mn = 1
        for ln, line in enumerate(notes_with_preamble.splitlines()):
            if "," in line:
                # Ensure at least 2 spaces between the "," and the comment
                trailing_spaces = len(line) - len(line.rstrip(" "))
                add_trailing_spaces = " " * max(0, 2 - trailing_spaces)
                comments[ln + line_offset] = f"{add_trailing_spaces}// measure {mn}"
                mn += 1
        return comments

    def run(self, sim: Simfile) -> bool:
        changed = False

        if CreateComments.LIBRARY_VERSION_PREAMBLE in self:
            comment_base = "// Generated by simfile {version} for Python"
            comment_pattern = comment_base.format(version=r"\S+")
            comment_text = comment_base.format(version=simfile.__version__) + "\n"
            first_property = next(iter(sim._properties.values()))
            changed |= CreateComments._update_or_create_preamble_line(
                first_property, comment_pattern, comment_text
            )

        if CreateComments.CHART_PREAMBLE in self:
            comment_base = (
                "//---------------{stepstype} - {description}----------------"
            )
            comment_pattern = comment_base.format(stepstype=r".*", description=r".*")

            for chart in sim.charts:
                comment_text = (
                    comment_base.format(
                        stepstype=chart.stepstype, description=chart.description
                    )
                    + "\n"
                )

                if isinstance(chart, SMChart):
                    fake_property = Property(
                        value="", msd_parameter=chart._real_parameter
                    )
                    changed_smchart_preamble = (
                        CreateComments._update_or_create_preamble_line(
                            fake_property, comment_pattern, comment_text
                        )
                    )
                    if changed_smchart_preamble:
                        chart._real_parameter = replace(
                            chart._real_parameter,
                            preamble=fake_property.msd_parameter.preamble,
                        )
                        changed = True

                elif isinstance(chart, SSCChart):
                    first_sscchart_property = next(iter(chart._properties.values()))
                    changed |= CreateComments._update_or_create_preamble_line(
                        first_sscchart_property, comment_pattern, comment_text
                    )

                else:
                    assert_never(chart)

        if CreateComments.CHART_MEASURES in self:
            for chart in sim.charts:
                if isinstance(chart, SMChart):
                    if chart.notes and not chart.notes.isspace():
                        line_offset = 0
                        for chart_prop in simfile.sm.SM_CHART_PROPERTIES:
                            if chart_prop == "NOTES":
                                break
                            property = chart._properties[chart_prop]
                            line_offset += (
                                len(
                                    (
                                        (property.msd_parameter.preamble or "")
                                        + property.value
                                        + property.msd_parameter.suffix
                                    ).splitlines()
                                )
                                - 1
                            )

                        comments = CreateComments._generate_measure_comments(
                            chart, line_offset=line_offset
                        )

                        if comments != chart._real_parameter.comments:
                            chart._real_parameter = replace(
                                chart._real_parameter, comments=comments
                            )
                            reencoded = reencode_msd(chart)
                            normalized_chart = SMChart.from_msd_parameter(reencoded)
                            chart._real_parameter = normalized_chart._real_parameter
                            chart._properties = normalized_chart._properties
                            changed = True

                elif isinstance(chart, SSCChart):
                    if chart.notes and not chart.notes.isspace():
                        comments = CreateComments._generate_measure_comments(chart)

                        notes_property = chart._properties["NOTES"]
                        if comments != notes_property.msd_parameter.comments:
                            notes_property.msd_parameter = replace(
                                notes_property.msd_parameter,
                                components=(
                                    notes_property.msd_parameter.key,
                                    notes_property.value,
                                ),
                                comments=comments,
                            )
                            reencoded = reencode_msd(notes_property.msd_parameter)
                            notes_property.value = reencoded.value
                            notes_property.msd_parameter = reencoded
                            changed = True

                else:
                    assert_never(chart)

        return changed


class CreateMissingProperties(enum.Enum):
    """
    Fill in any missing properties in the simfile with a default value.
    """

    SM5 = enum.auto()
    """
    Create the same default properties that the StepMania 5 editor creates,
    if they don't already exist.

    Most properties' default values are an empty string, but some have a
    specific non-empty default value, such as ``OFFSET`` and ``BPMS``.
    """

    def run(self, sim: Simfile) -> bool:
        changed = False

        if self is CreateMissingProperties.SM5:
            SimfileType = type(sim)
            blank = SimfileType.blank()
            for key in blank._properties.keys():
                if key not in sim:
                    sim[key] = blank[key] or ""
                    changed = True

            if SimfileType is SSCSimfile:
                for chart in sim.charts:
                    if timing_source(chart) is chart:
                        for prop, default_value in CHART_TIMING_DEFAULTS.items():
                            if prop.__get__(chart) is None:
                                prop.__set__(chart, default_value)
                                changed = True

        else:
            assert_never(self)

        return changed


class DestructivelyRemoveProperties(enum.Enum):
    """
    Remove any unknown properties (a destructive operation).
    """

    SM5 = enum.auto()
    """
    Remove all properties that are unknown to the StepMania 5 editor.
    """

    def run(self, sim: Simfile) -> bool:
        return False


class SortProperties(enum.Enum):
    """
    Sort the properties in the simfile.
    """

    SM5 = enum.auto()
    """
    Sort known properties to match the StepMania 5 editor's output.

    Unknown properties, if not removed, are sorted alphabetically after
    known properties.
    """

    def run(self, sim: Simfile) -> bool:
        return False


@dataclass
class DefaultBehaviors:
    preset: Optional[Preset] = None
    whitespace: Optional[Whitespace] = None
    line_endings: Optional[LineEndings] = None
    remove_comments: Optional[RemoveComments] = None
    create_comments: Optional[CreateComments] = None
    create_missing_properties: Optional[CreateMissingProperties] = None
    destructively_remove_properties: Optional[DestructivelyRemoveProperties] = None
    sort_properties: Optional[SortProperties] = None
