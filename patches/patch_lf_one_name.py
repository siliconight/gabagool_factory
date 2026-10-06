"""Level Factory 0.148.0: one business a shell, on its band and over its door.

The walker, 2026-10-06, option A on `docs/findings/two_names_one_building/`:
"Agreed" -- one name list on both of a building's signs, the door box's.

  * DEALT PER SHELL, NOT PER ROW. Zoo builds a shell's fixtures once and every
    instance of the shell wears that one door box, so a band dealt per row
    could give two instances of one shell two names over one door's one.
    `deal_signs` now deals each distinct shell (a row's archetype, or for a
    generated building the preset it was built from) one business, by a
    stable hash of the shell, no two shells on a street the same while the
    family has another. `_signs_for` maps rows through it.
  * THE DOOR WEARS THE BAND. A fixtures job's spec carries `sign_pack`: the
    pack its shell was dealt on the selected candidate's street, read off
    that candidate's judged site spec (the themed site stands the same
    buildings). The Zoo adapter passes it as `--sign-pack` (Zoo 1.79.0), and
    the fixtures job now depends on the candidate's Pixelcoat build, which
    makes the pack. A shell dealt no band (0.147.0) gets none, and its door
    is named by Zoo as before.
  * FINER FAMILIES, Zoo's door kinds: `card` and `video` before `shop` and
    `store` read them as retail; `pizza` is not `restaurant`; `brewery` is
    not `liquor`; `pharmacy` is not `retail`. Pixelcoat 0.61.0 fills each with
    exactly Zoo's names.

    python patch_lf_one_name.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {
    LF / "apps/cli/commands/__init__.py": [
        ('''    ("strip_club", "none"), ("parking", "none"),
    ("bank", "bank"), ("credit_union", "bank"), ("pawn", "pawn"),
    ("deli", "deli"), ("diner", "restaurant"), ("restaurant", "restaurant"),
    ("cheesesteak", "deli"), ("pizza", "restaurant"),
    ("brewery", "liquor"), ("distillery", "liquor"), ("bar", "bar"),
''',
         '''    ("strip_club", "none"), ("parking", "none"),
    # Zoo's door kinds (0.148.0), each its own family so a band can be dealt
    # the names its door is painted with: a card shop and a video store
    # before `shop` and `store` read them as retail
    ("card", "card"), ("video", "video"),
    ("bank", "bank"), ("credit_union", "bank"), ("pawn", "pawn"),
    ("deli", "deli"), ("diner", "restaurant"), ("restaurant", "restaurant"),
    ("cheesesteak", "deli"), ("pizza", "pizza"),
    ("brewery", "brewery"), ("distillery", "liquor"), ("bar", "bar"),
'''),
        ('''    ("store", "retail"), ("pharmacy", "retail"), ("laundr", "retail"),
)
''',
         '''    ("store", "retail"), ("pharmacy", "pharmacy"), ("laundr", "retail"),
)
'''),
        ('''def _signs_for(ws, buildings, pixelcoat_out: Path, theme: str) -> dict[str, str]:
    """Which sign each building wears: `{building id: pack directory}`.

    A building takes a business of its own family, chosen by a stable hash
    of its archetype and its place in the row, and no two buildings on one
    street take the same one while the family has another to give -- a
    strip with two GOOSE MARTs reads as a mistake, which it is. A building
    whose family the theme has nothing for takes a `default`; a theme with
    no signs profile gives nobody one, and Lot draws no band.
    """
    profile = _sign_profile(ws, theme)
    if not profile:
        return {}
    out: dict[str, str] = {}
    taken: set[str] = set()
''',
         '''def _shell_key(row) -> str:
    """The shell a site row stands: its archetype, or its id."""
    return str(row.get("archetype") or row.get("id") or "")


def sign_pack_dir(pixelcoat_out, slug: str) -> str:
    """Where Pixelcoat's theme build writes the pack for business ``slug``."""
    return str(Path(pixelcoat_out) / "signs" / f"sign_{slug}")


