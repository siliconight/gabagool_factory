r"""docs/: a workspace a record's script reads is named in full, never built (2026-10-13).

tools/factory_retire.py keeps a cold-run workspace while a record under docs/ (or a tool's tests)
names it -- as `workspaces/<name>`, or since patch_retire_bare_names.py as the bare name of a
directory on disk. A name a script BUILDS when it runs (`cold-$run-ws`, `"cold-%s-ws" % n`,
`f"cold-{n}-ws"`) names nothing, and every cold drive ends by applying the retire, so a workspace
only a built name refers to goes as soon as the count rules let it: on 2026-10-12 that took
cold-9261-ws and cold-9262-ws from engine_ab.py, lt_pole_ab.py, poles_price.sh and 9262's frames.

MEASURED before writing, on the tree at 654e9c0 (_scratch/2026-10-13_literal_workspaces/
built_names.py): 30 lines in 27 files build a cold-run workspace's name. Five are not readers of a
fixed set -- two lines of prose (the roadmap's account of cold_drive.sh, engine_ab.py's own note) and
three censuses that glob `cold-*-ws` and read whatever is on disk (enemy_inside_an_empty/
unreachable_spawns.py, rear_lane/rear_census.py, walkable_city/route_census.py); writing those out
would change what they read, so they are left. The other 22 are this patch. The template is a frame
or price script's `for run in A B` over `pkg="workspaces/cold-$run-ws/..."`, copied from run to run:
14 such files on 2026-10-12, 22 on 2026-10-13. The dry run listed 0 items; 50 of the 57 cold-run
workspaces on disk were named, and the seven that were not are the breadth sweep's, cold runs 9278
to 9284, read by sweep_table.py through a built name and kept by count alone.

  15 loops in 14 frame and price scripts  `for ws in cold-A-ws cold-B-ws`, the run taken back off
                    the name (`run=${ws#cold-}; run=${run%-ws}`), so every line after the loop's head
                    reads `$run` as before; poles_price.sh's `control:9261` pairs carry the name
  resume_from_export.sh   WS and the findings' two workspaces written out, PREV gone with them
  lt_pole_ab.py, rewalk.py   a literal table, and `_ws(n)` and the loop reading it
  findings_by_code.py, blender_width_compare.py, rebake_probe.py   take their runs from argv or the
                    environment; the interface stays, and the docstring or comment names the runs
                    their own record used (9198 against 9197; 9249, 9250, 9251; 9242 and 9243)
  sweep_table.py    argv too, and the exception, which says so: naming its seven runs' workspaces
                    would keep 4.8 GB nothing else keeps, on a disk 95% full; its table is in its
                    README, and without a workspace its grade cell reads "(no Laser Tag report)".
                    Left to the retire; the walker's to change.

Gone, each said in its own script: cold-9261-ws and cold-9262-ws (pole_frames.sh, poles_price.sh,
lt_pole_ab.py: CANNOT RUN AGAIN AS WRITTEN), cold-9203-ws (resume_from_export.sh), cold-9197-ws and
cold-9198-ws (findings_by_code.py), cold-9249-ws and cold-9250-ws (blender_width_compare.py), and ten
of rewalk.py's twelve.

MEASURED after (equivalence.py and compare_records.py, beside built_names.py): the patch run on HEAD's
22 copies gives the files on disk byte for byte. Each loop's old and new text, run in bash with cp, rm
and mkdir stubbed, leaves $run and $pkg (poles_price.sh's pairs: $name and $pkg) and the stubs' lines
the same, 16 of 16; every script parses (bash -n, compile()); the four .py files whose edits are prose
are the same AST without their docstrings; resume_from_export.sh opens the same two paths, and
lt_pole_ab.py's _ws and rewalk.py's RUNS give the same workspaces. File by file, each patched record
now names the workspaces it reads (four frame and price scripts already named theirs as paths and add
none; sweep_table.py adds none by choice). The whole tree adds four names, none on disk (cold-9197-ws,
cold-9198-ws, cold-9249-ws, cold-9250-ws), and nobody else's change is among them. The dry run lists
0 items before and after, and with the count rules off both list the sweep's seven and nothing else.
Names still built: 10 lines in 9 files -- the two prose lines, the three globs, the four interfaces.
So no workspace on disk is newly protected: each one these scripts read was already named as a path
somewhere, and is now named by the script that reads it.

Anchored: all 22 files pinned by hash and LF, every anchor matched exactly once, nothing written until
every file has staged.

    python patches/patch_records_literal_workspaces.py
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

NAMED = "# the workspaces named in full, so tools/factory_retire.py sees which ones this reads\n"
B_LF = '  pkg="workspaces/<WS>/.level_factory/exports/LF_restaurant_row_001.portable-godot"\n'
B_PKG = '  pkg="workspaces/<WS>/.level_factory/exports/$PKG"\n'
B_WALK = ('  rm -rf "$SCR/walk"\n'
          '  mkdir -p "$SCR/walk"\n'
          '  cp -r "workspaces/<WS>/.level_factory/exports/$PKG" "$SCR/walk/$PKG" || exit 1\n')


def _loop(runs, body, what):
    """A script's loop over runs, as (old, new, what). The new loop walks the workspaces' full
    names and takes the run back off each, so the lines after its head read `$run` as before."""
    old = "for run in %s; do\n" % " ".join(runs) + body.replace("<WS>", "cold-$run-ws")
    new = (NAMED + "for ws in %s; do\n" % " ".join("cold-%s-ws" % r for r in runs)
           + "  run=${ws#cold-}; run=${run%-ws}\n" + body.replace("<WS>", "$ws"))
    return old, new, what


GONE_9261 = ("# CANNOT RUN AGAIN AS WRITTEN (2026-10-13): workspaces/cold-9261-ws and workspaces/cold-9262-ws were\n"
             "# retired on 2026-10-12, when this loop built their names and nothing named them in a form\n"
             "# tools/factory_retire.py could see. %s is the record, kept as %s.\n")

FINDINGS_BY_CODE = (
    ("Reads `workspaces/cold-<N>-ws/.level_factory/validation/<mission>.json`, the\n"
     "file the driver's findings step counts. Prints what it found and stops.\n"
     '"""\n',
     "Reads `workspaces/cold-<N>-ws/.level_factory/validation/<mission>.json`, the\n"
     "file the driver's findings step counts. Prints what it found and stops.\n"
     "\n"
     "This record's comparison (\"Findings against 9197\", NOTES.md) is\n"
     "`findings_by_code.py 9198 9197 bank_block_001`: it read workspaces/cold-9198-ws\n"
     "and workspaces/cold-9197-ws, named in full here so tools/factory_retire.py sees\n"
     "them. Neither is on disk on 2026-10-13.\n"
     '"""\n',
     "the docstring"),
)
RESUME_9214 = (
    ("# Cold run 9214 resumed at its export leg after a recorded --retry: the driver's\n"
     "# own commands from `== export` on (tools/cold_drive/cold_drive.sh), unchanged.\n"
     "set -u\n"
     "N=9214; PREV=9203\n",
     "# Cold run 9214 resumed at its export leg after a recorded --retry: the driver's\n"
     "# own commands from `== export` on (tools/cold_drive/cold_drive.sh), unchanged but\n"
     "# for the workspaces, named in full (2026-10-13) so tools/factory_retire.py sees\n"
     "# what this reads: cold-9214-ws, and cold-9203-ws for the findings' baseline --\n"
     "# not on disk on 2026-10-13, so its count would read 0.\n"
     "set -u\n"
     "N=9214\n",
     "the header and the runs"),
    ("WS=workspaces/cold-$N-ws\n", "WS=workspaces/cold-9214-ws\n", "the workspace"),
    ("python - \"$N\" \"$PREV\" \"$M\" <<'PY'\n", "python - cold-9214-ws cold-9203-ws \"$M\" <<'PY'\n",
     "the findings' arguments"),
    ('    p = f"workspaces/cold-{n}-ws/.level_factory/validation/{sys.argv[3]}.json"\n',
     '    p = f"workspaces/{n}/.level_factory/validation/{sys.argv[3]}.json"\n',
     "the findings' path"),
)
REBAKE_9242 = (
    ("#: REBAKE_RUN names another run of the same lot to copy (9243 re-ran 9242 on Level Factory 0.178.5)\n",
     "#: REBAKE_RUN names another run of the same lot to copy (9243 re-ran 9242 on Level Factory 0.178.5):\n"
     "#: workspaces/cold-9242-ws by default, workspaces/cold-9243-ws with REBAKE_RUN=9243 -- named in full\n"
     "#: so tools/factory_retire.py sees what this record baked; the variable still takes any run\n",
     "REBAKE_RUN's comment"),
)
POLE_FRAMES_9262 = (
    ("#     bash docs/cold_runs/cold_9262/pole_frames.sh\n",
     "#     bash docs/cold_runs/cold_9262/pole_frames.sh\n#\n" + GONE_9261 % ("poles.png", "shot"),
     "the header"),
    _loop(("9261", "9262"), B_LF, "the frames' loop"),
)
POLES_PRICE = (
    ("#     bash docs/findings/pole_line/poles_price.sh\n",
     "#     bash docs/findings/pole_line/poles_price.sh\n#\n" + GONE_9261 % ("price_9261_9262/", "measured"),
     "the header"),
    ("for pair in control:9261 subject:9262; do\n"
     '  name="${pair%%:*}"; run="${pair##*:}"\n'
     '  pkg="workspaces/cold-$run-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"\n',
     NAMED +
     "for pair in control:cold-9261-ws subject:cold-9262-ws; do\n"
     '  name="${pair%%:*}"; ws="${pair##*:}"\n'
     '  pkg="workspaces/$ws/.level_factory/exports/LF_restaurant_row_001.portable-godot"\n',
     "the pairs"),
)
SWEEP_TABLE = (
    ("A run whose log lacks a field says so in its cell -- never a blank and never a zero. Prints the table and stops.\n"
     '"""\n',
     "A run whose log lacks a field says so in its cell -- never a blank and never a zero. Prints the table and stops.\n"
     "\n"
     "WHAT IT KEEPS (2026-10-13). The sweep ran it on cold runs 9278 to 9284 (README.md's table). It reads each\n"
     "run's workspace for the grade and stuck cells alone and names none of the seven in full, so\n"
     "`tools/factory_retire.py` keeps them by count only: once one is retired its row reads \"(no Laser Tag report)\"\n"
     "there, and README.md's table stays the record. Writing the seven names out here would keep them -- 4.8 GB on\n"
     "a disk 95% full on 2026-10-13 -- so they are left to the retire.\n"
     '"""\n',
     "the docstring"),
)
BLENDER_WIDTH = (
    ("    python docs/findings/grader_speed/blender_width_compare.py 9249 9250 9251\n"
     '"""\n',
     "    python docs/findings/grader_speed/blender_width_compare.py 9249 9250 9251\n"
     "\n"
     "That run read workspaces/cold-9249-ws, workspaces/cold-9250-ws and workspaces/cold-9251-ws, named in\n"
     "full here so tools/factory_retire.py sees them. On 2026-10-13 only cold-9251-ws is on disk.\n"
     '"""\n',
     "the docstring"),
)
LT_POLE_AB = (
    ("    python docs/findings/pole_line/lt_pole_ab.py\n"
     '"""\n',
     "    python docs/findings/pole_line/lt_pole_ab.py\n"
     "\n"
     "CANNOT RUN AGAIN AS WRITTEN (2026-10-13): workspaces/cold-9261-ws and workspaces/cold-9262-ws were\n"
     "retired on 2026-10-12, when `_ws` built their names and nothing named them in a form\n"
     "tools/factory_retire.py could see, so every arm has no project to copy. `lt_pole_ab.out.txt` is the\n"
     "record, kept as measured.\n"
     '"""\n',
     "the docstring"),
    ('X = F / "_scratch" / "pole_line" / "lt_pole_ab"\n',
     'X = F / "_scratch" / "pole_line" / "lt_pole_ab"\n'
     "#: the runs' workspaces, named in full so tools/factory_retire.py sees what this reads\n"
     'WORKSPACES = {9261: "cold-9261-ws", 9262: "cold-9262-ws"}\n',
     "the constants"),
    ('    return F / "workspaces" / f"cold-{n}-ws" / ".level_factory"\n',
     '    return F / "workspaces" / WORKSPACES[n] / ".level_factory"\n',
     "_ws"),
)
REWALK = (
    ("occurrence, `<run>_<mission>_<seed>`.\n",
     "occurrence, `<run>_<mission>_<seed>`.\n"
     "On 2026-10-13 only cold-9194-ws and cold-9204-ws of the twelve are on disk: a\n"
     "re-walk finds the others' staging folders absent, walks what is left and labels\n"
     "it by those two runs, so its labels need not match the results kept here.\n",
     "the docstring"),
    ("RUNS = range(9193, 9205)\n",
     "#: (run, its workspace), named in full so tools/factory_retire.py sees what this reads\n"
     'RUNS = ((9193, "cold-9193-ws"), (9194, "cold-9194-ws"), (9195, "cold-9195-ws"), (9196, "cold-9196-ws"),\n'
     '        (9197, "cold-9197-ws"), (9198, "cold-9198-ws"), (9199, "cold-9199-ws"), (9200, "cold-9200-ws"),\n'
     '        (9201, "cold-9201-ws"), (9202, "cold-9202-ws"), (9203, "cold-9203-ws"), (9204, "cold-9204-ws"))\n',
     "RUNS"),
    ("    for n in RUNS:\n"
     '        staging = ROOT / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "staging"\n',
     "    for n, ws in RUNS:\n"
     '        staging = ROOT / "workspaces" / ws / ".level_factory" / "staging"\n',
     "the walks' loop"),
)

