"""The snack form's every plan and its image, as one digest: run from a Zoo checkout's root. 1.133.0 must print what
1.132.0 printed -- the grocery form is new, and nothing that shipped may move."""
import hashlib
import itertools
import json
import sys

sys.path.insert(0, ".")
from zoo_keeper.core import snack_gondola_forms as S  # noqa: E402

h = hashlib.sha256()
cases = list(S.DC_SIZES) + [tuple(c) for c in itertools.product(*(S.RANGES[a] for a in ("width", "depth", "height")))]
for c in cases:
    for v in range(4):
        g = S.plan(*c, "snack_gondola", v)
        f = dict(g["facts"])
        f.pop("form", None)
        f.pop("faces", None)
        h.update(json.dumps([g["prims"], f], sort_keys=True, default=str).encode())
a = S.bag_art()
h.update(bytes(a["canvas"].buf))
print(len(cases) * 4, "plans; art", a["name"], "; digest", h.hexdigest())
