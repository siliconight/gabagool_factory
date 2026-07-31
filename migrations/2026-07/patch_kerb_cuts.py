"""Drop the kerb where a route crosses it.

`SIDEWALK_H` is 0.16 and the tallest step a 0.4 m capsule walks up unassisted is
0.117, so stepping off the ground onto a sidewalk is a wall. Reported from play:
walking from a spawn toward the street stops dead and needs a jump.

The fix is the one real streets use. A kerb is *supposed* to be a wall -- that is
what stops you wandering into traffic -- so the answer is not to flatten it, it
is to drop it where people are meant to cross. Lot already knows where that is:
`paths` are the site's designed circulation between buildings, and they run
straight through the sidewalks either side of any road they cross.

So the sidewalk stops being one long box. It becomes the segments between
crossings, plus a `kerbcut_` section at each crossing sitting flush with the road
surface (ROAD_THICK, 0.08). That makes every transition legal:

    ground   0.00  ->  kerbcut  0.08   = 0.08   walkable
    kerbcut  0.08  ->  sidewalk 0.16   = 0.08   walkable
    road     0.08  ->  kerbcut  0.08   = flush

and leaves the kerb a kerb everywhere else, which is correct rather than
convenient. `site_steps.py` reports whatever this does not reach.

Asserts its target before writing.
"""
import pathlib
import py_compile

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LOT_PY = ROOT / "lot" / "lot.py"
STEPS_PY = ROOT / "lot" / "site_steps.py"

OLD = '''        sw = rd.get("sidewalk")
        if sw:
            ux, uy = dx / length, dy / length        # along
            px, py = -uy, ux                          # perpendicular (left)
            off = w / 2 + sw / 2
            for side, sgn in (("L", 1), ("R", -1)):
                scx, scy = cx + px * off * sgn, cy + py * off * sgn
                bl, sr = _yaw_box_node(
                    f"sidewalk_{i}{side}", (length, SIDEWALK_H, sw),
                    (scx, SIDEWALK_H / 2, -scy), -ang, SIDEWALK_COLOR)
                body += bl
                sub += sr
'''

NEW = '''        sw = rd.get("sidewalk")
        if sw:
            ux, uy = dx / length, dy / length        # along
            px, py = -uy, ux                          # perpendicular (left)
            off = w / 2 + sw / 2
            # Where the site's own circulation crosses this kerb. A kerb is
            # SUPPOSED to be a wall -- 0.16 m against an unassisted step limit
            # of 0.117 -- and the answer is not to flatten it but to drop it
            # where people are meant to cross, exactly as a real street does.
            # Anything this does not reach is still a wall, and site_steps.py
            # says so rather than leaving it to be discovered in play.
            for side, sgn in (("L", 1), ("R", -1)):
                lcx, lcy = cx + px * off * sgn, cy + py * off * sgn
                cuts = _kerb_crossings(site_spec, bld,
                                       (ax, ay), (ux, uy), (px, py),
                                       off * sgn, length, sw)
                spans = _split_span(length, cuts)
                for j, (t0, t1, is_cut) in enumerate(spans):
                    seg = t1 - t0
                    if seg <= 0.05:
                        continue
                    mid = (t0 + t1) / 2.0 - length / 2.0
                    scx = lcx + ux * mid
                    scy = lcy + uy * mid
                    h = ROAD_THICK if is_cut else SIDEWALK_H
                    nm = (f"kerbcut_{i}{side}_{j}" if is_cut
                          else f"sidewalk_{i}{side}_{j}")
                    bl, sr = _yaw_box_node(
                        nm, (seg, h, sw), (scx, h / 2, -scy), -ang,
                        SIDEWALK_COLOR)
                    body += bl
                    sub += sr
'''

