"""Level Factory 0.151.0's tests, written first: the bake lays the rooms'
floor and frees it before it saves.

    python patch_lf_room_fill_tests.py

Appends two tests to `level_factory/tests/unit/test_light_bake.py` (8,335
bytes, LF, as read 2026-10-07). On 0.150.0 both must fail: the plugin never
asks Lux for a fill, and the report carries no `room_fills`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "level_factory" / "tests" / "unit" / "test_light_bake.py"

TAIL_OLD = ('    issues = [i for i in scan_closure(pkg).issues if i.startswith(LB.REPORT)]\n'
            '    assert issues == [], issues\n')
TAIL_NEW = TAIL_OLD + '''

def test_the_bake_lays_the_rooms_floor_and_frees_it_before_it_saves():
    """THE ROOMS' FLOOR (0.151.0). Lux >= 0.68.0 lays bake-only fills over the
    level's room probes (`LuxLightLoader.add_bake_fills`): the lightmap must
    keep their light and the shipped scene must not keep them. The plugin
    runs only inside the editor, so its order is read off its source: laid
    before the button is pressed, freed before the scene is saved, counted in
    the result."""
    src = LB.PLUGIN_SCRIPT.read_text(encoding="utf-8")
    lay = src.find("_fill = _lay_room_fill(")
    press = src.find("b.pressed.emit()")
    free = src.find("_free_room_fill()\\n\\t\\t\\t_busy = true\\n\\t\\t\\tEditorInterface.save_scene()")
    assert '"add_bake_fills"' in src, "the plugin never asks Lux for the rooms' floor"
    assert 0 <= lay < press, "the floor must be laid before Bake is pressed"
    assert free > press, "the floor must be freed after the bake and before the save"
    assert '"room_fills": _fill_count' in src, "the result must say how many fills the bake held"


def test_a_bake_reports_its_room_fills(tmp_path, monkeypatch):
    """What the plugin counted reaches `light_bake.json` and the export log."""
    pkg = _package(tmp_path)
    monkeypatch.setattr(LB, "_import", lambda d, g: True)

    def fake_editor(cmd, timeout):
        work = Path(cmd[cmd.index("--path") + 1])
        (work / LB.RESULT).write_text(json.dumps({"ok": True, "users": 12, "room_fills": 30}), encoding="utf-8")
        (work / "bake.tscn").write_text("[gd_scene format=3]\\n", encoding="utf-8")
        for f in ("bake.lmbake", "bake.exr", "bake.exr.import"):
            (work / f).write_text("x", encoding="utf-8")
        return 0, 3.0
    monkeypatch.setattr(LB, "_run", fake_editor)
    said = []
    r = LB.bake(pkg, "godot.exe", log=said.append)
    assert r["ok"] is True, r
    assert r["room_fills"] == 30
    assert json.loads((pkg / LB.REPORT).read_text(encoding="utf-8"))["room_fills"] == 30
    assert any("30 room fill(s)" in s for s in said), said
'''


def main():
    data = TEST.read_bytes()
    assert len(data) == 8335, "test file is %d bytes, read at 8,335" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(TAIL_OLD) == 1 and text.endswith(TAIL_OLD), "the tail anchor is not the file's end"
    TEST.write_bytes(text.replace(TAIL_OLD, TAIL_NEW).encode("utf-8"))
    print("test_light_bake.py: %d -> %d bytes" % (len(data), len(TAIL_NEW) - len(TAIL_OLD) + len(data)))


if __name__ == "__main__":
    main()
