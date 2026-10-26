"""Level Factory 0.253.0 on a clone: the Level Standard's designer brief (its section 16) on the Level tab -- Players,
which Lot and Laser Tag read, and the fantasy, scale, density, tone and playstyle, saved as intent. Anchored; refuses
on a miss.

    python edit_lf_brief.py <clone>

Copies tests/service/test_brief_fields.py from `src/`; adds the controls to `design.capabilities`, keeps the
standard's intent out of the pipeline's brief, and widens test_design's intent census by those five.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("tests/service/test_brief_fields.py",):
    dst = C / rel
    assert not dst.exists(), rel
    shutil.copyfile(HERE / "src" / rel, dst)
    print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    t = p.read_bytes().decode("utf-8")
    assert "\r\n" not in t
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes(t.encode("utf-8"))
    print("edited", rel, len(edits))


edit("packages/service/design.py", [
    ('''_INTENT_LABELS = {"route_shape": "Route shape",''', '''#: The Level Standard's designer brief (docs/LEVEL_STANDARD.md, the walker's section 16) that no tool reads yet:
#: saved with the design for the designer and for review, and kept OUT of the pipeline's brief, whose fields are
#: level_factory.mission_brief.v0.1's. Its HEIST, LOCATION and TIME are the template, Streets / Beyond the edge and
#: Time of day; its PLAYERS is the Players control; its TARGET SESSION is the template's ``target_minutes``, which
#: Lot's pacing estimate is measured against.
STANDARD_INTENT = (("fantasy", "Fantasy", "longtext",
                    "One sentence: what the crew is trying to do here, and what makes this place worth it."),
                   ("scale", "Scale", "text", "Small, medium or large, in your words."),
                   ("density", "Density", "text", "How tightly the place is built and used."),
                   ("tone", "Tone", "text", "Three to five words: familiar, worn, mundane, warm..."),
                   ("playstyle", "Playstyle", "text", "Stealth, loud, or how one turns into the other."))
_INTENT_LABELS = {"route_shape": "Route shape",'''),
    ('''    from apps.cli.commands import UNBUILT_BRIEF_FIELDS
    from packages.pipeline.road_grammar import GRAMMARS
''', '''    from apps.cli.commands import UNBUILT_BRIEF_FIELDS
    from packages.core.models import MissionBrief
    from packages.pipeline.road_grammar import GRAMMARS
'''),
    ('''        {"key": "roof_props", "label": "Roof clutter", "type": "boolean", "default": bool(brief.get("roof_props", True)),
         "support": "supported", "consumer": "Zoo's rooftop scatter", "rebuilds": "art"},
    ]
''', '''        {"key": "roof_props", "label": "Roof clutter", "type": "boolean", "default": bool(brief.get("roof_props", True)),
         "support": "supported", "consumer": "Zoo's rooftop scatter", "rebuilds": "art"},
        # the standard's PLAYERS (0.253.0): one spawn per crew member, and the crew Laser Tag plays
        {"key": "crew_size", "label": "Players", "type": "integer", "min": 1, "max": 4,
         "default": int(brief.get("crew_size", MissionBrief.__dataclass_fields__["crew_size"].default)),
         "support": "supported", "consumer": "Lot's crew spawns (lot/site_spawns.crew_spawns) and Laser Tag's crew",
         "rebuilds": "layout"},
    ]
    for key, label, kind, hint in STANDARD_INTENT:
        rows.append({"key": key, "label": label, "type": kind, "default": "", "support": "intent",
                     "note": "%s From the Level Standard's designer brief. Saved with the level for you and for "
                             "review; nothing builds from it yet." % hint})
'''),
    ('''    for key, value in doc["intent"].items():
        if key == "notes":
''', '''    for key, value in doc["intent"].items():
        if key in _STANDARD_KEYS:
            continue                    # the designer's, not the pipeline's: no brief field carries it
        if key == "notes":
'''),
    ('''def mission_id(doc: dict) -> str:''', '''_STANDARD_KEYS = {key for key, *_ in STANDARD_INTENT}


def mission_id(doc: dict) -> str:'''),
])

edit("tests/service/test_design.py", [
    ('''    assert intent == set(UNBUILT_BRIEF_FIELDS) | {"notes"}
''', '''    assert intent == set(UNBUILT_BRIEF_FIELDS) | {"notes"} | {k for k, *_ in design.STANDARD_INTENT}
'''),
])