def deal_signs(ws, buildings, theme: str) -> dict[str, str]:
    """Which business each SHELL is: `{shell: sign slug}` (0.148.0).

    One business a shell, not a row. Zoo builds a shell's door box once and
    every instance of it wears that box, so the band (Lot) and the door (Zoo)
    can only name one business if the shell is what is dealt -- the walker's
    option A, 2026-10-06: one name list on both signs. A shell takes a
    business of its own family, by a stable hash of the shell, and no two
    shells on one street take the same one while the family has another to
    give -- a strip with two JAWN'S HOAGIES reads as a mistake. A shell of no
    shop family takes none (0.147.0); a theme with no signs profile deals
    nobody, and Lot draws no band.
    """
    profile = _sign_profile(ws, theme)
    if not profile:
        return {}
    out: dict[str, str] = {}
    taken: set[str] = set()
'''),
        ('''    named = [s for s in profile if s.get("text")]
    for i, b in enumerate(buildings):
        family = sign_family(b.get("archetype") or b.get("id"))
        if family in NO_BAND:
            continue
''',
         '''    named = [s for s in profile if s.get("text")]
    for b in buildings:
        key = _shell_key(b)
        if key in out:
            continue                          # one business a shell
        family = sign_family(key)
        if family in NO_BAND:
            continue
'''),
        ('''        h = 2166136261
        for ch in f"{b.get('archetype', '')}:{i}":
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
        start = h % len(pool)
        pick = None
        for step in range(len(pool)):
            cand = pool[(start + step) % len(pool)]
            if cand["slug"] not in taken:
                pick = cand
                break
        pick = pick or pool[start]
        taken.add(pick["slug"])
        out[b["id"]] = str(Path(pixelcoat_out) / "signs" / f"sign_{pick['slug']}")
    return out
''',
         '''        h = 2166136261
        for ch in key:
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
        start = h % len(pool)
        pick = None
        for step in range(len(pool)):
            cand = pool[(start + step) % len(pool)]
            if cand["slug"] not in taken:
                pick = cand
                break
        pick = pick or pool[start]
        taken.add(pick["slug"])
        out[key] = pick["slug"]
    return out


def _signs_for(ws, buildings, pixelcoat_out: Path, theme: str) -> dict[str, str]:
    """Which sign each building wears: `{building id: pack directory}` -- its
    shell's business (`deal_signs`, 0.148.0)."""
    deal = deal_signs(ws, buildings, theme)
    return {b["id"]: sign_pack_dir(pixelcoat_out, deal[_shell_key(b)])
            for b in buildings if _shell_key(b) in deal}


def _door_sign_pack(ws, model, candidate_id, shell_id, pixelcoat_out) -> str:
    """The pack a fixtures job's door box wears (0.148.0, option A): the
    business `deal_signs` dealt its shell on the candidate's street, or ""
    when it was dealt none. Read off the candidate's judged site spec, whose
    buildings the themed site stands unchanged, through the same `_sign_rows`
    the site spec's own deal reads -- so the band and the door are one deal.
    ``shell_id`` is the library shell, or None for the brief's generated one,
    which reads as the preset it was built from."""
    seed = int(str(candidate_id).rsplit("_", 1)[-1])
    site = (ws.internal_dir / "temp" / model.mission_id
            / f"candidate_seed_{seed}" / "site.json")
    if not site.is_file():
        print(f"[fixtures] no site spec at {site}: the door box of "
              f"{shell_id or 'the generated shell'} is named by Zoo, not dealt")
        return ""
    rows = _sign_rows(json.loads(site.read_text(encoding="utf-8")).get("buildings") or [],
                      model.archetype)
    key = shell_id or _sign_rows([{"id": "_"}], model.archetype)[0]["archetype"]
    slug = deal_signs(ws, rows, model.theme).get(key)
    return sign_pack_dir(pixelcoat_out, slug) if slug else ""
