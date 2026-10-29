"""Level Factory 0.268.0: a gas station and a bank on one avenue (the walker's vertical slice, 2026-10-29).

`cluster.TEMPLATES` gains the factory's own `D01_delco_avenue` -- the gas station, one branch bank, the seeded draw
for the rest -- and `CATALOG_FAMILIES` a `branch_bank` use (`bank_branch` alone).

Proven: tests/unit/test_cluster.py fails on 0.267.0 (fails_on_old.out.txt); the clone's suite, exit 0, 2,771
passed, 18 skipped, 1 xfailed (suite_clone.out.txt); the slice made and walked from the clone (the factory's
docs/findings/slice_look/).
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'level_factory'
PINS = {'CHANGELOG.md': 'eec81d565badd84b', 'VERSION': '528fe08d3734c24f', 'packages/pipeline/cluster.py': '883c77bb8869ab7a', 'tests/unit/test_cluster.py': '4cc52b64a223ff17'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.267.0] - a drill zone names the door it opens\n', '## [0.268.0] - a gas station and a bank on one avenue\n\nThe walker, 2026-10-29, of the game\'s vertical slice: "Delco Ave. Gas Station + Bank + some random buildings". No\ncluster put a filling station and a bank on one street: the guide\'s roadside row (C08) lodges beside the fuel and its\ncivic centre (C02) banks beside a hall. `cluster.TEMPLATES` gains the factory\'s own recipe, `D01_delco_avenue` --\nthe gas station as the anchor, ONE branch bank beside it, no fabric, so the rest of the lot is the library\'s seeded\ndraw -- and `CATALOG_FAMILIES` a `branch_bank` use mapping to `bank_branch` alone, because `bank`\'s three families\nare drawn in turn and would stand three banks on the lot. The guide\'s eighteen keep their `C` ids; the factory\'s are\n`D`. Proven on the slice (the factory\'s `docs/vertical_slice/`, `docs/findings/slice_look/`): seed 9003\'s lot drew\ngas_station_a02, bank_branch_a02, card_shop_a01 and train_yard_a01, made and walked. Tests:\ntests/unit/test_cluster.py, the Delco avenue puts one bank beside the gas station (fails on 0.267.0).\n\n## [0.267.0] - a drill zone names the door it opens\n')], 'VERSION': [('lines 1-1', '0.267.0', '0.268.0')], 'packages/pipeline/cluster.py': [('lines 50-51', '    "C18_large_cultural_campus_edge": ("museum", ("park", "restaurant", "college"), ("office",)),\n}\n', '    "C18_large_cultural_campus_edge": ("museum", ("park", "restaurant", "college"), ("office",)),\n    # THE FACTORY\'S OWN, NOT THE GUIDE\'S (0.268.0): `D` ids. The walker, 2026-10-29, of the game\'s\n    # vertical slice: "Delco Ave. Gas Station + Bank + some random buildings". No guide recipe puts\n    # a filling station and a bank on one street -- the roadside row (C08) lodges beside the fuel,\n    # the civic centre (C02) banks beside the hall -- so the slice asks for its own: the gas station\n    # as the anchor (the brief\'s archetype), ONE branch bank beside it, and no fabric, so the rest\n    # of the lot is the library\'s seeded draw.\n    "D01_delco_avenue": ("fuel_station", ("branch_bank",), ()),\n}\n'), ('lines 67-68', '    "bank": ("bank_branch", "credit_union", "bank"),\n    "office": ("office", "office_stepped", "bank_tower"),\n', '    "bank": ("bank_branch", "credit_union", "bank"),\n    # one bank, not three: a use\'s families are drawn in turn, so `bank` puts every bank family\n    # it can find on the lot (0.268.0, D01)\n    "branch_bank": ("bank_branch",),\n    "office": ("office", "office_stepped", "bank_tower"),\n')], 'tests/unit/test_cluster.py': [('lines 12-13', '    assert len(cluster.TEMPLATES) == 18\n    for tid, (anchor, supporting, fabric) in cluster.TEMPLATES.items():\n', '    guide = {t: v for t, v in cluster.TEMPLATES.items() if t.startswith("C")}\n    assert len(guide) == 18\n    for tid, (anchor, supporting, fabric) in guide.items():\n'), ('lines 16-17', '        assert anchor and supporting and fabric\n\n', '        assert anchor and supporting and fabric\n    # the factory\'s own (0.268.0) are `D`, and nothing else\n    assert all(t.startswith(("C", "D")) for t in cluster.TEMPLATES)\n\n\ndef test_the_delco_avenue_puts_one_bank_beside_the_gas_station():\n    """FAILS ON 0.267.0: no such template. The walker\'s vertical slice, 2026-10-29: "Delco Ave. Gas\n    Station + Bank + some random buildings" -- the anchor, one branch bank, then the seeded draw."""\n    assert cluster.preferred_families("D01_delco_avenue") == ["bank_branch"]\n    entries = ENTRIES + [{"id": f"bank_branch_a0{i}", "family": "bank_branch"} for i in (2, 3)] + [\n        {"id": "credit_union_a01", "family": "credit_union"}]\n    pref = cluster.preferred_families("D01_delco_avenue")\n    rest = set()\n    for seed in (1, 5421, 9082, 9104, 9205):\n        lot = bl.pick_lot(entries, seed, 4, anchor="gas_station", preferred=pref)\n        fams = [e["family"] for e in lot]\n        assert fams[0] == "gas_station" and fams[1] == "bank_branch", (seed, fams)\n        assert "credit_union" not in fams[:2] and len(set(fams)) == 4\n        rest.add(tuple(fams[2:]))\n    assert len(rest) > 1                    # the rest is the seed\'s, not the template\'s\n\n')]}
WHOLE = {}
NEW_FILES = {}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s/%s has mixed line endings; nothing written" % (REPO.name, name))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %s/%s is %s, not the %s this patch was written against; nothing written"
                         % (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %s/%s: the anchor at %s is there %d times; nothing written"
                                 % (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
