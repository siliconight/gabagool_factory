"""Lux 0.63.0: the roller grill's heat lamp -- a `heat_lamp` rig for the
marker Zoo 1.57.x emits under the grill's hood. The walker, 2026-10-03: "a
dim but warm warming light to bring a bit more light to the dogs", and then
"light should show the buns too": an omni under the hood's top, a glow at
the measured level with a flattened falloff.

Anchored edits on `lux_light_loader.gd` (every anchor once; refuses on a
miss): the constants block (`lux_heat_lamp/consts.gd.txt`) after
`COUNTER_ACCENT_LEVEL`, the `"heat_lamp"` branch (`lux_heat_lamp/
branch.gd.txt`) before `"counter_accent"`; `tools/heat_lamp_selftest.gd`
copied from `lux_heat_lamp/`; CHANGELOG and VERSION from
`lux_heat_lamp/CHANGELOG_0.63.0.md`.

    python patch_lux_heat_lamp.py
    LUX_ROOT=<copy> python patch_lux_heat_lamp.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_heat_lamp"


def main():
    v = (LUX / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lux 0.62.0", v
    consts = (SRC / "consts.gd.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    branch = (SRC / "branch.gd.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert consts.startswith("## THE HEAT LAMP (0.63.0)") and branch.startswith('\t\t"heat_lamp":\n')
    p = LUX / "addons" / "lux" / "runtime" / "lux_light_loader.gd"
    s = p.read_text(encoding="utf-8")
    assert "heat_lamp" not in s, "already applied"
    a = "const COUNTER_ACCENT_LEVEL := 2.0\n"
    assert s.count(a) == 1
    s = s.replace(a, a + consts)
    b = '\t\t"counter_accent":\n'
    assert s.count(b) == 1
    s = s.replace(b, branch + b)
    p.write_text(s, encoding="utf-8", newline="\n")
    t = LUX / "tools" / "heat_lamp_selftest.gd"
    t.write_bytes((SRC / "heat_lamp_selftest.gd").read_bytes())
    entry = (SRC / "CHANGELOG_0.63.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LUX / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.63.0]" not in d
    head = b"# Changelog\n\n"
    assert d.startswith(head)
    cl.write_bytes(head + entry.encode("utf-8") + d[len(head):])
    (LUX / "VERSION").write_bytes(b"Lux 0.63.0")
    print("0.62.0 -> 0.63.0")


if __name__ == "__main__":
    main()
