"""Zoo README: the floater concept (roadmap 234), a section after Connectors -- documentation only.

Inserts `zoo_floaters/README_floaters.md` ahead of "## Organizing a collection", so it follows
"## Connectors (Lego-style anchoring)", the other concept about how parts meet. The README is pinned
by hash and the anchor asserted once; nothing written on a miss. No VERSION or CHANGELOG: Zoo takes
documentation-only commits ("docs: Adding a species ...", 531db42, f1fdf82), and the helper this
section describes will carry the version when it is built. Applied after factory 1.38.0's tags, so
Zoo's v1.100.0 tag stays on the release commit.

    python patches/patch_zoo_floaters_readme.py
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
README = ZOO / "README.md"
SECTION = HERE / "zoo_floaters" / "README_floaters.md"
SHA = "cff056ea88ebcc73"
ANCHOR = "## Organizing a collection (exhibits: zoo / museum)\n"


def main():
    raw = README.read_bytes()
    assert b"\r\n" not in raw, "Zoo's README is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA, ("README.md is not the file this patch read", got)
    text = raw.decode("utf-8")
    assert "## Floaters" not in text, "already applied"
    assert text.count(ANCHOR) == 1, ("the anchor", text.count(ANCHOR))
    section = SECTION.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    assert section.startswith("## Floaters (details laid on a surface"), section[:60]
    text = text.replace(ANCHOR, section.rstrip("\n") + "\n\n" + ANCHOR)
    README.write_bytes(text.encode("utf-8"))
    print("Zoo README: the floater concept, after Connectors")


if __name__ == "__main__":
    sys.exit(main())
