"""Zoo 1.75.0, second half: the genome notes spell the brand FLAPPAHS too.

`patch_zoo_flappahs.py` respelled every `.py`. Four species' notes kept the
old spelling -- coffee_island, price_pylon, pump, slush_machine -- one of them
calling FLAPPHAS "the store's settled name". Notes are description only: no
Zoo hash reads them (`kit.py` hashes openings and voids, `seeding` hashes
seeds), and the brand a player sees comes from `price_pylon_forms.STORE`.

A byte replace of an eight-letter word with an eight-letter word, so each
file keeps its own line endings (coffee_island.json is CRLF, the rest LF).

    python patch_zoo_flappahs_notes.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPECIES = ROOT / "zoo" / "zoo_keeper" / "genome" / "species"
FILES = ("coffee_island.json", "price_pylon.json", "pump.json", "slush_machine.json")
PAIRS = ((b"FLAPPHAS", b"FLAPPAHS"), (b"Flapphas", b"Flappahs"), (b"flapphas", b"flappahs"))


def main():
    staged = {}
    for name in FILES:
        path = SPECIES / name
        data = path.read_bytes()
        assert re.search(rb"(?i)flapphas", data), f"{name}: no old spelling"
        new = data
        for old, rep in PAIRS:
            new = new.replace(old, rep)
        assert not re.search(rb"(?i)flapphas", new), f"{name}: a casing the pairs miss"
        assert len(new) == len(data) and new.count(b"\r\n") == data.count(b"\r\n"), name
        json.loads(new)
        staged[path] = new
    for path, new in staged.items():
        path.write_bytes(new)
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
