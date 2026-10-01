"""Deli Counter 0.165.0, follow-up to `patch_dc_sign_business.py`: import the
module the new argument calls.

That patch passed `business=_ld.club_building_id(builder.s)` in
`write_light_manifest`, and its dry run checked only that the text
`import level_design as _ld` occurs in `deli_counter.py`. It does -- as a
LOCAL import inside `club_room_ids`, not at module scope. The first library
build raised `NameError: name '_ld' is not defined` in every building's light
manifest; `_run_in_blender.main` writes the build manifest after that call,
so it was skipped too, and `build.py --all` exited 0 with 128 of 131 shells
unrebuilt on disk. The fix imports it where it is used, beside the
function's own `import lights as _lights`.
"""
from __future__ import annotations

import pathlib

P = pathlib.Path(__file__).resolve().parents[1] / "deli_counter" / "deli_counter.py"

OLD = '''    import json
    import lights as _lights
    # The slab that caps each storey, from the ONE place that rule lives.'''
NEW = '''    import json
    import level_design as _ld
    import lights as _lights
    # The slab that caps each storey, from the ONE place that rule lives.'''


def main():
    raw = P.read_bytes()
    assert b"\r\n" not in raw
    s = raw.decode("utf-8")
    assert s.count(OLD) == 1, s.count(OLD)
    P.write_bytes(s.replace(OLD, NEW).encode("utf-8"))
    print("patched deli_counter.py")


if __name__ == "__main__":
    main()
