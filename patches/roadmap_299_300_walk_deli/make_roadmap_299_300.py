"""Write patches/patch_roadmap_299_300_walk_deli.py: roadmap 299 and 300 appended after the last item (asserted to be
298) -- the walker's walk of cold run 9383: 299 NARROWED (the black opening, the roof ladder, the stair's open
underside, each fixed in a tool and proven in a package), 300 OPEN (furniture with no arrangement). Copied from
`roadmap_296_298_drawings/make_roadmap_296_298.py`; it replaces no status. Refuses if the name is taken.

    python patches/roadmap_299_300_walk_deli/make_roadmap_299_300.py
"""
import pathlib
import subprocess

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_299_300_walk_deli.py"
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


DC1 = commit("deli_counter", "0.261.0: ")
DC2 = commit("deli_counter", "0.262.0: ")
LF = commit("level_factory", "0.237.0: ")
LADDER = commit(".", "patches + tools: the walk copy climbs the package's own ladder volume")

ITEM299 = (
    "*STATUS: NARROWED 2026-10-23 -- three of the four findings fixed in a tool and proven in a package. The black "
    "opening: Level Factory 0.237.0 (" + LF + ", `patches/patch_lf_backdrop_frame.py`) lays the backdrop's ground as "
    "a frame round the plate; cold run 9385 (0 interventions), deli_a03's ground-floor ladder hole into the basement "
    "through its rim p95 161 where 9384 read 12. The roof ladder: the root's `tools/walk_ladders.gd` (" + LADDER
    + ") adopts the package's own climb volume; 9384's walk copy climbs to feet 7.603 against the roof's 6.6. The "
    "stair's open underside: Deli Counter 0.262.0 (" + DC2 + ", `patches/patch_dc_solid_undersides.py`), solid, the "
    "nav gate 8 of 8, every library stair solid unless named; in 9385's package. Also shipped on the way: Deli "
    "Counter 0.261.0 (" + DC1 + ") lights every opening's landing; the cold drive runs `tools/light_check.py`, which "
    "now judges an opening through its rim. LEFT: finding 3, filed as roadmap 300; the three rooms the light check "
    "fails in this level (deli_a03's basement vault p50 3, the office lobby 8, the pharmacy's retail floor 2), the "
    "MOODY floor the walker's call; the walker's eye on 9385's walk copy.*\n\n"
    "**299. The walker's walk of cold run 9383: a black opening, a ladder that cannot be climbed, a stair open "
    "underneath.** The walker, 2026-10-23, in deli_a03: \"this shouldn't look pitch black\", \"im stuck trying to get "
    "up the ladder to the roof\", \"this stair has unexpected space below it\", and the rule \"you should be able to "
    "see into holes to know you can go forward into them\" -- and \"i want all of these fixes to persist in our tools "
    "so that future levels don't have these same issues\" (`docs/findings/walk_2026-10-23_deli/`). **The black "
    "opening, REFUTED AND KEPT: the basement's dim light.** The basement is MOODY by rule and the light check passed "
    "its cold storage at p50 10, so Deli Counter 0.261.0 lit every opening's landing; cold run 9384 carried the lamps "
    "and they changed the view through the basement stair by nothing measurable (through its rim p50 31.3 to 31.5). "
    "**The cause:** Level Factory 0.211.0's backdrop ground, an unshaded plane at y -0.10 laid \"so the plate covers "
    "it wherever both stand\" -- inside every ground slab (-0.30..0.00), a black lid on every hole down into a "
    "basement, in every level since 0.211.0 with one. Found by the inspection light (still black), every visible "
    "instance crossing the hole's column (`hole_column.gd`), and hiding it alone in a copy (the ladder and the lit "
    "floor). **The instrument that missed it:** the light check held an opening to its frame's p50, and a frame "
    "looking down an opening is mostly the floor round it -- it passed the black hole at 42 and failed the "
    "broken-floor hole and the roof hatch, which read; it now projects the rim and holds p95 through it to 20, "
    "PROVISIONAL (`patches/patch_light_check_through_rim.py`). **The ladder:** the walk copy's ladder script sized "
    "its climb volume from a marker Deli Counter emits only for hatch links and ignored the package's own; 17 roof "
    "ladders in the library could not be climbed in a walk copy. **The stair:** deli_a03's `deli_stair_up` was opened "
    "underneath by hand in Deli Counter 0.124.1, its foot otherwise reachable only from under its high end; 0.189.0's "
    "wider door had made that unnecessary and nothing asked. **What would close it:** roadmap 300; the three dark "
    "rooms answered by the walker's floor or by light; the walker's walk of 9385's copy.\n")

ITEM300 = (
    "*STATUS: OPEN 2026-10-23 -- the walker's walk of cold run 9383, finding 3; read, not started.*\n\n"
    "**300. Furniture is placed with no arrangement.** The walker, 2026-10-23, of deli_a03's stair landing: \"layout of "
    "these tables doesn't seem to have a rhyme or reason\". Read off Deli Counter (`docs/findings/walk_2026-10-23_deli/`"
    ", finding 3): no pass that places these pieces has a notion of arrangement. The landing, `upper_hall`, role "
    "`connector`, takes the gallery-and-chapel `hall` kind by its id's token (`level_design._room_kind`: id tokens "
    "before role, by design) and gets a service counter, benches, vending and a dining table; 45 connector rooms in "
    "the library resolve to that kind, nearly all `upper_hall` or `back_hall` -- hallways. Role alone cannot decide: "
    "`connector` covers 896 rooms, kitchens, offices and bars among them (2026-10-23 census). seed_cover lays shuffled "
    "first-fit pieces on a jittered grid, facing by coin flip; wall pieces at shuffled random spots; floor hosts first "
    "fit, facing away from the room's middle. Over 427 specs, 59 % of seed_cover's archetype pieces stand isolated. "
    "**What would close it:** a room a stair or ladder lands in is circulation first -- its landing kept clear and its "
    "kind not a seating hall; floor pieces laid in rows or against a wall by a rule a reader can state (desks in rows, "
    "wall runs packed from a corner); seed_cover's archetype pass retired where furnish runs; each step held to the "
    "route census (`route_cost.py`) and the walker's density band (2026-10-21: not crowded, not barren, 12-25 % floor "
    "share); a refurnish, since stored specs carry older furnishing; the walker's eye on a walk copy.\n")
for item, n in ((ITEM299, 299), (ITEM300, 300)):
    status, body = item.split("\n\n")
    assert "\n" not in status and status.endswith("*") and body.startswith("**%d. " % n) and body.count("\n") == 1

PATCH = '''"""Roadmap 299 (NARROWED) and 300 (OPEN) filed: the walker's walk of cold run 9383 -- the black opening, the roof ladder
and the stair's open underside fixed and proven in a package; the furniture's arrangement open. Copied from
`patch_roadmap_296_298_drawings.py`; it replaces no status. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_299_300_walk_deli.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

NEW_ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if "\\n**299. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 298 or heads[-1] != 298:
        raise SystemExit("REFUSED: the last item is not 298; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    for item in NEW_ITEMS:
        text = text + "\\n" + item
    for n in (299, 300):
        if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*%%d\\. " %% n, text)) != 1:
            raise SystemExit("REFUSED: item %%d's status does not adjoin its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 299 NARROWED and 300 OPEN filed; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([ITEM299, ITEM300],)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; Deli Counter", DC1, DC2, "Level Factory", LF, "root", LADDER)
