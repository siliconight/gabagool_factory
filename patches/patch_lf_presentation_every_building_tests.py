"""Level Factory 0.149.0, the tests for `patch_lf_presentation_every_building.py`,
applied first so they are seen failing on 0.148.0.

    python patch_lf_presentation_every_building_tests.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"
GATES = LF / "tests" / "unit" / "test_presentation_gates_are_reported.py"
DRIVER_TEST = LF / "tests" / "unit" / "test_circulation_gate_reads_its_arms.py"

GATES_TAIL = '''    codes = _codes(PresentationAdapter().normalize_validation([man]))
    assert "PRESENTATION_ZFIGHT" in codes
    assert "PRESENTATION_PLACEMENT_MISMATCH" in codes
'''

GATES_ADD = '''

# ---- every placed building, not the first manifest (0.149.0) ----------------
#
# A varied lot composes one package per building, under `presentation/lot/`.
# `normalize_validation` read `next(...)` of the sorted manifests, which is
# the first building's. In cold run 9187 three of fifteen failed z-fight --
# deli_a01 203 pairs, office 121, rail_station_a02 117 -- and the one finding
# recorded was deli_a01's (`docs/findings/presentation_gates/` at the factory
# root).

def _lot(tmp_path, buildings, root=None):
    """A varied lot's outputs: one package a building, and the mission's own
    shell at the root when ``root`` is given."""
    base = tmp_path / "presentation"
    paths = []
    for bid, blocks in buildings.items():
        d = base / "lot" / bid
        d.mkdir(parents=True)
        man = {"schema": "portable.v1", "walkable": True, "closure": {"portable": True}}
        man.update(blocks)
        (d / "portable_resource_manifest.json").write_text(json.dumps(man), encoding="utf-8")
        paths.append(d / "portable_resource_manifest.json")
    if root is not None:
        base.mkdir(parents=True, exist_ok=True)
        man = {"schema": "portable.v1", "walkable": True, "closure": {"portable": True}}
        man.update(root)
        (base / "portable_resource_manifest.json").write_text(json.dumps(man), encoding="utf-8")
        paths.append(base / "portable_resource_manifest.json")
    return sorted(paths)


def test_every_placed_building_is_read(tmp_path):
    outs = _lot(tmp_path, {
        "deli_a01": {"zfight_check": dict(COLD_9005, pairs=203, solids=761)},
        "gs_empty_rowhome_a": {},
        "office": {"zfight_check": dict(COLD_9005, pairs=121, solids=422)},
        "rail_station_a02": {"zfight_check": dict(COLD_9005, pairs=117, solids=397)}})
    z = [i for i in PresentationAdapter().normalize_validation(outs)
         if i["code"] == "PRESENTATION_ZFIGHT"]
    assert sorted(i["location"] for i in z) == ["deli_a01", "office", "rail_station_a02"]
    assert all(i["message"].startswith(i["location"] + ": ") for i in z)


def test_an_unplaced_mission_shell_is_not_read_in_a_lot(tmp_path):
    """A varied lot composes the mission's own shell for the job's output
    contract and places each building instead (`_LOT_SUBDIR`). 9187's root
    package lists dangling refs; read, it would block a level that does not
    contain it."""
    outs = _lot(tmp_path, {"deli_a01": {}}, root={
        "closure": {"portable": False, "dangling_refs": ["site.tscn -> res://x.glb"]}})
    assert "PRESENTATION_UNRESOLVED_REF" not in _codes(
        PresentationAdapter().normalize_validation(outs))


def test_a_single_shell_mission_reads_its_root(tmp_path):
    outs = _lot(tmp_path, {}, root={
        "closure": {"portable": False, "dangling_refs": ["site.tscn -> res://x.glb"]}})
    assert "PRESENTATION_UNRESOLVED_REF" in _codes(
        PresentationAdapter().normalize_validation(outs))


#: cold run 9187's deli_a01, as Deli Counter 0.191.0's gate reads it: the
#: dressing arm clean, the shell arm naming a counter over the stairwell.
DELI_9187 = {"ok": False,
             "shell": {"ok": False, "source": "shell", "volumes": 14, "props": 154,
                       "declared_props": 154, "excused": [],
                       "conflicts": [{"prop": "counter_island_upper_hall_2",
                                      "volume": "stair:deli_stair_up",
                                      "penetration": 0.8}]},
             "dressing": {"ok": True, "source": "dressing", "volumes": 14,
                          "nodes": 8, "props": 249, "conflicts": []}}


def test_a_failing_circulation_arm_becomes_a_finding(tmp_path):
    """No branch read `circulation_check` at all: every cold run from 9164
    to 9187 failed it and none reached a finding."""
    issues = PresentationAdapter().normalize_validation(
        _lot(tmp_path, {"deli_a01": {"circulation_check": DELI_9187}}))
    circ = [i for i in issues if i["code"] == "PRESENTATION_CIRCULATION"]
    assert len(circ) == 1
    assert circ[0]["location"] == "deli_a01"
    assert "counter_island_upper_hall_2 0.8 m into stair:deli_stair_up" in circ[0]["message"]
    assert "(shell)" in circ[0]["message"]
    assert circ[0]["blocking"] is False and circ[0]["severity"] == "moderate"


def test_a_passing_circulation_check_says_nothing(tmp_path):
    clean = {"ok": True, "shell": dict(DELI_9187["shell"], ok=True, conflicts=[]),
             "dressing": DELI_9187["dressing"]}
    issues = PresentationAdapter().normalize_validation(
        _lot(tmp_path, {"deli_a01": {"circulation_check": clean}}))
    assert "PRESENTATION_CIRCULATION" not in _codes(issues)


def test_a_circulation_gate_that_did_not_run_is_said(tmp_path):
    broken = {"ok": False, "source": "dressing", "error": "gate failed to run: boom"}
    issues = PresentationAdapter().normalize_validation(
        _lot(tmp_path, {"office": {"circulation_check": broken}}))
    assert "gate failed to run: boom" in _one(issues, "PRESENTATION_CIRCULATION")["message"]


def test_an_unreadable_manifest_is_said(tmp_path):
    """It used to return quietly: a broken manifest silencing every finding
    about its package is "I cannot see it" reported as "it is not there"."""
    outs = _lot(tmp_path, {"office": {}})
    outs[0].write_text("{not json", encoding="utf-8")
    msg = _one(PresentationAdapter().normalize_validation(outs),
               "PRESENTATION_MANIFEST_UNREADABLE")["message"]
    assert msg.startswith("office: ")
'''

DRIVER_BODY = '''"""The circulation gate's line reads each arm it was given (0.149.0).

