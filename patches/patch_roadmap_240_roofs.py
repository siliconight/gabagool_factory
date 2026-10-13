"""Roadmap 240, 2026-10-12 night: the roofscape's "silver" grounded at the walker's asking and the rowhome
Empties roofed in tar (Deli Counter 0.210.0, cold run 9268; `docs/reference/ROWHOUSE_ROOFS.md`). Replaces
the end of 240's status (asserted once and still above its heading) and appends one paragraph to its body.
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_240_roofs.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S240_OLD = ("Left: the street lights' shadow cost, the walker's call with that seen; the frames beside the comps "
            "for the walker's eye; then the rowhouse front and the silver roofs.*")
S240_NEW = ("The rowhome Empties' roofs are tar (Deli Counter 0.210.0, cold run 9268), the membrane under any "
            "coating and what every other delco roof wore; the \"silver\" was the factory's reading of a photo "
            "and an uncited comment, and is an aluminum coating whose 1990s prevalence has no source "
            "(`docs/reference/ROWHOUSE_ROOFS.md`). Left: the street lights' shadow cost, the walker's call with "
            "that seen; the frames beside the comps for the walker's eye; then the rowhouse front, the "
            "roofscape's rear ells, and the coating when a 1990s source says how common it was.*")

BODY_240 = """

**THE ROOFS, GROUNDED, 2026-10-12 night** (`docs/reference/ROWHOUSE_ROOFS.md`). The walker, of this item's "silver roofs": "should it be silver?... where are you getting that from vs. concrete?... silver doesn't seem like a material for rooftop, perhaps aluminum but I'd want to ground that in something first". **RETRACTED, KEPT as this item's wording above:** "most silver-coated" was the factory's description of the walker's aerial comp (the photograph not stored), and Deli Counter 0.175.0's "A 1990s rowhouse roof is flat tar, silver-coated" cited nothing; the code meanwhile roofed the twelve rowhome Empties in `concrete` (Pixelcoat's `concrete_delco`; under `street`, `cinderblock_delco`, a block wall). Grounded: "silver" roof coatings are asphalt carrying aluminum flakes, made for built-up and modified-bitumen roofs (Karnak, Garland, Barrett product data); Philadelphia's cool-roof law of May 2010 is when white reflective roofs became policy, so a modern aerial's white roofs likely postdate 1997; how many 1990s Philadelphia rowhouse roofs carried the coating, no source found (1990s USGS black-and-white aerials would show it, a download for the walker's yes). The walker: "tar now, coating later". Deli Counter 0.210.0 (`patches/patch_dc_rowhome_tar_roof.py`): `empty_rowhome`'s roof `tar` and the twelve specs with it, a `tar` row in `KIND_BY_MATERIAL`, `_spec_material_ids` reading `roof_material` (it read none); the library rebuilt, 146 shells, the manifests moving only their build time and the twelve's spec hash. Cold run 9268 (0 interventions): each Empty's roof `roof_delco_1997_01_*.glb` in `M_Skin_tar_delco_1997`; the frames move on the roofs (9.4 % and 6.8 % of pixels past 8 codes at the two roof stations) and not at the controls (0.007 % and 0.4 %), quiet at blue hour (`docs/cold_runs/cold_9268/roofs.png`)."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE ROOFS, GROUNDED, 2026-10-12 night" not in text, "already applied"
    assert text.count(S240_OLD) == 1, "240's status end not found once"
    text = text.replace(S240_OLD, S240_NEW)
    h = text.find("\n\n**240. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s:h].endswith(S240_NEW), "240's status does not sit above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**241. ", nxt) > nxt, "241 does not follow 240"
    text = text[:nxt] + BODY_240 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 240: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
