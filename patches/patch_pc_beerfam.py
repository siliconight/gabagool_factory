"""Pixelcoat 0.71.0: the beer family.

BEER WORLD and CASE LOT BEER join a beer family.

Proven: fails_on_old.out.txt; suite_clone.out.txt.
"""
import base64
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'pixelcoat'
PINS = {'CHANGELOG.md': '6371b2f0b9bfee5c', 'VERSION': '00d5483f6156c340', 'pixelcoat/version.py': '26d08c1185bb046a', 'profiles/signs/delco.json': '033fba902484bacf', 'profiles/signs/delco_1997.json': '06c2a5f8e0970897', 'tests/test_one_name_list.py': '0ceefa0314453a59'}
EDITS = {'CHANGELOG.md': [('lines 1-2', '# Changelog\n\n', '# Changelog\n\n## [0.71.0] - the beer family\n\nDeli Counter 0.297.0 builds a beer distributor (the walker, 2026-10-31: "liquor store should have neon beer company\nsigns"). BEER WORLD and CASE LOT BEER join a `beer` family, in both theme profiles, in the order Zoo\'s\n`storefront_names` (>= 1.157.0) names a distributor\'s door -- one list for the band and the door, held by\n`tests/test_one_name_list.py`. They keep `liquor` and `warehouse`.\n\n')], 'VERSION': [('lines 1-1', 'Pixelcoat 0.70.0', 'Pixelcoat 0.71.0')], 'pixelcoat/version.py': [('lines 33-33', '_FALLBACK = "0.70.0"\n', '_FALLBACK = "0.71.0"\n')], 'profiles/signs/delco.json': [('lines 82-85', '   "border": "#ffffff",\n   "families": [\n    "liquor",\n    "warehouse",\n', '   "border": "#ffffff",\n   "families": [\n    "beer",\n    "liquor",\n    "warehouse",\n'), ('lines 95-98', '   "border": "#f5e6c8",\n   "families": [\n    "liquor",\n    "warehouse"\n', '   "border": "#f5e6c8",\n   "families": [\n    "beer",\n    "liquor",\n    "warehouse"\n')], 'profiles/signs/delco_1997.json': [('lines 93-96', '      "border": "#ffffff",\n      "families": [\n        "liquor",\n        "warehouse",\n', '      "border": "#ffffff",\n      "families": [\n        "beer",\n        "liquor",\n        "warehouse",\n'), ('lines 109-112', '      "border": "#f5e6c8",\n      "families": [\n        "liquor",\n        "warehouse"\n', '      "border": "#f5e6c8",\n      "families": [\n        "beer",\n        "liquor",\n        "warehouse"\n')], 'tests/test_one_name_list.py': [('lines 19-19', '             "video": "video", "brewery": "brewery"}\n', '             "video": "video", "brewery": "brewery",\n             # the beer distributor (0.71.0; Zoo 1.157.0, Deli Counter 0.297.0)\n             "beer": "beer"}\n')]}
WHOLE = {}
NEW_FILES = {}
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
