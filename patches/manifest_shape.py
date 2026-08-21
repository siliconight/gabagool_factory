import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "factory.manifest.json")
with open(P, "r", encoding="utf-8") as fh:
    m = json.load(fh)
print("top-level keys: %s" % ", ".join(m.keys()))
print("factory_version: %r" % m.get("factory_version"))
for key in ("tools", "pins", "components", "require", "audit"):
    v = m.get(key)
    if v is None:
        continue
    print("")
    print("m[%r] is a %s with %d entr(ies)" % (key, type(v).__name__, len(v)))
    items = v.items() if isinstance(v, dict) else enumerate(v)
    for k, entry in items:
        name = k if isinstance(v, dict) else (entry.get("name") if isinstance(entry, dict) else k)
        if str(name) in ("zoo", "pixelcoat"):
            print("  %s -> %s" % (name, json.dumps(entry, indent=4)[:600]))
print("")
d = m.get("description")
if isinstance(d, str):
    print("description is a %d-char string; first 400:" % len(d))
    print(d[:400])
elif d is not None:
    print("description type: %s" % type(d).__name__)
