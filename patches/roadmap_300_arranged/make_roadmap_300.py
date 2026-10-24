"""Write patches/patch_roadmap_300_arranged.py: roadmap 300's status replaced (the block above its heading, embedded
exactly, the earlier status kept) -- NARROWED, a hall that names nothing else is a hallway and a room's seeded pieces
stand on a lattice, with a census that measures it. Copied from `roadmap_296_298_drawings/make_roadmap_296_298.py`.
Refuses if the name is taken.

    python patches/roadmap_300_arranged/make_roadmap_300.py
"""
import pathlib
import re
import subprocess

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_300_arranged.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t


def commit(repo, subject_start):
    out = subprocess.run(["git", "-C", str(F / repo), "log", "-30", "--format=%h %s"], capture_output=True,
                         text=True, check=True).stdout.splitlines()
    hits = [l.split(" ", 1)[0] for l in out if l.split(" ", 1)[1].startswith(subject_start)]
    assert len(hits) == 1, (repo, subject_start, hits)
    return hits[0]


DC3 = commit("deli_counter", "0.263.0: ")
DC4 = commit("deli_counter", "0.264.0: ")


def status_of(n):
    m = list(re.finditer(r"(?m)^\*\*%d\. " % n, t))
    assert len(m) == 1, n
    h = m[0].start()
    s = t.rindex("\n\n", 0, h - 2) + 2
    block = t[s:h - 2]
    assert block.startswith("*STATUS: ") and block.endswith("*") and "\n" not in block, n
    heading = t[h - 2:t.index("\n", h)]
    assert t.count(heading) == 1, n
    return heading, block


H300, OLD300 = status_of(300)
assert OLD300.startswith("*STATUS: OPEN 2026-10-23 -- the walker's walk of cold run 9383, finding 3"), OLD300[:100]
NEW300 = (
    "*STATUS: NARROWED 2026-10-23 -- the walker: \"do the full correct fix, allowing us to have nuance and flavor, but "
    "not look like random assortment\". Two steps shipped. Deli Counter 0.263.0 (" + DC3 + ", "
    "`patches/patch_dc_hallway.py`): a hall that names nothing else is a hallway, furnished on its walls -- 40 rooms "
    "in 38 specs lost their gallery sets, deli_a03's landing among them; routes over 10 % 26 -> 23 pairs. Deli Counter "
    "0.264.0 (" + DC4 + ", `patches/patch_dc_seed_lines.py`): `arrangement.py`, the first instrument for \"reads as "
    "designed\" (roadmap 18) -- each piece's visible reason, or loose -- and a room's seeded pieces on a lattice, one "
    "line or rows, one kind a row, each cleared by its own footprint and off the room's routes; seeded pieces loose "
    "95.4 -> 13.8 % in fresh presets, which is what Level Factory builds a mission's shell from, 71.8 -> 3.8 % in the "
    "library; routes no worse. Cold run 9386 (0 interventions): the landing's frames before and after "
    "(`docs/findings/walk_2026-10-23_deli/landing_938[56]_*.png`). LEFT: floor hosts -- desks and tables, 258 rooms "
    "repeating one, a seeded desk with no chair -- laid in patterns with their chairs (prototyped, "
    "`_scratch/wip_dc_seed_lines/hosts_proto.py`); the lived-in touches on the order (`lived-in-touches`); the "
    "counter islands and planters rendering as plain boxes; the walker's eye on 9386. Earlier status kept: "
    + OLD300[len("*STATUS: "):])
assert "\n" not in NEW300 and NEW300.endswith("*")

PATCH = '''"""Roadmap 300 NARROWED (Deli Counter 0.263.0 hallways and 0.264.0 seeded pieces on a lattice with its census,
cold run 9386). Copied from `patch_roadmap_296_298_drawings.py`: the status block the paragraph directly above its
heading, asserted to be the one this was written against, replaced with one that keeps it after "Earlier status
kept:". The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_300_arranged.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUSES = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    for n, heading, old, new in STATUSES:
        if text.count(heading) != 1:
            raise SystemExit("REFUSED: %%d's heading is not there once; nothing written" %% n)
        h = text.find(heading)
        s = text.rindex("\\n\\n", 0, h) + 2
        if text[s:h] != old:
            raise SystemExit("REFUSED: %%d's status block is not the one this was written against; nothing written" %% n)
        text = text[:s] + new + text[h:]
        if text.count(new + heading) != 1:
            raise SystemExit("REFUSED: %%d's status no longer adjoins its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 300 NARROWED; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([(300, H300, OLD300, NEW300)],)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; Deli Counter", DC3, DC4)
