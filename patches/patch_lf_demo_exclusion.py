"""Level Factory 0.144.4: a shell Deli Counter calls a demo is never drawn into
a lot (roadmap 185).

The breadth sweep drew `setback_demo` and `pvp_station_ref` into
card_block_001's lots (cold runs 9170 and 9174). Of the five demo and
reference specs in Deli Counter, three were complete and drawable
(`setback_demo`, `pvp_station_ref`, `survival_demo`); `kitbash_demo` and
`rarity_demo` were held out only by incomplete builds. Deli Counter 0.187.0
writes `demo` into `<id>.validation.json`; this reads it, the way it reads
`facade`, and never the name.

    python patch_lf_demo_exclusion.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {
    LF / "packages/pipeline/building_library.py": [
        ("""    Two kinds, and they are found two different ways because they ARE two
    different things.
""",
         """    Three kinds, found two different ways because they ARE different
    things: one by the prefix this pipeline writes, two by Deli Counter's own
    word.
"""),
        ("""    floor plates with nothing joining them. A mission placed in one has
    nowhere to go.)
""",
         """    floor plates with nothing joining them. A mission placed in one has
    nowhere to go.)

    **Demos**, by Deli Counter's own word for that too (0.144.4, roadmap 185):
    `demo` in the same manifest, written by Deli Counter 0.187.0 for a spec
    that exists to demonstrate or test a capability. The breadth sweep drew
    `setback_demo` and `pvp_station_ref` into card_block_001's lots (cold runs
    9170 and 9174): complete builds carrying every manifest a building does,
    with nothing but the name to say otherwise -- and a name is not read here.
"""),
        ("""    if (data or {}).get("facade") is True:
        return ("Deli Counter reports facade=true in its validation manifest: "
                "a street wall with no interior, not a building a mission can "
                "be placed inside")
    return ""
""",
         """    if (data or {}).get("facade") is True:
        return ("Deli Counter reports facade=true in its validation manifest: "
                "a street wall with no interior, not a building a mission can "
                "be placed inside")
    if (data or {}).get("demo") is True:
        return ("Deli Counter reports demo=true in its validation manifest: a "
                "spec that demonstrates or tests a capability, not a building "
                "a level stands")
    return ""
"""),
    ],
    LF / "tests/unit/test_source_library.py": [
        ("""    _shell(tmp_path, "gs_facade_but_a_real_building", facade=False)
    _shell(tmp_path, "quiet_row_a01", facade=True)
    complete, _i, non_source = bl.index(tmp_path)
    assert [e["id"] for e in complete] == ["gs_facade_but_a_real_building"]
    assert [e["id"] for e in non_source] == ["quiet_row_a01"]
""",
         """    _shell(tmp_path, "gs_facade_but_a_real_building", facade=False)
    _shell(tmp_path, "quiet_row_a01", facade=True)
    complete, _i, non_source = bl.index(tmp_path)
    assert [e["id"] for e in complete] == ["gs_facade_but_a_real_building"]
    assert [e["id"] for e in non_source] == ["quiet_row_a01"]


def test_a_demo_is_never_drawn_and_the_rule_reads_the_flag_not_the_name(tmp_path):
    \"\"\"0.144.4, roadmap 185: the breadth sweep drew `setback_demo` and
    `pvp_station_ref` into card_block_001's lots. Deli Counter 0.187.0 writes
    `demo: true` into the validation manifest; the name says nothing. Put
    wrong on purpose both ways, as the facade rule is.\"\"\"
    _shell(tmp_path, "setback_demo_but_a_real_building", facade=False)
    _shell(tmp_path, "quiet_block_a01")
    (tmp_path / "quiet_block_a01.validation.json").write_text(
        '{"facade": false, "demo": true}')
    complete, _i, non_source = bl.index(tmp_path)
    assert [e["id"] for e in complete] == ["setback_demo_but_a_real_building"]
    assert [e["id"] for e in non_source] == ["quiet_block_a01"]
    assert "demo" in non_source[0]["reason"]
"""),
    ],
}


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
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
