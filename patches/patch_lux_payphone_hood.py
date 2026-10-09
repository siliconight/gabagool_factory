"""Lux 0.70.0: the payphone's hood lamp -- a `payphone_hood` row for the marker
Zoo 1.89.0 hangs under a payphone's roof (roadmap 210). Cold run 9212 found
the booth a silhouette at midnight; the walker, 2026-10-09: "yes light it".

One tube's downlight, cool fluorescent, its range a ceiling lamp's for the
drop the marker carries and its energy putting PAYPHONE_HOOD_LEVEL --
REFERENCE_POOL x 0.75, set from frames of a lamp stood live in cold run 9212's
package (`docs/findings/payphone_light/`) -- on the ground under it. Not
preset scaled: a street fixture.

Anchored edits on `lux_light_loader.gd` (every anchor once; refuses on a
miss): the constants block (`lux_payphone_hood/consts.gd.txt`) after
`STREETLIGHT_LEVEL`, the `"payphone_hood"` branch (`lux_payphone_hood/
branch.gd.txt`) before `"streetlight"`; `tools/payphone_hood_selftest.gd`
copied from `lux_payphone_hood/`, refused if present; CHANGELOG and VERSION
from `lux_payphone_hood/CHANGELOG_0.70.0.md`.

    python patch_lux_payphone_hood.py
    LUX_ROOT=<copy> python patch_lux_payphone_hood.py [--draft]

`--draft` lets a changelog still carrying RESULT_ placeholders through, and
only against a LUX_ROOT copy: the selftests' results are measured there first.
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_payphone_hood"
DRAFT = "--draft" in sys.argv


def main():
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    v = (LUX / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lux 0.69.0", v
    consts = (SRC / "consts.gd.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    branch = (SRC / "branch.gd.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert consts.startswith("## THE PAYPHONE'S HOOD LAMP (0.70.0") and branch.startswith('\t\t"payphone_hood":\n')
    entry = (SRC / "CHANGELOG_0.70.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert DRAFT or "RESULT_" not in entry, "the changelog still carries an unfilled result"
    p = LUX / "addons" / "lux" / "runtime" / "lux_light_loader.gd"
    raw = p.read_bytes()
    assert b"\r\n" not in raw, "the loader is LF; it has CRLF now"
    s = raw.decode("utf-8")
    assert "payphone" not in s, "already applied"
    a = "const STREETLIGHT_LEVEL := REFERENCE_POOL * 0.75\n"
    assert s.count(a) == 1, s.count(a)
    s = s.replace(a, a + consts)
    b = '\t\t"streetlight":\n'
    assert s.count(b) == 1, s.count(b)
    s = s.replace(b, branch + b)
    t = LUX / "tools" / "payphone_hood_selftest.gd"
    assert not t.exists(), t
    cl = LUX / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.70.0]" not in d
    head = b"# Changelog\n\n"
    assert d.startswith(head)
    # every check passed: now write
    p.write_bytes(s.encode("utf-8"))
    t.write_bytes((SRC / "payphone_hood_selftest.gd").read_bytes().replace(b"\r\n", b"\n"))
    cl.write_bytes(head + entry.encode("utf-8") + d[len(head):])
    (LUX / "VERSION").write_bytes(b"Lux 0.70.0")
    print("0.69.0 -> 0.70.0")


if __name__ == "__main__":
    main()
