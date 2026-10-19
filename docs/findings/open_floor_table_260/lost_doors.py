"""The builder's 'door ... sits in a cut-away part of the run and is not built' test, replayed per spec without Blender."""
import glob, json, os, sys
DC = sys.argv[1]; sys.path.insert(0, DC); os.chdir(DC)
import partition_bounds, setbacks, spec_loader, stairwell
for path in sorted(glob.glob(os.path.join(DC, "specs", "*.json"))):
    name = os.path.basename(path)[:-5]
    if name.startswith("lf_"):
        continue
    try:
        s = spec_loader.load_spec(path)
    except Exception as e:
        print(name, "LOAD ERROR", e); continue
    voids = stairwell.wall_voids(s) if (s.stairs or getattr(s, "ramps", None) or getattr(s, "slab_holes", None)) else {}
    for i, p in enumerate(s.partitions):
        raw_lo, raw_hi = min(p.start, p.end), max(p.start, p.end)
        spans = partition_bounds.partition_spans(p.start, p.end, p.axis, p.pos, s.footprint_x, s.footprint_y,
                                                 voids.get(p.story, ()), min_span=s.wall_thick,
                                                 extent=setbacks.storey_extent(s, p.story))
        if not spans:
            continue
        for op in p.openings:
            if not any(partition_bounds.remap_opening(op.pos, raw_lo, raw_hi, lo, hi) is not None for lo, hi in spans):
                print("%s int_%d_%d %s pos %+.3f" % (name, p.story, i, op.kind, op.pos))
