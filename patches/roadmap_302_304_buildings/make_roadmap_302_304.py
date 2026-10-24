"""Write patches/patch_roadmap_302_304_buildings.py: roadmap 302, 303 and 304 appended after the last item (asserted to
be 301) -- the walker's asks of 2026-10-23: restrooms in buildings, a laundromat, a better bank. Copied from
`roadmap_301_runtime_structures/make_roadmap_301.py`; it replaces no status. Refuses if the name is taken.

    python patches/roadmap_302_304_buildings/make_roadmap_302_304.py
"""
import pathlib

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
dest = F / "patches" / "patch_roadmap_302_304_buildings.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t
ASK = ("The walker, 2026-10-23, with roadmap 300's lived-in touches (\"people forget to put the toilet seat down, push "
       "their chair in, turn off the lights\"): \"we should have some toilets in buildings, and a laundrymat, and i "
       "want to see a better bank one of these days\".")

ITEMS = [
    ("*STATUS: OPEN 2026-10-23 -- the walker's ask; read, not started.*\n\n"
     "**302. No building has a restroom.** " + ASK + " Read the same day: the library holds one restroom, "
     "`gs_corner_station`'s, and it furnishes as a mechanical room (`level_design._room_kind`: no restroom kind, no "
     "recipe) -- a furnace and a water heater where a toilet should be; Zoo has no toilet, urinal, sink or stall "
     "species; `combat_audit` already names `restroom` among its utility roles. A real deli, office, bar, bank or club has one or more, and it is where "
     "the walker's first lived-in touch lives: a toilet seat left up. **What would close it:** Zoo species for a toilet "
     "(seat down and up as two states), a sink and a stall partition, by the gap protocol; a Deli Counter `restroom` "
     "kind and recipe -- fixtures against the walls, stalls in a row -- and a rule that gives a building of a family "
     "that has one a small room off a corridor, its door counted in the route census; the library refurnished; a cold "
     "run with the walker's eye on it.\n"),
    ("*STATUS: OPEN 2026-10-23 -- the walker's ask; read, not started.*\n\n"
     "**303. There is no laundromat.** " + ASK + " Read the same day: no Deli Counter family and no Zoo washer, "
     "dryer, folding table or change machine -- the only laundromat is a picture, Zoo's `shop_laundry` pane painted "
     "behind a corner shop's glass (`zoo_keeper/core/shop_panes.py`), its awning colour named in `shop_awning_forms`. **What would close it:** a laundromat family from Deli Counter -- a "
     "storefront room of washers in rows and stacked dryers on a wall, folding tables, plastic chairs, a change machine "
     "and a back room -- its machines Zoo species, its sign a Pixelcoat skin under an invented Delco name the walker "
     "picks (`fake-delco-brands-funny-and-crass`); Lot placing it where a strip's storefront can stand; arranged by "
     "roadmap 300's rules from the start; a cold run with the walker's eye on it.\n"),
    ("*STATUS: OPEN 2026-10-23 -- the walker's ask; what \"better\" means not yet said.*\n\n"
     "**304. The walker wants a better bank.** " + ASK + " The library holds eight banks -- `bank`, `bank_branch_a02` to "
     "`a04`, `bank_job`, `bank_tower_a01` to `a03` -- and the bank-block missions build their shells from the `bank` "
     "preset. What reads wrong in them has not been said, and guessing would spend the work on the wrong thing. "
     "**What would close it:** the walker's eye on a bank -- a walk copy or frames of the lobby, the teller line, the "
     "vault and the offices -- and their words on what is missing; each answer grown in the tool that owns it; a "
     "cold run of a bank block walked again.\n"),
]
for item, n in zip(ITEMS, (302, 303, 304)):
    status, body = item.split("\n\n")
    assert "\n" not in status and status.endswith("*") and body.startswith("**%d. " % n) and body.count("\n") == 1

PATCH = '''"""Roadmap 302, 303 and 304 (OPEN) filed: the walker's asks of 2026-10-23 -- restrooms in buildings, a laundromat,
a better bank. Copied from `patch_roadmap_301_runtime_structures.py`; it replaces no status. The index is NOT touched
here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_302_304_buildings.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
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
    if "\\n**302. " in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    heads = [int(m.group(1)) for m in re.finditer(r"(?m)^\\*\\*(\\d+)\\. ", text)]
    if max(heads) != 301 or heads[-1] != 301:
        raise SystemExit("REFUSED: the last item is not 301; nothing written")
    if not text.endswith("\\n") or text.endswith("\\n\\n"):
        raise SystemExit("REFUSED: the roadmap does not end on one newline; nothing written")
    for item in NEW_ITEMS:
        text = text + "\\n" + item
    for n in (302, 303, 304):
        if len(re.findall(r"(?m)^\\*STATUS: [^\\n]*\\*\\n\\n\\*\\*%%d\\. " %% n, text)) != 1:
            raise SystemExit("REFUSED: item %%d's status does not adjoin its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 302, 303 and 304 OPEN filed; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (ITEMS,)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars")
