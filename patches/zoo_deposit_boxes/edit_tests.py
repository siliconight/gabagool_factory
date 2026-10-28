"""Edit a Zoo clone's coplanar residue for 1.140.0: the deposit boxes' frame keeps the rule, and its 884 pairs leave
the table. Run from the clone's root. Asserts every anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("tests/test_coincident_faces.py", [
('''RESIDUE = {
    "safe_deposit_boxes": (884, 822, 62, 411, 2.08, 1169.8),
''', '''RESIDUE = {
'''),
('''    inside one fracture fragment as `rubble_frag`'s are: 2999."""
    total = sum(v[0] for v in RESIDUE.values()) + sum(GATED.values())
    assert total == 2999, total
    exposed = sum(v[3] for v in RESIDUE.values())
    assert exposed == 974, exposed
    # 0.96.0's, the ATM's, sign_box's and the payphone's went; the fan's split; hole_spoil's came
    assert total + 18 + 6 + 6 + 2 - 1 - 3 == 3027''',
'''    inside one fracture fragment as `rubble_frag`'s are: 2999. 1.140.0 drew
    the deposit boxes' doors and stood their frame's rails off its stiles,
    and the species' 884 (411 exposed), every one the frame's crossings,
    went: 2115."""
    total = sum(v[0] for v in RESIDUE.values()) + sum(GATED.values())
    assert total == 2115, total
    exposed = sum(v[3] for v in RESIDUE.values())
    assert exposed == 563, exposed
    # 0.96.0's, the ATM's, sign_box's, the payphone's and the deposit boxes' went; the fan's split; hole_spoil's came
    assert total + 18 + 6 + 6 + 2 + 884 - 1 - 3 == 3027'''),
('''                          "flat_top_grill", "red_maple", "callery_pear",
                          "safe_deposit_boxes", "street_tree"}, sorted(worse)''',
'''                          "flat_top_grill", "red_maple", "callery_pear",
                          "street_tree"}, sorted(worse)'''),
])


edit("tests/test_material_options_closed.py", [
('''        # a night depository is polished stainless (UL 771), a cash cart a
        # steel cage (1.139.0)
        "night_drop", "cash_cart")''',
'''        # a night depository is polished stainless (UL 771), a cash cart a
        # steel cage (1.139.0)
        "night_drop", "cash_cart",
        # a vault's deposit boxes are steel doors in a steel frame (1.140.0, the
        # walker's bank comp 12); `metal` stood them in street rust
        "safe_deposit_boxes")'''),
])
