"""Level Factory 0.150.0: VERSION and CHANGELOG for the deli's words.

    python patch_lf_0150_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-07.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

ENTRY = '''## [0.150.0] - A brief that asks for a deli gets the corner deli

**Refused since 0.146.0.** `deli`, `night_deli` and `stop_n_go` were left
refused (`UnknownArchetype`), "outside the three kinds, and the detail audit
of 2026-10-06 lists them as open". A brief that asked for a deli in plain
words never reached a building.

**The delis are no longer open there**, generated and drawn alike:
- **Deli Counter 0.199.0** stops the case at its wall. It used to run 0.825 m
  out into the market aisles.
- **Zoo 1.81.0** builds the case as a species of its own: curved glass, a lit
  deck, logs cut to the glass. **Deli Counter 0.200.0** routes it.
- **Deli Counter 0.201.0** hangs a beer sign in the deli's front window and
  tapes sale posters under it.

**The words, in `_ARCHETYPE_ALIASES`:**
- `deli`, `delicatessen` and `night_deli` build `corner_deli`;
- `stop_n_go` builds `convenience_store`. It is the library's Flappahs store
  by another name, and 0.147.0 already dresses it in FLAPPAHS.

**Left refused, as 0.146.0 decided:**
- `corner_store`: as often the deli as the Flappahs store in Philadelphia;
- `nightclub` and `night_club`: no recipe;
- `truck_stop`: a diesel plaza, not the corner station.

**The fascia needs nothing new.** `_sign_rows` already reads a generated
row's preset through `_preset_for` (0.146.0), so a `deli` brief's building
is dealt from Pixelcoat's deli family.

**Unproven until it runs cold:** a one-building `deli` brief, which takes the
generated path.

**Tests:** `tests/unit/test_dc_preset_registry.py` +1. It fails on 0.149.0,
where every one of those words raised. `tests/test_archetype_resolution.py`
draws its cases from the alias table, so it grows by four.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = LF / "VERSION"
    assert v.read_bytes().strip() == b"0.149.0", v.read_bytes()
    cl = LF / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.149.0] - Every placed building's package is read"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(v.read_bytes().replace(b"0.149.0", b"0.150.0"))
    print("Level Factory 0.150.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
