.. _examples:

Learn by example
================

This page includes examples of varying length
demonstrating correct & type-checked **simfile** library usage.
You're free to use these recipes & scripts as-is,
modify them to suit your needs,
or simply use them as a learning aid.

Recipes
~~~~~~~

This section includes short snippets of code
that demonstrate basic library usage.
These recipes are in the public domain.

Get charts for one game mode
----------------------------

.. code:: python

    from typing import Iterator
    from simfile.types import Chart

    # Imperative version
    def charts_for_stepstype(charts, stepstype='dance-single') -> Iterator[Chart]:
        for chart in charts:
            if chart.stepstype == stepstype:
                yield chart
    
    # One-liner version
    def charts_for_stepstype(charts, stepstype='dance-single') -> Iterator[Chart]:
        yield from filter(lambda chart: chart.stepstype == stepstype, charts)


Get the hardest chart
---------------------

.. code:: python

    from typing import Optional, Sequence
    from simfile.types import Chart

    # Imperative version
    def get_hardest_chart(charts) -> Optional[Chart]:
        hardest_chart: Optional[Chart] = None
        hardest_meter: Optional[int] = None

        for chart in charts:
            # Remember to convert `meter` to an integer for comparisons
            meter = int(chart.meter or "1")
            if hardest_meter is None or meter > hardest_meter:
                hardest_chart = chart
                hardest_meter = meter

        return hardest_chart

    # One-liner version
    def get_hardest_chart(charts: Sequence[Chart]) -> Optional[Chart]:
        return max(
            charts,
            key=lambda chart: int(chart.meter or "1"),
            default=None,
        )


Mirror a chart's notes
----------------------

.. code:: python

    from typing import Iterator
    from simfile.types import Chart
    from simfile.notes import Note, NoteData

    def mirror_note(note: Note, columns: int) -> Note:
        # Make a new Note with all fields the same except for column
        return note._replace(
            # You could replace this expression with anything you want
            column=columns - note.column - 1
        )
    
    def mirror_notes(notedata: NoteData) -> Iterator[Note]:
        columns = notedata.columns
        for note in notedata:
            yield mirror_note(note, columns)

    def mirror_chart_in_place(chart: Chart) -> None:
        notedata = NoteData(chart)
        mirrored = NoteData.from_notes(
            mirror_notes(notedata),
            columns=notedata.columns,
        )
        # Assign str(NoteData) to Chart.notes to update the chart's notes
        chart.notes = str(mirrored)

Remove all but one chart from a simfile
---------------------------------------

.. code:: python

    from typing import Optional
    from simfile.types import Chart, Charts, Simfile

    # When you have multiple parameters of the same type (str in this case),
    # it's good practice to use a * pseudo-argument to require them to be named
    def find_chart(charts: Charts, *, stepstype: str, difficulty: str) -> Optional[Chart]:
        for chart in charts:
            if chart.stepstype == stepstype and chart.difficulty == difficulty:
                return chart

    def remove_other_charts(sf: Simfile, *, stepstype='dance-single', difficulty='Challenge'):
        the_chart = find_chart(sf.charts, stepstype=stepstype, difficulty=difficulty)
        if the_chart:
            # Replace the simfile's charts with a list of one
            sf.charts = [the_chart]  # type: ignore
        else:
            # You could alternatively raise an exception, pick a different chart,
            # set sf.charts to an empty list, etc.
            print(f"No {stepstype} {difficulty} chart found for {repr(sf)}")

Full scripts
~~~~~~~~~~~~

This section includes complete, ready-to-use scripts
that automate repetitive tasks on simfile packs.
These scripts are licensed under the MIT License,
the same license as the **simfile** library itself.

change_sync_bias.py
-------------------

