"""Level Factory 0.146.0, second half: a fascia is dealt a business's name,
never the fuel price board.

Found while writing Pixelcoat 0.58.0's release, before anything shipped. The
`gas_station` family in both sign profiles is now FLAPPAHS and `fuel_price`,
the price board (Pixelcoat 0.34.0), which has no `text`: it suits a station
and names nobody. `_signs_for` picks from a family's pool by hash, so
measured with this checkout's own `_signs_for` on `delco_1997`:

    generated gas_station alone          b0 = fuel_price
    gas_station_a02 at row index 0, 2    fuel_price
    gas_station_a01 at row index 1, 3    fuel_price

`patch_lf_flappahs_store.py`'s `_sign_rows` is what exposed it. Until then a
generated row read as `default` and never reached the gas pool. No recorded
cold run dealt the board (every `shop sign(s)` line under docs/cold_runs and
workspaces), so excluding it changes no level that shipped.

Every entry without `text` in both profiles is `fuel_price` alone (checked
2026-10-06), so "a name" and "not the board" are the same rule today.

    python patch_lf_signs_names_only.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {
    LF / "apps/cli/commands/__init__.py": [
        ('''    out: dict[str, str] = {}
    taken: set[str] = set()
    for i, b in enumerate(buildings):
        family = sign_family(b.get("archetype") or b.get("id"))
        pool = [s for s in profile if family in (s.get("families") or [])]
        if not pool:
            pool = [s for s in profile if "default" in (s.get("families") or [])]
''',
         '''    out: dict[str, str] = {}
    taken: set[str] = set()
    # A fascia names a business (0.146.0). Pixelcoat's fuel price board sits
    # in the `gas_station` family because it suits a station, but it names
    # nobody: with that family down to FLAPPAHS and the board (Pixelcoat
    # 0.58.0), a generated gas station standing alone was dealt the board in
    # place of its brand. An entry with no text is never dealt.
    named = [s for s in profile if s.get("text")]
    for i, b in enumerate(buildings):
        family = sign_family(b.get("archetype") or b.get("id"))
        pool = [s for s in named if family in (s.get("families") or [])]
        if not pool:
            pool = [s for s in named if "default" in (s.get("families") or [])]
'''),
    ],
    LF / "tests/unit/test_signs_in_site_spec.py": [
        ('''    assert rows[0] == {"id": "b0"}          # the site spec's own rows are untouched
''',
         '''    assert rows[0] == {"id": "b0"}          # the site spec's own rows are untouched


def test_a_station_and_a_store_wear_flappahs_never_the_price_board():
    """0.146.0. The walker, 2026-10-06: "Flappahs store always Flappahs".
    The gas family is FLAPPAHS and the fuel price board (Pixelcoat 0.58.0),
    and the board names nobody. Before names-only dealing a generated gas
    station standing alone drew the board, and so did `gas_station_a02` at
    the head of a row."""
    ws = _Workspace()
    for archetype in ("gas_station", "convenience_store"):
        rows = cmds._sign_rows([{"id": "b0"}], archetype)
        signs = cmds._signs_for(ws, rows, Path("/px/out"), "delco_1997")
        assert Path(signs["b0"]).name == "sign_flappahs", (archetype, signs)
    for archetype in ("gas_station_a01", "gas_station_a02", "convenience_store_a01"):
        for i in range(4):
            rows = [{"id": f"x{j}", "archetype": "deli_a01"} for j in range(i)]
            rows.append({"id": "b", "archetype": archetype})
            signs = cmds._signs_for(ws, rows, Path("/px/out"), "delco_1997")
            assert Path(signs["b"]).name == "sign_flappahs", (archetype, i, signs)
    # one brand a site: a station beside the store is FLAPPAHS twice
    rows = [{"id": "b0", "archetype": "gas_station_a02"},
            {"id": "b1", "archetype": "convenience_store_a01"}]
    signs = cmds._signs_for(ws, rows, Path("/px/out"), "delco_1997")
    assert {Path(d).name for d in signs.values()} == {"sign_flappahs"}, signs
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
