"""tools/factory_retire.py: a workspace a record's SCRIPT names is referenced too.

The retire rule keeps a cold-run workspace that a file under docs/ (or a tool's tests) names, and it
read only .md, .py, .txt and .json for the name. A record's frame script is .sh: cold run 9240's
`roof_frames.sh` names `workspaces/cold-9226-ws` as its control package, and the dry run of
2026-10-11 listed cold-9226-ws as "beyond the newest 12, unreferenced" -- an --apply would have
deleted the package that script re-shoots. The scan reads the scripts a record carries as well
(.sh, .ps1, .cmd, .bat, .gd), and the selftest names a workspace from a .sh, which fails without it.

A path a script builds from a loop variable (`workspaces/cold-$run-ws`) is still invisible to a
name scan; this does not claim otherwise. Those scripts' runs are the newest ones, kept by count.

Anchored, the file pinned by hash, nothing written on a miss:

    python patches/patch_retire_scans_scripts.py && python tools/factory_retire.py --selftest
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "factory_retire.py"
SHA = "524127a7dabd0247"

EXT_OLD = '            if os.path.splitext(p)[1].lower() not in (".md", ".py", ".txt", ".json"):\n'
EXT_NEW = ("            # a record's scripts name workspaces too: 9240's roof_frames.sh names\n"
           "            # its control package, and a scan of .md/.py/.txt/.json missed it\n"
           "            if os.path.splitext(p)[1].lower() not in _SCANNED:\n")
CONST_OLD = "KEEP_WORKSPACES = 12\n"
CONST_NEW = ("KEEP_WORKSPACES = 12\n"
             "#: the files a reference scan reads: records, and the scripts a record carries\n"
             "_SCANNED = (\".md\", \".py\", \".txt\", \".json\", \".sh\", \".ps1\", \".cmd\", \".bat\", \".gd\")\n")
DOC_OLD = "                 a file under docs/ or a tool repo's tests names it (a finding\n"
DOC_NEW = "                 a file under docs/ -- a record or its script -- or a tool repo's tests names it (a finding\n"
TEST_OLD = ('    for n in range(1, 6):\n'
            '        os.makedirs(os.path.join(root, "workspaces", "cold-%d-ws" % n))\n')
TEST_NEW = ('    # a record\'s script names cold-2-ws as its control package\n'
            '    os.makedirs(os.path.join(root, "docs", "cold_runs", "cold_6"))\n'
            '    open(os.path.join(root, "docs", "cold_runs", "cold_6", "frames.sh"), "w").write(\n'
            '        \'PKG_C="workspaces/cold-2-ws/.level_factory/exports/LF_x.portable-godot"\\n\')\n'
            + TEST_OLD)
ASSERT_OLD = '    assert "cold-1-ws: cold-run workspace" in whys and "cold-2-ws: cold-run workspace" in whys, whys\n'
ASSERT_NEW = ('    assert "cold-1-ws: cold-run workspace" in whys, whys\n'
              '    assert not any(w.startswith("cold-2-ws") for w in whys), "a workspace a script names stays"\n')


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def main():
    raw = TOOL.read_bytes()
    assert b"\r\n" not in raw, "factory_retire.py is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA, ("factory_retire.py is not the file this patch read", got)
    text = raw.decode("utf-8")
    assert "_SCANNED" not in text, "already applied"
    text = _once(text, CONST_OLD, CONST_NEW, "the constants")
    text = _once(text, EXT_OLD, EXT_NEW, "the scan's extensions")
    text = _once(text, DOC_OLD, DOC_NEW, "the docstring's rule")
    text = _once(text, TEST_OLD, TEST_NEW, "the selftest's workspaces")
    text = _once(text, ASSERT_OLD, ASSERT_NEW, "the selftest's assertion")
    TOOL.write_bytes(text.encode("utf-8"))
    print("factory_retire.py: a record's scripts are scanned for workspace names")


if __name__ == "__main__":
    sys.exit(main())
