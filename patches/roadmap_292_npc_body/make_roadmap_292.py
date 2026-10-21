"""Write patches/patch_roadmap_292_npc_body.py: 292's status (the block above its heading, embedded exactly) replaced
-- CLOSED, keeping its earlier status. Copied from `roadmap_284_table_chairs/make_roadmap_284.py`. Refuses if the
name is taken.

    python patches/roadmap_292_npc_body/make_roadmap_292.py
"""
import pathlib
import re
import subprocess

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_292_npc_body.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t


def head(repo, version_file_text, prefix):
    assert (F / repo / "VERSION").read_bytes() == version_file_text, repo
    line = subprocess.run(["git", "-C", str(F / repo), "log", "-1", "--format=%h %s"], capture_output=True,
                          text=True, check=True).stdout.strip()
    h, subject = line.split(" ", 1)
    assert subject.startswith(prefix), subject
    return h


# the three commits, read from the repos, not typed
LF = head("level_factory", b"0.231.0", "0.231.0: ")
LOT = head("lot", b"Lot 0.126.1", "0.126.1: ")
DC = head("deli_counter", b"Deli Counter 0.253.0", "0.253.0: ")


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


H292, OLD292 = status_of(292)
assert OLD292 == "*STATUS: OPEN 2026-10-21 -- found shipping Level Factory 0.230.0 (roadmap 289); not started.*"
NEW292 = (
    "*STATUS: CLOSED 2026-10-21 -- the enemy's body is the contract's NPC, and the NPC is the player until it says "
    "otherwise. Settled in the contract: Deli Counter 0.253.0 (" + DC + ", `patches/patch_dc_npc_body.py`) makes "
    "`characters.npc_standard` govern -- `npc_body()` is its stated metrics over the player's, it states none, and "
    "its restated radius and height, read by nothing, are gone -- and `sightlines.crew_sight_height_m` and "
    "`enemy_sight_height_m` copies of the bodies' eyes, `sight_heights()` refusing one that disagrees (\"one body, "
    "one eye\") as `cover_break_height` already refused an aim copy; no sightline copy is merged into a contract that "
    "omits it any more, which had refused a contract stating only its body for disagreeing with a 1.0 m aim it never "
    "wrote. The seam: Level Factory 0.231.0 (" + LF + ", `patches/patch_lf_enemy_eye.py`) writes the scenario's "
    "`enemy_eye_height_m` from that block, the player's where it states none, and a test like roadmap 123's has one "
    "stated 2.05 m body move both sides to a 1.85 m eye, in the scenario `run` writes and the engagement the advisory "
    "is given (`test_the_enemy_sights_from_the_contract.py`; on 0.230.0 four of its six fail on behaviour); "
    "`LT_SIGHT_ONE_EYE` now speaks only for a distinct NPC eye or a brief moving one side. Lot 0.126.1 (" + LOT + ", "
    "`patches/patch_lot_npc_fallback.py`) shipped first: its contract fallback mirrored the NPC's two numbers, and "
    "Lot 0.126.0's guard fails against the new contract (it carries the queued `urban_tree_stations` docstring fix "
    "too). Cold run 9375 (restaurant_row_001 at seed 9003, the three tools the only ones moved): 0 interventions; the "
    "three staged scenarios byte for byte 9374's, the enemy's eye now the contract's 1.6; findings 108 -> 108, "
    "identical; the bake unchanged (`docs/cold_runs/cold_9375/NOTES.md`). REFUTED, kept: the item's \"the enemy's "
    "body size follows nothing\" -- Laser Tag 0.26.0 (roadmap 197) builds every enemy's capsule, mesh and agent from "
    "the scenario's `player_radius_m` and `player_height_m`, which the seam writes from the contract "
    "(`test_enemy_is_the_contracts.gd`, its check [2]); a distinct NPC class with its own radius or height would want "
    "a Laser Tag field, one bounded change, when one ships. Earlier status kept: " + OLD292[len("*STATUS: "):])
assert "\n" not in NEW292 and NEW292.endswith("*")

PATCH = '''"""Roadmap 292 CLOSED (Level Factory 0.231.0, Lot 0.126.1, Deli Counter 0.253.0: the enemy's body is the
contract's). Copied from `patch_roadmap_284_table_chairs.py`: replaces 292's status block (the paragraph directly
above its heading, asserted to be the one this was written against) with one that keeps it after "Earlier status
kept:". The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_292_npc_body.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    for n, heading, old, new in ITEMS:
        if new[:80] in text:
            raise SystemExit("REFUSED: %%d already applied; nothing written" %% n)
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
    print("roadmap 292: CLOSED, the earlier status kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % ([(292, H292, OLD292, NEW292)],)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars; LF", LF, "Lot", LOT, "DC", DC)
