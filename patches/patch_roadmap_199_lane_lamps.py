"""Roadmap 199: the lane's lamps (Lot 0.116.0, cold run 9238). Appends one body paragraph at the
end of 199's body (before the next item's status block); the status block is not touched -- the
lane was always lit or not as a look, and what 199 leaves is unchanged. Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_199_lane_lamps.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
HEAD = "\n\n**199. "
TAIL = ("a street's kerbs, markings and furniture are per-piece draws, a merge per road per material "
        "the lever.")
BODY_ADD = """

**THE LANE'S LAMPS, 2026-10-11** (Lot 0.116.0, `patches/patch_lot_lane_lamps.py`; `docs/cold_runs/cold_9238/NOTES.md`). The dark lane was a design call, and the walker asked for the calls to be made: the first one -- wall packs on the rear walls -- was revised by measuring 9237's lights manifest before building it, because the row's rear walls stand 14 m off the lane (the 6 m yard and the 8 m setback) and the one rear wall pack reaches 5.5 m, while the lane's other side is the plate's edge. The mechanism was one line: `site_furniture.plan_furniture` skips a road without a sidewalk, so a lane stood no lamp, tree or anything else. `plan_lane_lamps` stands the street's own lamp along a lane: as many as its slab carries at 40 m (further apart than two of the lamp's 14 m reaches, so a pool ends before the next begins), half a spacing in from each mouth, on the side the buildings it runs behind stand (`lane_side`, by their centres), 0.6 m beyond the paved edge, clear of the path corridors -- a rear spur stops half a metre short of the lane's edge, so its corridor is the only thing that says where it is, and the draft's first test stood a lamp on one -- the footprints, the parking fields, its mouths and the markers. Cold run 9238 (9233's lot, 0 interventions): two lamps on the lane, +2 draws a heading median and +0.04 ms p95 against 9237's package, inside the controls' 0.10 ms spread, no new mesh over the 8-light cap; the frames show a warm pool on the lane at each pole and the dark between. The one new finding (`LT_MAP_PLAYER_STUCK` on an unpicked candidate) is 38 m from that candidate's nearest lane lamp, on the main street's sidewalk. Still open beside it: the lane's own stop control is never stood (`LOT_TRAFFIC_CONTROL_NO_BAND`, no band for a sign), recorded and not called."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE LANE'S LAMPS, 2026-10-11" not in text, "already applied"
    h = text.find(HEAD)
    assert h > 0 and text.count(HEAD) == 1, "199's heading not found once"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h, "no status block after 199's body"
    body = text[h:nxt]
    assert body.endswith(TAIL), ("199's body does not end where this patch read it", body[-120:])
    text = text[:nxt] + BODY_ADD + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 199: one paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
