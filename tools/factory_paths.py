"""Where the factory is, asked once, so six tools cannot disagree about it.

WHY THIS EXISTS. Every checker and harness computed its own root as

    ROOT = pathlib.Path(__file__).resolve().parent

which answers "the directory I am in". That was the same answer as "the factory
root" only because nothing had ever moved. It stops being the same answer the
moment a tool is relocated -- and it stops SILENTLY. check_all.py's gd_files()
would scan its own directory, find four .gd files instead of 104, and report
`gdscript  clean  0`. A guardrail that narrows its own scope while still saying
clean is worse than no guardrail, because it costs you the attention you would
otherwise have spent looking.

WHY A MARKER RATHER THAN A DEPTH. `parent.parent` encodes how deeply a tool
happens to sit today, so it breaks the next time the layout changes and it
breaks the same silent way. `factory.manifest.json` is what makes a directory
the factory root -- it is the coordination data the root repo exists to track --
so walking up to it is a derivation rather than a guess. Tools work at the root,
in tools/, or nested deeper later, with nobody revisiting this.

WHY A SHARED MODULE RATHER THAN SIX COPIES. rebuild_buildings.py already imports
check_freshness instead of restating the hash rule, with the reason written
above the import: two copies of a rule drift, and a drifted second copy is the
recurring defect of this toolchain. The same argument applies here. It also buys
a loud failure: a checker copied somewhere without this module raises
ImportError instead of quietly checking the wrong tree.
"""
import pathlib

#: The file that marks the factory root. Not a convention picked for this
#: module -- it is the coordination manifest the root repo exists to hold, and
#: the .gitignore there ignores every tool repo precisely because this file and
#: its siblings are the only thing that directory owns.
MARKER = "factory.manifest.json"


def factory_root(start=None):
    """The directory holding factory.manifest.json, at or above `start`.

    `start` defaults to this module's own location, which is correct for every
    caller that sits beside it. Pass a path to resolve from somewhere else.
    """
    here = pathlib.Path(start or __file__).resolve()
    for d in (here, *here.parents):
        if (d / MARKER).is_file():
            return d
    raise SystemExit(
        f"no {MARKER} at or above {here}.\n"
        f"  That file marks the factory root. Either this tool has been copied\n"
        f"  outside the factory, or the manifest is missing from the root.\n"
        f"  Nothing was checked -- and a check that did not run is not a check\n"
        f"  that passed.")


def script_dir():
    """The directory the CALLING file sits in -- siblings, not the tree.

    Deliberately separate from factory_root(). These were one answer while
    everything lived at the root; conflating them again is the defect this
    module exists to prevent.
    """
    return pathlib.Path(__file__).resolve().parent
