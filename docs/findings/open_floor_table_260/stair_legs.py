"""Every multi-storey switchback leg in the library with whether its flight is solid under it and carries a side guard and a back, against the Deli Counter checkout given.

    python stair_legs.py <deli_counter> > legs.txt

The candidates test_stair_back counts. Diffed across 0.233.0 and 0.234.0 it names the one leg that moved: legs_0233.txt, legs_0234.txt.
"""
import glob, os, sys
DC = sys.argv[1]
sys.path.insert(0, DC); os.chdir(DC)
import spec_loader, stairwell as S
out = set()
for path in sorted(glob.glob(os.path.join(DC, "specs", "*.json"))):
    name = os.path.basename(path)[:-5]
    if name.startswith("lf_"):
        continue
    sp = spec_loader.load_spec(path)
    if not sp.stairs:
        continue
    guards = S.stair_guards(sp)
    for i, st in enumerate(sp.stairs):
        if st.style != "switchback" or S.single_run(st):
            continue
        sid = S.stair_ident(st, i)
        lo, hi = min(st.from_story, st.to_story), max(st.from_story, st.to_story)
        for s in range(lo, hi):
            solid = S.flight_solid_under(sp, st, s)
            side = any(p["stair"] == sid and p["story"] == s and p["kind"] == "side" for p in guards)
            back = any(p["stair"] == sid and p["story"] == s and p["kind"] == "back" for p in guards)
            out.add((name, sid, s, solid, side, back))
for row in sorted(out):
    print("%s|%s|%d|solid=%s|side=%s|back=%s" % row)
