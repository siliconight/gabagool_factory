"""Roadmap 309, its first measurement: which of Deli Counter's library families no brief can anchor. A family is a
built shell's name less its `_aNN` suffix (`deli_counter/build/*.manifest.json`, lf_ specs excepted); a brief can
anchor it when Level Factory's `_preset_for` resolves the family's name to a Deli Counter preset. Prints each family,
its shell count and the preset or the refusal. Measurements only.

    python docs/findings/civic_anchor_309/families_without_preset.py
"""
import collections
import pathlib
import re
import sys

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "level_factory"))
from adapters.deli_counter import UnknownArchetype, _preset_for  # noqa: E402

fam = collections.Counter()
for m in sorted((F / "deli_counter" / "build").glob("*.manifest.json")):
    name = m.name[:-len(".manifest.json")]
    if name.startswith("lf_"):
        continue
    fam[re.sub(r"_a\d+$", "", name)] += 1
ok, no = [], []
for f, n in sorted(fam.items()):
    try:
        ok.append((f, n, _preset_for(f)))
    except UnknownArchetype:
        no.append((f, n))
print("families %d (shells %d): anchorable %d (shells %d), not %d (shells %d)" % (
    len(fam), sum(fam.values()), len(ok), sum(n for _f, n, _p in ok), len(no), sum(n for _f, n in no)))
print("\nANCHORABLE (family -> preset):")
for f, n, p in ok:
    print("  %-32s %2d  -> %s" % (f, n, p))
print("\nNO PRESET:")
for f, n in no:
    print("  %-32s %2d" % (f, n))
