"""Edit a Deli Counter clone's tests for 0.277.0 (after edit_dc_produce_section.py). Run from the clone's root.
Asserts every anchor once; refuses on a miss."""
from pathlib import Path

p = Path("tests/test_furnish.py")
raw = p.read_bytes()
crlf = b"\r\n" in raw
t = raw.decode("utf-8").replace("\r\n", "\n")


def sub(old, new):
    global t
    assert t.count(old) == 1, (old[:70], t.count(old))
    t = t.replace(old, new)


sub('''    "snack_gondola": ((1.2, 14.0), (0.6, 1.5), (1.2, 2.2)),''',
    '''    "snack_gondola": ((1.2, 14.0), (0.6, 1.5), (1.2, 2.2)),
    # Zoo 1.132.0, Deli Counter 0.277.0's produce section
    "produce_table": ((1.2, 4.8), (0.8, 1.6), (0.8, 1.1)),''')
sub('''    assert naming == {"card_shop"}, naming''',
    '''    # 0.277.0: the supermarket's produce tables, its anchors -- islands below
    # cover height, which a shopper walks round
    assert naming == {"card_shop", "supermarket"}, naming''')
if crlf:
    t = t.replace("\n", "\r\n")
p.write_bytes(t.encode("utf-8"))
print("tests/test_furnish.py edited", "CRLF" if crlf else "LF")
