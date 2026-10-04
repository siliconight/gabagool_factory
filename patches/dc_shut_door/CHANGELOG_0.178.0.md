## [0.178.0] - An Empty's doorway is tagged so Zoo shuts it

0.174.0 made an Empty's doors solid in collision -- there is nothing behind
them -- and left the visual a doorway frame with no leaf. Zoo's doorway is a
frame and its trim; a leaf exists only for storefront doors. So every Empty
showed a doorway into a dark box that a player walks into as an invisible
wall. Seen in cold runs 9146-9148's `empties_one_front_*` frames.

An Empty's windows have carried `glazing: "facade"` since 0.80.0, which Zoo
reads as "nothing behind this opening" and glazes opaque. Its doorways now
carry the same tag, and Zoo 1.61.0 fills a tagged doorway with a painted
panel door set back from the face.

`test_facade_glazing.py`'s "a facade door carries no glazing" is RETRACTED
in place, above its replacement: it was true while no facade had a door
anyone could see into.
