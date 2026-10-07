"""Copy a package and stand the box the deli case replaced in the case's
place, leaving every other byte alone. Used to price Zoo 1.81.0's
`deli_case` (three submissions: painted metal, glass, glow) against the plain
box every deli built before it (one), on cold run 9190's own level.

    python case_box_variant.py <package> <dest> <box.glb>

THE BOX is cold run 9189's `prop_delco_1997_03_w700_d110_h130_mglass.glb`, the
module 9189's deli_a01 instanced for `deli_case_cover` -- 7.0 m long, before
Deli Counter 0.199.0 trimmed the case to 5.815 m off its wall. It is copied
beside the case's GLB and its node scaled along x by 5.815 / 7.0, so it fills
the slot the case fills. Both modules pivot at their centre.

Refuses unless the case's resource and node are each found exactly once.
"""
import pathlib
import re
import shutil
import sys

CASE = "prop_deli_case_delco_1997_03_w582_d110_h130_mglass"
SCALE_X = 5.815 / 7.0


def main():
    pkg, dest, box = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
    assert box.is_file(), box
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(pkg, dest)
    shutil.rmtree(dest / ".godot", ignore_errors=True)
    scene = dest / "lot" / "deli_a01" / "site.tscn"
    raw = scene.read_bytes()
    # the exported scene is CRLF (9190's: 2,009 of 2,009 lines); measured in
    # LF and written back in the file's own endings, so only the two edits move
    crlf = raw.count(b"\r\n")
    assert crlf in (0, raw.count(b"\n")), "mixed line endings in %s" % scene
    text = raw.decode("utf-8").replace("\r\n", "\n")
    old_path = f"res://lot/deli_a01/art/zoo/{CASE}.glb"
    new_path = f"res://lot/deli_a01/art/zoo/{box.name}"
    assert text.count(old_path) == 1, f"the case's resource found {text.count(old_path)} times"
    text = text.replace(old_path, new_path)
    node = re.compile(r'(\[node name="deli_case_cover"[^\n]*\]\ntransform = Transform3D\()'
                      r'([^,]+), (.*)\)')
    hits = node.findall(text)
    assert len(hits) == 1, f"the case's node found {len(hits)} times"
    text = node.sub(lambda m: f"{m.group(1)}{SCALE_X:.6f}, {m.group(3)})", text)
    out = text.replace("\n", "\r\n") if crlf else text
    scene.write_bytes(out.encode("utf-8"))
    assert len(out.encode("utf-8")) - len(raw) == len(new_path) - len(old_path) + len("%.6f" % SCALE_X) - 3, \
        "the scene changed in more than the two edits"
    shutil.copy2(box, dest / "lot" / "deli_a01" / "art" / "zoo" / box.name)
    print("box stood in the case's place:", new_path, "x scaled", round(SCALE_X, 6))


if __name__ == "__main__":
    main()
