"""Inside Blender: the five golden digests of Zoo's `tests/test_club_bpy.py`, as a given Zoo builds them.

    blender -b --factory-startup --python docs/findings/club_digests/digests_at.py -- <zoo root> <out.json>

The Zoo at `<zoo root>` (a checkout or a `git archive` of one) supplies `zoo_keeper`; the test's own `_build`,
`_digest` and `MAIN_DIGESTS` come from the CURRENT Zoo's `tests/test_club_bpy.py` beside the factory, so every
version is measured by one instrument and compared against one set of pins. Each key is built once, in a temporary
folder, through the kit path the test uses.

Writes `{"root", "zoo_version", "digests": {key: digest or "ERROR: ..."}, "stored": {key: digest}}` and prints a
line per key: the digest, and whether it is the pinned one. It names no cause.
"""
import importlib.util
import json
import sys
import tempfile
import traceback
from pathlib import Path

argv = sys.argv[sys.argv.index("--") + 1:]
ROOT, OUT = Path(argv[0]).resolve(), Path(argv[1])
F = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("club_test", F / "zoo" / "tests" / "test_club_bpy.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)

import zoo_keeper  # noqa: E402

assert Path(zoo_keeper.__file__).resolve().is_relative_to(ROOT), (zoo_keeper.__file__, ROOT)
version = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").is_file() else "?"


def _name(key):
    sp, dims, fields = key
    return "%s %s %s" % (sp, "x".join("%g" % v for v in dims), ",".join("%s=%s" % kv for kv in fields) or "-")


got = {}
for key in sorted(T.MAIN_DIGESTS):
    sp, dims, fields = key
    try:
        with tempfile.TemporaryDirectory() as td:
            _res, objs = T._build(Path(td), sp, dims, **dict(fields))
            got[_name(key)] = T._digest(objs)
    except Exception as exc:  # an old Zoo that cannot build a key says so, and the rest still run
        got[_name(key)] = "ERROR: %s: %s" % (type(exc).__name__, str(exc).splitlines()[0][:160] if str(exc) else "")
        traceback.print_exc()
stored = {_name(k): v for k, v in T.MAIN_DIGESTS.items()}
OUT.write_text(json.dumps({"root": str(ROOT), "zoo_version": version, "digests": got, "stored": stored},
                          indent=1), encoding="utf-8")
for name in sorted(got):
    print("[digests_at] %-46s %s %s" % (name, got[name][:40], "PINNED" if got[name] == stored[name] else "differs"))
