"""Edit a Zoo clone's check_desk genome for 1.141.0: the budget the pens' ball chains cost. Run from the clone's root.
Asserts the 1.140.0 value; refuses on a miss."""
import json

P = "zoo_keeper/genome/species/check_desk.json"
raw = open(P, "rb").read().decode("utf-8")
crlf = "\r\n" in raw
text = raw.replace("\r\n", "\n")
g = json.loads(text)
assert json.dumps(g, indent=1, ensure_ascii=False) + "\n" == text, "the genome does not round-trip"
assert g["budgets"] == {"tris_lod0": 2000}, g["budgets"]
# 1.141.0: two pens on ball chains, 68 beads of 12 triangles; the widest desk (3.2 m) builds 2,764
g["budgets"] = {"tris_lod0": 3000}
out = json.dumps(g, indent=1, ensure_ascii=False) + "\n"
open(P, "wb").write((out.replace("\n", "\r\n") if crlf else out).encode("utf-8"))
print(P, "edited", "CRLF" if crlf else "LF")
