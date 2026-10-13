"""Deli Counter 0.211.0, the suite's catch: `test_empty_door_leaf._doors` read "a sill" as "a window", and
0.211.0's front door stands raised over its stoop, with a sill under it.

The suite on `patch_dc_rowhome_stoop.py`: `test_every_empty_door_is_filled_and_has_its_collider` found one
door a shell where it wants two -- the front door's `ext_0_S_open0_sill` took it out of the count. The door
itself is as it should be, read off the built `gs_empty_rowhome_a.glb`: `ext_0_S_open0_leaf`, its collider
`ext_col_0_S_open0_leaf-convcolonly`, a lintel and now a sill. A window always carries its pane (on a
facade and in a building you enter, `_opening_piece`), so "a lintel and no pane" is the door. The control
beside it (no shell that is not a facade grows a leaf) is unchanged in what it asserts.

One anchored edit, asserted once, the file's sha16 pinned:

    python patches/patch_dc_door_leaf_raised.py
"""
import hashlib
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
REL = "test_empty_door_leaf.py"
SHA = "f281ba0cb9805a0b"
OLD = ("def _doors(names):\n"
       "    \"\"\"`ext_<storey>_<facing>_open<k>` openings with a lintel and neither a\n"
       "    sill nor a pane: the doors.\"\"\"\n"
       "    out = set()\n"
       "    for n in names:\n"
       "        m = re.match(r\"^(ext_\\d+_[NESW]_open\\d+)_lintel$\", n)\n"
       "        if m and m.group(1) + \"_sill\" not in names and m.group(1) + \"_pane\" not in names:\n"
       "            out.add(m.group(1))\n"
       "    return out\n")
NEW = ("def _doors(names):\n"
       "    \"\"\"`ext_<storey>_<facing>_open<k>` openings with a lintel and no pane:\n"
       "    the doors. A window always carries its pane; a SILL no longer says\n"
       "    window, since a rowhome's front door stands raised over its stoop with\n"
       "    a sill under it (0.211.0).\"\"\"\n"
       "    out = set()\n"
       "    for n in names:\n"
       "        m = re.match(r\"^(ext_\\d+_[NESW]_open\\d+)_lintel$\", n)\n"
       "        if m and m.group(1) + \"_pane\" not in names:\n"
       "            out.add(m.group(1))\n"
       "    return out\n")


def main():
    p = DC / REL
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA, (REL, "is not the file this patch read", got)
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    assert crlf in (0, lf), (REL, "mixed line endings")
    eol = b"\r\n" if crlf else b"\n"
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.count(OLD) == 1, (REL, "anchor", text.count(OLD))
    p.write_bytes(text.replace(OLD, NEW).encode("utf-8").replace(b"\n", eol))
    print(REL + ": a door is an opening with a lintel and no pane")


if __name__ == "__main__":
    main()