.. code:: python

    R"""
    Add or subtract the standard ITG sync bias (9 milliseconds)
    to all of the sync offsets in a pack.

    This script updates the offsets of both SM and SSC simfiles,
    including any SSC charts with their own timing data.

    If you actually intend to use this script in practice,
    you may want to keep track of which packs you've already adjusted
    using a text file in each pack directory or some other system.

    Usage examples:

        # Convert a pack from "null sync" to "ITG sync"
        python change_sync_bias.py +9 "C:\StepMania\Songs\My Pack"

        # Convert a pack from "ITG sync" to "null sync"
        python change_sync_bias.py -9 "C:\StepMania\Songs\My Pack"
    """
    import argparse
    from decimal import Decimal
    import sys
    from typing import Union

    import simfile
    import simfile.dir


    class ChangeSyncBiasArgs:
        """Stores the command-line arguments for this script."""

        pack: str
        itg_to_null: bool
        null_to_itg: bool


    def argparser():
        """Get an ArgumentParser instance for this command-line script."""
        parser = argparse.ArgumentParser(prefix_chars="-+")
        parser.add_argument("pack", type=str, help="path to the pack to modify")
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "-9", "--itg-to-null", action="store_true", help="subtract 9ms from offsets"
        )
        group.add_argument(
            "+9", "--null-to-itg", action="store_true", help="add 9ms to offsets"
        )
        return parser


    def adjust_offset(
        obj: Union[simfile.types.Simfile, simfile.ssc.SSCChart],
        delta: Decimal,
    ):
        """Add the delta to the simfile or SSC chart's offset, if present."""
        if obj.offset is not None:
            obj.offset = str(Decimal(obj.offset) + delta)


    def change_sync_bias(simfile_path: str, args: ChangeSyncBiasArgs):
        """
        Add or subtract 9 milliseconds to the simfile's offset,
        as well as any SSC charts with their own timing data.

        This saves the updated simfile to its original location
        and writes a backup copy with a ~ appended to the filename.
        """
        # Map the +9 or -9 arg to the actual offset delta.
        #
        # We don't have to check both itg_to_null and null_to_itg
        # because the mutually exclusive & required argument group
        # ensures that exactly one of them will be True.
        delta = Decimal("-0.009" if args.itg_to_null else "+0.009")

        # You could specify output_filename here to write the updated file elsewhere
        with simfile.mutate(
            input_filename=f"{simfile_path}",
            backup_filename=f"{simfile_path}~",
        ) as sf:
            print(f"Processing {simfile_path}")

            # Always adjust the simfile's offset
            adjust_offset(sf, delta)

            # Additionally try to adjust SSC charts' offsets.
            # This won't do anything unless the chart has its own timing data.
            if isinstance(sf, simfile.ssc.SSCSimfile):
                for chart in sf.charts:
                    adjust_offset(chart, delta)


    def main(argv):
        # Parse command-line arguments
        args = argparser().parse_args(argv[1:], namespace=ChangeSyncBiasArgs())

        # Iterate over SimfileDirectory objects from the pack
        # so that we can easily get the .sm and/or .ssc paths
        for simfile_dir in simfile.dir.SimfilePack(args.pack).simfile_dirs():

            # Try to update whichever formats exist
            for simfile_path in [simfile_dir.sm_path, simfile_dir.ssc_path]:
                if simfile_path:
                    change_sync_bias(simfile_path, args)


    if __name__ == "__main__":
        main(sys.argv)


sort_by_difficulty.py
---------------------

