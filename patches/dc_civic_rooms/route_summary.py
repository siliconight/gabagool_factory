"""The route census (`docs/findings/furnish_route_cost/route_cost.py --spec`) on the twelve specs with civic rooms,
before (Deli Counter 0.269.0, the real repo) and after (the 0.270.0 clone): per spec, the pairs over the guide's 1.10
detour, closed to a body, closed to the bake, narrowed to single file, and the worst detour. Reads
route_before_<spec>.out.txt and route_after_<spec>.out.txt beside this file; fails on a report it cannot parse.

    python patches/dc_civic_rooms/route_summary.py > patches/dc_civic_rooms/route_summary.out.txt
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SPECS = ["courthouse_a02", "courthouse_a03", "final_stand", "funeral_home_a01", "funeral_home_a02",
         "landmark_hall_a01", "landmark_hall_a02", "landmark_hall_a03", "mansion_a03", "museum_a01", "museum_a02",
         "museum_a03"]
PATS = {
    "over_1.10": r"FURNISHED / AUTHORED, over the \d+ pairs joined in both: .*?> 1\.10 \(the guide's warning\): (\d+) pairs",
    "max": r"FURNISHED / AUTHORED, over the \d+ pairs joined in both: .*?max ([0-9.]+)",
    "closed_body": r"pairs furnishing closes to the body .*?: (\d+)",
    "closed_bake": r"pairs furnishing closes to the bake .*?: (\d+)",
    "single_file": r"pairs furnishing narrows from two abreast to single file .*?: (\d+)",
}


def read(path):
    t = path.read_text(encoding="utf-8")
    out = {}
    for k, p in PATS.items():
        m = re.search(p, t)
        assert m, "%s: no %s line -- not the census's report" % (path.name, k)
        out[k] = m.group(1)
    return out


print("%-18s %-8s %9s %6s %11s %11s %11s" % ("spec", "arm", "over 1.10", "max", "closed body", "closed bake",
                                                "single file"))
for s in SPECS:
    for arm in ("before", "after"):
        r = read(HERE / ("route_%s_%s.out.txt" % (arm, s)))
        print("%-18s %-8s %9s %6s %11s %11s %11s" % (s, arm, r["over_1.10"], r["max"], r["closed_body"],
                                                        r["closed_bake"], r["single_file"]))
