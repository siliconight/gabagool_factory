"""Zoo 1.157.0: a beer distributor's door names it.

storefront_names gains the beer kind: BEER WORLD, CASE LOT BEER; trade BEER.

Proven: fails_on_old.out.txt; suite_clone.out.txt.
"""
import base64
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'zoo'
PINS = {'CHANGELOG.md': '2805496ccef51802', 'VERSION': '022a8c622c96346c', 'zoo_keeper/core/storefront_names.py': '30fa07732812bdc9'}
EDITS = {'CHANGELOG.md': [('lines 1-1', "## [1.156.0] - a window neon's beer bent in a script\n", '## [1.157.0] - a beer distributor\'s door names it\n\nDeli Counter 0.297.0 builds a beer distributor (the walker, 2026-10-31: "liquor store should have neon beer company\nsigns"). `storefront_names.KINDS` gains `beer` (by the words `beer` and `distributor`): BEER WORLD and CASE LOT BEER,\nthe names the theme already gave a distributor\'s band; its door\'s trade is BEER.\n\nTests: tests/test_beer_kind.py (fails on 1.156.0: a beer distributor shows a street number over its door).\n\n## [1.156.0] - a window neon\'s beer bent in a script\n')], 'VERSION': [('lines 1-1', '1.156.0', '1.157.0')], 'zoo_keeper/core/storefront_names.py': [('lines 57-58', '    ("brewery", ("brewery",), ("DOWN THE SHORE BREWING", "HONEST HON BREW CO")),\n    ("casino", ("casino",), ("LUCKY JAWN CASINO", "THE BROKE BANK CASINO")),\n', '    ("brewery", ("brewery",), ("DOWN THE SHORE BREWING", "HONEST HON BREW CO")),\n    # THE BEER DISTRIBUTOR (1.157.0; Deli Counter 0.297.0\'s `beer_distributor`): Pennsylvania\'s 1999 case-beer shop,\n    # the walker\'s liquor-store photographs (the factory\'s docs/reference/STORE_SIGNAGE_COMPS.md). The names the\n    # theme already gave a distributor\'s band.\n    ("beer", ("beer", "distributor"), ("BEER WORLD", "CASE LOT BEER")),\n    ("casino", ("casino",), ("LUCKY JAWN CASINO", "THE BROKE BANK CASINO")),\n'), ('lines 119-119', '         "brewery": "BREWERY", "casino": "CASINO", "funeral": "FUNERAL HOME", "country": "CLUBHOUSE"}\n', '         "brewery": "BREWERY", "beer": "BEER", "casino": "CASINO", "funeral": "FUNERAL HOME", "country": "CLUBHOUSE"}\n')]}
WHOLE = {}
NEW_FILES = {'tests/test_beer_kind.py': '"""A beer distributor\'s door names it (1.157.0).\n\nThe walker, 2026-10-31: "liquor store should have neon beer company signs". Deli Counter 0.297.0 builds a beer\ndistributor -- Pennsylvania\'s 1999 case-beer shop -- and its band and its door read from this table, as every shop\'s\ndo. FAILS ON 1.156.0: no `beer` kind; a `beer_distributor` shows a street number over its door.\n"""\nfrom zoo_keeper.core import storefront_names as SN\n\n\ndef test_a_beer_distributor_is_named_from_the_beer_kind():\n    said = SN.sign_for("beer_distributor_a01")\n    assert said["kind"] == "beer" and said["text"] in ("BEER WORLD", "CASE LOT BEER")\n    assert SN.trade_for("beer_distributor_a01")["text"] == "BEER"\n\n\ndef test_a_brewery_is_still_a_brewery():\n    assert SN.sign_for("brewery_a01")["kind"] == "brewery"\n'}
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