'''),
        ('''                specs[job.job_id] = {
                    "mode": "fixtures",
                    "seed": int(str(job.candidate_id).rsplit("_", 1)[-1]),
                    "theme": model.theme or batch.get("theme_family", ""),
                    "lights_path": lights_path,
                    # A fixture build that fails IS a failure — hardware is
                    # load-bearing for the lighting contract, unlike kit
                    # module misses.
                }
''',
         '''                specs[job.job_id] = {
                    "mode": "fixtures",
                    "seed": int(str(job.candidate_id).rsplit("_", 1)[-1]),
                    "theme": model.theme or batch.get("theme_family", ""),
                    "lights_path": lights_path,
                    # A fixture build that fails IS a failure — hardware is
                    # load-bearing for the lighting contract, unlike kit
                    # module misses.
                }
                # THE DOOR WEARS THE BAND (0.148.0): the business this shell
                # was dealt, as the pack its street band wears. Found by
                # candidate, as the dressing branch finds its pixelcoat job.
                pix_job = next(
                    (j.job_id for j in plan.graph.topological_order()
                     if j.adapter_id == "pixelcoat"
                     and j.candidate_id == job.candidate_id), None)
                if pix_job:
                    door = _door_sign_pack(
                        ws, model, job.candidate_id, entry["id"] if entry else None,
                        _latest_output(jobs_dir / pix_job, "."))
                    if door:
                        specs[job.job_id]["sign_pack"] = door
'''),
    ],
    LF / "adapters/zoo/__init__.py": [
        ('''            if job_spec.get("fixture_types"):
                zoo_args += ["--fixture-types",
                             *[str(t) for t in job_spec["fixture_types"]]]
''',
         '''            if job_spec.get("fixture_types"):
                zoo_args += ["--fixture-types",
                             *[str(t) for t in job_spec["fixture_types"]]]
            # the business the shell's band was dealt (0.148.0): its door box
            # wears the same pack (Zoo 1.79.0)
            if job_spec.get("sign_pack"):
                zoo_args += ["--sign-pack", str(job_spec["sign_pack"])]
'''),
    ],
    LF / "packages/pipeline/planner.py": [
        ('''                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="blender",
                depends_on=[deli_sel_jid],
                expected_outputs=[],  # zoo names by scope_id at exec; adapter checks
''',
         '''                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="blender",
                # 0.148.0: and the Pixelcoat build, whose sign pack the door
                # box now wears (the band's business, one name on both)
                depends_on=[deli_sel_jid, pixelcoat_jid],
                expected_outputs=[],  # zoo names by scope_id at exec; adapter checks
'''),
    ],
    LF / "tests/unit/test_fixture_pipeline.py": [
        ('''def test_zoo_fixtures_marker_contract_blocks(tmp_path):
''',
         '''def test_the_fixtures_build_waits_for_the_sign_pack_it_wears():
    """0.148.0: a door box wears its band's Pixelcoat pack, so the bake
    depends on the Pixelcoat build that makes it."""
    brief = _Brief()
    p1 = plan_mission(brief, seed_base=7, layers={planner_mod.LAYER_ART})
    plan = plan_mission(brief, seed_base=7, layers={planner_mod.LAYER_ART},
                        selected_candidate=_selected(p1))
    stages = {j.stage_id: j for j in plan.graph.jobs()}
    assert stages["pixelcoat_build"].job_id in stages["zoo_fixtures_build"].depends_on


def test_zoo_fixtures_mode_passes_the_door_its_pack(tmp_path):
    """0.148.0: `sign_pack` reaches Zoo as `--sign-pack` (Zoo 1.79.0)."""
    lights = tmp_path / "shell.lights.json"
    lights.write_text(json.dumps({
        "light_manifest_version": "1.1", "building_id": "lf_m1",
        "anchors": [{"id": "a", "type": "sign", "pos": [0, 0, 3]}]}))
    pack = str(tmp_path / "signs" / "sign_jawns_hoagies")
    spec = {"mode": "fixtures", "lights_path": str(lights), "theme": "delco",
            "sign_pack": pack}
    cmds = ZooAdapter().plan_commands(spec, {
        "repository": str(tmp_path), "work_dir": str(tmp_path / "work"),
        "blender_executable": "blender"})
    args = list(cmds[0].arguments)
    assert args[args.index("--sign-pack") + 1] == pack