.. code:: python

    R"""
    Change the title of every simfile in a pack
    so that they are sorted by difficulty in StepMania.

    This script finds the hardest chart of a given stepstype (dance-single by default)
    and puts its meter (difficulty number) between brackets at the start of the title
    and translittitle.

    Usage examples:

        # Sort a pack by difficulty
        python sort_by_difficulty.py "C:\StepMania\Songs\My Pack"

        # Unsort by difficulty (remove the title prefixes)
        python sort_by_difficulty.py -r "C:\StepMania\Songs\My Pack"

        # Customize stepstype and digits
        python sort_by_difficulty.py -s dance-double -d 3 "C:\StepMania\My Pack"
    """
    import argparse
    import sys
    from typing import Optional, Sequence

    import simfile
    import simfile.dir


    class SortByDifficultyArgs:
        """Stores the command-line arguments for this script."""

        pack: str
        stepstype: str
        digits: int
        remove: bool


    def argparser():
        """Get an ArgumentParser instance for this command-line script."""
        parser = argparse.ArgumentParser()
        parser.add_argument("pack", type=str, help="path to the pack to modify")
        parser.add_argument("-s", "--stepstype", type=str, default="dance-single")
        parser.add_argument(
            "-d",
            "--digits",
            type=int,
            default=2,
            help="minimum digits (will add leading zeroes)",
        )
        parser.add_argument(
            "-r",
            "--remove",
            action=argparse.BooleanOptionalAction,
            help="remove meter prefix",
        )
        return parser


    def hardest_chart(
        charts: Sequence[simfile.types.Chart], stepstype: str
    ) -> Optional[simfile.types.Chart]:
        """
        Find & return the hardest chart (numerically) of a given stepstype.

        Returns None if there are no charts matching the stepstype.
        """
        return max(
            [c for c in charts if c.stepstype == stepstype],
            key=lambda c: int(c.meter or "1"),
            default=None,
        )


    def prefix_title_with_meter(simfile_path: str, args: SortByDifficultyArgs):
        """
        Add (or remove) a numeric prefix to the simfile's title and titletranslit.

        This saves the updated simfile to its original location
        and writes a backup copy with a ~ appended to the filename.
        """
        # You could specify output_filename here to write the updated file elsewhere
        with simfile.mutate(
            input_filename=f"{simfile_path}",
            backup_filename=f"{simfile_path}~",
        ) as sf:
            print(f"Processing {simfile_path}")

            # It's very unlikely for the title property to be blank or missing.
            # This is mostly to satisfy type-checkers.
            current_title = sf.title or ""
            current_titletranslit = sf.titletranslit or ""

            if args.remove:
                def remove_starting_brackets(current_text: str) -> str:
                """
                If current_text has a bracketed number at the start of the text, remove it and return it
                Otherwise, return current_text unchanged. 
                """
                # Look for a number in brackets at the start of the text
                    if current_text.startswith("["):
                        open_bracket_index = current_text.find("[")
                        close_bracket_index = current_text.find("]")
                        bracketed_text = current_text[
                            open_bracket_index + 1 : close_bracket_index
                        ]
                        if bracketed_text.isnumeric():
                            # Remove the bracketed number from the text
                            return current_title[close_bracket_index + 1 :].lstrip(" ")
                    return current_title
                sf.title = remove_starting_brackets(sf.title)
                sf.titletranslit = remove_starting_brackets(sf.titletranslit)
            else:
                # Find the hardest chart (numerically) within a stepstype
                # and use it to prefix the title
                chart = hardest_chart(sf.charts, args.stepstype)

                # Skip this simfile if there were no charts for the stepstype.
                # Nothing will be written to disk in this case.
                if not chart:
                    raise simfile.CancelMutation

                # It's very unlikely for the meter property to be blank or missing.
                # This is mostly to satisfy type-checkers.
                meter = chart.meter or "1"

                # Put the meter at the start of the title,
                # filling in leading zeros per arguments
                sf.title = f"[{meter.zfill(args.digits)}] {current_title}"
                sf.titletranslit = f"[{meter.zfill(args.digits)}] {current_titletranslit}"


    def main(argv):
        # Parse command-line arguments
        args = argparser().parse_args(argv[1:], namespace=SortByDifficultyArgs())

        # Iterate over SimfileDirectory objects from the pack
        # so that we can easily get the .sm and/or .ssc paths
        for simfile_dir in simfile.dir.SimfilePack(args.pack).simfile_dirs():

            # Try to update whichever formats exist
            for simfile_path in [simfile_dir.sm_path, simfile_dir.ssc_path]:
                if simfile_path:
                    prefix_title_with_meter(simfile_path, args)


    if __name__ == "__main__":
        main(sys.argv)
