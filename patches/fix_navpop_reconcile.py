import os, sys
P = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "patch_navgate_population.py")
with open(P, "r", encoding="utf-8") as fh:
    src = fh.read()

SUBS = [
(
"unjudged, failures, navnull, disagree = [], [], 0, []",
"unjudged, failures, navnull, disagree, explained = [], [], 0, [], []"
),
(
'''    if checked == 0:
        unjudged.append({"shell": name, "checked": 0,
                         "navigable": nav if nav != "ABSENT" else None,
                         "reason": classify(name)})
        if nav is not None:
            disagree.append((name, nav))
''',
'''    st_ok = d.get("stairs_ok", d.get("ok"))
    if checked == 0:
        unjudged.append({"shell": name, "checked": 0,
                         "navigable": nav if nav != "ABSENT" else None,
                         "stairs_ok": st_ok,
                         "reason": classify(name)})
        # navigable is a conjunction: a stair failure forces False without the
        # marker state mattering. That is the gate short-circuiting correctly,
        # NOT an inconsistency. Only a shell that passes stairs, checks zero
        # markers and still reports a non-null navigable is unexplained.
        if nav is not None and st_ok is False:
            explained.append((name, nav))
        elif nav is not None:
            disagree.append((name, nav))
'''
),
(
'''if disagree:
    print("  DISAGREEMENT -- unjudged but navigable is not null:")
    for n, v in disagree:
        print("      %-40s navigable=%r" % (n, v))
    print("      (0 markers checked should imply navigable null; it does not here)")
''',
'''if explained:
    print("  unjudged with a non-null navigable, EXPLAINED by a stair failure:")
    for n, v in explained:
        print("      %-40s navigable=%r (stairs failed, so navigable is" % (n, v))
        print("      %-40s  False on the stair verdict alone)" % "")
if disagree:
    print("  UNEXPLAINED -- passes stairs, checked zero markers, navigable not null:")
    for n, v in disagree:
        print("      %-40s navigable=%r" % (n, v))
'''
),
(
'''    "known_inconsistency": (
        [{"shell": n, "navigable": v,
          "note": "0 markers checked should imply navigable null"}
         for n, v in disagree] or None),
''',
'''    "navigable_null_reconciliation": {
        "unjudged": len(unjudged),
        "navigable_null": navnull,
        "explained_by_stair_failure": [
            {"shell": n, "navigable": v,
             "note": "navigable is a conjunction; a stair failure forces False "
                     "without marker state mattering. Not an inconsistency."}
            for n, v in explained],
        "unexplained": [
            {"shell": n, "navigable": v,
             "note": "passes stairs, checked zero markers, yet navigable is not "
                     "null -- this one is not accounted for"}
            for n, v in disagree] or None,
    },
'''
),
]

for old, new in SUBS:
    n = src.count(old)
    if n != 1:
        print("REFUSING -- a block appears %d time(s), expected 1:" % n)
        print("    %s" % old.splitlines()[0][:90])
        sys.exit(1)
    src = src.replace(old, new)

with open(P + ".pre_fix3", "w", encoding="utf-8", newline="") as fh:
    pass
with open(P, "w", encoding="utf-8", newline="") as fh:
    fh.write(src)
print("patched %d block(s) in %s" % (len(SUBS), os.path.basename(P)))
