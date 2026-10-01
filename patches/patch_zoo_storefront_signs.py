"""Zoo 1.37.0: the lit sign over a building's door says who is inside.

Cold run 9120's FLAPPHAS walk: the box over the gas station's door was lit
and blank. Not one store's defect -- Deli Counter derives a sign over the
storefront door of every building with windows and a door (102 across the
library), and `sign_box` painted its face only from a Pixelcoat sign pack,
which no theme ships, so all of them were plain glowing panels.

This patch (Zoo side; Deli Counter's `patch_dc_sign_business.py` stamps the
anchor with the building's identity):

  * NEW `core/storefront_names.py` (staged in the session scratchpad and
    copied in): the kind of business read from the identity's words, its
    name from the kind's list by the identity's crc32 -- the neon's key, so
    a club's door says what its neon says; FLAPPHAS at a gas station; plain
    words on civic buildings; a street number on anything else.
  * `core/fixtures.py`: an anchor's `business` rides its placement.
  * `bpylayer/build.py`: and reaches the recipe's plan beside `anchor_id`.
  * `recipes/sign_box.py`: with no sign pack, the face is painted art in
    one backlit atlas (material still `_Face`, so a power cut takes it),
    and the face no longer has a back lying on the cabinet's front.
  * `core/card_art.py`: dispatches the `storefront_sign` tile kind.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib
import shutil
import sys

ZOO = pathlib.Path(__file__).resolve().parents[1] / "zoo"
STAGE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None


def _edit(rel, pairs):
    p = ZOO / rel
    raw = p.read_bytes()
    assert b"\r\n" not in raw, f"{rel}: CRLF in an LF file"
    s = raw.decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
        s = s.replace(old, new)
    p.write_bytes(s.encode("utf-8"))
    print("patched", rel)


FIX_OLD = '''            if a.get("color"):
                # the gel: the lens reads in the colour of the pool it makes
                placement["gel"] = str(a.get("color"))
'''
FIX_NEW = FIX_OLD + '''            if a.get("business"):
                # WHO IS INSIDE (1.37.0): the building's identity, which the
                # sign's face reads its name from (`storefront_names`)
                placement["business"] = str(a.get("business"))
'''

BUILD_OLD = '''        sp_plan["anchor_id"] = p["anchor_id"]
'''
BUILD_NEW = BUILD_OLD + '''        # 1.37.0: and the building's identity, which a sign's face names
        if p.get("business"):
            sp_plan["business"] = p["business"]
'''

CARD_OLD = '''    if kind.startswith("pump_"):
        from . import pump_forms as PF
        return PF.paint(spec)
'''
CARD_NEW = CARD_OLD + '''    # THE SIGN OVER A DOOR (1.37.0): `storefront_names`' face
    if kind == "storefront_sign":
        from . import storefront_names as SN
        return SN.paint(spec)
'''

SIGN_FACE_OLD = '''    # Face: the lit panel, its front at x=0 (the anchor plane).
    face_t = 0.02
    bm = geometry.new_bm()
    geometry.add_box(bm, (-face_t / 2.0, 0.0, 0.0), (face_t, w, h))
    face = geometry.bm_to_object(
        bm, "SignBox_Face", collection, bevel=0.0, texel=1.0,
        rng=rng, wear=0.0)
    objs.append(face)
'''
SIGN_FACE_NEW = '''    # Face: the lit panel, its front at x=0 (the anchor plane). A sign pack
    # dresses it below; without one (1.37.0) it is painted art naming the
    # business, built here and lit in the block after the cabinet.
    face_t = 0.02
    pack = None
    skins_dir, skin_theme = materials.get_skin_library()
    if skins_dir:
        from ..core import skins as skinlib
        pack = skinlib.pick_pack(
            skinlib.find_sign_packs(skins_dir, skin_theme),
            str(plan.get("anchor_id", "")))
    face = None
    if pack:
        bm = geometry.new_bm()
        geometry.add_box(bm, (-face_t / 2.0, 0.0, 0.0), (face_t, w, h))
        face = geometry.bm_to_object(
            bm, "SignBox_Face", collection, bevel=0.0, texel=1.0,
            rng=rng, wear=0.0)
        objs.append(face)
'''

SIGN_LIT_OLD = '''    # Branded face when the skin library ships sign packs (Pixelcoat
    # ``signs_<theme>/``): the pack albedo becomes the lit artwork, picked
    # deterministically per anchor id so each storefront keeps its sign
    # across rebuilds. The material name keeps the ``_Face`` suffix — Lux's
    # emissive binder keys on it, so the power cut kills branded and flat
    # signs alike. No packs -> the flat acrylic glow, unchanged.
    pack = None
    skins_dir, skin_theme = materials.get_skin_library()
    if skins_dir:
        from ..core import skins as skinlib
        pack = skinlib.pick_pack(
            skinlib.find_sign_packs(skins_dir, skin_theme),
            str(plan.get("anchor_id", "")))
    if pack:
        _planar_uv_fit(face, w, h)
        lit = materials.make_emissive_textured_material(
            f"M_SignBox_{pack['id']}_Face", pack,
            style.get("emissive_strength", 2.2))
    else:
        lit = materials.make_emissive_material(
            "M_SignBox_Face",
            style.get("emissive_color", [1.0, 0.93, 0.78]),
            style.get("emissive_strength", 2.2))
    materials.assign([face], lit)
'''
SIGN_LIT_NEW = '''    # Branded face when the skin library ships sign packs (Pixelcoat
    # ``signs_<theme>/``): the pack albedo becomes the lit artwork, picked
    # deterministically per anchor id so each storefront keeps its sign
    # across rebuilds. The material name keeps the ``_Face`` suffix — Lux's
    # emissive binder keys on it, so the power cut kills branded and named
    # signs alike.
    if pack:
        _planar_uv_fit(face, w, h)
        lit = materials.make_emissive_textured_material(
            f"M_SignBox_{pack['id']}_Face", pack,
            style.get("emissive_strength", 2.2))
        materials.assign([face], lit)
    else:
        # NO PACK -> THE BUSINESS'S NAME (1.37.0). Until this the face was a
        # flat warm glow, and no theme ships a pack, so every derived sign
        # in the library -- 102 -- was a blank lit box (cold run 9120). The
        # name comes from the anchor's `business` (Deli Counter's identity
        # for the building); a sign without one is named from its anchor id,
        # which no kind matches, so it shows a street number -- never blank.
        from ..core import prims as P
        from ..core import storefront_names as SN
        from ..core import price_pylon_forms as PY
        from ._card_atlas import build_art
        said = SN.sign_for(plan.get("business") or plan.get("anchor_id", ""))
        front = P.mesh("SignBox_FaceFront", "glow",
                       [(0.0, -w / 2.0, -h / 2.0), (0.0, w / 2.0, -h / 2.0),
                        (0.0, w / 2.0, h / 2.0), (0.0, -w / 2.0, h / 2.0)], [(0, 1, 2, 3)])
        front["tile"] = "face"
        front["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
        # the panel's four edges; its front is the art and its back lies on
        # the cabinet's front (6 shared planes in the census until 1.37.0)
        rim = P.box("SignBox_FaceRim", "glow", (-face_t, -w / 2.0, -h / 2.0), (0.0, w / 2.0, h / 2.0))
        rim["faces"] = [f for k, f in enumerate(rim["faces"]) if k in (0, 1, 2, 4)]
        rim["tile"] = "edge"
        rim["uvs"] = [((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))] * len(rim["faces"])
        tiles = {"face": {"kind": "storefront_sign", "w_m": w, "h_m": h,
                          "text": said["text"], "colours": said["colours"]},
                 "edge": {"kind": "storefront_sign", "w_m": 0.1, "h_m": 0.1, "edge": True,
                          "text": "", "colours": said["colours"]}}
        got, _atlas = build_art([front, rim], collection, dict(plan, _tiles=tiles), streams,
                                "SignBox_Face", lit=(PY.GLOW_EMISSION, PY.GLOW_ALBEDO))
        objs += got
        print(f"[sign_box] {w:.2f} x {h:.2f} {said['kind']}: {said['text']}")
'''


def main():
    assert STAGE and (STAGE / "storefront_names.py").exists(), "pass the stage directory"
    assert not (ZOO / "zoo_keeper/core/storefront_names.py").exists(), "already applied"
    _edit("zoo_keeper/core/fixtures.py", [(FIX_OLD, FIX_NEW)])
    _edit("zoo_keeper/bpylayer/build.py", [(BUILD_OLD, BUILD_NEW)])
    _edit("zoo_keeper/core/card_art.py", [(CARD_OLD, CARD_NEW)])
    _edit("zoo_keeper/recipes/sign_box.py", [(SIGN_FACE_OLD, SIGN_FACE_NEW), (SIGN_LIT_OLD, SIGN_LIT_NEW)])
    shutil.copyfile(STAGE / "storefront_names.py", ZOO / "zoo_keeper/core/storefront_names.py")
    print("copied core/storefront_names.py")


if __name__ == "__main__":
    main()
