"""Write patches/patch_roadmap_296_298_drawings.py: roadmap 296's status replaced (the block above its heading,
embedded exactly, the earlier status kept) -- NARROWED, a level's package carries its buildings' drawings -- and 298
appended after the last item (asserted to be 297): the walker's main-drag comp, filed for later. Copied from
`roadmap_284_296_desk_move/make_roadmap_284_296.py`. Refuses if the name is taken.

    python patches/roadmap_296_298_drawings/make_roadmap_296_298.py
"""
import pathlib
import re
import subprocess

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_296_298_drawings.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t


def commit(repo, subject_start):
    """The commit whose subject starts so, read from the repo, not typed."""
    out = subprocess.run(["git", "-C", str(F / repo), "log", "-30", "--format=%h %s"], capture_output=True,
                         text=True, check=True).stdout.splitlines()
    hits = [l.split(" ", 1)[0] for l in out if l.split(" ", 1)[1].startswith(subject_start)]
    assert len(hits) == 1, (repo, subject_start, hits)
    return hits[0]


DC = commit("deli_counter", "0.257.0: ")
LF0 = commit("level_factory", "0.232.0: ")
LF1 = commit("level_factory", "0.232.1: ")


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


H296, OLD296 = status_of(296)
assert OLD296.startswith("*STATUS: OPEN 2026-10-21 -- the walker's answer on roadmap 293"), OLD296[:100]
NEW296 = (
    "*STATUS: NARROWED 2026-10-21 -- a level's package carries its buildings' drawings, and names them. Deli Counter "
    "0.257.0 (" + DC + ", `patches/patch_dc_drawings.py`): `build_package(..., spec_path=)` draws a building from its "
    "spec into its package's `drawings/` -- the exploded axonometric and a plan a storey, each beside a `.import` that "
    "keeps it as the file it is (measured on Godot 4.7, `patches/dc_drawings/keep_probe.py`: left to the default "
    "import, deli_a03's axonometric is a 136,248-byte texture in every level; kept, none is made, and a game still "
    "reads it and draws it with `Image.load_svg_from_string`), and `drawings.json`; a facade gets its reason instead, "
    "its drawing an empty walled box; an axonometric's canvas holds its own text. Level Factory 0.232.0 (" + LF0
    + ", `patches/patch_lf_drawings.py`): the library and the compose name each building's spec, and the export "
    "writes `buildings.json` at the package's root -- every standing instance, where it stands, its drawings as "
    "`res://` paths the closure verdict resolves. Cold run 9377 (0 interventions; the level 9376's, the bake's 2,947 "
    "users the same): ten drawings shipped, present, kept, none made a texture -- and two holes, closed by Level "
    "Factory 0.232.1 (" + LF1 + ", `patches/patch_lf_drawings_fix.py`): the 26 Empties composed with no spec, and the "
    "mission shell's drawings at a varied lot's package root. Cold run 9378 (0 interventions, the level 9377's) proved "
    "both. The walker's review page, built from 9378's package: https://claude.ai/artifact/BG8SRKn7xVCEz3L3JFyg3y "
    "(`docs/findings/walker_review_2026-10-21_drawings/`). LEFT: the walker's answers there -- each building's "
    "drawing, whether a facade should carry a front elevation, what players should see; the in-game screen, which "
    "is the game's. Earlier status kept: " + OLD296[len("*STATUS: "):])
assert "\n" not in NEW296 and NEW296.endswith("*")

ITEM298 = ("*STATUS: OPEN 2026-10-21 -- the walker's comp, written up in `docs/reference/MAIN_DRAG_COMP.md`; filed for "
           "later, as the walker asked.*\n\n") + (
    "**298. A main drag: the walker's remix of the Industrial Highway through Tinicum, as a level comp.** The walker, "
    "2026-10-21, with a street map of PA-291 through Essington and Tinicum: \"save this for later...do a remix of this "
    "street, main drag, to have a cheesteak shop, bank, coffeshop, wawa ,ect ect for a level comp\". Written up in "
    "`docs/reference/MAIN_DRAG_COMP.md` (the map not stored): a four-lane arterial with a service road on its business "
    "side, a freight line right behind it, side streets every block into a rowhome grid, the expressway cloverleaf as "
    "the backdrop; along the drag every business under an invented Delco name, the Wawa FLAPPAHS. Read for it (Deli "
    "Counter's specs, 2026-10-21): the bank, FLAPPAHS and its forecourt, the pizzeria, the dive club, the tow yard and "
    "the warehouses exist; a cheesesteak shop, a coffee shop and a hot dog stand have no family; Lot lays no rail; and "
    "a lot is drawn by seed, a brief anchoring one building (`building_library.lot_for_brief`). **What would close "
    "it:** a cheesesteak shop and a coffee shop grown as Deli Counter families, their fixtures as Zoo species and "
    "their signs as Pixelcoat skins under names the walker picks; a brief that names the businesses its main drag "
    "stands; a four-lane arterial with a service road, and a rail edge, from Lot; a cold run of the remix, walked by "
    "the walker.\n")
assert "\n" not in ITEM298[:-1].replace("*\n\n**", "*  **")

PATCH = '''"""Roadmap 296 NARROWED (a level's package carries its buildings' drawings and names them: Deli Counter 0.257.0,
Level Factory 0.232.0 and 0.232.1, cold runs 9377 and 9378, the walker's review page) and 298 filed (the walker's
main-drag comp). Copied from `patch_roadmap_284_296_desk_move.py`: the status block the paragraph directly above its
heading, asserted to be the one this was written against, replaced with one that keeps it after "Earlier status
kept:"; the new item appended after the last, asserted to be 297. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_296_298_drawings.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUSES = %r
NEW_ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**298. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
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
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 297 or heads[-1] != 297:
        raise SystemExit("REFUSED: the last item is not 297; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    for item in NEW_ITEMS:
        text = text + "\\n" + item
    if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*298\\. ", text)) != 1:
        raise SystemExit("REFUSED: item 298's status does not adjoin its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 296 NARROWED, 298 filed; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([(296, H296, OLD296, NEW296)], [ITEM298])
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; Deli Counter", DC, "Level Factory", LF0, LF1)
