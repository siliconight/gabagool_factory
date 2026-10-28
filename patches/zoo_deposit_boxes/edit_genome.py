"""Edit a Zoo clone's safe_deposit_boxes genome for 1.140.0: bare steel, the lock, plate and drawn parts, and the
budget the hardware costs. Run from the clone's root. Asserts the 1.139.0 values; refuses on a miss."""
import json

P = "zoo_keeper/genome/species/safe_deposit_boxes.json"
raw = open(P, "rb").read().decode("utf-8")
g = json.loads(raw)
assert json.dumps(g, indent=1, ensure_ascii=False) + "\n" == raw
assert g["materials"] == {"default": "metal", "options": ["metal", "laminate"]}, g["materials"]
assert g["parts"] == ["SafeDepositBoxes_Backing", "SafeDepositBoxes_Divider"], g["parts"]
assert g["budgets"] == {"tris_lod0": 1400}, g["budgets"]
g["materials"] = {"default": "metal_bare", "options": ["metal_bare", "laminate"]}
g["parts"] = ["SafeDepositBoxes_Backing", "SafeDepositBoxes_Divider", "SafeDepositBoxes_Lock",
              "SafeDepositBoxes_Plate", "SafeDepositBoxes_Drawn"]
# 1.140.0: two unbevelled plates a door (24 triangles) over at most 16 x 16 doors, on the frame's 1,400
g["budgets"] = {"tris_lod0": 8000}
n = 0
for name, st in g["styles"].items():
    if st.get("material") == "metal":
        st["material"] = "metal_bare"
        n += 1
assert n == 4, n
open(P, "wb").write((json.dumps(g, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
print(P, "edited;", n, "styles to metal_bare")
