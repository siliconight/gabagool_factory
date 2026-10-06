"""Level Factory 0.145.0: the lot library by default, wherever it can honour
the brief.

The walker, 2026-10-06: yes. Three of the breadth sweep's ten missions named no
`lot_library`, so each placed one generated shell N times (restaurant_row_001:
three copies; warehouse_yard_001: two) and stood no Empties, which need a
library. A blanket default would have been wrong: `anchor_families` finds no
family for `county_hospital` in today's library (it has clinics), so a hospital
brief would have lost its hospital -- the "bank block with no bank" failure the
anchor rule exists to stop.

So: decided once, at `batch create`, and written into the workspace's copy of
the brief, which `plan`, `run` and the functional lock all read. A brief that
names no library, asks for two or more buildings, and whose archetype anchors
on a family in the configured Deli Counter's `build/` gets that library. Every
other brief is stored as written. `"none"` keeps the generated shell and is
stored as no library.

    python patch_lf_lot_library_default.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

BRIEF_MODEL_OLD = '''def _brief_model(brief: dict) -> MissionBrief:
    fields = {k: v for k, v in brief.items() if k in MissionBrief.__dataclass_fields__}
    fields.pop("schema", None)
'''
BRIEF_MODEL_NEW = '''def _brief_model(brief: dict) -> MissionBrief:
    fields = {k: v for k, v in brief.items() if k in MissionBrief.__dataclass_fields__}
    fields.pop("schema", None)
    # `"none"` is the brief's word for "no library" (0.145.0), never a path.
    if str(fields.get("lot_library") or "").strip().lower() == LOT_LIBRARY_NONE:
        fields["lot_library"] = ""
'''

HELPER_ANCHOR = '''# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def cmd_init(args) -> int:
'''
HELPER_NEW = '''#: A brief's word for "place my own generated building" (0.145.0).
LOT_LIBRARY_NONE = "none"


def _default_lot_library(ws: Workspace, brief: dict) -> str:
    """Give a brief the workspace's lot library when it named none and the
    library can honour it (0.145.0). Changes `brief` in place; returns the
    line to print, or "" when there is nothing to say.

    WHY A DEFAULT. A brief without `lot_library` places one generated shell
    N times -- roadmap item 37's four-building site that is one building four
    times -- and stands no Empties, which draw from the library. The breadth
    sweep built three such missions (restaurant_row_001 three copies,
    warehouse_yard_001 two, county_hospital_001 one). The walker, 2026-10-06:
    the library by default.

    WHY ONLY SOMETIMES. The library places a lot anchored on the brief's
    archetype (`building_library.anchor_families`, the rule `pick_lot`
    draws with), and today it holds no family for `county_hospital`. A
    blanket default would swap that mission's hospital for whatever the seed
    drew: the "bank block with no bank" the anchor rule was written for. And
    `lot_for` places no lot at all for fewer than two buildings, so a
    library there would change the brief's signature and nothing else.

    WHY HERE. Decided once, when the brief enters the workspace, and recorded
    in the workspace's copy, which `plan`, `run` and the functional lock all
    read. A mission already in a workspace keeps the brief it was graded on;
    the library stayed opt-in until now for exactly that reason.
    """
    mid = brief.get("mission_id", "?")
    word = str(brief.get("lot_library") or "").strip()
    if word.lower() == LOT_LIBRARY_NONE:
        brief["lot_library"] = ""
        return f"[batch] {mid}: no lot library, as the brief asks"
    if word:
        return ""
    count = int(brief.get("building_count", 1) or 1)
    if count < 2:
        return ""
    deli = (ws.load_tools_local().get("repositories") or {}).get("deli_counter")
    build = Path(str(deli)) / "build" if deli else None
    if build is None or not build.is_dir():
        return (f"[batch] {mid}: no lot library in the brief and no Deli Counter "
                f"build to default to; it places its generated building")
    from packages.pipeline import building_library
    archetype = str(brief.get("archetype") or "")
    complete = building_library.index(build)[0]
    anchors = building_library.anchor_families(complete, archetype)
    if not anchors:
        return (f"[batch] {mid}: keeps its generated building -- the library at "
                f"{build} has no family for archetype {archetype!r}")
    brief["lot_library"] = str(build)
    return (f"[batch] {mid}: no lot library in the brief; drawing from {build} "
            f"(archetype {archetype!r} anchors on {', '.join(anchors)})")


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def cmd_init(args) -> int:
'''

BATCH_OLD = '''        brief = json.loads(brief_src.read_text(encoding="utf-8"))
        mdir = ws.mission_dir(batch_id, mission_id)
'''
BATCH_NEW = '''        brief = json.loads(brief_src.read_text(encoding="utf-8"))
        # THE LOT LIBRARY BY DEFAULT (0.145.0): decided once, here, and kept
        # in the workspace's copy of the brief -- see `_default_lot_library`.
        note = _default_lot_library(ws, brief)
        if note:
            print(note)
        mdir = ws.mission_dir(batch_id, mission_id)
'''

MODEL_OLD = '''    #: grade.
    lot_library: str = ""
'''
MODEL_NEW = '''    #: grade.
    #:
    #: THE DEFAULT SINCE 0.145.0, where it can honour the brief: `batch create`
    #: writes the workspace's Deli Counter `build/` here when the brief names
    #: none, asks for two or more buildings, and its archetype anchors on a
    #: family there (`apps/cli/commands._default_lot_library`). The workspace's
    #: copy of the brief records it, so a mission already graded keeps the
    #: brief it was graded on. `"none"` keeps the generated shell.
    lot_library: str = ""
'''

TEST = '''"""The lot library by default, wherever it can honour the brief (0.145.0).

