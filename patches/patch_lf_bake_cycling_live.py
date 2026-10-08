"""Level Factory 0.160.0: the light bake keeps a cycling rig live (roadmap 213).

The walker, 2026-10-08, left live or baked to us and asked for a brighter
stage; the call is live, so the club's stage colour cycle runs. The bake
marked every Lux rig resource without a `failing_kind` BAKE_STATIC, and a
baked stage rig stops cycling (`lux_stage_light_rig.gd`, `_cycles()`).

THE TRAP THE FIX STEPS AROUND. The cycle is the rig NODE's: `cycle_period_s`
and `colors` are `LuxStageLightRig` exports. `mark_steady_rigs` reads rig
RESOURCES, which carry only `bake_mode` and the lamp numbers. So the bake
reads which resources a cycling node uses -- `_cycling_rigs`, the rig's own
test, `cycle_period_s` > 0 over two or more `colors` -- and leaves those
resources as Lux wrote them. Lux 0.69.0 is the other half: a cycling rig's
lamps carry no indirect energy, so a live stage bakes no frozen bounce.

Anchored edits (every anchor once; refuses on a miss; nothing is written until
every anchor in every file matched):
- `packages/exporting/light_bake.py`: the module note, `mark_steady_rigs` (a
  third count, `cycling`), and the bake's log line.
- `tests/unit/test_light_bake.py`: its two assertions on the return carry
  the new key.
New file from `lf_bake_cycling_live/`: `tests/unit/test_light_bake_cycling.py`.
CHANGELOG and VERSION from `lf_bake_cycling_live/CHANGELOG_0.160.0.md`.

    python patch_lf_bake_cycling_live.py
    LF_ROOT=<copy> python patch_lf_bake_cycling_live.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_cycling_live"
CHANGELOG_HEAD = "## [0.159.0] - The light census counts what the renderer pairs, beside what reaches\n"

NOTE_OLD = (
    "  * the steady lights marked STATIC: every Lux rig in the presentation scene\n"
    "    whose resource carries no `failing_kind` gets `bake_mode = 1`. A failing\n"
    "    fixture (a stuttering tube, a cycling pole, a wavering bulb) stays live.\n")
NOTE_NEW = (
    "  * the steady lights marked STATIC: every Lux rig in the presentation scene\n"
    "    whose resource carries no `failing_kind` gets `bake_mode = 1`. A failing\n"
    "    fixture (a stuttering tube, a cycling pole, a wavering bulb) stays live,\n"
    "    and so does a rig a CYCLING node uses -- a club's stage (0.160.0).\n")

MARK_OLD = (
    "def mark_steady_rigs(scene: Path) -> dict:\n"
    "    \"\"\"`bake_mode = 1` on every Lux rig resource in `scene` that carries no\n"
    "    `failing_kind`. ``{\"static\": n, \"live\": n}``. Refuses a scene with no\n"
    "    rig script, which is a scene this does not understand.\"\"\"\n"
    "    text = Path(scene).read_text(encoding=\"utf-8\")\n"
    "    m = re.search(r'\\[ext_resource type=\"Script\" (?:uid=\"[^\"]*\" )?path=\"res://[^\"]*lux_light_rig\\.gd\" id=\"([^\"]+)\"\\]', text)\n"
    "    if m is None:\n"
    "        raise ValueError(f\"{scene}: no lux_light_rig.gd script resource\")\n"
    "    rig = m.group(1)\n"
    "    blocks = re.split(r\"(?=^\\[)\", text, flags=re.M)\n"
    "    static = live = 0\n"
    "    for i, b in enumerate(blocks):\n"
    "        if not b.startswith('[sub_resource type=\"Resource\"') or f'script = ExtResource(\"{rig}\")' not in b:\n"
    "            continue\n"
    "        if re.search(r\"^failing_kind = [1-9]\", b, flags=re.M):\n"
    "            live += 1\n"
    "            continue\n")
MARK_NEW = (
    "def _cycling_rigs(blocks: list) -> set:\n"
    "    \"\"\"The rig resource ids a CYCLING node uses (0.160.0, roadmap 213): a node\n"
    "    whose `cycle_period_s` is over 0 across two or more `colors` --\n"
    "    `LuxStageLightRig._cycles()`'s own test, read off the scene text. The\n"
    "    cycle is the node's and the bake mode is the resource's, so this is the\n"
    "    only place the two meet.\"\"\"\n"
    "    out = set()\n"
    "    for b in blocks:\n"
    "        if not b.startswith(\"[node \"):\n"
    "            continue\n"
    "        rig = re.search(r'^rig = SubResource\\(\"([^\"]+)\"\\)$', b, flags=re.M)\n"
    "        period = re.search(r\"^cycle_period_s = ([0-9.eE+-]+)$\", b, flags=re.M)\n"
    "        colors = re.search(r\"^colors = PackedColorArray\\(([^)]*)\\)$\", b, flags=re.M)\n"
    "        if not (rig and period and colors):\n"
    "            continue\n"
    "        n_colors = len([v for v in colors.group(1).split(\",\") if v.strip()]) // 4\n"
    "        if float(period.group(1)) > 0.0 and n_colors > 1:\n"
    "            out.add(rig.group(1))\n"
    "    return out\n"
    "\n"
    "\n"
    "def mark_steady_rigs(scene: Path) -> dict:\n"
    "    \"\"\"`bake_mode = 1` on every Lux rig resource in `scene` that carries no\n"
    "    `failing_kind` and no cycling node uses (`_cycling_rigs`, 0.160.0).\n"
    "    ``{\"static\": n, \"live\": n, \"cycling\": n}`` -- `live` the failing ones.\n"
    "    A resource a cycling node uses is left as Lux wrote it: baked, a stage\n"
    "    rig stops cycling. Refuses a scene with no rig script, which is a scene\n"
    "    this does not understand.\"\"\"\n"
    "    text = Path(scene).read_text(encoding=\"utf-8\")\n"
    "    m = re.search(r'\\[ext_resource type=\"Script\" (?:uid=\"[^\"]*\" )?path=\"res://[^\"]*lux_light_rig\\.gd\" id=\"([^\"]+)\"\\]', text)\n"
    "    if m is None:\n"
    "        raise ValueError(f\"{scene}: no lux_light_rig.gd script resource\")\n"
    "    rig = m.group(1)\n"
    "    blocks = re.split(r\"(?=^\\[)\", text, flags=re.M)\n"
    "    cycling_ids = _cycling_rigs(blocks)\n"
    "    static = live = cycling = 0\n"
    "    for i, b in enumerate(blocks):\n"
    "        if not b.startswith('[sub_resource type=\"Resource\"') or f'script = ExtResource(\"{rig}\")' not in b:\n"
    "            continue\n"
    "        if re.search(r\"^failing_kind = [1-9]\", b, flags=re.M):\n"
    "            live += 1\n"
    "            continue\n"
    "        rid = re.match(r'\\[sub_resource type=\"Resource\" id=\"([^\"]+)\"\\]', b)\n"
    "        if rid and rid.group(1) in cycling_ids:\n"
    "            cycling += 1\n"
    "            continue\n")

RETURN_OLD = (
    "    Path(scene).write_text(\"\".join(blocks), encoding=\"utf-8\", newline=\"\\n\")\n"
    "    return {\"static\": static, \"live\": live}\n")
RETURN_NEW = (
    "    Path(scene).write_text(\"\".join(blocks), encoding=\"utf-8\", newline=\"\\n\")\n"
    "    return {\"static\": static, \"live\": live, \"cycling\": cycling}\n")

LOG_OLD = (
    "            \"%d steady rig(s) baked, %d failing left live; %s; %d users, %s s in the editor\"\n"
    "            % (len(report[\"imports\"][\"baked\"]), sum(report[\"primitives\"].values()),\n"
    "               len(report[\"imports\"][\"dynamic\"]), report[\"rigs\"][\"static\"], report[\"rigs\"][\"live\"],\n")
LOG_NEW = (
    "            \"%d steady rig(s) baked, %d failing and %d cycling left live; %s; %d users, %s s in the editor\"\n"
    "            % (len(report[\"imports\"][\"baked\"]), sum(report[\"primitives\"].values()),\n"
    "               len(report[\"imports\"][\"dynamic\"]), report[\"rigs\"][\"static\"], report[\"rigs\"][\"live\"],\n"
    "               report[\"rigs\"][\"cycling\"],\n")

TEST_OLD_1 = "    assert LB.mark_steady_rigs(scene) == {\"static\": 2, \"live\": 1}\n"
TEST_NEW_1 = "    assert LB.mark_steady_rigs(scene) == {\"static\": 2, \"live\": 1, \"cycling\": 0}\n"
TEST_OLD_2 = "    assert r[\"rigs\"] == {\"static\": 2, \"live\": 1}\n"
TEST_NEW_2 = "    assert r[\"rigs\"] == {\"static\": 2, \"live\": 1, \"cycling\": 0}\n"

EDITS = {
    "packages/exporting/light_bake.py": [
        (NOTE_OLD, NOTE_NEW), (MARK_OLD, MARK_NEW), (RETURN_OLD, RETURN_NEW), (LOG_OLD, LOG_NEW),
    ],
    "tests/unit/test_light_bake.py": [
        (TEST_OLD_1, TEST_NEW_1), (TEST_OLD_2, TEST_NEW_2),
    ],
}
NEW = {"tests/unit/test_light_bake_cycling.py": "test_light_bake_cycling.py"}


def stage(root):
    """{path: bytes} for every edited and new file under ``root``, or raise.
    Nothing is written here: every anchor in every file must match first."""
    staged = {}
    for rel in NEW:
        assert not (root / rel).exists(), ("already applied", rel)
    for name, edits in EDITS.items():
        p = root / name
        d = p.read_bytes()
        crlf = b"\r\n" in d
        assert not (crlf and d.replace(b"\r\n", b"").count(b"\n")), (name, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in edits:
            n = t.count(old)
            assert n == 1, (name, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    for rel, src in NEW.items():
        staged[root / rel] = (SRC / src).read_bytes()
    return staged


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.159.0", repr(v)
    staged = stage(LF)
    entry = (SRC / "CHANGELOG_0.160.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    c = (LF / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:80]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    (LF / "CHANGELOG.md").write_bytes((entry + text).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.160.0")
    print("Level Factory 0.159.0 -> 0.160.0")


if __name__ == "__main__":
    main()
