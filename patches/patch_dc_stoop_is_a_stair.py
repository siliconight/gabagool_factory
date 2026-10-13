"""Deli Counter 0.211.1: a stoop is circulation, not a prop standing in it (factory roadmap 240; found by
cold run 9271, `PRESENTATION_CIRCULATION` 0 -> 12, "stoop_landing 0.15 m into doorway:ext_0_S_open0").

Anchored edits, each asserted exactly once and the file's sha16 pinned, nothing written until all of them
matched:
  deli_counter.py                 `_stoop` draws its landing and treads with the surface role `stair`
  test_stoop_circulation.py       NEW (`dc_stoop_is_a_stair/test_stoop_circulation.py.txt`)
CHANGELOG and VERSION from `dc_stoop_is_a_stair/CHANGELOG_0.211.1.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. The shells are rebuilt after (`build.py --all`, Blender): the build's freshness
is read off `deli_counter.py`'s time.

Read before it was written, in this session: `_stoop` (0.211.0), `_box` (a VISUAL box's role goes to
`surface_roles` and picks its greybox material, `_paint`; `stair` is `gb_stair`), the role tint table,
every reader of `surface_roles` (Deli Counter's `circulation.shell_prop_boxes`, the only one asking for
`prop`; Lot namespaces them; Level Factory reads none), `circulation.doorway_volume` (`wall bottom +
sill`, against `_opening_piece`'s `wall bottom + floor_thick / 2 + sill`), `check_shell` and its caller
`portable_building` (greybox glb, slot manifest, gameplay). Every file LF.

    python patches/patch_dc_stoop_is_a_stair.py --results-pending
    (build.py --all; python -m pytest -q in deli_counter)
    python patches/patch_dc_stoop_is_a_stair.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_stoop_is_a_stair"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILD": "result_build.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.211.0", b"Deli Counter 0.211.1"
CHANGELOG_HEAD = "## [0.211.0] - a rowhome Empty stands three steps up, on a stoop"
SHA = {"deli_counter.py": "8273298a3dbfe05d"}
NEW = {"test_stoop_circulation.py": "test_stoop_circulation.py.txt"}

EDITS = {
    "deli_counter.py": [
        ("        steps up to its raised front door. The landing and the treads are\n"
         "        visuals recorded as `prop` slots in concrete, so the art pass dresses\n"
         "        them as it does a volume;",
         "        steps up to its raised front door. The landing and the treads are\n"
         "        `stair` to the circulation gate -- the way to the door, never a prop\n"
         "        standing in its doorway (0.211.1) -- and visuals recorded as `prop`\n"
         "        slots in concrete, so the art pass dresses them as it does a volume;"),
        ("        for name, (c, size) in pieces:\n"
         "            self._box(name, c, size, self.VISUAL, role=\"prop\")\n",
         "        for name, (c, size) in pieces:\n"
         "            # A STOOP IS CIRCULATION (0.211.1): drawn `prop`, the landing read\n"
         "            # as a prop 0.15 m into its own doorway in all twelve rowhomes\n"
         "            # (cold run 9271) -- `circulation.doorway_volume` starts a door at\n"
         "            # its wall's bottom plus its sill, 0.15 m under the threshold the\n"
         "            # landing's top is. A flight's treads are `stair`, and so is this.\n"
         "            self._box(name, c, size, self.VISUAL, role=\"stair\")\n"),
    ],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.211.1.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.211.1: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.211.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.211.1] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    for rel in NEW:
        assert not (DC / rel).exists(), ("already applied", rel)
    writes = {}
    for rel, pairs in EDITS.items():
        p = DC / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    news = {rel: (SRC / src).read_bytes().replace(b"\r\n", b"\n") for rel, src in NEW.items()}
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    for rel, data in news.items():
        (DC / rel).write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    print("Deli Counter 0.211.0 -> 0.211.1")


if __name__ == "__main__":
    main()
