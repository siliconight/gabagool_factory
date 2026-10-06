"""Pixelcoat 0.59.0: `cli.main._ZOO_KINDS` is Zoo's `skins.KNOWN_KINDS`
again, and a test reads Zoo to say so.

`_ZOO_KINDS` is a COPY of another repo's list, and it drifted. Measured
2026-10-06, both read as source with `ast`:
- Zoo 1.75.0 knows 38 kinds and this lists 36.
- `wood_panel` and `slatwall` are in Zoo, there since Zoo 0.95.0's card shop,
  and missing here. So `_warn_unknown_kind` told an author their pack would
  reach no mesh, and it would.
- The test standing guard asserted they were ABSENT
  (`test_card_shop_surfaces.test_the_new_kinds_are_not_claimed_as_kinds_zoo_knows`).
  Its docstring says "When Zoo grows them, this test is what says so". It
  never read Zoo, so it could not.

Zoo 1.77.0 adds `chain_link` (the fence's fabric, this repo's 0.56.0
profile). All three join the list. The stale test becomes a mirror:
- it finds a Zoo checkout by walking up from the test;
- it reads `KNOWN_KINDS` with `ast`;
- it asserts the two sets are equal;
- it skips only when no Zoo checkout is found.

    python patch_pixelcoat_zoo_kinds.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PX = ROOT / "pixelcoat"

EDITS = {
    PX / "pixelcoat/cli/main.py": [
        ('''              # a house's own brick (0.57.0, Zoo 1.73.0): the comp's row is
              # brown, red and orange, one brick a house
              "brick_brown", "brick_orange")
''',
         '''              # a house's own brick (0.57.0, Zoo 1.73.0): the comp's row is
              # brown, red and orange, one brick a house
              "brick_brown", "brick_orange",
              # the card shop's panels (0.44.0), which Zoo has known since
              # its 0.95.0 and this list missed until 0.59.0
              "wood_panel", "slatwall",
              # a fence's wire fabric (0.56.0, Zoo 1.77.0)
              "chain_link")
'''),
    ],
    PX / "tests/test_card_shop_surfaces.py": [
        ('''def test_the_new_kinds_are_not_claimed_as_kinds_zoo_knows():
    """`cli.main._ZOO_KINDS` mirrors Zoo's `skins.KNOWN_KINDS`, and the
    warning it drives is the only thing that tells an author a pack will
    reach no mesh. `wood_panel` and `slatwall` are not in Zoo's vocabulary
    yet, so listing them here would turn a true warning into a false
    reassurance. When Zoo grows them, this test is what says so.
    """
    from pixelcoat.cli import main as cli
    for kind in ("wood_panel", "slatwall"):
        assert kind not in cli._ZOO_KINDS, (
            f"{kind} is listed as a kind Zoo knows -- check "
            f"zoo_keeper/core/skins.KNOWN_KINDS actually has it")
''',
         '''def test_the_kinds_zoo_knows_are_the_kinds_zoo_knows():
    """`cli.main._ZOO_KINDS` mirrors Zoo's `skins.KNOWN_KINDS`, and the
    warning it drives is the only thing that tells an author a pack will
    reach no mesh. Until 0.59.0 this test asserted `wood_panel` and
    `slatwall` were absent, "until Zoo grows them" -- and never read Zoo,
    so when Zoo 0.95.0 grew them it went on passing while the warning lied.
    It reads Zoo now, as source (Zoo's skins module is pure, but importing
    another repo's package from here is a coupling this suite does not
    need)."""
    import ast
    from pathlib import Path

    from pixelcoat.cli import main as cli
    skins = None
    for parent in Path(__file__).resolve().parents:
        cand = parent / "zoo" / "zoo_keeper" / "core" / "skins.py"
        if cand.is_file():
            skins = cand
            break
    if skins is None:
        pytest.skip("no Zoo checkout above this repo")
    tree = ast.parse(skins.read_text(encoding="utf-8"))
    known = next(ast.literal_eval(n.value) for n in tree.body
                 if isinstance(n, ast.Assign)
                 and any(getattr(t, "id", None) == "KNOWN_KINDS" for t in n.targets))
    assert set(cli._ZOO_KINDS) == set(known), (
        f"missing here: {sorted(set(known) - set(cli._ZOO_KINDS))}; "
        f"not in Zoo ({skins}): {sorted(set(cli._ZOO_KINDS) - set(known))}")
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
