"""Lot 0.86.0: flyer sleeves round the poles (Zoo `pole_flyers`), in tiers.

Anchored: each anchor must match exactly once or nothing is written.
"""
import pathlib
import sys

LOT = pathlib.Path(__file__).resolve().parent.parent / "lot"

CONSTS_OLD = '''#: The band a slot asks Zoo to fill. A wall: `poster_wall_forms.band_height
#: ("alley", 2)`, a two-course collage whose sheets wander down it. A pole:
#: ONE sheet's own height (`poster_art.SIZES_M["alley"][1]`), not
#: `band_height("alley", 1)` -- that band is a sheet plus the WANDER a run of
#: several spreads across, and one sheet cannot fill it. 0.84.0 asked for
#: 0.52 and Zoo's exact fit refused all four pole modules in cold run 9116
#: ("height=0.420m != exact target 0.520m"); Zoo's planner fills 0.42 in
#: every variant. Pinned against Zoo in tests/test_site_posters.py.
BAND_WALL = 0.814
BAND_POLE = 0.42
#: One alley sheet's width (Zoo `poster_art.SIZES_M["alley"][0]`).
SHEET_W = 0.30
'''
CONSTS_NEW = '''#: The band a wall slot asks Zoo to fill: `poster_wall_forms.band_height
#: ("alley", 2)`, a two-course collage whose sheets wander down it. Pinned
#: against Zoo in tests/test_site_posters.py.
#:
#: (0.84.0-0.85.0 also hung ONE flat alley sheet on a pole -- first at a band
#: one sheet cannot fill, which Zoo refused in cold run 9116, then at the
#: sheet's own 0.42. Cold run 9118 showed a 0.30 m sheet standing proud of a
#: 0.12 m pole reads as a small sign; the walker sent photographs of real
#: poles, and Zoo 1.34.0 drew them. 0.86.0 hangs `pole_flyers` instead.)
BAND_WALL = 0.814
'''

POLES_OLD = '''#: The pole species handbills go on, and each pole's half-width at 1.6 m:
#: Zoo's streetlight pole is a 0.06 m radius cylinder at the slot's centre;
#: the sign post is a 0.10 m u-channel.
POLES = {"streetlight": 0.06, "sign_post": 0.05}
#: One pole in this many carries a handbill.
POLE_EVERY = 2
'''
POLES_NEW = '''#: THE POLES (0.86.0): the species flyers go on, and the radius a sleeve
#: round each must clear. Zoo's streetlight pole is a 0.06 m cylinder at the
#: slot's centre; the sign post a 0.10 m square u-channel, whose CORNERS are
#: its half-diagonal out (0.0707), not its half-width -- a sleeve at the
#: half-width would pass through them.
POLES = {"streetlight": 0.06, "sign_post": 0.0707}
#: Zoo `pole_flyers_forms`: a sleeve is `LAYERS` papers `LAYER` apart, the
#: innermost `AIR` off the pole, so its outer radius is pole + AIR + 3 LAYER.
#: Pinned against Zoo in tests/test_site_posters.py.
FLYER_LAYERS = 4
FLYER_LAYER = 0.004
#: The tiers a pole can carry, from the walker's photographs: bare, two
#: sheets, a column, wrapped. Their bands (height of paper, metres) and where
#: the paper starts above the sidewalk -- different per tier, so no two tiers
#: share a centreline (the placement guide's "repeated perfect centerline"
#: tell): a pair at the head, a column at the chest, a wrap from the knee.
#: Each start moves by up to `START_JITTER`, pole to pole.
TIERS = ("bare", "pair", "stack", "wrap")
TIER_BAND = {"pair": 0.78, "stack": 1.12, "wrap": 1.72}
TIER_START = {"pair": 1.22, "stack": 0.86, "wrap": 0.36}
START_JITTER = 0.1
#: Paper stops where a standing person can still paste it (the guide:
#: "Posters placed far above reach need a reason"), and on a sign post under
#: its blade (Lot's MUTCD blades are 0.3048 m tall at the top of a 2.4384 m
#: post), a hand clear of it.
REACH = 2.1
BLADE_CLEAR = round(2.4384 - 0.3048 - 0.05, 4)
#: How papered a pole is, by a hash of its name: the share of poles at each
#: tier; and one tier denser near a junction -- the corner poles are where a
#: street's flyers go ("a known place for flyers", the placement guide).
TIER_SHARE = (0.30, 0.35, 0.22, 0.13)
JUNCTION_M = 10.0
'''

