"""Which of `level_design._seed_clear`'s rules refuses each held wall slot a store's next video poker cabinet is
offered. `why.py` beside this says THAT `_seed_clear` refuses; this says WHICH `return False` it reached, by
tracing the function's own frame, and prints the rule's line with the comment above it. The candidates are
`_place_fixture`'s own (`_wall_slots` with its arguments, the cabinet's ordinal stream `k` = the cabinets the room
already holds), and `_seed_clear` is called exactly as `_place_fixture` calls it for a standing piece. A probe:
prints and stops (roadmap 196's four short stores).

    python why_rule.py <deli_counter dir> <spec name> <room id>
"""
import collections
import inspect
import json
import os
import random
import sys

dc = os.path.abspath(sys.argv[1])
sys.path.insert(0, dc)
os.chdir(dc)
import level_design as L  # noqa: E402

KEY = "video_poker_store"
spec = json.load(open(os.path.join("specs", sys.argv[2] + ".json"), encoding="utf-8"))
room = [r for r in spec["rooms"] if r.get("id") == sys.argv[3]][0]
p = L._PIECES[KEY]
story = room.get("story", 0)
rtag = L._room_tag(room)
k = sum(1 for stem, _s, _v in L._room_names(spec, rtag) if stem == KEY)
rng = random.Random(f"{spec.get('seed', 0)}:{room['id']}:fixture:{KEY}:{k}")
sizes = list(L._palette(spec, KEY))
rng.shuffle(sizes)
inner = L._nested_rects(spec, room)

code = L._seed_clear.__code__
src, first = inspect.getsourcelines(L._seed_clear)
hit = {}


def tracer(frame, event, arg):
    if frame.f_code is code:
        if event == "return":
            hit["line"] = frame.f_lineno
            hit["value"] = arg
        return tracer
    return None


why = collections.Counter()
where = collections.defaultdict(list)
total = passed = 0
for _r in range(L._FIXTURE_ROUNDS):
    for size in sizes:
        for spot in L._wall_slots(spec, room, size[0], size[1], rng, with_front=True,
                                  over_openings=L._over_openings(spec, story, p, size[2]),
                                  off_glass=p["off_glass"], back_off=L.piece_back_off(p)):
            w, d, h = size
            qx, qy = spot[0], spot[1]
            half = max(w, d) / 2.0
            if L._over_rects(inner, qx, qy, half, half):
                why["over a nested room (before _seed_clear)"] += 1
                continue
            total += 1
            hit.clear()
            sys.settrace(tracer)
            try:
                ok = L._seed_clear(spec, room, qx, qy, [], half=half, above=None, below=None,
                                   over_openings=L.hangs_over_openings(spec, story, None))
            finally:
                sys.settrace(None)
            if ok:
                passed += 1
                continue
            why[hit.get("line")] += 1
            where[hit.get("line")].append((round(qx, 2), round(qy, 2)))

print("%s %s: cabinet ordinal k=%d, bounds %s; %d candidate(s) reached _seed_clear, %d passed it"
      % (sys.argv[2], room["id"], k, room["bounds"], total, passed))
for line, n in why.most_common():
    if isinstance(line, str):
        print("  %3d  %s" % (n, line))
        continue
    i = line - first
    text = src[i].strip() if 0 <= i < len(src) else "?"
    # the nearest comment or condition above the return, for a reader
    ctx = [s.strip() for s in src[max(0, i - 4):i] if s.strip()]
    print("  %3d  line %d: %s   <- %s" % (n, line, text, " / ".join(ctx[-2:])[:160]))
    print("        e.g. at %s" % where[line][:3])
