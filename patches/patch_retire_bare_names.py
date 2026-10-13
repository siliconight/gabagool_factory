r"""tools/factory_retire.py: a workspace a record names BARE is referenced too (2026-10-12).

The retire rule keeps a cold-run workspace that a file under docs/ (or a tool's tests) names, and it
matched one shape, `workspaces[/\]<name>-ws`. docs/findings/route_snag/ holds two scripts that never
write it:

  engine_ab.py       built its lots' names, `"cold-%d-ws" % run` for 9261, 9262 and 9263, and no
                     record named the first two in any form a scan could see. Every cold drive ends
                     by applying the retire; on 2026-10-12 the drives of 9263, 9264, 9265 and 9266
                     each removed one workspace, 0.9 GB (their driver.log -- which one each took is
                     inferred from the newest-four window, not logged), and cold-9261-ws and
                     cold-9262-ws went with 9265's and 9266's, after engine_ab.out.txt was written at
                     14:12. A name a script BUILDS is no name to any scan: engine_ab.py now writes its
                     three out (RUNS), and its docstring says the 9261 and 9262 arms cannot run
                     again. engine_ab.out.txt, their record, is untouched.
  engine_breadth.py  lists its sixteen lots under seven workspaces bare ("cold-9264-ws", ...,
                     "line-after-gas_block_001-ws") and joins the path with pathlib, so the slash
                     the pattern wants is never written. Those seven survive because other records
                     happen to name them as paths.

The scan now also counts the bare name of every directory under workspaces/, each on its own and as a
word (`\b<name>\b`). Only names on disk are asked for, so the fragment of a built name (`d-ws` in
`"cold-%d-ws"`) names nothing, and a name inside a longer token (`after-cold-9264-ws`) still names its
workspace -- which taking the token whole and then asking whether it is on disk
(`\b([A-Za-z0-9_.-]+-ws)\b`) would drop. The selftest names cold-0-ws bare in a finding's script, as
engine_breadth.py does, and fails without the scan.

MEASURED on the tree at be7dd38 (2,684 files, 55.3 MB; the instruments are in
_scratch/2026-10-12_retire_bare_names/). Before writing: of the 41 cold-N-ws on disk the path
pattern names 39, and the bare name as a word, the token form and a plain substring each name the
same 39; the two nothing names are the newest, cold-9266-ws and cold-9267-ws, kept by count. After
(compare_scans.py, HEAD's file and this one asked of one tree in one process): the dry run lists 0
items before and after; with the count rules off (keep=0, keep_pushed=0) both list cold-9266-ws and
cold-9267-ws and nothing else; the whole scan adds four names, none of them a cold-N-ws (ab-zoo-a-ws,
ab-zoo-b-ws, line-after-crossroads_9600-ws, line-after-gas_block_001-ws), and drops none; file by
file, 45 of the 163 files holding "-ws" name a workspace the path pattern does not see there. The scan
takes 0.64 s against 0.59 s (1.15 s before a "-ws" guard skipped the files holding none). So nothing
on today's tree is newly protected: this protects the next workspace a record names only bare.

REFUTED, and kept: patch_retire_scans_scripts.py (2026-10-11) let a built name pass -- "Those
scripts' runs are the newest ones, kept by count." The count was twelve. The pushed rule added the
next day keeps four and moves one workspace a cold run: engine_ab.out.txt was written at 14:12, and
the window had passed 9261 and 9262 by 9265's retire at 17:59 and 9266's at 19:24 (inferred from the
window; the log records only counts).

STILL INVISIBLE: fourteen other records build workspace names at runtime (`cold-%d-ws`,
`cold-$run-ws`, `cold-{n}-ws`). Three read 9261 and 9262 and lost them with engine_ab.py:
docs/findings/pole_line/lt_pole_ab.py, docs/findings/pole_line/poles_price.sh and
docs/cold_runs/cold_9262/pole_frames.sh. Every workspace the other eleven read that is still on disk
is named as a path somewhere today; two of them (cold_9198/findings_by_code.py,
grader_speed/blender_width_compare.py) take their runs from argv, and no scan can say what they read.

Anchored, both files pinned by hash, nothing written until every anchor in both has matched:

    python patches/patch_retire_bare_names.py && python tools/factory_retire.py --selftest
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "factory_retire.py"
ENGINE_AB = ROOT / "docs" / "findings" / "route_snag" / "engine_ab.py"

DOC_OLD = ("                 that still reads one keeps it). Regenerable from\n"
           "                 docs/cold_runs/cold_N/.\n")
DOC_NEW = ("                 that still reads one keeps it) -- by path, or by the bare name of a\n"
           "                 directory under workspaces/ standing as a word. A name a script\n"
           "                 BUILDS (`\"cold-%d-ws\" % run`) is no name, so a record writes its\n"
           "                 names out: on 2026-10-12 the retire took cold-9261-ws and\n"
           "                 cold-9262-ws from under docs/findings/route_snag/engine_ab.py that\n"
           "                 way. Regenerable from docs/cold_runs/cold_N/.\n")
FDOC_OLD = '    """Every `workspaces/<name>-ws` a doc or a test names."""\n'
FDOC_NEW = ('    """Every workspace a doc or a test names: `workspaces/<name>-ws`, or the bare\n'
            '    name of a directory under workspaces/ standing as a word."""\n')
