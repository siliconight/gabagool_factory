"""Roadmap 238, 2026-10-13: the reflection atlas sized to the package -- Level Factory 0.198.0, proven in cold run
9274 (`docs/cold_runs/cold_9274/`). Replaces 238's status, OPEN -> NARROWED with the evidence in it (asserted
once and still directly above its heading), and appends one paragraph to its body, before 239's status. The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_238_atlas_shipped.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S238_HEAD = "*STATUS: OPEN 2026-10-13 -- RE-MEASURED BY PART, the first attribution RETRACTED and kept below."
S238_NEW = ("*STATUS: NARROWED 2026-10-13 -- the reflection atlas sized to the package and proven: Level Factory "
            "0.198.0 writes it from the package's probes (32 slots of 64 for cold run 9273's 23, where Godot's "
            "default 64 of 256 was 257 of the package's 314.6 MiB of texture memory), and cold run 9274's "
            "package holds 65.6 MiB after its warm-up, -249.0 (-79 %), under the 100 this item set (0 "
            "interventions; findings 117, 9273's issue ids; draws +0.0, p95 -0.02 ms against a 0.07 floor; no "
            "frame moved more than 0.02 % of its pixels past 32 codes). The sky is not resident, the first "
            "attribution RETRACTED and kept below (`docs/findings/texture_memory/`). Left: the walker's eye on "
            "the interiors (`docs/cold_runs/cold_9274/atlas.png`; 128 or 256 is one constant, "
            "`godot_project.REFLECTION_ATLAS_SIZE`); the probe in every cold run's record beside the price; "
            "compression of the level's own ~30 MiB.*")

BODY_238 = """

**THE ATLAS, SIZED AND PROVEN, 2026-10-13** (`patches/patch_lf_reflection_atlas.py`; `docs/findings/texture_memory/atlas_frames.sh`; `docs/cold_runs/cold_9274/`). **Priced first**, on four copies of 9273's package with the face size set by `override.cfg` and a second unchanged copy as the control, at look_shots' derived stations and twelve interiors: texture memory 314.6 MiB at 256, 121.8 at 128, 73.5 at 64 (all at 64 slots); at 64 no pixel of any frame moved more than 32 codes and at most 2.7 % moved more than 8, in one drywall room, brick rooms not at all. **Level Factory 0.198.0** writes the atlas as it writes the light cap: `count_package_probes` counts the package's ReflectionProbe nodes (9273's text 23, its running tree 23), the slots are that count rounded up to a power of two (23 -> 32; four slots for 23 probes stalled a run, and a package past the default's 64 probes now gets more slots where the default overflowed), the face size is `REFLECTION_ATLAS_SIZE`, 64, and a package with no probe writes no line. **Cold run 9274** (0 interventions, its merge, bake and findings 9273's to the count): the package says `reflection_count=32`, `reflection_size=64`; it holds 65.6 MiB where 9273's held 314.6, the 65.5 predicted; its frames move as the pricing said, the drywall room 2.675 % past 8 codes and nothing past 32 beyond spawn's 0.020 against the control's 0.015; its price is flat. **What 128 or 256 would buy back:** a sharper reflection on a glossy surface; the interiors measured are concrete, drywall and brick."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE ATLAS, SIZED AND PROVEN, 2026-10-13" not in text, "already applied"
    h = text.find("\n\n**238. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s + 2:h].startswith(S238_HEAD), "238's status is not the one this patch read"
    assert text.count(S238_HEAD) == 1, "238's status head not found once"
    text = text[:s + 2] + S238_NEW + text[h:]
    h = text.find("\n\n**238. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert text[s + 2:h] == S238_NEW, "238's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**239. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "239 does not follow 238"
    assert text.rfind("**THE MEMORY BY PART, 2026-10-13**", h, nxt) > h, "the memory paragraph is not 238's last"
    text = text[:nxt] + BODY_238 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 238: NARROWED and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
