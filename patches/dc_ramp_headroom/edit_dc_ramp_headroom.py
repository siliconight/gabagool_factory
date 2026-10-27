"""Deli Counter 0.273.0 on a clone: a ramp's cut begins where a body clears the slab, and furnish keeps off it (the
factory's roadmap 270; the walker on seed 9205's parking garage, 2026-10-26: "i can't use this wide ramp to go up or
down?"). Anchored; refuses on a miss.

    python edit_dc_ramp_cut.py <clone>

Copies tests/test_ramp_cut_headroom.py and migrations/migrate_ramp_cut.py from `src/`, then RUNS the migration
(it moves two authored pieces in foundry_heist_vertical and refurnishes the specs with furniture in a cut).
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("tests/test_ramp_cut_headroom.py", "migrations/migrate_ramp_cut.py"):
    assert not (C / rel).exists(), rel
    shutil.copyfile(HERE / "src" / rel, C / rel)
    print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("edited", rel, len(edits))


edit("stairwell.py", [
    ('''def _ramp_ascent(rp):
    """``(t_low, t_head, lateral centre)`` on the ramp's ascent axis. The box''',
     '''def _ramp(rp):
    """A ramp as attributes, whether a `spec_types.Ramp` or a spec's dict (furnish reads specs as dicts)."""
    if not isinstance(rp, dict):
        return rp
    from types import SimpleNamespace
    d = {"run": 8.0, "width": 2.0, "axis": "Y", "thickness": 0.3, "cut_slabs": True}
    d.update(rp)
    return SimpleNamespace(**d)


def _spec_value(spec, key, default=None):
    return spec.get(key, default) if isinstance(spec, dict) else getattr(spec, key, default)


def _ramp_ascent(rp):
    """``(t_low, t_head, lateral centre)`` on the ramp's ascent axis. The box'''),
    ('''    t = rp.y if rp.axis == "Y" else rp.x
    return t - rp.run / 2.0, t + rp.run / 2.0, (rp.x if rp.axis == "Y" else rp.y)


def ramp_cut_span(rp):
    """``(t_mid, t_head)`` on the ascent axis: where the slab over a ramp is
    open -- from the ramp's middle, where its cut has always begun, to its
    HEAD, where the ramp meets the floor it climbs to, and never past it.

    NOT YET WHERE A BODY NEEDS IT. Measured on the nine library ramps (the
    factory's docs/findings/ramp_cut_241/): where the cut begins, the clearance
    between the slab's underside and the ramp's top face is 1.04 to 1.55 m,
    under a body's 1.8 m, so a body walking up meets the slab's edge. The agent
    contract's `min_headroom_m` would open each cut 1.4 to 3.2 m further down
    its ramp -- under furniture that furnish lays without reading a ramp's cut
    -- so that waits on furnish learning ramps (the factory's roadmap)."""
    t_low, t_head, _lat = _ramp_ascent(rp)
    return (t_low + t_head) / 2.0, t_head
''', '''    rp = _ramp(rp)
    t = rp.y if rp.axis == "Y" else rp.x
    return t - rp.run / 2.0, t + rp.run / 2.0, (rp.x if rp.axis == "Y" else rp.y)


def ramp_cut_span(rp, spec=None):
    """``(t_start, t_head)`` on the ascent axis: where the slab over a ramp is
    open -- from where a body walking up first needs it open to the ramp's
    HEAD, where the ramp meets the floor it climbs to, and never past it.

    WHERE A BODY NEEDS IT (0.273.0, the factory's roadmap 270). The ramp's top
    rises `rise` over its `run`; the slab it climbs to stands `rise - slab` over
    the floor it climbs from. The cut must begin where the gap between the two
    falls to the agent contract's `min_headroom_m` (2.0): at
    ``t_low + run * (rise - slab - headroom) / rise``, and never later than the
    ramp's middle, where every cut began until now. Measured before, on the nine
    library ramps (the factory's docs/findings/ramp_cut_241/): the gap where the
    cut began was 1.04 to 1.55 m, so a body walking up met the slab's edge -- the
    walker, on seed 9205's garage: "i can't use this wide ramp to go up or
    down?". Furnish keeps every piece off the longer cut (`level_design`'s
    `ramp_holes`), which is what held this back.

    Without ``spec`` (no storey height, no slab) the cut begins at the middle, as
    it always did."""
    rp = _ramp(rp)
    t_low, t_head, _lat = _ramp_ascent(rp)
    t_mid = (t_low + t_head) / 2.0
    if spec is None:
        return t_mid, t_head
    rise = float(_spec_value(spec, "story_height", 0.0)) * (rp.to_story - rp.from_story)
    slab = float(_spec_value(spec, "floor_thick", 0.0) or 0.0)
    if rise <= 0.0:
        return t_mid, t_head
    room = rise - slab - agent_contract.min_headroom()
    return min(t_mid, t_low + rp.run * max(0.0, room) / rise), t_head
'''),
    ('''def ramp_hole(rp):''', '''def ramp_hole(rp, spec=None):'''),
    ('''    t_mid, t_head = ramp_cut_span(rp)
    return _ramp_rect(rp, t_mid, t_head)''', '''    t_start, t_head = ramp_cut_span(rp, spec)
    return _ramp_rect(_ramp(rp), t_start, t_head)'''),
    ('''        if getattr(rp, "cut_slabs", True) and rp.to_story > rp.from_story:
            cx, cy, sx, sy = ramp_hole(rp)
            out.setdefault(rp.to_story, []).append(''', '''        if getattr(rp, "cut_slabs", True) and rp.to_story > rp.from_story:
            cx, cy, sx, sy = ramp_hole(rp, spec)
            out.setdefault(rp.to_story, []).append('''),
    ('''        cx, cy, sx, sy = ramp_hole(rp)
        x0, y0, x1, y1 = cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2''',
     '''        cx, cy, sx, sy = ramp_hole(rp, spec)
        x0, y0, x1, y1 = cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2'''),
    ('''                cx, cy, sx, sy = ramp_hole(rp)
                holes.append((cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2))''',
     '''                cx, cy, sx, sy = ramp_hole(rp, spec)
                holes.append((cx - sx / 2, cy - sy / 2, cx + sx / 2, cy + sy / 2))'''),
])