BARE_OLD = '    dirs = [os.path.join(root, "docs"), os.path.join(root, "PIPELINE_ROADMAP.md")]\n'
BARE_NEW = ('    # a bare name is a name too: engine_breadth.py lists its lots as "cold-9264-ws",\n'
            '    # and a pathlib join (`F / "workspaces" / "cold-9241-ws"`) never writes the slash\n'
            '    # the pattern wants. Only names on disk are asked for, each on its own and as a\n'
            '    # word: `"cold-%d-ws"` names nothing, and `after-cold-9264-ws` still names 9264\n'
            '    # (a token taken whole and then looked up on disk would drop that one)\n'
            '    ws = os.path.join(root, "workspaces")\n'
            '    bare = {n: re.compile(r"\\b%s\\b" % re.escape(n)) for n in (os.listdir(ws) if os.path.isdir(ws) else ())\n'
            '            if n.endswith("-ws") and os.path.isdir(os.path.join(ws, n))}\n'
            + BARE_OLD)
TRY_OLD = ('            try:\n'
           '                names.update(pat.findall(open(p, encoding="utf-8", errors="replace").read()))\n'
           '            except OSError:\n'
           '                pass\n')
TRY_NEW = ('            try:\n'
           '                text = open(p, encoding="utf-8", errors="replace").read()\n'
           '            except OSError:\n'
           '                continue\n'
           '            names.update(pat.findall(text))\n'
           '            if "-ws" not in text:  # every name ends so; 163 of 2,684 files held one, 2026-10-12\n'
           '                continue\n'
           '            for n, rx in bare.items():\n'
           '                if n not in names and n in text and rx.search(text):\n'
           '                    names.add(n)\n')
TEST_OLD = ('    for n in range(1, 6):\n'
            '        os.makedirs(os.path.join(root, "workspaces", "cold-%d-ws" % n))\n')
TEST_NEW = ('    # a finding\'s script lists its lot bare and joins the path itself (engine_breadth.py)\n'
            '    os.makedirs(os.path.join(root, "docs", "findings", "ab"))\n'
            '    open(os.path.join(root, "docs", "findings", "ab", "ab.py"), "w").write(\n'
            '        \'LOTS = [("cold-0-ws", "deli_001", "seed_9191")]\\n\'\n'
            '        \'lf = F / "workspaces" / LOTS[0][0] / ".level_factory"\\n\')\n'
            '    for n in range(0, 6):\n'
            '        os.makedirs(os.path.join(root, "workspaces", "cold-%d-ws" % n))\n')