POLE_FN_START = "def plan_pole_bills(site_spec, roads, findings=None):"
POLE_FN_END = "LIGHT = light_from()"
POLE_FN_NEW = '''def _nearest(roads, px, py):
    """``(distance, point, road)`` for the road nearest (px, py), or None."""
    best = None
    for road in roads or []:
        dx, dy = px - road.a[0], py - road.a[1]
        t = max(0.0, min(road.length, dx * road.along[0] + dy * road.along[1]))
        q = road.point(t)
        d = math.hypot(px - q[0], py - q[1])
        if best is None or d < best[0]:
            best = (d, q, road)
    return best


def _near_junction(roads, px, py, own):
    """Is a road other than the pole's own within `JUNCTION_M` of its edge?"""
    for road in roads or []:
        if road is own:
            continue
        dx, dy = px - road.a[0], py - road.a[1]
        t = max(0.0, min(road.length, dx * road.along[0] + dy * road.along[1]))
        q = road.point(t)
        if math.hypot(px - q[0], py - q[1]) <= road.width / 2.0 + JUNCTION_M:
            return True
    return False


def tier_for(name, junction):
    """The pole's tier: `TIER_SHARE` by a hash of its name, one denser at a
    junction."""
    u = (_h(name, "tier") % 10000) / 10000.0
    acc, t = 0.0, 0
    for t, share in enumerate(TIER_SHARE):
        acc += share
        if u < acc:
            break
    if junction:
        t = min(len(TIERS) - 1, t + 1)
    return TIERS[t]


def plan_pole_bills(site_spec, roads, findings=None):
    """Hung `pole_flyers` sleeves round the streetlights and sign posts.

    Each pole gets a tier (`tier_for`); a band that starts where that tier
    starts (jittered) and stops within reach -- and under a sign post's
    blade; and a front that faces the night's key light by 0.85.0's rule: of
    the pole's four faces, sidewalk side first, the first turned to the
    light by `LIT_MIN`. A wrap is paper all round; its front is only where
    its newest sheets begin."""
    out, tiers = [], {t: 0 for t in TIERS}
    for i, cv in enumerate(site_spec.get("cover", []) or []):
        sp = cv.get("species")
        if sp not in POLES or not cv.get("at"):
            continue
        px, py = cv["at"]
        near = _nearest(roads, px, py)
        if near is None or near[0] < 1e-6:
            continue
        name = cv.get("name") or f"cover_{i}"
        tier = tier_for(name, _near_junction(roads, px, py, near[2]))
        tiers[tier] += 1
        if tier == "bare":
            continue
        ax, ay = (px - near[1][0]) / near[0], (py - near[1][1]) / near[0]
        lx, ly = LIGHT
        faces = (("sidewalk", ax, ay), ("along", -ay, ax), ("along", ay, -ax),
                 ("road", -ax, -ay))
        side, nx, ny = next(((f, x, y) for f, x, y in faces if x * lx + y * ly >= LIT_MIN),
                            max(faces, key=lambda f_: f_[1] * lx + f_[2] * ly))
        top_max = min(REACH, BLADE_CLEAR) if sp == "sign_post" else REACH
        band = TIER_BAND[tier]
        start = TIER_START[tier] + ((_h(name, "start") % 2001) / 1000.0 - 1.0) * START_JITTER
        start = max(0.05, min(start, top_max - band))
        diameter = round(2.0 * (POLES[sp] + AIR + (FLYER_LAYERS - 1) * FLYER_LAYER), 3)
        out.append(_record(f"pole_flyers_{i}", (px, py), facing_yaw(nx, ny),
                           (diameter, diameter, band), round(start + band / 2.0, 3),
                           host=f"pole:cover_{i}", base=cv.get("base"),
                           species="pole_flyers", form=tier, face=side,
                           lit=round(nx * lx + ny * ly, 3)))
    if findings is not None:
        findings.append(f"{CODE_ALLEY_POSTERS}: {len(out)} pole(s) papered -- "
                        + ", ".join(f"{t} {n}" for t, n in tiers.items()))
    return out


def _record(name, at, yaw, dims, z, host, base=None, species="poster_wall", form="alley",
            **extra):
    w, d, h = dims
    rec = {"name": name, "species": species, "form": form,
           "variant": _h(name) % VARIANTS,
           "at": [round(at[0], 4), round(at[1], 4)], "yaw": yaw,
           "dims": [w, d, h], "z": z, "base": base, "host": host,
           "source": "site_posters"}
    rec.update(extra)
    return rec


'''

LOT_MAT_OLD = '''                   # the handbills (site_posters): paper, the genome's own kind
                   "poster_wall": "paper"}'''
LOT_MAT_NEW = '''                   # the handbills (site_posters): paper, the genome's own kind
                   "poster_wall": "paper", "pole_flyers": "paper"}'''


def main():
    p = LOT / "site_posters.py"
    s = p.read_bytes().decode("utf-8")
    assert "\r\n" not in s
    for a, b in ((CONSTS_OLD, CONSTS_NEW), (POLES_OLD, POLES_NEW)):
        if s.count(a) != 1:
            sys.exit(f"REFUSED: site_posters.py anchor x{s.count(a)}: {a[:80]}")
        s = s.replace(a, b, 1)
    if s.count(POLE_FN_START) != 1 or s.count(POLE_FN_END) != 1:
        sys.exit("REFUSED: pole function anchors")
    a, b = s.index(POLE_FN_START), s.index(POLE_FN_END)
    s = s[:a] + POLE_FN_NEW + s[b:]
    q = LOT / "lot.py"
    t = q.read_bytes().decode("utf-8")
    if t.count(LOT_MAT_OLD) != 1:
        sys.exit("REFUSED: lot.py material anchor")
    t = t.replace(LOT_MAT_OLD, LOT_MAT_NEW, 1)
    p.write_bytes(s.encode("utf-8"))
    q.write_bytes(t.encode("utf-8"))
    print("patched site_posters.py and lot.py")


if __name__ == "__main__":
    main()
