"""A price whose subject moved a geometry-derived station: compare the headings that stood in the same place.

    python docs/findings/urban_street/price_matched.py <price dir>

`docs/findings/horizon_glow/price_glow.py` refuses a comparison when the subject's headings are not the control's
(STATIONS DIFFER), and rightly: a heading that stood somewhere else measured something else. Some stations are
derived from the level's own geometry -- `longest_sightline` is the longest line the map holds -- so a change to
the geometry can move one, and then the honest comparison is over the headings that did not move. This reads the
three reports price_glow kept (`perf_control_1.json`, `perf_glow.json` -- the subject --, `perf_control_2.json`),
keys every heading by (station, its position to 0.1 m, yaw), names the headings in one and not the others, and
over the rest prints the draw calls and p95 frame time: the subject against the two controls' mean, per heading
on the mean and median, with the controls' own spread as the noise floor. Prints what it measured and stops.
"""
import json
import pathlib
import statistics as st
import sys

D = pathlib.Path(sys.argv[1])


def _table(name):
    doc = json.loads((D / f"perf_{name}.json").read_text(encoding="utf-8"))
    if doc.get("schema") != "level_factory.perf_stations.v1" or not doc.get("complete"):
        raise SystemExit(f"UNKNOWN SHAPE: {name}")
    out = {}
    for row in doc["rows"]:
        pos = tuple(round(float(v), 1) for v in row["pos"])
        for h in row["headings"]:
            out[(row["station"], pos, h["yaw"])] = (int(h["draws"]), float(h["ms_p95"]))
    return out


def main():
    c1, s, c2 = _table("control_1"), _table("glow"), _table("control_2")
    common = sorted(set(c1) & set(s) & set(c2))
    for name, t in (("control_1", c1), ("subject", s), ("control_2", c2)):
        odd = sorted(set(t) - set(common))
        if odd:
            print(f"{name}: {len(odd)} heading(s) not in the others: {odd}")
    dd, dp, floor = [], [], []
    for k in common:
        cd = (c1[k][0] + c2[k][0]) / 2.0
        cp = (c1[k][1] + c2[k][1]) / 2.0
        dd.append(s[k][0] - cd)
        dp.append(s[k][1] - cp)
        floor.append(abs(c1[k][1] - c2[k][1]))
    print(f"{len(common)} headings matched")
    print(f"draws: subject - controls' mean, mean {st.mean(dd):+.1f}, median {st.median(dd):+.1f}, "
          f"min {min(dd):+.0f}, max {max(dd):+.0f}")
    print(f"p95 ms: subject - controls' mean, median {st.median(dp):+.2f}, max {max(dp):+.2f}; "
          f"the controls' spread, median {st.median(floor):.2f}")


if __name__ == "__main__":
    main()
