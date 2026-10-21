"""arena_a02's rebuilt records against HEAD, keyed by what each entry IS rather than where it sits in its list:
slots by `slot_id`, gameplay's keyed sections by their name or id, lights' anchors by their id. `record_moves.py`
compares leaf by leaf with list positions in the path, so a slot list that lost four entries near its front reads as
hundreds of moves (960 in this build's slots.json, 199 in its gameplay.json) and attributes none of them. Build-time
keys (`*_utc`) set aside. Paths are Deli Counter's; prints what it found and stops.

    python patches/dc_ticket_queue/slot_moves.py
"""
import json
import subprocess

DC = r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter"


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if not k.endswith("_utc")}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def pair(rel):
    old = json.loads(subprocess.run(["git", "-C", DC, "show", "HEAD:" + rel], capture_output=True, check=True).stdout)
    new = json.load(open(DC + "\\" + rel.replace("/", "\\"), encoding="utf-8"))
    return strip(old), strip(new)


def key_of(e):
    """What an entry IS: its slot id, id, name or node; an opening, which carries none, by its wall, kind and place."""
    for k in ("slot_id", "id", "name", "node", "slot_ref", "ref"):
        if isinstance(e, dict) and e.get(k) is not None:
            return "%s=%s" % (k, e[k])
    if isinstance(e, dict) and {"wall", "kind", "x", "y"} <= set(e):
        return "%s %s at (%s, %s)" % (e["wall"], e["kind"], e["x"], e["y"])
    return None


def keyed(rows):
    out, dup = {}, 0
    for i, e in enumerate(rows):
        k = key_of(e) or "#%d %s" % (i, json.dumps(e, sort_keys=True)[:80])
        if k in out:
            dup += 1
            k = "%s (again %d)" % (k, dup)
        out[k] = e
    return out


def diff_fields(a, b):
    keys = sorted(set(a) | set(b)) if isinstance(a, dict) and isinstance(b, dict) else []
    return ["%s: %r -> %r" % (k, a.get(k, "<absent>"), b.get(k, "<absent>")) for k in keys if a.get(k) != b.get(k)]


def report(rel, section, old_rows, new_rows):
    a, b = keyed(old_rows), keyed(new_rows)
    gone, came = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    moved = [k for k in sorted(set(a) & set(b)) if a[k] != b[k]]
    print("%s %s: %d -> %d entries; %d gone, %d new, %d changed" % (rel, section, len(a), len(b), len(gone),
                                                                     len(came), len(moved)))
    for k in gone:
        print("   gone %s" % k)
    for k in came:
        print("   new  %s" % k)
    for k in moved:
        print("   changed %s: %s" % (k, "; ".join(diff_fields(a[k], b[k]))[:600]))


old, new = pair("build/arena_a02.slots.json")
report("slots.json", "slots", old["slots"], new["slots"])
others = sorted(k for k in set(old) | set(new) if k != "slots" and old.get(k) != new.get(k))
print("slots.json other keys moved: %s" % (others or "none"))
for k in others:
    print("   %s: %r -> %r" % (k, old.get(k), new.get(k)))

old, new = pair("build/arena_a02.gameplay.json")
for k in sorted(set(old) | set(new)):
    a, b = old.get(k), new.get(k)
    if a == b:
        continue
    if isinstance(a, list) and isinstance(b, list):
        report("gameplay.json", k, a, b)
    elif isinstance(a, dict) and isinstance(b, dict):
        ks = sorted(set(a) | set(b))
        ch = [x for x in ks if a.get(x) != b.get(x)]
        print("gameplay.json %s: %d keys changed" % (k, len(ch)))
        for x in ch:
            print("   %s: %r -> %r" % (x, a.get(x, "<absent>"), b.get(x, "<absent>")))
    else:
        print("gameplay.json %s: %r -> %r" % (k, a, b))

old, new = pair("build/arena_a02.lights.json")
for k in sorted(set(old) | set(new)):
    a, b = old.get(k), new.get(k)
    if a == b:
        continue
    if isinstance(a, list) and isinstance(b, list):
        report("lights.json", k, a, b)
    else:
        print("lights.json %s: %r -> %r" % (k, a, b))

old, new = pair("build/arena_a02.manifest.json")
print("manifest.json: %s" % ("; ".join(diff_fields(old, new)) or "the same"))
