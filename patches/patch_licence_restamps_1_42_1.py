"""Factory 1.42.1's tool releases: Dispatch 0.5.4, Laser Tag 0.32.1, Patina 0.32.1 and Pipeline 0.6.1 -- each the
release that carries its MIT `LICENSE`.

The walker's call, 2026-10-26: every factory repo carries MIT. Each of these four committed its `LICENSE` that day,
after the tag factory 1.41.0 named it, so factory 1.42.0 -- packaged from those tags -- shipped them as 1.41.0 did:
no `LICENSE` of their own for Dispatch, Laser Tag and Pipeline, Patina's earlier one (the factory's
docs/findings/stranger_install/zip_same_1420.out.txt). A release is how a commit reaches the package, so each gets
one: VERSION and a CHANGELOG entry, nothing else. The licence commits are already on each repo's main.

What it changes (anchored; each file read as bytes, its line endings kept; nothing written unless all four match):
  * dispatch, lasertag, patina, pipeline -- VERSION, and a CHANGELOG entry above the newest, in each file's own form;
    dispatch/__init__.py and patina/version.py -- the `__version__` each package stamps.

    python patches/patch_licence_restamps_1_42_1.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WHY = ("The walker's call, 2026-10-26: every factory repo carries MIT. This repo's `LICENSE` was committed that day, "
       "after the tag factory 1.41.0 named; factory 1.42.0 packaged that tag and so shipped without it. This release "
       "carries it, and changes nothing else.")

# repo -> (old VERSION bytes, new VERSION bytes, changelog anchor (the newest entry's heading), new entry)
PLAN = {
    "dispatch": (b"0.5.3\n", b"0.5.4\n", "## v0.5.3 — 2026-10-16\n",
                 "## v0.5.4 — 2026-10-28\n\n**The MIT licence travels.** " + WHY + "\n\n"),
    "lasertag": (b"Laser Tag 0.32.0", b"Laser Tag 0.32.1", "## [0.32.0] - an arrival is at the point",
                 "## [0.32.1] - the MIT licence travels\n\n" + WHY + "\n\n"),
    "patina": (b"Patina 0.32.0", b"Patina 0.32.1", "## [0.32.0] - the Godot half is gone",
               "## [0.32.1] - the MIT licence travels\n\n### Changed\n- **`LICENSE` is MIT.** " + WHY + "\n\n"),
    "pipeline": (b"Pipeline 0.6.0", b"Pipeline 0.6.1", "## [v0.6.0] - guard-rail evidence stamped",
                 "## [v0.6.1] - the MIT licence travels\n\n" + WHY + "\n\n"),
}


#: what the package stamps on what it writes, held to VERSION by each repo's own tests
#: (dispatch's `test_drop_links`, patina's `test_version_file`): repo -> (file, old line, new line)
STAMPS = {
    "dispatch": ("dispatch/__init__.py", '__version__ = "0.5.3"\n', '__version__ = "0.5.4"\n'),
    "patina": ("patina/version.py", '__version__ = "0.32.0"\n', '__version__ = "0.32.1"\n'),
}


def main():
    out = {}
    stamps = {}
    for repo, (rel, old, new) in STAMPS.items():
        p = ROOT / repo / rel
        raw = p.read_bytes()
        crlf = raw.count(b"\r\n")
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if text.count(old) != 1:
            raise SystemExit("REFUSED: %s/%s has %r %d times; nothing written" % (repo, rel, old, text.count(old)))
        text = text.replace(old, new)
        stamps[p] = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
    for repo, (old_v, new_v, anchor, entry) in PLAN.items():
        v = ROOT / repo / "VERSION"
        if v.read_bytes() != old_v:
            raise SystemExit("REFUSED: %s/VERSION reads %r, not %r; nothing written" % (repo, v.read_bytes(), old_v))
        lic = (ROOT / repo / "LICENSE").read_text(encoding="utf-8")
        if not lic.startswith("MIT License"):
            raise SystemExit("REFUSED: %s/LICENSE is not MIT; nothing written" % repo)
        cl = ROOT / repo / "CHANGELOG.md"
        raw = cl.read_bytes()
        crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
        if crlf not in (0, lf):
            raise SystemExit("REFUSED: %s/CHANGELOG.md has mixed line endings; nothing written" % repo)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        if text.count(anchor) != 1:
            raise SystemExit("REFUSED: %s/CHANGELOG.md has its newest heading %d times; nothing written"
                             % (repo, text.count(anchor)))
        text = text.replace(anchor, entry + anchor)
        out[repo] = (v, new_v, cl, (text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    for p, body in stamps.items():
        p.write_bytes(body)
    for repo, (v, new_v, cl, body) in out.items():
        v.write_bytes(new_v)
        cl.write_bytes(body)
        print("%s: %s" % (repo, new_v.decode().strip()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
