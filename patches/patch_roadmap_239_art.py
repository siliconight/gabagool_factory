"""Roadmap 239: the lightmap's import kept (Level Factory 0.183.0, cold run 9249), the legs profiled
(cold run 9250), Blender three at a time (Level Factory 0.184.0 and 0.185.0, cold run 9251). Rewrites
the status's tail and adds the art leg to the open list; each anchor asserted once, nothing written
on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_art.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S_OLD = ("read back off what ships since 0.182.0. Open: the light bake's and the sidecar step's imports, "
         "the walk copy's, and the grader's step (4x against the game's 1/60 s, the walker's call).*\n")
S_NEW = ("read back off what ships since 0.182.0; 0.183.0 keeps the editor's import of the lightmap (the "
         "bake's second import 50.3 -> 4.6 s): cold run 9249's export 418 -> 282 s, the drive 12.1 "
         "minutes. Then the art leg: cold run 9250 profiled the legs, and 9251 ran Blender three at a "
         "time (Level Factory 0.184.0's override, 0.185.0's default): the Blender window 114.0 -> 45.7 s, "
         "the drive 10.8 minutes, every model the same as two runs at one already make it. Open: the "
         "compose job's sixteen commands in turn, the work done for a cache hit before the cache is "
         "asked, the light bake's and the sidecar step's imports, the walk copy's, the Blender builds' "
         "reproducibility, and the grader's step (4x against the game's 1/60 s, the walker's call).*\n")
O_OLD = "the last import and refuses a package that still lacks one.\n2. **"
O_NEW = ("the last import and refuses a package that still lacks one.\n"
         "2. **The art leg -- MEASURED, PARTLY DONE.** Cold run 9250 ran its legs under cProfile "
         "(`PROFILE_LEGS=1`, `tools/cold_drive/cold_drive.sh`); its job records put the critical path in "
         "about 102 s of Blender jobs one after another, the compose job's sixteen commands in turn (64 "
         "s), and work the scheduler does before it asks the cache: a git probe per job (30 s summed) and "
         "a staged Godot project for each Laser Tag and walk-test plan, cache hits included (38 s). "
         "Level Factory 0.185.0 runs Blender three at a time where the machine allows, measured in cold "
         "run 9251 (`docs/findings/grader_speed/blender_width_compare.py`). Left: the compose commands "
         "side by side, the probe and the staging after the cache is asked. **Found on the way:** the "
         "Blender builds are not reproducible run to run -- a model built twice from the same inputs "
         "comes back with its triangles or merged vertices in another order and its weighted normals a "
         "few 1e-4 apart; Python's per-process hash seed is the first suspect, unmeasured.\n"
         "3. **")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "2. **The art leg -- MEASURED, PARTLY DONE.**" not in text, "already applied"
    for old, what in ((S_OLD, "239's status tail"), (O_OLD, "239's item 2 boundary")):
        assert text.count(old) == 1, (what, text.count(old))
    text = text.replace(S_OLD, S_NEW).replace(O_OLD, O_NEW)
    # the step item, item 2 before, follows the new item 2 as item 3
    assert text.count("3. **The grader's step, the walker's call.**") == 1, "the step item is not where read"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's art leg recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
