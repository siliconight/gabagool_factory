"""tools/dressing_in_nav: read merged dressing, and never report clean on nothing.

Zoo 1.68.0 merges a building's covers one side per material: the nodes are
`Cover<side>_<material>` (or `Cover<side>_<kind>` for a cover alone in its
group), not `Cover_<kind>`. With its default prefix `Cover_` this tool would
match none of them, print a TOTAL of 0 and "No cover stands in walkable
space" -- a check that cannot fail. So:

  * the prefix default is `Cover`, matching both spellings;
  * a run that matched NO cover is NOT MEASURED, exit 2, before any verdict;
  * the docstring says what one merged node is, and how to get per-cover
    precision back (Zoo's `--no-merge-parts`, the one-build control).

Anchored edits (every anchor once; refuses on a miss).

    python patch_tools_dressing_nav_merged.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = ROOT / "tools" / "dressing_in_nav.py"
GD = ROOT / "tools" / "dressing_in_nav.gd"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


DOC_OLD = '''WHAT IT CANNOT TELL YOU. Firing lines.'''
DOC_NEW = '''MERGED DRESSING (Zoo >= 1.68.0). Zoo merges a building's covers one SIDE per
material, so a node is no longer one cover: it is every cover on that side in
that material, named `Cover<side>_<material>` (a cover alone in its group keeps
`Cover<side>_<kind>`). Its box runs from the wall to the proudest cover on it
and from the curb to the gutter, so a finding names a side, not a cover, and
the step-to-head window no longer separates a gutter at 9 m from a base
course at the foot inside one node. For per-cover precision build the
dressing with Zoo's `--no-merge-parts` -- the one-build control -- and walk
that. The default prefix `Cover` matches both spellings, and a run that
matched no cover at all is NOT MEASURED rather than clean.

WHAT IT CANNOT TELL YOU. Firing lines.'''

PROBE_OLD = '''          step_clear=0.15, body_height=1.8, prefix="Cover_", backing=0.0,'''
PROBE_NEW = '''          step_clear=0.15, body_height=1.8, prefix="Cover", backing=0.0,'''

ARG_OLD = '''    ap.add_argument("--prefix", default="Cover_",
                    help="node-name prefix of the geometry to test; "
                         "'WallPack_' checks the light fixtures instead")'''
ARG_NEW = '''    ap.add_argument("--prefix", default="Cover",
                    help="node-name prefix of the geometry to test (default "
                         "'Cover': Zoo's merged `Cover<side>_*` and the older "
                         "`Cover_<kind>`); 'WallPack_' checks the light "
                         "fixtures instead")'''

MAIN_OLD = '''    except ProbeFailed as exc:
        sys.stderr.write("[dressing_in_nav] NOT MEASURED: %s\\n" % exc)
        return 2
    if args.json:'''
MAIN_NEW = '''    except ProbeFailed as exc:
        sys.stderr.write("[dressing_in_nav] NOT MEASURED: %s\\n" % exc)
        return 2
    # NOTHING MATCHED IS NOT CLEAN. A prefix that names no node -- the old
    # `Cover_` against Zoo >= 1.68.0's merged `Cover<side>_*` -- counts 0
    # covers and 0 offenders, and the report below would call that clear.
    if "error" not in r and not r.get("covers"):
        sys.stderr.write("[dressing_in_nav] NOT MEASURED: no MeshInstance3D "
                         "named %r* in the scene\\n" % args.prefix)
        return 2
    if args.json:'''

GD_OLD = '''		"dressing_nav/prefix", "Cover_"))'''
GD_NEW = '''		"dressing_nav/prefix", "Cover"))'''


def main():
    _edit(PY, [(DOC_OLD, DOC_NEW), (PROBE_OLD, PROBE_NEW), (ARG_OLD, ARG_NEW), (MAIN_OLD, MAIN_NEW)])
    _edit(GD, [(GD_OLD, GD_NEW)])
    print("applied: dressing_in_nav reads merged dressing and refuses an empty match")


if __name__ == "__main__":
    main()
