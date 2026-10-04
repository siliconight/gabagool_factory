"""Deli Counter 0.176.0: one module name, one geometry, in every building.

Cold run 9148: an Empty's 3.1 m and 2.8 m walls (0.175.2) shared one Zoo
module name, and the 2.8 m panel stood in every 3.1 m slot. Across the
library as built, 14 names covered two sizes, all in the 8 facade shells.
See `dc_key_height/CHANGELOG_0.176.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  themed_tscn.py         the mirror honours `fit.key_height`;
                         `mark_height_keys(slots)`
  deli_counter.py        `write_slot_manifest` marks before writing
  docs/SLOT_MANIFEST.md  the field
Copies the test; CHANGELOG and VERSION. `python build.py --all` follows.

    python patch_dc_key_height.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_key_height"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


MIRROR_OLD = '''    height_cm = (int(round(dims[2] * 100))
                 if exact and typ in VOLUME_ROLES + CORNER_ROLES else None)
    vtag = void_tag(fit.get("voids")) if typ in PLATE_ROLES else None
    otag = opening_tag(fit.get("openings")) if typ in OPENING_ROLES else None
'''
MIRROR_NEW = '''    # `fit.key_height` (0.176.0, Zoo 1.60.0): see `mark_height_keys`.
    height_cm = (int(round(dims[2] * 100))
                 if exact and (typ in VOLUME_ROLES + CORNER_ROLES
                               or fit.get("key_height")) else None)
    vtag = void_tag(fit.get("voids")) if typ in PLATE_ROLES else None
    otag = opening_tag(fit.get("openings")) if typ in OPENING_ROLES else None
'''

MARK_ANCHOR = '''def resolve_themed_stem(slot: dict, theme: str, style: int, state: str = None,
                        material: str = None):
'''
MARK_NEW = '''def mark_height_keys(slots: list) -> list:
    """Mark ``fit.key_height`` on every slot whose module NAME would cover
    more than one height in this building; return the slots, marked.

    A wall, doorway or window is named by its width (`module_stem`: "the
    storey height is fixed"). An Empty broke that (0.175.2) -- walls 3.1 m
    where no slab sits above, 2.8 m under the roof -- and the two built as one
    Zoo file, so cold run 9148 stood 2.8 m panels in 3.1 m slots. Grouping by
    the name THIS module builds, rather than restating its key, means the
    mark can never disagree with the name it repairs. Only a colliding name
    is marked, so every other building keeps every name (on 0.175.2: 14
    names, all in the 8 facade shells). Zoo (>= 1.60.0) and
    `resolve_themed_stem` both add `_h<cm>` to a marked slot.
    """
    groups = {}
    for i, s in enumerate(slots):
        stem, unit = resolve_themed_stem(s, "greybox", 1, material=stem_material(s))
        if stem is None or unit:
            continue
        h = round(float(s["fit"]["dims"][2]), 4)
        groups.setdefault(stem, {}).setdefault(h, []).append(i)
    out = list(slots)
    for by_h in groups.values():
        if len(by_h) < 2:
            continue
        for idxs in by_h.values():
            for i in idxs:
                out[i] = dict(out[i], fit=dict(out[i].get("fit") or {}, key_height=True))
    return out


def resolve_themed_stem(slot: dict, theme: str, style: int, state: str = None,
                        material: str = None):
'''

WRITE_OLD = '''    if _unmapped:
        print(f"[deli_counter] slot manifest: {len(_unmapped)} slot(s) name a "
'''
WRITE_NEW = '''    # ONE NAME, ONE GEOMETRY (0.176.0): a name that would cover two heights
    # is marked, so Zoo builds -- and the composer asks for -- one each.
    import themed_tscn as _tt
    _slots = _tt.mark_height_keys(_slots)
    if _unmapped:
        print(f"[deli_counter] slot manifest: {len(_unmapped)} slot(s) name a "
'''

DOC_OLD = '''  - `collision` — the collision mode the replacement must provide. **Constraint:** a themed module must
'''
DOC_NEW = '''  - `key_height` — present and true only when this slot's module name would otherwise cover two
    heights in one building (0.176.0); Zoo (>= 1.60.0) and `themed_tscn` then add `_h<cm>` to the
    name. Set by `themed_tscn.mark_height_keys` as the manifest is written. Today only facade shells
    (Empties) carry it: their walls are full-storey below the roof storey and stop under the roof.
  - `collision` — the collision mode the replacement must provide. **Constraint:** a themed module must
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.175.2"
    _edit(DC / "themed_tscn.py", [(MIRROR_OLD, MIRROR_NEW), (MARK_ANCHOR, MARK_NEW)])
    _edit(DC / "deli_counter.py", [(WRITE_OLD, WRITE_NEW)])
    _edit(DC / "docs" / "SLOT_MANIFEST.md", [(DOC_OLD, DOC_NEW)])
    shutil.copyfile(SRC / "test_key_height.py", DC / "test_key_height.py")
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.176.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.176.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.176.0")


if __name__ == "__main__":
    main()
