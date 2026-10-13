"""One digest over every Deli Counter preset as Level Factory can make it -- did a change move a generated building?

    python docs/findings/agent_contract_follows/preset_digest.py <deli_counter dir>

Level Factory builds a mission's own building from a preset at run time, so a library shell's build manifest
(`outputs_sha256_16`) cannot say whether a change moved it. This makes every preset in `presets.REGISTRY` in each
of the modes "heist", "assault" and "survival" at one to four floors on seed 9104 -- a combination the preset
refuses (TypeError, ValueError) is skipped -- and prints how many specs it made and one sha256 over them all
(`json.dumps`, keys sorted). Run it on two Deli Counter directories; the same digest means the same buildings.
For Deli Counter 0.215.0: 0.214.0 and 0.215.0 both 228 specs, d53248c1158e3405; 0.213.0, the control,
eae19d7fad1d830f. Prints what it measured and stops.
"""
import hashlib
import json
import sys

sys.path.insert(0, sys.argv[1])
import presets   # noqa: E402

h = hashlib.sha256()
n = 0
for name in sorted(presets.REGISTRY):
    for mode in ("heist", "assault", "survival"):
        for floors in (1, 2, 3, 4):
            try:
                spec = presets.make(name, seed=9104, mode=mode, floors=floors)
            except (TypeError, ValueError):
                continue
            h.update(json.dumps(spec, sort_keys=True).encode("utf-8"))
            n += 1
print(n, "specs, sha256", h.hexdigest()[:16])
