"""Deli Counter 0.187.0: a spec can say it is a demo, and the validation
manifest carries it (roadmap 185).

The breadth sweep (cold runs 9170 and 9174) drew `setback_demo` and
`pvp_station_ref` into card_block_001's lots. Level Factory draws any complete
shell Deli Counter does not call a facade, and refuses to guess from names.
So the word has to come from Deli Counter, the way `facade` does: a spec
field, written into `<id>.validation.json` by `evidence.collect`.

The walker, 2026-10-06: yes, keep demo and reference shells out of levels.

    python patch_dc_demo_flag.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
DEMOS = ("setback_demo", "pvp_station_ref", "survival_demo", "kitbash_demo", "rarity_demo")

EDITS = {
    DC / "spec_types.py": [(
        """    facade: bool = False
    # A VACANT facade (0.179.0)""",
        """    facade: bool = False
    # A DEMO (0.187.0): a spec that exists to demonstrate or test a capability
    # -- stepped setbacks, kitbash assets, rarity tiers, a survival layout, a
    # PvP station reference -- not a building a level stands. It builds and
    # validates like any other; the flag only says where it belongs. A tool
    # that assembles levels reads it from the validation manifest the way it
    # reads `facade` (Level Factory's `building_library.source_exclusion`).
    demo: bool = False
    # A VACANT facade (0.179.0)""")],
    DC / "schema/level.schema.json": [(
        """    "vacant": {
      "type": "boolean",""",
        """    "demo": {
      "type": "boolean",
      "description": "a spec that demonstrates or tests a capability, not a building a level stands (0.187.0); written to <id>.validation.json so level tools leave it out"
    },
    "vacant": {
      "type": "boolean",""")],
    DC / "evidence.py": [(
        """    facade = bool(getattr(spec, "facade", False))
    report["facade"] = facade
""",
        """    facade = bool(getattr(spec, "facade", False))
    report["facade"] = facade
    # A DEMO (0.187.0): carried for the level tools, which leave it out of a
    # lot as they leave out a facade. It changes nothing this report judges.
    report["demo"] = bool(getattr(spec, "demo", False))
""")],
}

TEST = '''"""A demo spec says so, and its validation manifest carries it (0.187.0).

The breadth sweep drew `setback_demo` and `pvp_station_ref` into
card_block_001's lots (cold runs 9170, 9174; roadmap 185). Level Factory
reads Deli Counter's own word for what a shell is -- `facade` -- rather than
guessing from a name, so the word for a demo has to come from here too.

Run:  python -m pytest test_demo_flag.py -q
"""
import json
import os

import evidence
import spec_loader

HERE = os.path.dirname(os.path.abspath(__file__))
DEMOS = ("setback_demo", "pvp_station_ref", "survival_demo", "kitbash_demo",
         "rarity_demo")


def _spec(name):
    return os.path.join(HERE, "specs", name + ".json")


def test_the_five_demo_specs_say_so():
    for name in DEMOS:
        assert spec_loader.load_spec(_spec(name)).demo is True, name


def test_a_building_is_not_a_demo_unless_it_says_so():
    assert spec_loader.load_spec(_spec("deli_a01")).demo is False


def test_the_schema_declares_it():
    with open(os.path.join(HERE, "schema", "level.schema.json"), encoding="utf-8") as f:
        schema = json.load(f)
    assert schema["properties"]["demo"]["type"] == "boolean"


def test_the_validation_manifest_carries_it():
    """`evidence.collect` builds the report `write_reports` saves as
    `<id>.validation.json`, which is the file Level Factory reads."""
    report, _, _ = evidence.collect(_spec("setback_demo"))
    assert report["demo"] is True
    report, _, _ = evidence.collect(_spec("deli_a01"))
    assert report["demo"] is False
'''


def _eol(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    assert crlf in (0, data.count(b"\n")), "mixed line endings"
    return "\r\n" if crlf else "\n"


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        eol = _eol(data)
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for name in DEMOS:
        path = DC / "specs" / (name + ".json")
        data = path.read_bytes()
        eol = _eol(data)
        text = data.decode("utf-8")
        assert '"demo"' not in text, f"{path} already says demo"
        pat = re.compile(r'^([ \t]*)"name": "' + re.escape(name) + r'",' + re.escape(eol), re.M)
        hits = pat.findall(text)
        assert len(hits) == 1, f"{path}: name line matched {len(hits)} times"
        text = pat.sub(lambda m: m.group(0) + m.group(1) + '"demo": true,' + eol, text, count=1)
        json.loads(text)  # still JSON
        staged[path] = text
    test = DC / "test_demo_flag.py"
    assert not test.exists()
    staged[test] = TEST
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
