"""Deli Counter 0.214.0, second edit: the vault door's aperture named among what does not follow the contract yet.

Applied after `patch_dc_door_width.py`, in the same release. `clearances.re_derive_when` lists what one change to
a body moves on its own and what does not; it named `stairwell.LANDING_DEPTH` and missed the vault door. Its
aperture, 1.3 x 2.1 m, is the door minimum rounded up and the headroom plus 0.1 -- by comment, in three
literals across two tools: `vault_room.APERTURE` and `spec_types`' vault default in Deli Counter, and
`vault_forms.DEFAULT_OPENING` in Zoo, the round door built to it. A minimum raised past 1.3 would leave the
vault under it with nothing saying so. Found reading the other tools' uses of `min_door_width_m` for the
walker's "so we can make singular changes when we know the size of characters in the game".

Anchored edits, each asserted exactly once and each file's sha16 pinned (the files as the first patch wrote
them), nothing written until both matched:
  agent_contract.json   `re_derive_when`'s NOT YET FOLLOWING sentence names the vault aperture; every other
                        value checked unchanged
  test_door_width.py    the phrase list asks for `vault_room.APERTURE` too

    python patches/patch_dc_door_width_vault_note.py
"""
import hashlib
import json
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SHA = {"agent_contract.json": "b9ed4a7f46e253b8", "test_door_width.py": "7e2cb8718a164676"}

CONTRACT_OLD = ("NOT YET FOLLOWING: stairwell.LANDING_DEPTH, the 1.2 m of clear floor at a stair's ends, is a "
                "literal. Then rebuild")
CONTRACT_NEW = ("NOT YET FOLLOWING, as literals: stairwell.LANDING_DEPTH, the 1.2 m of clear floor at a stair's "
                "ends; and the vault door's aperture, 1.3 x 2.1 m -- this block's door minimum rounded up and "
                "its headroom plus 0.1 -- in Deli Counter (vault_room.APERTURE, spec_types' vault default) and "
                "in Zoo (vault_forms.DEFAULT_OPENING, the round door built to it), so a minimum raised past 1.3 "
                "leaves the vault under it. Then rebuild")
TEST_OLD = "                   \"stairwell.LANDING_DEPTH\"):\n"
TEST_NEW = "                   \"stairwell.LANDING_DEPTH\", \"vault_room.APERTURE\"):\n"


def _read(rel):
    raw = (DC / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    assert b"\r\n" not in raw, (rel, "is LF")
    return raw.decode("utf-8")


def main():
    contract = _read("agent_contract.json")
    test = _read("test_door_width.py")
    for rel, text, old in (("agent_contract.json", contract, CONTRACT_OLD), ("test_door_width.py", test, TEST_OLD)):
        assert text.count(old) == 1, (rel, "anchor", text.count(old))
    new_contract = contract.replace(CONTRACT_OLD, CONTRACT_NEW)
    was, now = json.loads(contract), json.loads(new_contract)
    assert "vault_room.APERTURE" in now["clearances"]["re_derive_when"]
    now["clearances"]["re_derive_when"] = was["clearances"]["re_derive_when"]
    assert now == was, "agent_contract.json: something besides re_derive_when moved"
    # both anchored: now write
    (DC / "agent_contract.json").write_bytes(new_contract.encode("utf-8"))
    (DC / "test_door_width.py").write_bytes(test.replace(TEST_OLD, TEST_NEW).encode("utf-8"))
    print("Deli Counter 0.214.0: the vault aperture named in clearances.re_derive_when")


if __name__ == "__main__":
    main()