The breadth sweep built three missions that named no `lot_library`: one
generated shell placed N times, and no Empties. A blanket default would have
cost county_hospital_001 its hospital -- today's library has no hospital
family -- so the default follows the anchor rule `pick_lot` draws with, and
`lot_for`'s own floor of two buildings.

Run:  python -m pytest tests/unit/test_lot_library_default.py -q
"""
from apps.cli.commands import LOT_LIBRARY_NONE, _brief_model, _default_lot_library


class _WS:
    def __init__(self, deli):
        self._deli = deli

    def load_tools_local(self):
        return {"repositories": {"deli_counter": str(self._deli)} if self._deli else {}}


def _library(tmp_path, ids=("deli_a01", "warehouse_a01", "clinic_a01", "bank_tower_a01")):
    build = tmp_path / "deli_counter" / "build"
    build.mkdir(parents=True)
    for aid in ids:
        for suf in (".glb", ".gameplay.json", ".validation.json"):
            (build / (aid + suf)).write_text("{}")
        (build / (aid + ".slots.json")).write_text('{"coverage": {"wall": 40}}')
    return tmp_path / "deli_counter", build


def _brief(**kw):
    return {"mission_id": "m", "building_count": 3, **kw}


def test_a_brief_whose_archetype_the_library_anchors_gets_the_library(tmp_path):
    """FAILS BEFORE 0.145.0: restaurant_row_001 (corner_deli, 3) and
    warehouse_yard_001 (industrial_warehouse, 2) placed generated copies."""
    deli, build = _library(tmp_path)
    for archetype, count in (("corner_deli", 3), ("industrial_warehouse", 2)):
        b = _brief(archetype=archetype, building_count=count)
        note = _default_lot_library(_WS(deli), b)
        assert b["lot_library"] == str(build), b
        assert "anchors on" in note


def test_an_archetype_with_no_family_keeps_its_generated_building(tmp_path):
    """county_hospital_001's case: a clinic is not a hospital."""
    deli, _ = _library(tmp_path)
    b = _brief(archetype="county_hospital")
    note = _default_lot_library(_WS(deli), b)
    assert "lot_library" not in b
    assert "no family for archetype 'county_hospital'" in note


def test_one_building_is_left_alone(tmp_path):
    """`lot_for` places no lot below two buildings, so a library there would
    change the signature and nothing else."""
    deli, _ = _library(tmp_path)
    b = _brief(archetype="corner_deli", building_count=1)
    assert _default_lot_library(_WS(deli), b) == "" and "lot_library" not in b


def test_a_brief_that_names_a_library_or_says_none_is_obeyed(tmp_path):
    deli, _ = _library(tmp_path)
    own = _brief(archetype="corner_deli", lot_library="D:/elsewhere/build")
    assert _default_lot_library(_WS(deli), own) == ""
    assert own["lot_library"] == "D:/elsewhere/build"
    none = _brief(archetype="corner_deli", lot_library="None")
    _default_lot_library(_WS(deli), none)
    assert none["lot_library"] == ""


def test_no_deli_counter_configured_changes_nothing(tmp_path):
    b = _brief(archetype="corner_deli")
    note = _default_lot_library(_WS(None), b)
    assert "lot_library" not in b and "no Deli Counter build" in note


def test_none_is_never_read_as_a_path():
    model = _brief_model(_brief(display_name="m", lot_library=LOT_LIBRARY_NONE))
    assert model.lot_library == ""
'''

EDITS = {
    LF / "apps/cli/commands/__init__.py": [
        (BRIEF_MODEL_OLD, BRIEF_MODEL_NEW), (HELPER_ANCHOR, HELPER_NEW), (BATCH_OLD, BATCH_NEW)],
    LF / "packages/core/models.py": [(MODEL_OLD, MODEL_NEW)],
}
NEW_FILES = {LF / "tests/unit/test_lot_library_default.py": TEST}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in NEW_FILES.items():
        assert not path.exists(), f"{path} already exists"
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