edit("deli_counter.py", [
    ('''                hx, hy, hsx, hsy = stairwell.ramp_hole(rp)''',
     '''                hx, hy, hsx, hsy = stairwell.ramp_hole(rp, self.s)'''),
])

edit("level_design.py", [
    ('''    if above is None:
        for h in spec.get("slab_holes", []) or []:
            if int(h.get("story", 0) or 0) != story:
                continue
            hx0, hx1 = h["x"] - h["size_x"] / 2.0, h["x"] + h["size_x"] / 2.0
            hy0, hy1 = h["y"] - h["size_y"] / 2.0, h["y"] + h["size_y"] / 2.0
            if px + hx > hx0 - 0.3 and px - hx < hx1 + 0.3 and \\
                    py + hy > hy0 - 0.3 and py - hy < hy1 + 0.3:
                return False
''', '''    if above is None:
        for h in spec.get("slab_holes", []) or []:
            if int(h.get("story", 0) or 0) != story:
                continue
            hx0, hx1 = h["x"] - h["size_x"] / 2.0, h["x"] + h["size_x"] / 2.0
            hy0, hy1 = h["y"] - h["size_y"] / 2.0, h["y"] + h["size_y"] / 2.0
            if px + hx > hx0 - 0.3 and px - hx < hx1 + 0.3 and \\
                    py + hy > hy0 - 0.3 and py - hy < hy1 + 0.3:
                return False
        # AND A RAMP'S CUT (0.273.0, roadmap 270), the same way: the builder
        # opens it in this storey's slab, and its start moved down the ramp to
        # where a body clears the slab -- under furniture that read only
        # authored holes (foundry_heist_vertical's forklift, cbp_town_finale's
        # chairs, found on a rail's line by 0.241.0's build).
        for hx0, hy0, hx1, hy1 in ramp_holes(spec, story):
            if px + hx > hx0 - 0.3 and px - hx < hx1 + 0.3 and \\
                    py + hy > hy0 - 0.3 and py - hy < hy1 + 0.3:
                return False
'''),
    ('''    for h in spec.get("slab_holes") or []:
        if int(h.get("story", 0) or 0) == story:
            boxes.append((h["x"] - h["size_x"] / 2.0, h["y"] - h["size_y"] / 2.0,
                          h["x"] + h["size_x"] / 2.0, h["y"] + h["size_y"] / 2.0))
''', '''    for h in spec.get("slab_holes") or []:
        if int(h.get("story", 0) or 0) == story:
            boxes.append((h["x"] - h["size_x"] / 2.0, h["y"] - h["size_y"] / 2.0,
                          h["x"] + h["size_x"] / 2.0, h["y"] + h["size_y"] / 2.0))
    boxes.extend(ramp_holes(spec, story))      # a ramp's cut is a hole too (0.273.0)
'''),
    ('''def is_corner_store_floor(room, building):''', '''def ramp_holes(spec, story):
    """``[(x0, y0, x1, y1)]``: the slab cuts the spec's ramps open in ``story``'s floor (`stairwell.ramp_hole`, from
    where a body clears the slab to the ramp's head) -- what furnish keeps off, as it keeps off an authored hole."""
    import stairwell
    out = []
    for r in spec.get("ramps") or []:
        if not r.get("cut_slabs", True) or int(r.get("to_story", 0)) <= int(r.get("from_story", 0)):
            continue
        if int(r.get("to_story", 0)) != int(story):
            continue
        cx, cy, sx, sy = stairwell.ramp_hole(r, spec)
        out.append((cx - sx / 2.0, cy - sy / 2.0, cx + sx / 2.0, cy + sy / 2.0))
    return out


def is_corner_store_floor(room, building):'''),
])

# the 0.241.0 rail tests ask the rails of the cut the builder makes, which needs the spec now (0.273.0)
_rt = (C / "tests" / "test_ramp_cut.py")
_raw = _rt.read_bytes().decode("utf-8")
_i = _raw.index("def test_a_ramps_cut_is_railed_and_its_head_left_open")
_j = _raw.index("def test_no_wall_stands_across_a_ramps_head")
_mid = _raw[_i:_j]
assert _mid.count("stairwell.ramp_hole(rp)") == 3, _mid.count("stairwell.ramp_hole(rp)")
_rt.write_bytes((_raw[:_i] + _mid.replace("stairwell.ramp_hole(rp)", "stairwell.ramp_hole(rp, spec)")
                 + _raw[_j:]).encode("utf-8"))
print("edited tests/test_ramp_cut.py 3")

import subprocess  # noqa: E402
done = subprocess.run([sys.executable, str(C / "migrations" / "migrate_ramp_cut.py")], capture_output=True, text=True,
                      cwd=str(C))
print(done.stdout.strip())
assert done.returncode == 0 and "2 spec(s) cleared" in done.stdout, done.stdout + done.stderr
