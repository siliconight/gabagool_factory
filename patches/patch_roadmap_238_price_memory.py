"""Roadmap 238, 2026-10-13: the package's memory in every price -- Level Factory 0.199.0, validated against
`texture_split_probe.gd` on cold run 9276's package (`docs/findings/texture_memory/`, "In the price"). 238's
status "Left" rewritten and one paragraph appended at the item's end, before the next status. The index is
NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_238_price_memory.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S238_OLD = ("Left: the walker's eye on the interiors (`docs/cold_runs/cold_9274/atlas.png`; 128 or 256 is one "
            "constant, `godot_project.REFLECTION_ATLAS_SIZE`); the probe in every cold run's record beside the "
            "price; compression of the level's own ~30 MiB.*")
S238_NEW = ("The memory is in every price since Level Factory 0.199.0 (2026-10-13): the fixed-station harness "
            "reads the engine's texture, buffer and video memory once every station is warm, and on cold run "
            "9276's package reads 76.0 MiB of textures in play where `texture_split_probe.gd` reads 65.6 after "
            "the package's own warm-up -- two moments, the gap measured (below). Left: the walker's eye on the "
            "interiors (`docs/cold_runs/cold_9274/atlas.png`; 128 or 256 is one constant, "
            "`godot_project.REFLECTION_ATLAS_SIZE`); the 8 MiB a camera adds at the stations, unattributed; "
            "compression of the level's own ~30 MiB.*")

BODY_238 = """

**IN THE PRICE, 2026-10-13** (`docs/findings/texture_memory/`, "In the price"; `patches/patch_lf_perf_memory.py`). Level Factory 0.199.0's `perf_stations.gd` reads the engine's texture, buffer and video memory into its report once every station has been warmed, before the measured passes, and `perf_stations_run.py` prints them in MiB beside the passes -- a report from before says it carries none, and one with only some of the three prints none of them; the factory's `price_glow.py` prints each run's. **Two instruments, two moments.** On an imported copy of cold run 9276's package the harness reads textures 76.0 MiB, buffers 48.0, video 123.9; `texture_split_probe.gd`'s `mission` arm reads 65.6 and 48.0 on the same copy, after the package's own warm-up with its last view nearly empty. `perf_memprobe.py` prints the harness's reading at three points: 67.9 MiB with the scene in, 67.9 with its camera at the first station, 76.0 once every station is warm, in every run; with the positional shadow atlas at 0 and the directional at 256 the same, so the shadow atlases are not the gap. The window accounts for about 1.3 MiB (1280 x 720 against 1152 x 648); the rest grows while a camera stands at the stations, and is not attributed. Buffers are not steady from run to run at one moment (48.0 to 56.1 MiB); textures have been. The price's figure is the level in play, and the one to compare between prices. **Found on the way, not fixed:** the harness sets `current_scene` before adding the scene to the tree, which the engine refuses, so that line does nothing; fixing it may change what a package's scripts see, so it waits for a change priced on its own."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**IN THE PRICE, 2026-10-13**" not in text, "already applied"
    assert text.count(S238_OLD) == 1, "238's status clause not found once"
    text = text.replace(S238_OLD, S238_NEW)
    h = text.find("\n\n**238. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and S238_NEW in text[s:h], "238's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    nh = re.search(r"\n\n\*\*(\d+)\. ", text[nxt:])
    assert nxt > h and nh and nh.group(1) == "239" \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "239 does not follow 238"
    text = text[:nxt] + BODY_238 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 238: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
