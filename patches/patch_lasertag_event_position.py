"""Laser Tag 0.23.2: a named event is logged at the position it carries.

`LT_MetricsCollector.record_event` ended `_log_event(event_name, null,
Vector3.ZERO, metadata)`, so every named event -- PlayerStuck, EnemyStuck,
RouteProgress, ObjectiveReached -- went into the report with a top-level
`position` of (0, 0, 0), while both stuck emitters (`LT_BotPlayerController.
_update_stuck`, `LT_EnemyBrain._on_stuck`) put the real one in
`metadata.position`. Every reader took the top-level field, and Level
Factory's cold-run notes for 9140 and 9141 recorded seed 9181's stuck events
as carrying "no position" and left two attributions open on it. Read from
the metadata, 1,354 of that candidate's 1,378 stuck events are the crew at
one spot, Godot (55.3, 6.0, 13.1) -- six metres up.

Anchored edit (once; refuses on a miss): `LT_MetricsCollector.gd`. The test
runner copied from `lasertag_event_position/`. CHANGELOG and VERSION from
`lasertag_event_position/CHANGELOG_0.23.2.md`.

    python patch_lasertag_event_position.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LT = HERE.parent / "lasertag"
SRC = HERE / "lasertag_event_position"


def main():
    v = (LT / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Laser Tag 0.23.1", v
    p = LT / "addons" / "laser_tag_tool" / "scripts" / "metrics" / "LT_MetricsCollector.gd"
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    old = ("\t\t\"TeamWipe\":\n"
           "\t\t\tcurrent[\"team_wipe\"] = true\n"
           "\t_log_event(event_name, null, Vector3.ZERO, metadata)\n")
    new = ("\t\t\"TeamWipe\":\n"
           "\t\t\tcurrent[\"team_wipe\"] = true\n"
           "\t# Logged where the event happened when it says (0.23.2): the stuck\n"
           "\t# emitters carry it in `metadata.position`, and a top-level (0, 0, 0)\n"
           "\t# read as \"no position\" to every reader of the report.\n"
           "\tvar at := Vector3.ZERO\n"
           "\tvar p: Variant = metadata.get(\"position\", null)\n"
           "\tif p is Array and (p as Array).size() >= 3:\n"
           "\t\tat = Vector3(float(p[0]), float(p[1]), float(p[2]))\n"
           "\t_log_event(event_name, null, at, metadata)\n")
    assert s.count(old) == 1, "anchor"
    s = s.replace(old, new)
    p.write_bytes((s.replace("\n", "\r\n") if crlf else s).encode("utf-8"))
    shutil.copyfile(SRC / "test_event_carries_its_position.gd",
                    LT / "addons" / "laser_tag_tool" / "runners" / "tests" / "test_event_carries_its_position.gd")
    ch = LT / "CHANGELOG.md"
    c = ch.read_text(encoding="utf-8")
    assert c.startswith("# Changelog\n\n## [0.23.1]"), "changelog head"
    c = c.replace("# Changelog\n\n", "# Changelog\n\n" + (SRC / "CHANGELOG_0.23.2.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n", 1)
    ch.write_text(c, encoding="utf-8", newline="\n")
    (LT / "VERSION").write_text("Laser Tag 0.23.2", encoding="utf-8", newline="\n")
    print("Laser Tag 0.23.2 applied")


if __name__ == "__main__":
    main()