#: (file, sha256[:16] of the file this patch read, a marker only the patched file holds, edits)
FILES = (
    ("docs/cold_runs/cold_9198/findings_by_code.py", "086a896e5baefa3e", "This record's comparison", FINDINGS_BY_CODE),
    ("docs/cold_runs/cold_9214/resume_from_export.sh", "6a40b529283a2f3e", "WS=workspaces/cold-9214-ws", RESUME_9214),
    ("docs/cold_runs/cold_9241/fixture_frames.sh", "46bfa8468282a430", "for ws in cold-",
     (_loop(("9238", "9239", "9241"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9242/pendant_frames.sh", "0ac1dbc67825c7c4", "for ws in cold-",
     (_loop(("9241", "9242"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9242/rebake_probe.py", "dc822dfa6e66cc84", "workspaces/cold-9242-ws by default", REBAKE_9242),
    ("docs/cold_runs/cold_9243/pendant_frames.sh", "228833f1397f642e", "for ws in cold-",
     (_loop(("9241", "9243"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9244/pendant_frames.sh", "7840c5b3b8d0041a", "for ws in cold-",
     (_loop(("9241", "9244"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9245/roof_frames.sh", "33fa181671ead6bc", "for ws in cold-",
     (_loop(("9244", "9245"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9248/roof_frames.sh", "329d433e2382afe8", "for ws in cold-",
     (_loop(("9245", "9248"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9262/pole_frames.sh", "bd093da886c7ed8c", "for ws in cold-", POLE_FRAMES_9262),
    ("docs/cold_runs/cold_9268/roof_frames.sh", "9eafc4528ce3f376", "for ws in cold-",
     (_loop(("9267", "9268"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9269/drains.sh", "91de04692e67abe3", "for ws in cold-",
     (_loop(("9268", "9269"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9270/drains.sh", "b6924a6521e6c6a1", "for ws in cold-",
     (_loop(("9269", "9270"), B_LF, "the frames' loop"),)),
    ("docs/cold_runs/cold_9271/stoops.sh", "1af5fcf7ee05e4e3", "for ws in cold-",
     (_loop(("9270", "9271"), B_PKG, "the frames' loop"),)),
    ("docs/cold_runs/cold_9272/stoops.sh", "1a9890c275bbc7db", "for ws in cold-",
     (_loop(("9271", "9272"), B_PKG, "the frames' loop"),)),
    ("docs/cold_runs/cold_9273/railings.sh", "ef85c785ce3b5e84", "for ws in cold-",
     (_loop(("9272", "9273"), B_WALK, "the walk's loop"),
      _loop(("9272", "9273"), B_PKG, "the frames' loop"))),
    ("docs/cold_runs/cold_9274/atlas.sh", "cb62cacf0f9f5001", "for ws in cold-",
     (_loop(("9273", "9274"), B_PKG, "the frames' loop"),)),
    ("docs/findings/breadth_sweep_2026-10-13/sweep_table.py", "fa38710a7756bd36", "WHAT IT KEEPS (2026-10-13)", SWEEP_TABLE),
    ("docs/findings/grader_speed/blender_width_compare.py", "66dbbc11328c4d14", "That run read workspaces/cold-9249-ws",
     BLENDER_WIDTH),
    ("docs/findings/pole_line/lt_pole_ab.py", "68e305f6e2a4fd16", "WORKSPACES = {", LT_POLE_AB),
    ("docs/findings/pole_line/poles_price.sh", "ae050f1623f06fbe", "control:cold-9261-ws", POLES_PRICE),
    ("docs/findings/walktest_crew_body/rewalk.py", "648d0d9591bd8ba5", '(9193, "cold-9193-ws")', REWALK),
)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def build(root=ROOT):
    """``{path: bytes}`` for every file, every anchor matched; nothing is written here."""
    staged = {}
    for rel, sha, marker, edits in FILES:
        path = root / rel
        raw = path.read_bytes()
        assert b"\r\n" not in raw, "%s is LF" % rel
        text = raw.decode("utf-8")
        assert marker not in text, "%s: already applied" % rel
        got = hashlib.sha256(raw).hexdigest()[:16]
        assert got == sha, ("%s is not the file this patch read" % rel, got)
        for old, new, what in edits:
            text = _once(text, old, new, "%s: %s" % (rel, what))
        staged[path] = text.encode("utf-8")
    return staged


def main():
    staged = build()
    for path, data in staged.items():
        path.write_bytes(data)
    print("%d records name their workspaces in full" % len(staged))


if __name__ == "__main__":
    sys.exit(main())
