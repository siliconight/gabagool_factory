#!/bin/bash
# Prove patch_lf_ground_unshaded.py (0.215.0) on a throwaway copy of level_factory at its HEAD (0.212.0) with
# 0.213.0 and 0.214.0 applied first (its anchors assume them), LF_ROOT pointing at the copy; the real repo
# untouched. The ground tests run before the patch (the restated one must fail, the new one must not exist) and
# after (all must pass); then the scene it writes is compared, line by line at the material, with the priced
# unshaded arm (`ground_strip.py unshaded` on 9308's backdrop): the price applies to what ships only if they agree.
F=/c/Projects/gabagool_studios/gabagool_factory
S="$1"
C="$S/lf_copy2"
TALLY='import re,sys;from collections import Counter;L=open(sys.argv[1],encoding="utf-8",errors="replace").read().splitlines();c="".join(re.sub(r"\s*\[\s*\d+%\]$","",l) for l in L if re.search(r"\[\s*\d+%\]$",l));print("tally",len(c),dict(Counter(c)))'
run_tests() {
  local label="$1"; shift
  (cd "$C" && python -m pytest -q "$@" > "$S/prove_run2.txt" 2>&1; echo "$label: exit $?")
  python -c "$TALLY" "$S/prove_run2.txt"
  grep -E "^FAILED|^ERROR" "$S/prove_run2.txt" | cut -c1-150
}
rm -rf "$C" && mkdir -p "$C"
git -C "$F/level_factory" archive HEAD | tar -x -C "$C" || exit 2
echo "copy at $(git -C "$F/level_factory" rev-parse --short HEAD), VERSION $(cat "$C/VERSION")"
LF_ROOT="$C" python "$F/patches/patch_lf_layers_shown.py" --results-pending > /dev/null || exit 3
LF_ROOT="$C" python "$F/patches/patch_lf_venv_pins.py" --results-pending > /dev/null || exit 4
echo "== 0.215.0's restated test against 0.214.0's backdrop_layer (must fail on the record)"
cp "$C/tests/unit/test_backdrop_ground.py" "$S/test_backdrop_ground_before.py"
LF_ROOT="$C" python "$F/patches/patch_lf_ground_unshaded.py" --results-pending || exit 5
cp "$C/tests/unit/test_backdrop_ground.py" "$S/test_backdrop_ground_after.py"
git -C "$F/level_factory" show HEAD:packages/exporting/backdrop_layer.py > "$C/packages/exporting/backdrop_layer.py"
run_tests "control (0.214.0's module, 0.215.0's tests)" tests/unit/test_backdrop_ground.py
echo "== apply 0.215.0's module again and run the ground tests (must pass)"
rm -rf "$C/packages/exporting/backdrop_layer.py"
cd "$C" && git -C "$F/level_factory" show HEAD:packages/exporting/backdrop_layer.py > "$C/packages/exporting/backdrop_layer.py" && cd "$S"
# re-apply the module edits alone: restore VERSION/CHANGELOG/test state the patch expects, then run it once more
git -C "$F/level_factory" show HEAD:tests/unit/test_backdrop_ground.py > "$C/tests/unit/test_backdrop_ground.py"
printf '0.214.0' > "$C/VERSION"
python - "$C" <<'EOF'
import pathlib, sys
c = pathlib.Path(sys.argv[1])
cl = c / "CHANGELOG.md"
text = cl.read_text(encoding="utf-8")
head = text.index("## [0.214.0] - What the three pins bring is held too")
cl.write_text(text[head:], encoding="utf-8")
EOF
LF_ROOT="$C" python "$F/patches/patch_lf_ground_unshaded.py" --results-pending || exit 6
run_tests "patched 0.215.0" tests/unit/test_backdrop_ground.py tests/unit/test_backdrop_layer.py
echo "== the material the patched module writes, against the priced unshaded arm's"
python - "$C" "$F" <<'EOF'
import pathlib, re, sys
c, f = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
sys.path.insert(0, str(c))
from packages.exporting import backdrop_layer as B
scene = ('[gd_scene load_steps=3 format=3]\n\n[ext_resource type="Mesh" path="res://backdrop/a.res" id="Mesh_a__N"]\n\n'
         '[sub_resource type="MultiMesh" id="MM_a__N"]\ninstance_count = 1\n\n[node name="site_backdrop" type="Node3D"]\n\n'
         '[node name="dress_a__N" type="MultiMeshInstance3D" parent="."]\nmultimesh = SubResource("MM_a__N")\n')
text, rec = B.with_ground(scene, [{"pos": [0.0, 0.0, 0.0], "side": "N"}])
pat = re.compile(r'\[sub_resource type="StandardMaterial3D" id="BackdropGround_mat"\]\n(.*?)\n\n', re.S)
mine = pat.search(text).group(1).split("\n")
priced = pat.search((f / "_scratch/price_ground/unshaded/site_backdrop.tscn").read_text(encoding="utf-8")).group(1).split("\n")
print("patched module writes:", mine)
print("priced arm carries:   ", priced)
print("the same material, line for line:", mine == priced, "| record:", rec)
EOF
echo "== heads"; head -1 "$C/CHANGELOG.md"; cat "$C/VERSION"; echo
rm -rf "$C" "$S/prove_run2.txt" "$S/test_backdrop_ground_before.py" "$S/test_backdrop_ground_after.py"
echo "copy removed"