HELPERS = '''

def _kerb_crossings(site_spec, bld, origin, along, perp, offset, length, width):
    """Distances along a kerb where the site's own paths cross it.

    Returns the centre of each crossing measured from the road's start point.
    A path that runs parallel, or crosses beyond either end, contributes
    nothing -- there is no crossing to drop."""
    ox, oy = origin
    ux, uy = along
    px, py = perp
    # A point on this kerb is origin + u*t + p*offset.
    kx, ky = ox + px * offset, oy + py * offset
    out = []
    for p in site_spec.get("paths", []) or []:
        try:
            pax, pay = bld[p["from"]]["at"] if "from" in p else p["a"]
            pbx, pby = bld[p["to"]]["at"] if "to" in p else p["b"]
        except (KeyError, TypeError):
            continue
        vx, vy = pbx - pax, pby - pay
        # solve  k + u*t = pa + v*s   for t
        den = ux * (-vy) - uy * (-vx)
        if abs(den) < 1e-9:
            continue                      # parallel: never crosses
        rx, ry = pax - kx, pay - ky
        t = (rx * (-vy) - ry * (-vx)) / den
        s = (ux * ry - uy * rx) / den
        if not (-0.05 <= s <= 1.05):
            continue                      # crosses the LINE, not the path
        if t < 0.0 or t > length:
            continue                      # past the end of this kerb
        out.append((t, float(p.get("width", 6.0))))
    return out


def _split_span(length, cuts, margin=0.6):
    """[(t0, t1, is_cut)] along a kerb: crossings, and the kerb between them.

    `margin` widens each crossing past the path itself so a body approaching at
    an angle still meets the dropped section rather than clipping its corner --
    the same reason a real dropped kerb is wider than the crossing painted on
    it."""
    spans = []
    bands = []
    for t, w in sorted(cuts):
        half = w / 2.0 + margin
        bands.append((max(0.0, t - half), min(length, t + half)))
    merged = []
    for b in bands:
        if merged and b[0] <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b[1]))
        else:
            merged.append(b)
    cursor = 0.0
    for b0, b1 in merged:
        if b0 > cursor:
            spans.append((cursor, b0, False))
        spans.append((b0, b1, True))
        cursor = b1
    if cursor < length:
        spans.append((cursor, length, False))
    return spans
'''

ANCHOR = "def _outdoor_nodes("


def main() -> int:
    src = LOT_PY.read_text(encoding="utf-8")
    if "_kerb_crossings" in src:
        print("lot.py: already patched")
    else:
        if src.count(OLD) != 1:
            raise SystemExit("lot.py: the sidewalk emission block is not where "
                             "this expected it. Nothing written.")
        if src.count(ANCHOR) != 1:
            raise SystemExit("lot.py: cannot find _outdoor_nodes. Nothing written.")
        src = src.replace(OLD, NEW)
        at = src.index(ANCHOR)
        src = src[:at] + HELPERS.lstrip("\n") + "\n\n" + src[at:]
        LOT_PY.write_text(src, encoding="utf-8")
        py_compile.compile(str(LOT_PY), doraise=True)
        print("lot.py: kerb cuts emitted where paths cross, and it compiles")

    print("\n=========== rebuild a site and re-measure ===========")
    import subprocess
    import sys
    spec = ROOT / "lot" / "specs" / "ballpark_block" / "ballpark_block_site.json"
    proj = ROOT / "_runs" / "ballpark_block_proj"
    r = subprocess.run([sys.executable, str(ROOT / "lot" / "lot.py"),
                        str(spec), str(proj), "--navqa"],
                       capture_output=True, text=True, cwd=str(ROOT / "lot"))
    for ln in (r.stdout or "").splitlines():
        if "[lot]" in ln:
            print("  " + ln)
    if r.returncode != 0:
        print((r.stderr or "")[-600:])
        return 1
    sys.path.insert(0, str(ROOT / "lot"))
    import json as _json
    import site_steps as _S
    spec_json = _json.loads(spec.read_text(encoding="utf-8"))
    tscn = str(proj / "ballpark_block.tscn")
    rows = _S.steps(tscn, radius_m=0.4, floor_max_angle_deg=45.0, assist_m=0.5)
    seen = set()
    for r2 in rows:
        key = (r2["from"].rstrip("0123456789LR_"),
               r2["to"].rstrip("0123456789LR_"), r2["rise_m"])
        if key in seen:
            continue
        seen.add(key)
        flag = ("ok" if r2["walkable_unassisted"]
                else ("needs step-up" if r2["climbable_with_assist"] else "JUMP"))
        print(f"  {r2['from']:<18} {r2['from_top']:+.3f}  ->  {r2['to']:<18} "
              f"{r2['to_top']:+.3f}   rise {r2['rise_m']:.3f}   {flag}")
    issues = _S.findings(tscn, radius_m=0.4, floor_max_angle_deg=45.0,
                         assist_m=0.5, site_spec=spec_json)
    print()
    if not issues:
        print("  no step findings -- every route crosses at a dropped kerb")
    for f in issues:
        print(f"  [{f['code']}] ({f['severity']}) {f['message'][:300]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