Deli Counter writes `circulation_check` as two arms and a verdict when a
building has a greybox and a dressing layer: `{"ok", "shell", "dressing"}`.
The driver printed `len(circ["conflicts"])` and `circ.get("volumes", "?")`
from the top of that, so every cold run from 9164 to 9187 logged

    [compose] circulation gate [FAIL]: 0 prop conflict(s) across ? circulation volume(s)

-- a FAIL with nothing in it, on every building, which is a line nobody reads.
"""
import importlib.util
import sys
from pathlib import Path

_SCRIPT = (Path(__file__).resolve().parents[2] / "assets" / "scripts"
           / "run_presentation_compose.py")


def _driver():
    spec = importlib.util.spec_from_file_location("run_presentation_compose",
                                                  _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


TWO_ARMS = {"ok": False,
            "shell": {"ok": False, "volumes": 14, "props": 154,
                      "excused": [{"prop": "stair_guard_back_15",
                                   "volume": "stair:s0", "penetration": 0.34}],
                      "conflicts": [{"prop": "counter_island_upper_hall_2",
                                     "volume": "stair:deli_stair_up",
                                     "penetration": 0.8}]},
            "dressing": {"ok": True, "volumes": 14, "nodes": 8, "props": 249,
                         "conflicts": []}}


def test_the_line_reads_each_arm():
    line, details = _driver().circulation_gate(TWO_ARMS)
    assert line.startswith("[compose] circulation gate [FAIL]: ")
    assert "shell 1 conflict(s) across 14 volume(s), 1 excused" in line
    assert "dressing 0 conflict(s) across 14 volume(s)" in line
    assert details == ["[compose]   shell: counter_island_upper_hall_2 intrudes "
                       "0.8m into stair:deli_stair_up"]


def test_one_arm_reads_its_own_counts():
    line, details = _driver().circulation_gate(
        {"ok": True, "source": "shell", "volumes": 9, "props": 3, "conflicts": []})
    assert line == ("[compose] circulation gate [OK]: shell 0 conflict(s) "
                    "across 9 volume(s)")
    assert details == []


def test_an_arm_that_did_not_run_says_why():
    line, _ = _driver().circulation_gate(
        {"ok": False, "source": "dressing", "error": "gate failed to run: boom"})
    assert "dressing 0 conflict(s) across ? volume(s) (gate failed to run: boom)" in line
'''


def main():
    data = GATES.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(GATES_TAIL), "the gates test no longer ends where it did"
    assert "_lot(" not in text
    assert not DRIVER_TEST.exists(), DRIVER_TEST
    GATES.write_bytes((text + GATES_ADD).encode("utf-8"))
    DRIVER_TEST.write_bytes(DRIVER_BODY.encode("utf-8"))
    print("tests: 7 adapter cases, 3 driver cases")


if __name__ == "__main__":
    main()