def test_zoo_fixtures_marker_contract_blocks(tmp_path):
'''),
    ],
    LF / "tests/unit/test_signs_in_site_spec.py": [
        ('''def test_a_band_names_a_shop():
''',
         '''def test_a_shell_is_dealt_one_business_wherever_it_stands():
    """0.148.0: Zoo builds a shell's door box once, so every instance of the
    shell must wear one band; two shells still never repeat."""
    ws = _Workspace()
    rows = [{"id": "b0", "archetype": "deli_a01"}, {"id": "b1", "archetype": "bank_tower_a03"},
            {"id": "b2", "archetype": "deli_a01"}, {"id": "b3", "archetype": "deli_a02"}]
    signs = cmds._signs_for(ws, rows, Path("/px/out"), "delco_1997")
    assert signs["b0"] == signs["b2"]
    assert signs["b0"] != signs["b3"]               # another deli shell, another name
    deal = cmds.deal_signs(ws, rows, "delco_1997")
    assert set(deal) == {"deli_a01", "bank_tower_a03", "deli_a02"}


def test_zoos_door_kinds_are_families_of_their_own():
    """0.148.0: so a band can be dealt the names its door is painted with
    (Pixelcoat 0.61.0 holds each family to Zoo's list)."""
    for shell, family in (("card_shop_a01", "card"), ("video_store_a01", "video"),
                          ("pharmacy_a01", "pharmacy"), ("primos_pizza", "pizza"),
                          ("brewery_a01", "brewery"), ("deli_a01", "deli"),
                          ("bank_branch_a02", "bank"), ("pawn_shop_a01", "pawn"),
                          ("supermarket_a01", "supermarket")):
        assert cmds.sign_family(shell) == family, shell


def test_a_door_wears_its_shells_band(tmp_path):
    """0.148.0: the fixtures job's pack is the deal the site spec's band
    reads -- library shells by id, the generated one by its preset."""
    ws = _Workspace(internal_dir=tmp_path / "internal")
    model = SimpleNamespace(mission_id="m", archetype="corner_deli", theme="delco_1997")
    site = tmp_path / "internal" / "temp" / "m" / "candidate_seed_9181" / "site.json"
    site.parent.mkdir(parents=True)
    rows = [{"id": "b0", "archetype": "deli_a01"}, {"id": "b1", "archetype": "casino_a02"}]
    site.write_text(json.dumps({"buildings": rows}), encoding="utf-8")
    band = cmds._signs_for(ws, rows, Path("/px/out"), "delco_1997")
    door = cmds._door_sign_pack(ws, model, "m.candidate.seed_9181", "deli_a01", Path("/px/out"))
    assert door == band["b0"] and door.endswith("sign_" + cmds.deal_signs(ws, rows, "delco_1997")["deli_a01"])
    assert cmds._door_sign_pack(ws, model, "m.candidate.seed_9181", "casino_a02", Path("/px/out")) == ""
    # the brief's own generated shell: rows with no archetype, read as the preset
    site.write_text(json.dumps({"buildings": [{"id": "b0"}]}), encoding="utf-8")
    gen = cmds._door_sign_pack(ws, model, "m.candidate.seed_9181", None, Path("/px/out"))
    assert gen and "sign_" in gen
    # no site spec: said, and Zoo names the door
    assert cmds._door_sign_pack(ws, model, "m.candidate.seed_1", "deli_a01", Path("/px/out")) == ""


def test_a_band_names_a_shop():
'''),
    ],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
