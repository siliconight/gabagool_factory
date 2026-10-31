"""Level Factory 0.276.0: a beer distributor on Delco Avenue.

SIGN_FAMILIES beer; D01_delco_avenue asks for a beer distributor after its bank.

Proven: fails_on_old.out.txt; suite_clone.out.txt.
"""
import base64
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'level_factory'
PINS = {'CHANGELOG.md': '80da8ee93d5d5b42', 'VERSION': 'd4f88ba8de0f48fd', 'apps/cli/commands/__init__.py': '2c1377a1b82ad7a8', 'packages/pipeline/cluster.py': 'c8c4fe5a9471b793', 'tests/unit/test_cluster.py': '37f23c05d210c991'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.275.0] - the avenue and its side streets\n', '## [0.276.0] - a beer distributor on Delco Avenue\n\nThe walker, 2026-10-31: "liquor store should have neon beer company signs" (the factory\'s\n`docs/reference/STORE_SIGNAGE_COMPS.md`). Deli Counter 0.297.0 builds a beer distributor -- Pennsylvania\'s 1999\ncase-beer shop, the one the walker\'s liquor-store photographs are of.\n\n### Added\n- **`SIGN_FAMILIES` `("beer", "beer")`**: a `beer_distributor` matched no family and dealt no band; it is the beer\n  family, whose names Zoo (>= 1.157.0) paints over its door and Pixelcoat (>= 0.71.0) holds as one list.\n- **`D01_delco_avenue` asks for a beer distributor** after its branch bank (`CATALOG_FAMILIES["beer_distributor"]`):\n  the anchor, the bank, the distributor, then the seeded draw.\n\nTests: tests/unit/test_beer_family.py, tests/unit/test_cluster.py (fail on 0.275.0).\n\n## [0.275.0] - the avenue and its side streets\n')], 'VERSION': [('lines 1-1', '0.275.0', '0.276.0')], 'apps/cli/commands/__init__.py': [('lines 1629-1630', '    ("brewery", "brewery"), ("distillery", "liquor"), ("bar", "bar"),\n    ("supermarket", "supermarket"), ("market", "supermarket"),\n', '    ("brewery", "brewery"), ("distillery", "liquor"), ("bar", "bar"),\n    # the beer distributor (0.276.0; Deli Counter 0.297.0): its own family, the names Zoo paints over its door\n    ("beer", "beer"),\n    ("supermarket", "supermarket"), ("market", "supermarket"),\n')], 'packages/pipeline/cluster.py': [('lines 57-57', '    "D01_delco_avenue": ("fuel_station", ("branch_bank",), ()),\n', '    # AND A BEER DISTRIBUTOR (0.276.0). The walker, 2026-10-31: "liquor store should have neon beer company signs",\n    # with liquor-store photographs (the factory\'s docs/reference/STORE_SIGNAGE_COMPS.md) -- in 1999 Pennsylvania\n    # the case-beer distributor is that shop. Second, after the bank: the anchor, the bank, the distributor, then\n    # the seeded draw.\n    "D01_delco_avenue": ("fuel_station", ("branch_bank", "beer_distributor"), ()),\n'), ('lines 77-78', '    "branch_bank": ("bank_branch",),\n    "office": ("office", "office_stepped", "bank_tower"),\n', '    "branch_bank": ("bank_branch",),\n    "beer_distributor": ("beer_distributor",),\n    "office": ("office", "office_stepped", "bank_tower"),\n')], 'tests/unit/test_cluster.py': [('lines 25-25', '    assert cluster.preferred_families("D01_delco_avenue") == ["bank_branch"]\n', '    # and a beer distributor after it (0.276.0): the walker\'s liquor store\n    assert cluster.preferred_families("D01_delco_avenue") == ["bank_branch", "beer_distributor"]\n'), ('lines 27-27', '        {"id": "credit_union_a01", "family": "credit_union"}]\n', '        {"id": "credit_union_a01", "family": "credit_union"},\n        {"id": "beer_distributor_a01", "family": "beer_distributor"}]\n'), ('lines 34-35', '        assert "credit_union" not in fams[:2] and len(set(fams)) == 4\n        rest.add(tuple(fams[2:]))\n', '        assert fams[2] == "beer_distributor", (seed, fams)\n        assert "credit_union" not in fams[:3] and len(set(fams)) == 4\n        rest.add(tuple(fams[3:]))\n')]}
WHOLE = {}
NEW_FILES = {'tests/unit/test_beer_family.py': '"""A beer distributor reads as the beer family (0.276.0): its band is dealt the names Zoo paints over its door.\n\nThe walker, 2026-10-31: "liquor store should have neon beer company signs". FAILS ON 0.275.0: `beer_distributor`\nmatches no family and deals no band.\n"""\nfrom apps.cli import commands as cmd\n\n\ndef test_a_beer_distributor_is_the_beer_family_and_deals_a_band():\n    assert cmd.sign_family("beer_distributor_a01") == "beer"\n    assert "beer" not in cmd.NO_BAND\n    # the families it must not steal\n    assert cmd.sign_family("brewery_a01") == "brewery" and cmd.sign_family("self_storage_a03") == "warehouse"\n'}
#: binary files (a font, a texture): base64, each pinned by its sha256
BINARY_FILES = {}


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
    for name in list(NEW_FILES) + list(BINARY_FILES):
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %s/%s exists already; nothing written" % (REPO.name, name))
    blobs = {}
    for name, (digest, b64) in BINARY_FILES.items():
        blobs[name] = base64.b64decode(b64)
        if hashlib.sha256(blobs[name]).hexdigest() != digest:
            raise SystemExit("REFUSED: %s/%s does not decode to its sha256; nothing written" % (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, raw in blobs.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(raw)
    print("%s: %d files edited, %d written" % (REPO.name, len(out), len(NEW_FILES) + len(blobs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
