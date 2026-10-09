"""Zoo 1.90.0: the sign over a door is painted smooth, in its owner's face, and sampled filtered.

Roadmap 219, the walker's note 10, walking club_block_014 on 2026-10-09: "need better looking
fonts on these signs", then "use Blue Highway for the shop signs". The sign photographed,
strip_club_a01's door box, is Zoo's: in cold run 9213's package its material is
`M_SignBox_Face_SignBox_Face_256x52_..._Face`, `_card_atlas.build_art`'s, and no Pixelcoat sign
pack is in that package at all. `storefront_names.paint` set the name in `pixel_type`'s Pixel
Operator at 80 px a metre and `sign_box` sampled it Closest.

Now the name is `smooth_type` coverage at three times the texel, in the voice's face -- Blue
Highway Condensed for a shop (the weight recommended to the walker with the mock-up), Aileron
Bold for a civic building (the catalog's institution) -- outlined in the rule, and `sign_box`
builds the art `smooth` (a bled gutter, a Linear sampler).

Anchored edits, every file pinned by hash, every anchor once, nothing written until all match:
- `zoo_keeper/core/storefront_names.py`: numpy; everything from `TEXEL` to the end, asserted
  equal to `zoo_sign_smooth/old_paint_block.py.txt`, becomes `new_paint_block.py.txt`;
- `zoo_keeper/recipes/sign_box.py`: the face tile carries its voice; `build_art(..., smooth=True)`;
- `tests/test_storefront_names.py`: `smooth_type` imported; the every-name test paints each
  name in its own voice; five tests (`tests_new.py.txt`); the built test asks the sampler.
CHANGELOG and VERSION from `zoo_sign_smooth/CHANGELOG_1.90.0.md`.

    python patch_zoo_sign_smooth.py [--suite-pending]
    ZOO_ROOT=<copy> python patch_zoo_sign_smooth.py --draft

`--draft` lets a changelog still carrying RESULT_ placeholders through, and only against a
ZOO_ROOT copy. `--suite-pending` lets exactly one through, RESULT_SUITE, into the repo: the
suite's count is only true of the repo's own checkout, so it is run after this writes and filled
in by hand before the commit, which a grep for RESULT_ guards.
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ZOO = pathlib.Path(os.environ.get("ZOO_ROOT") or HERE.parent / "zoo")
SRC = HERE / "zoo_sign_smooth"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

#: sha256[:16] of each file as read on 2026-10-09 for this patch
SHA = {
    "zoo_keeper/core/storefront_names.py": "db4fb25850f647eb",
    "zoo_keeper/recipes/sign_box.py": "d38d76bfb7655b09",
    "tests/test_storefront_names.py": "45540d6d06f325e0",
}

OLD_BLOCK = (SRC / "old_paint_block.py.txt").read_bytes().decode("utf-8")
NEW_BLOCK = (SRC / "new_paint_block.py.txt").read_bytes().decode("utf-8").replace("\r\n", "\n")
TESTS_NEW = (SRC / "tests_new.py.txt").read_bytes().decode("utf-8").replace("\r\n", "\n")

SN_IMPORT_OLD = "import re\nimport zlib\n\nfrom . import club_names as CN\n"
SN_IMPORT_NEW = "import re\nimport zlib\n\nimport numpy as np\n\nfrom . import club_names as CN\n"

BOX_OLD = (
    "        tiles = {\"face\": {\"kind\": \"storefront_sign\", \"w_m\": w, \"h_m\": h,\n"
    "                          \"text\": said[\"text\"], \"colours\": said[\"colours\"]},\n"
    "                 \"edge\": {\"kind\": \"storefront_sign\", \"w_m\": 0.1, \"h_m\": 0.1, \"edge\": True,\n"
    "                          \"text\": \"\", \"colours\": said[\"colours\"]}}\n"
    "        got, _atlas = build_art([front, rim], collection, dict(plan, _tiles=tiles), streams,\n"
    "                                \"SignBox_Face\", roughness=SIGN_ROUGHNESS,\n"
    "                                lit=(PY.GLOW_EMISSION, SIGN_ALBEDO))\n"
)
BOX_NEW = (
    "        # IN ITS OWNER'S HAND, PAINTED SMOOTH (1.90.0): the name is coverage\n"
    "        # at three times the texel, in the face of the voice the kind speaks\n"
    "        # in, so the art is built `smooth` -- a bled gutter and a filtered\n"
    "        # sample -- where Closest would step every edge of it\n"
    "        tiles = {\"face\": {\"kind\": \"storefront_sign\", \"w_m\": w, \"h_m\": h,\n"
    "                          \"text\": said[\"text\"], \"colours\": said[\"colours\"],\n"
    "                          \"voice\": SN.voice_for(said[\"kind\"])},\n"
    "                 \"edge\": {\"kind\": \"storefront_sign\", \"w_m\": 0.1, \"h_m\": 0.1, \"edge\": True,\n"
    "                          \"text\": \"\", \"colours\": said[\"colours\"]}}\n"
    "        got, _atlas = build_art([front, rim], collection, dict(plan, _tiles=tiles), streams,\n"
    "                                \"SignBox_Face\", roughness=SIGN_ROUGHNESS,\n"
    "                                lit=(PY.GLOW_EMISSION, SIGN_ALBEDO), smooth=True)\n"
)

T_IMPORT_OLD = ("from zoo_keeper.core import price_pylon_forms as PY\n"
                "from zoo_keeper.core import storefront_names as SN\n")
T_IMPORT_NEW = ("from zoo_keeper.core import price_pylon_forms as PY\n"
                "from zoo_keeper.core import smooth_type as ST\n"
                "from zoo_keeper.core import storefront_names as SN\n")
T_EVERY_OLD = (
    "def test_every_name_sets_on_every_sign_the_library_derives():\n"
    "    texts = SN.all_strings() + list(CN.NAMES) + [str(SN.NUMBERS[1])]\n"
    "    for w in WIDTHS:\n"
    "        for t in texts:\n"
    "            c = SN.paint({\"w_m\": w, \"h_m\": 0.6, \"text\": t, \"colours\": PY.COLOURWAYS[0]})\n"
    "            assert not c.unset, (w, t)\n"
)
T_BPY_OLD = "    assert pbr.get(\"roughnessFactor\", 1.0) == pytest.approx(1.0), pbr\n"
T_BPY_NEW = (
    T_BPY_OLD
    + "    # 1.90.0: the face is sampled with filtering (glTF magFilter 9729): its\n"
    "    # letter is coverage, which Closest would step -- and a texture every\n"
    "    # sampler filters ships VRAM-compressed (Level Factory 0.128.0)\n"
    "    used = [t[\"index\"] for t in (pbr.get(\"baseColorTexture\"), face.get(\"emissiveTexture\")) if t]\n"
    "    assert used, face\n"
    "    for ti in used:\n"
    "        assert doc[\"samplers\"][doc[\"textures\"][ti][\"sampler\"]][\"magFilter\"] == 9729, face[\"name\"]\n"
)

EDITS = {
    "zoo_keeper/core/storefront_names.py": [(SN_IMPORT_OLD, SN_IMPORT_NEW), (OLD_BLOCK, NEW_BLOCK)],
    "zoo_keeper/recipes/sign_box.py": [(BOX_OLD, BOX_NEW)],
    "tests/test_storefront_names.py": [(T_IMPORT_OLD, T_IMPORT_NEW), (T_EVERY_OLD, TESTS_NEW),
                                       (T_BPY_OLD, T_BPY_NEW)],
}
#: the old block is the file's tail: what replaces it is the whole of the end
TAILS = {"zoo_keeper/core/storefront_names.py": OLD_BLOCK}

CHANGELOG_HEAD = ("## [1.89.0] - the payphone lit: a backlit header, a hood lamp's diffuser, "
                  "and the lamp's marker\n")


def _stage(root, edits):
    """{path: bytes}: every file's new content, every anchor matched once;
    raises before anything is written. Every target is LF and stays so."""
    staged = {}
    for rel, pairs in edits.items():
        p = root / rel
        d = p.read_bytes()
        got = hashlib.sha256(d).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        assert b"\r\n" not in d and b"\r" not in d, (rel, "has CR; this patch writes LF files")
        t = d.decode("utf-8")
        if rel in TAILS:
            assert t.endswith(TAILS[rel]), (rel, "the old block is not the file's tail")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = t.encode("utf-8")
    return staged


def main():
    if DRAFT and not os.environ.get("ZOO_ROOT"):
        sys.exit("refusing: --draft is for a ZOO_ROOT copy, never the repo")
    v = (ZOO / "VERSION").read_bytes()
    assert v == b"1.89.0", repr(v)
    staged = _stage(ZOO, EDITS)
    entry = (SRC / "CHANGELOG_1.90.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [1.90.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    cl = ZOO / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r" not in data, "CHANGELOG.md is not LF"
    text = data.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    assert "## [1.90.0]" not in text, "already applied"
    # Every anchor and hash matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    # one blank line between entries, the file's convention (1.89.0's patch
    # joined its entry to 1.88.0's heading without one; left as published)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8"))
    (ZOO / "VERSION").write_bytes(b"1.90.0")
    print("Zoo 1.89.0 -> 1.90.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
