"""Roadmap 234 and 242, two status lines brought up to date (2026-10-12 night). Each anchor asserted once;
a status already carrying its new text is reported and left. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check`.

  234  its status said the floater concept was staged to land after factory 1.38.0's tags; it landed on
       2026-10-11 as Zoo f288f7a ("docs: Floaters, a core concept"). The helper is what is left.
  242  its "two routes a run shorter under 0.29.0, not attributed": attributed -- every run that ended
       short ended in a team wipe early in the run (`docs/findings/route_snag/README.md`, the last
       paragraph). This one was first applied inline the same night and is recorded here.

    python patches/patch_roadmap_234_242_status.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("234",
     "The concept is staged as a Zoo README section (`patches/zoo_floaters/README_floaters.md`, "
     "`patches/patch_zoo_floaters_readme.py`) to land after factory 1.38.0's tags. Owner: Zoo.*",
     "The concept landed as a Zoo README section on 2026-10-11 (Zoo f288f7a, "
     "`patches/patch_zoo_floaters_readme.py`); the helper it describes, `geometry.add_floater` and "
     "`add_flat_floater`, is not built. Owner: Zoo.*"),
    ("242",
     "two routes a run shorter under 0.29.0, not attributed; the engine, the game's choice.*",
     "two routes a run shorter under 0.29.0, attributed to team wipes early in the run, the encounter "
     "and not the traversal; the engine, the game's choice.*"),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    for item, old, new in EDITS:
        if text.count(new) == 1 and old not in text:
            print("roadmap %s: already up to date" % item)
            continue
        assert text.count(old) == 1, (item, text.count(old))
        text = text.replace(old, new)
        print("roadmap %s: status brought up to date" % item)
    RM.write_bytes(text.encode("utf-8"))


if __name__ == "__main__":
    main()