ASSERT_OLD = '    assert not any(w.startswith("cold-3-ws") for w in whys), "a referenced workspace stays"\n'
ASSERT_NEW = (ASSERT_OLD +
              '    assert not any(w.startswith("cold-0-ws") for w in whys), "a workspace a script names bare stays"\n')

EDOC_OLD = ('Copies go to `_scratch/engine_ab/` and are removed after. It prints what it measured and stops.\n'
            '"""\n')
EDOC_NEW = ('Copies go to `_scratch/engine_ab/` and are removed after. It prints what it measured and stops.\n'
            '\n'
            'CANNOT RUN AGAIN AS WRITTEN (2026-10-12). That day\'s cold-run retire steps removed\n'
            'workspaces/cold-9261-ws and workspaces/cold-9262-ws: this script built their names as\n'
            '`"cold-%d-ws" % run`, which `tools/factory_retire.py`\'s reference scan cannot see, and no\n'
            'other record named them. Its 9261 and 9262 arms have no lot to read; `engine_ab.out.txt` is\n'
            'their record, kept as measured. As written it stops at 9261\'s missing job report, and 9263\'s\n'
            'arm runs with RUNS cut to that one. RUNS writes the names out so the scan sees what is left.\n'
            '"""\n')
ECONST_OLD = "CORNER = (-66.35, -4.94)          # plan: the deli register counter's south-west corner pin\n"
ECONST_NEW = (ECONST_OLD +
              "#: (run, its workspace), the names written out: `tools/factory_retire.py` keeps a workspace\n"
              "#: a record names, and `\"cold-%d-ws\" % run` named none (see above)\n"
              "RUNS = ((9261, \"cold-9261-ws\"), (9262, \"cold-9262-ws\"), (9263, \"cold-9263-ws\"))\n")
ELOOP_OLD = ('    for run in (9261, 9262, 9263):\n'
             '        ws = F / "workspaces" / ("cold-%d-ws" % run) / ".level_factory"\n')
ELOOP_NEW = ('    for run, name in RUNS:\n'
             '        ws = F / "workspaces" / name / ".level_factory"\n')

#: (file, sha256[:16] of the file this patch read, a marker only the patched file holds, edits)
FILES = (
    (TOOL, "87b135b8eb6f8aea", "bare = {n: re.compile(", (
        (DOC_OLD, DOC_NEW, "the docstring's rule"),
        (FDOC_OLD, FDOC_NEW, "the scan's docstring"),
        (BARE_OLD, BARE_NEW, "the names on disk"),
        (TRY_OLD, TRY_NEW, "the scan's read"),
        (TEST_OLD, TEST_NEW, "the selftest's workspaces"),
        (ASSERT_OLD, ASSERT_NEW, "the selftest's assertion"))),
    (ENGINE_AB, "ec97937bf93cc2c8", "for run, name in RUNS:", (
        (EDOC_OLD, EDOC_NEW, "engine_ab's docstring"),
        (ECONST_OLD, ECONST_NEW, "engine_ab's constants"),
        (ELOOP_OLD, ELOOP_NEW, "engine_ab's loop"))),
)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def build():
    """``{path: bytes}`` for both files, every anchor matched; nothing is written here."""
    staged = {}
    for path, sha, marker, edits in FILES:
        raw = path.read_bytes()
        assert b"\r\n" not in raw, "%s is LF" % path.name
        text = raw.decode("utf-8")
        assert marker not in text, "%s: already applied" % path.name
        got = hashlib.sha256(raw).hexdigest()[:16]
        assert got == sha, ("%s is not the file this patch read" % path.name, got)
        for old, new, what in edits:
            text = _once(text, old, new, what)
        staged[path] = text.encode("utf-8")
    return staged


def main():
    staged = build()
    for path, data in staged.items():
        path.write_bytes(data)
    print("factory_retire.py: a workspace a record names bare is referenced; engine_ab.py writes its names out")


if __name__ == "__main__":
    sys.exit(main())
