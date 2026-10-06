"""Level Factory 0.149.0: the presentation adapter reads every placed
building's package, names the building in each finding, and reads the
circulation gate. The compose driver prints that gate from its arms.

MEASURED (`docs/findings/presentation_gates/` at the factory root, cold run
9187):
- `normalize_validation` read `next(...)` of 16 sorted manifests, which is
  lot/deli_a01's. Three of fifteen buildings failed z-fight (deli_a01 203
  pairs, office 121, rail_station_a02 117), and one finding was recorded.
- It had no branch for `circulation_check`. Every cold run from 9164 to 9187
  failed that gate on every building, and none reached a finding.
- The driver printed the gate from the top of Deli Counter's two-arm schema,
  "0 prop conflict(s) across ? circulation volume(s)": a FAIL with nothing in
  it.
- Deli Counter 0.191.0 makes the gate honest (parts, not merged nodes; a
  stair's guards excused). On 9187's buildings it now names one thing:
  deli_a01's counter island over its stairwell.

    python patch_lf_presentation_every_building.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"
ADAPTER = LF / "adapters" / "presentation" / "__init__.py"
DRIVER = LF / "assets" / "scripts" / "run_presentation_compose.py"

ADAPTER_OLD = '''        manifest = next((p for p in output_paths
                         if p.name == "portable_resource_manifest.json"), None)
        if manifest is None:
            return issues
        try:
            man = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return issues

        # Closure: a dangling res:// ref means Lux will light a broken scene.
        closure = man.get("closure") or {}
        if closure and not closure.get("portable", True):
            issues.append({
                "code": "PRESENTATION_UNRESOLVED_REF",
                "severity": "blocker", "category": "packaging",
                "message": ("composed scene has dangling/absolute resource refs: "
                            f"{(closure.get('dangling_refs') or [])[:5]}"),
                "blocking": True, "raw_source_path": str(manifest)})

        # Ground-truth placement gate: themed visuals must sit on DC's collision.
        # A partial kit leaves slots greybox, and those are not counted -- the
        # gate checks only the modules the composer placed. This was advisory
        # from the day it was written, and every cold run from 9001 to 9012
        # carried it as a moderate finding nobody read (9005: 30 mismatched;
        # 9012's bank: 18) while the packages shipped wall remainders standing
        # across their walls. The walker found one beside a doorway. The
        # driver's exit is advisory by design (`exit_advisory`), so this
        # finding is where the red has to live: it blocks, and names the slots.
        pc = man.get("placement_check")
        if pc and pc.get("mismatched"):
            named = ", ".join(
                f"{m.get('slot')} ({m.get('stem')}: placed "
                f"{m.get('placed_extent')} on greybox {m.get('greybox_extent')})"
                for m in (pc.get("mismatches") or [])[:5] if isinstance(m, Mapping))
            issues.append({
                "code": "PRESENTATION_PLACEMENT_MISMATCH",
                "severity": "blocker", "category": "collision",
                "message": (f"{pc.get('mismatched')} themed module(s) do not match "
                            f"the greybox footprint (visual off the collision); "
                            f"{pc.get('matched')}/{pc.get('checked')} aligned. "
                            f"Worst: {named or 'not reported'}"),
                "blocking": True, "raw_source_path": str(manifest)})

        # Z-FIGHTING: the composer computes it, prints "the package would
        # flicker", exits 3 -- and nothing read it. `presentation_compose`'s
        # exit code is advisory by design, so the job records SUCCEEDED, and
        # with no branch here the finding never reached a status line. Three
        # cold runs shipped a package the composer itself said would flicker
        # and each was recorded as clean (roadmap 133).
        #
        # Advisory, like the placement gate beside it: coplanar faces are an
        # art defect and refusing to build the level over one would stop it
        # existing long enough to be looked at. Loud, though -- the count and
        # the worst offenders by name, so it is actionable rather than a
        # number.
        #
        # `buried_pairs` and `greybox_internal_pairs` are broken out because
        # they are not the same defect: a pair where one face is buried inside
        # a solid cannot flicker, and a pair between two greybox faces is
        # under the art rather than in it. Reporting the total alone would
        # send somebody hunting for 30 visible seams when this scene has 8.
        zf = man.get("zfight_check")
        if isinstance(zf, Mapping) and zf.get("ok") is False:
            pairs = int(zf.get("pairs") or 0)
            buried = int(zf.get("buried_pairs") or 0)
            internal = int(zf.get("greybox_internal_pairs") or 0)
            visible = max(0, pairs - buried - internal)
            worst = ", ".join(
                f"{f.get('a')} / {f.get('b')}"
                for f in (zf.get("findings") or [])[:3] if isinstance(f, Mapping))
            issues.append({
                "code": "PRESENTATION_ZFIGHT",
                "severity": "moderate", "category": "presentation",
                "message": (
                    f"{pairs} coplanar face pair(s) across "
                    f"{zf.get('solids')} solids in {zf.get('scene')} — the "
                    f"package would flicker where two surfaces share a plane. "
                    f"{buried} buried, {internal} greybox-internal, so "
                    f"{visible} can be seen. Worst: {worst or 'not reported'}"),
                "blocking": False, "raw_source_path": str(manifest)})

        # No themed modules resolved at all = the kit didn't feed the compose.
        if not man.get("walkable", True):
            issues.append({
                "code": "PRESENTATION_NO_BASE",
                "severity": "moderate", "category": "packaging",
                "message": "no greybox base composed — level has no floors to stand on",
                "blocking": False, "raw_source_path": str(manifest)})
        return issues
'''

ADAPTER_NEW = '''        # EVERY PLACED BUILDING, NOT THE FIRST MANIFEST (0.149.0). A varied
        # lot composes one package a building under `_LOT_SUBDIR`, and this
        # read `next(...)` of the sorted manifests -- the first building's.
        # In cold run 9187 three of fifteen failed z-fight (deli_a01 203
        # pairs, office 121, rail_station_a02 117) and the one finding
        # recorded was deli_a01's. Each building is read now, and each
        # finding names it.
        for manifest, building in _placed_manifests(output_paths):
            try:
                man = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                # Said, not swallowed: an unreadable manifest used to return
                # quietly and take every finding about its package with it.
                issues.append({
                    "code": "PRESENTATION_MANIFEST_UNREADABLE",
                    "severity": "moderate", "category": "packaging",
                    "message": (f"{building}: the composed package's manifest "
                                f"could not be read ({exc}), so none of its "
                                f"gates were"),
                    "blocking": False, "location": building,
                    "raw_source_path": str(manifest)})
                continue
            issues.extend(_manifest_issues(man, manifest, building))
        return issues


def _placed_manifests(output_paths) -> list:
    """``[(manifest, building)]`` for every package the level PLACES.

    A varied lot places one package a building under `_LOT_SUBDIR`. The
    mission's own shell is composed to the root for the job's output contract
    and placed only when there is no lot (see `_LOT_SUBDIR`). Reading the
    root of a lot would report on a package the level does not contain:
    9187's lists dangling refs, which block.
    """
    mans = sorted(p for p in output_paths
                  if p.name == "portable_resource_manifest.json")
    lot = [p for p in mans if p.parent.parent.name == "lot"
           and p.parent.parent.parent.name == _OUT_SUBDIR]
    if lot:
        return [(p, p.parent.name) for p in lot]
    return [(p, _STABLE_BID) for p in mans[:1]]


def _circulation_arms(circ) -> list:
    """``[(arm, check)]`` of a `circulation_check`. Deli Counter writes two
    arms and a verdict when a package has a greybox and a dressing layer,
    and one check carrying its ``source`` otherwise. The compose driver
    splits it the same way (`circulation_gate`)."""
    if not isinstance(circ, Mapping):
        return []
    arms = [(k, circ[k]) for k in ("shell", "dressing")
            if isinstance(circ.get(k), Mapping)]
    return arms or [(str(circ.get("source") or "shell"), circ)]


def _manifest_issues(man, manifest, building) -> list:
    """The gates of ONE composed package; every finding names its building."""
    issues: list[dict] = []
    where = f"{building}: "

    # Closure: a dangling res:// ref means Lux will light a broken scene.
    closure = man.get("closure") or {}
    if closure and not closure.get("portable", True):
        issues.append({
            "code": "PRESENTATION_UNRESOLVED_REF",
            "severity": "blocker", "category": "packaging",
            "message": (where + "composed scene has dangling/absolute resource refs: "
                        f"{(closure.get('dangling_refs') or [])[:5]}"),
            "blocking": True, "location": building, "raw_source_path": str(manifest)})

    # Ground-truth placement gate: themed visuals must sit on DC's collision.
    # A partial kit leaves slots greybox, and those are not counted -- the
    # gate checks only the modules the composer placed. This was advisory
    # from the day it was written, and every cold run from 9001 to 9012
    # carried it as a moderate finding nobody read (9005: 30 mismatched;
    # 9012's bank: 18) while the packages shipped wall remainders standing
    # across their walls. The walker found one beside a doorway. The
    # driver's exit is advisory by design (`exit_advisory`), so this
    # finding is where the red has to live: it blocks, and names the slots.
    pc = man.get("placement_check")
    if pc and pc.get("mismatched"):
        named = ", ".join(
            f"{m.get('slot')} ({m.get('stem')}: placed "
            f"{m.get('placed_extent')} on greybox {m.get('greybox_extent')})"
            for m in (pc.get("mismatches") or [])[:5] if isinstance(m, Mapping))
        issues.append({
            "code": "PRESENTATION_PLACEMENT_MISMATCH",
            "severity": "blocker", "category": "collision",
            "message": (where + f"{pc.get('mismatched')} themed module(s) do not "
                        f"match the greybox footprint (visual off the collision); "
                        f"{pc.get('matched')}/{pc.get('checked')} aligned. "
                        f"Worst: {named or 'not reported'}"),
            "blocking": True, "location": building, "raw_source_path": str(manifest)})

    # Z-FIGHTING: the composer computes it, prints "the package would
    # flicker", exits 3 -- and nothing read it. `presentation_compose`'s
    # exit code is advisory by design, so the job records SUCCEEDED, and
    # with no branch here the finding never reached a status line. Three
    # cold runs shipped a package the composer itself said would flicker
    # and each was recorded as clean (roadmap 133).
    #
    # Advisory, like the placement gate beside it: coplanar faces are an
    # art defect and refusing to build the level over one would stop it
    # existing long enough to be looked at. Loud, though -- the count and
    # the worst offenders by name, so it is actionable rather than a
    # number.
    #
    # `buried_pairs` and `greybox_internal_pairs` are broken out because
    # they are not the same defect: a pair where one face is buried inside
    # a solid cannot flicker, and a pair between two greybox faces is
    # under the art rather than in it. Reporting the total alone would
    # send somebody hunting for 30 visible seams when this scene has 8.
    zf = man.get("zfight_check")
    if isinstance(zf, Mapping) and zf.get("ok") is False:
        pairs = int(zf.get("pairs") or 0)
        buried = int(zf.get("buried_pairs") or 0)
        internal = int(zf.get("greybox_internal_pairs") or 0)
        visible = max(0, pairs - buried - internal)
        worst = ", ".join(
            f"{f.get('a')} / {f.get('b')}"
            for f in (zf.get("findings") or [])[:3] if isinstance(f, Mapping))
        issues.append({
            "code": "PRESENTATION_ZFIGHT",
            "severity": "moderate", "category": "presentation",
            "message": (
                where + f"{pairs} coplanar face pair(s) across "
                f"{zf.get('solids')} solids in {zf.get('scene')} — the "
                f"package would flicker where two surfaces share a plane. "
                f"{buried} buried, {internal} greybox-internal, so "
                f"{visible} can be seen. Worst: {worst or 'not reported'}"),
            "blocking": False, "location": building, "raw_source_path": str(manifest)})

    # CIRCULATION (0.149.0): props in a ladder's climb volume, a doorway or a
    # stair's column, by Deli Counter's gate. Nothing read it, and every cold
    # run from 9164 to 9187 failed it on every building -- on merged cover
    # boxes, which Deli Counter 0.191.0 reads as parts. Born moderate and
    # advisory, as a new gate is here; one finding an arm that failed.
    for arm, check in _circulation_arms(man.get("circulation_check")):
        if check.get("ok") is not False:
            continue
        conflicts = [c for c in (check.get("conflicts") or []) if isinstance(c, Mapping)]
        named = ", ".join(f"{c.get('prop')} {c.get('penetration')} m into "
                          f"{c.get('volume')}" for c in conflicts[:3])
        issues.append({
            "code": "PRESENTATION_CIRCULATION",
            "severity": "moderate", "category": "collision",
            "message": (where + f"{len(conflicts)} prop(s) stand in circulation "
                        f"({arm})" + (f": {named}" if named else "")
                        + (f" ({check.get('error')})" if check.get("error") else "")),
            "blocking": False, "location": building, "raw_source_path": str(manifest)})

    # No themed modules resolved at all = the kit didn't feed the compose.
    if not man.get("walkable", True):
        issues.append({
            "code": "PRESENTATION_NO_BASE",
            "severity": "moderate", "category": "packaging",
            "message": where + "no greybox base composed — level has no floors to stand on",
            "blocking": False, "location": building, "raw_source_path": str(manifest)})
    return issues
'''

DRIVER_FN_OLD = '''def placement_gate(pc: dict) -> tuple[str, str | None]:
'''
DRIVER_FN_NEW = '''def circulation_gate(circ: dict) -> tuple[str, list]:
    """The circulation gate's log line, and a line naming each conflict.

    Deli Counter writes two arms and a verdict when a package has a greybox
    and a dressing layer, ``{"ok", "shell", "dressing"}``, and one check
    carrying its ``source`` otherwise. This printed the counts from the top
    of either, so every cold run from 9164 to 9187 logged "[FAIL]: 0 prop
    conflict(s) across ? circulation volume(s)" on every building: a red
    with nothing in it (0.149.0). The adapter splits the arms the same way
    (`adapters.presentation._circulation_arms`).
    """
    arms = [(k, circ[k]) for k in ("shell", "dressing")
            if isinstance(circ.get(k), dict)]
    arms = arms or [(str(circ.get("source") or "shell"), circ)]
    tag = "OK" if circ.get("ok") else "FAIL"
    parts, details = [], []
    for arm, a in arms:
        conflicts = a.get("conflicts") or []
        excused = a.get("excused") or []
        parts.append(f"{arm} {len(conflicts)} conflict(s) across "
                     f"{a.get('volumes', '?')} volume(s)"
                     + (f", {len(excused)} excused" if excused else "")
                     + (f" ({a.get('error')})" if a.get("error") else ""))
        for c in conflicts[:10]:
            details.append(f"[compose]   {arm}: {c.get('prop')} intrudes "
                           f"{c.get('penetration')}m into {c.get('volume')}")
    return f"[compose] circulation gate [{tag}]: " + "; ".join(parts), details


def placement_gate(pc: dict) -> tuple[str, str | None]:
'''

DRIVER_MAIN_OLD = '''    circ = man.get("circulation_check")
    if circ is not None:
        ctag = "OK" if circ.get("ok") else "FAIL"
        print(f"[compose] circulation gate [{ctag}]: "
              f"{len(circ.get('conflicts') or [])} prop conflict(s) across "
              f"{circ.get('volumes', '?')} circulation volume(s)"
              + (f" ({circ.get('error')})" if circ.get("error") else ""))
        if not circ.get("ok"):
            for c in (circ.get("conflicts") or [])[:10]:
                print(f"[compose]   {c.get('prop')} intrudes "
                      f"{c.get('penetration')}m into {c.get('volume')}",
                      file=sys.stderr)
            print("[compose] ERROR: dressing blocks circulation -- see "
                  "circulation_check in the manifest.", file=sys.stderr)
            return 6
'''
DRIVER_MAIN_NEW = '''    circ = man.get("circulation_check")
    if circ is not None:
        line, details = circulation_gate(circ)
        print(line)
        if not circ.get("ok"):
            for d in details:
                print(d, file=sys.stderr)
            print("[compose] ERROR: a prop blocks circulation -- see "
                  "circulation_check in the manifest.", file=sys.stderr)
            return 6
'''


def _patch(path, edits):
    data = path.read_bytes()
    assert b"\r\n" not in data, f"{path.name} is LF"
    text = data.decode("utf-8")
    for old, new in edits:
        n = text.count(old)
        assert n == 1, (path.name, "anchor matched %d times" % n, old[:70])
        text = text.replace(old, new)
    return text


def main():
    adapter = _patch(ADAPTER, [(ADAPTER_OLD, ADAPTER_NEW)])
    assert adapter.endswith(ADAPTER_NEW), "the tail replaced is not the file's end"
    driver = _patch(DRIVER, [(DRIVER_FN_OLD, DRIVER_FN_NEW), (DRIVER_MAIN_OLD, DRIVER_MAIN_NEW)])
    ADAPTER.write_bytes(adapter.encode("utf-8"))
    DRIVER.write_bytes(driver.encode("utf-8"))
    print("adapters/presentation: every placed building, named, and circulation read")
    print("run_presentation_compose.py: the circulation gate printed from its arms")


if __name__ == "__main__":
    main()
