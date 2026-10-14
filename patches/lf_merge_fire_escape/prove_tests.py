"""Prove Level Factory 0.209.0's two new tests fail where they should and pass where they should.

1. the rule test against 0.208.0's merge_empties.gd (git show b8fe4f7) -> FAIL; against 0.209.0's -> PASS
2. the schema test against a Deli Counter whose enum names a second side -> FAIL; one without the field -> FAIL;
   the real Deli Counter -> PASS
The patched script is restored byte for byte and its hash checked before this exits.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LF = F / "level_factory"
GD = LF / "assets" / "godot" / "merge_empties.gd"
T = "tests/unit/test_merge_empties.py"
RULE = T + "::test_a_walk_up_s_fire_escape_merges_with_its_front"
SCHEMA = T + "::test_deli_counter_stands_a_fire_escape_only_on_the_front"


def pytest(node, env=None):
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", node], cwd=LF,
                       capture_output=True, text=True, env=env)
    tail = [l for l in (p.stdout + p.stderr).splitlines() if l.strip()][-3:]
    return p.returncode, tail


patched = GD.read_bytes()
digest = hashlib.sha256(patched).hexdigest()
old = subprocess.run(["git", "-C", str(LF), "show", "b8fe4f7:assets/godot/merge_empties.gd"],
                     capture_output=True).stdout
assert old and b'begins_with("fire_escape_")' not in old and b'begins_with("fire_escape_")' in patched
try:
    GD.write_bytes(old)
    rc, tail = pytest(RULE)
    print("rule test on 0.208.0's script: exit %d  %s" % (rc, tail[-1] if tail else ""))
finally:
    GD.write_bytes(patched)
assert hashlib.sha256(GD.read_bytes()).hexdigest() == digest, "the patched script was not restored"
rc, tail = pytest(RULE)
print("rule test on 0.209.0's script: exit %d  %s" % (rc, tail[-1] if tail else ""))

real = json.loads((F / "deli_counter" / "schema" / "level.schema.json").read_text(encoding="utf-8"))
with tempfile.TemporaryDirectory() as td:
    for label, mutate in (("enum front+back", lambda s: s["properties"]["fire_escape_stack"].__setitem__(
                              "enum", ["front", "back", None])),
                          ("no field", lambda s: s["properties"].pop("fire_escape_stack"))):
        root = pathlib.Path(td) / label.replace(" ", "_").replace("+", "_") / "deli_counter"
        (root / "schema").mkdir(parents=True)
        s = json.loads(json.dumps(real))
        mutate(s)
        (root / "schema" / "level.schema.json").write_text(json.dumps(s), encoding="utf-8")
        env = dict(os.environ, LF_DC_ROOT=str(root))
        rc, tail = pytest(SCHEMA, env)
        print("schema test, Deli Counter with %-15s: exit %d  %s" % (label, rc, tail[-1] if tail else ""))
env = {k: v for k, v in os.environ.items() if k != "LF_DC_ROOT"}
rc, tail = pytest(SCHEMA, env)
print("schema test, the real Deli Counter:          exit %d  %s" % (rc, tail[-1] if tail else ""))
