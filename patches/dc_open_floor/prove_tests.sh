#!/bin/bash
# Prove patch_dc_open_floor.py (Deli Counter 0.223.0) on a throwaway copy of deli_counter's python, schema and
# specs at HEAD (6c312336, 0.222.0), DC_ROOT pointing at it: the new tests fail before (no open_floors), pass
# after, beside L24's and the layout tests. Then apply it to the real repo with its results pending, write the
# baseline (its census), run the full suite, fill both results, commit (with -F alone) and push. Stops at the
# first step that fails. Removes only the throwaway copy it made, by its literal path.
F=/c/Projects/gabagool_studios/gabagool_factory
D=$F/deli_counter
S="$1"
C="$S/dc_copy"
rm -rf "$S/dc_copy" && mkdir -p "$C"
(cd "$D" && git archive HEAD -- '*.py' schema specs walk_reach_baseline.json VERSION CHANGELOG.md | tar -x -C "$C") || exit 2
echo "copy at $(git -C "$D" rev-parse --short HEAD), $(cat "$C/VERSION"), $(ls "$C"/*.py | wc -l) python files, $(ls "$C/specs" | wc -l) specs"
echo "== 0.223.0's tests on the unpatched copy (the six that touch the code must fail)"
cp "$F/patches/dc_open_floor/test_open_floor.py.txt" "$C/test_open_floor.py"
printf '{"open_floors": {}, "reason": "empty, for the proof"}\n' > "$C/open_floor_baseline.json"
(cd "$C" && python -m pytest -q test_open_floor.py 2>&1 | tail -3 | cut -c1-160)
rm -f "$S/dc_copy/test_open_floor.py" "$S/dc_copy/open_floor_baseline.json"
echo "== apply 0.223.0 to the copy"
DC_ROOT="$C" python "$F/patches/patch_dc_open_floor.py" --results-pending || exit 3
(cd "$C" && python open_floor_baseline.py | tail -1)
echo "== the patched copy: the new tests, L24's, the layout and tactical tests (must pass)"
(cd "$C" && python -m pytest -q test_open_floor.py test_walk_reach.py test_layout_coherence.py test_partition_bounds.py 2>&1 | tail -3 | cut -c1-160)
(cd "$C" && python -c "import json; print(json.load(open('schema/level.schema.json'))['properties']['rooms']['items']['properties']['open_to'])")
rm -rf "$S/dc_copy"
echo "== apply 0.223.0 to the real repo ($(date +%H:%M:%S))"
python "$F/patches/patch_dc_open_floor.py" --results-pending || exit 4
git -C "$D" status --short
echo "== the census (the baseline written)"
(cd "$D" && python open_floor_baseline.py | tee "$F/patches/dc_open_floor/census.out.txt" | tail -4)
tail -1 "$F/patches/dc_open_floor/census.out.txt" | sed 's/ -> .*//' > "$F/patches/dc_open_floor/result_census.txt"
echo "== the suite ($(date +%H:%M:%S))"
(cd "$D" && python -m pytest -q > "$F/_scratch/dc_0223_suite.txt" 2>&1; echo "suite exit $?")
tail -1 "$F/_scratch/dc_0223_suite.txt" | cut -c1-160
grep -E "^FAILED|^ERROR" "$F/_scratch/dc_0223_suite.txt" | head -8 | cut -c1-160
if grep -qE "^FAILED|^ERROR| failed" "$F/_scratch/dc_0223_suite.txt"; then echo "the suite failed; stopping before the fill"; exit 5; fi
line=$(tail -1 "$F/_scratch/dc_0223_suite.txt" | sed 's/^=* *//; s/ *=*$//')
printf '%s\n' "\`python -m pytest -q\`: $line, exit 0 -- 0.222.0's 1,540 and \`test_open_floor.py\`'s 9" > "$F/patches/dc_open_floor/result_suite.txt"
python "$F/patches/patch_dc_open_floor.py" --fill || exit 6
if grep -q "RESULT_" "$D/CHANGELOG.md"; then echo "an unfilled RESULT_ is left in the CHANGELOG"; exit 7; fi
printf '\n%s\n' "Suite: $line, exit 0. The census: $(cat "$F/patches/dc_open_floor/result_census.txt")." >> "$F/_scratch/dc_0223_commit_msg.txt"
git -C "$D" add -A || exit 8
git -C "$D" status --short
git -C "$D" commit -q -F "$F/_scratch/dc_0223_commit_msg.txt" || exit 9
git -C "$D" log -1 --format="%h %s" | cut -c1-90
echo "attribution lines: $(git -C "$D" log -1 --format=%B | grep -ci 'co-authored\|generated with\|claude')"
git -C "$D" push origin main 2>&1 | tail -1
echo "DC at $(git -C "$D" rev-parse --short HEAD), $(cat "$D/VERSION"), clean: $(git -C "$D" status --short | wc -l) changes ($(date +%H:%M:%S))"
