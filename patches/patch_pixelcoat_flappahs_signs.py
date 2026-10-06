"""Pixelcoat 0.58.0: a gas station's and a convenience store's fascia always
read FLAPPAHS.

The walker, 2026-10-06: "Flappahs store always Flappahs". Zoo builds every
station's pumps, pylon, coffee island and slush machine in the Flappahs brand,
so one brand per site means the fascia says FLAPPAHS too.

  * `delco_1997` -- the theme nearly every brief names -- had NO FLAPPAHS
    sign: its `gas_station` family was GOOSE MART, QUIK KORNER and LUBE-N-GO,
    and cold run 9165 dealt the Flappahs store LUBE-N-GO. (Corrected before
    release: this said "under a FLAPPHAS pylon", but Lot stands a pylon only
    on a forecourt, and that store has none.)
    The entry is copied from `delco`, which the walker named on 2026-09-26,
    with families `convenience` and `gas_station` only: adding it to
    `default` would re-deal every unbranded building's fascia.
  * In both profiles the `gas_station` and `convenience` families keep
    FLAPPAHS alone (and `fuel_price`, the price board). GOOSE MART keeps
    `default`; LUBE-N-GO keeps `auto`; QUIK KORNER, whose families were only
    those two, joins `retail` rather than going unused.

Each profile must round-trip exactly through `json.dumps` at its own indent
before it is touched, so the rewrite changes nothing but the entries above.

    python patch_pixelcoat_flappahs_signs.py
"""
import copy
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIGNS = ROOT / "pixelcoat" / "profiles" / "signs"
BRANDED = {"gas_station", "convenience"}


def _load(path):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, f"{path}: CRLF"
    text = raw.decode("utf-8")
    data = json.loads(text)
    for indent in (1, 2):
        if json.dumps(data, indent=indent, ensure_ascii=False) + "\n" == text:
            return data, indent
    raise SystemExit(f"{path}: does not round-trip through json.dumps; edit by hand")


def _rehome(signs):
    for s in signs:
        fams = s.get("families") or []
        if s.get("slug") in ("flappahs", "fuel_price") or not (set(fams) & BRANDED):
            continue
        kept = [f for f in fams if f not in BRANDED]
        if not kept:
            assert s["slug"] == "quik_korner", s["slug"]
            kept = ["retail"]
        s["families"] = kept


def main():
    staged = {}
    delco, d_indent = _load(SIGNS / "delco.json")
    flap = next(s for s in delco["signs"] if s.get("slug") == "flappahs")
    _rehome(delco["signs"])
    staged["delco.json"] = (delco, d_indent)

    d97, i97 = _load(SIGNS / "delco_1997.json")
    assert not [s for s in d97["signs"] if s.get("slug") == "flappahs"]
    entry = copy.deepcopy(flap)
    entry["families"] = ["convenience", "gas_station"]
    _rehome(d97["signs"])
    d97["signs"].insert(0, entry)
    staged["delco_1997.json"] = (d97, i97)

    for name, (data, indent) in staged.items():
        for f in BRANDED:
            who = [s["slug"] for s in data["signs"] if f in (s.get("families") or [])]
            assert set(who) <= {"flappahs", "fuel_price"} and "flappahs" in who, (name, f, who)
        (SIGNS / name).write_bytes(
            (json.dumps(data, indent=indent, ensure_ascii=False) + "\n").encode("utf-8"))
        print("patched", name)


if __name__ == "__main__":
    main()
