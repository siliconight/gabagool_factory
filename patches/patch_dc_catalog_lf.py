"""Deli Counter 0.295.1: CATALOG.md is written in LF.

catalog.py opens CATALOG.md with newline="\n", so a commit hook no longer leaves it dirty with CRLF.

Proven: tests/test_catalog_transients.py fails on 0.295.0 (fails_on_old.out.txt); the clone's suite.
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / 'deli_counter'
PINS = {'CHANGELOG.md': 'e0d77ecf4185fec0', 'VERSION': '63f851b4ba2ad1fc', 'catalog.py': '8332d90b714a5aa9', 'tests/test_catalog_transients.py': '9b9ba1383b331e3c'}
EDITS = {'CHANGELOG.md': [('lines 1-1', '## [0.295.0] - a storey nobody reaches is a facade\n', '## [0.295.1] - CATALOG.md is written in LF\n\n### Fixed\n- **`catalog.py` wrote `specs/CATALOG.md` in text mode**, CRLF on Windows, so every commit hook -- which runs it --\n  left the tracked file dirty with nothing changed but its endings, to be restored by hand after each commit. A dirty\n  tracked file is what Level Factory folds into its build fingerprint (`tests/test_catalog_transients.py`, roadmap 73),\n  so a hook\'s leftover could cache-miss every later job of a run. It writes `newline="\\n"`. Queued since 0.294.0 to\n  ride the next change and missed by 0.295.0. Tests: tests/test_catalog_transients.py (fails on 0.295.0).\n\n## [0.295.0] - a storey nobody reaches is a facade\n')], 'VERSION': [('lines 1-1', 'Deli Counter 0.295.0', 'Deli Counter 0.295.1')], 'catalog.py': [('lines 174-174', '    with open(out, "w", encoding="utf-8") as f:\n', '    # LF ON EVERY PLATFORM (0.295.1): text mode wrote CRLF on Windows, so every commit hook left this tracked file\n    # dirty with nothing changed but its endings -- and a dirty tracked file is folded into Level Factory\'s build\n    # fingerprint, the cache-busting roadmap 73 fixed for the transients (tests/test_catalog_transients.py)\n    with open(out, "w", encoding="utf-8", newline="\\n") as f:\n')], 'tests/test_catalog_transients.py': [('lines 26-27', 'import shutil\nfrom pathlib import Path\n', 'import shutil\nimport subprocess\nimport sys\nfrom pathlib import Path\n'), ('lines 74-74', '        transient.unlink(missing_ok=True)\n', '        transient.unlink(missing_ok=True)\n\n\ndef test_writing_the_catalogue_leaves_it_byte_identical():\n    """FAILS ON 0.295.0 ON WINDOWS: `catalog.py` wrote in text mode, CRLF, so every commit hook left CATALOG.md dirty\n    with only its endings changed -- the same dirty tracked file this module\'s roadmap 73 guard exists for."""\n    out = SPECS / "CATALOG.md"\n    before = out.read_bytes()\n    try:\n        subprocess.run([sys.executable, str(HERE / "catalog.py")], cwd=HERE, check=True, capture_output=True)\n        after = out.read_bytes()\n        assert b"\\r\\n" not in after, "catalog.py wrote CRLF"\n        assert after == before, "catalog.py moved CATALOG.md"\n    finally:\n        out.write_bytes(before)\n')]}
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
