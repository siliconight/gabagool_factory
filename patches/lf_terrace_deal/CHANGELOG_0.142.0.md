## [0.142.0] - The terrace deals its houses rather than drawing them

Cold run 9160 doubled the rowhome Empties to twelve (Deli Counter 0.184.0),
expecting a row of about 26 houses to show each design about twice. Its
three candidates measured otherwise:

| seed | houses | designs used | most of one design |
|---|---|---|---|
| 9080 | 25 | 10 of 12 | 5 |
| 9181 | 31 | 12 of 12 | 6 |
| 9282 | 29 | 10 of 12 | 5 |

The terrace drew each house uniformly from the library and turned away only
an immediate repeat (`empties.terrace`). A bigger library moves the mean; the
spread is the draw's own.

- **`empties._deal`**: every design once, in an order shuffled off the
  terrace's own stream (Fisher-Yates), dealt from the end of the list and
  refilled when empty. A row of n houses from k designs now shows each
  floor(n/k) or one more times, and every design by the k-th house.
- **A deal does not repeat across its boundary.** If the first house of a
  new deal would be the one just placed, it trades places with the next.
- **A pick that a southward road turns away stays on the bag** and is
  placed past the road. Only a house that is placed is dealt.
- The terrace has its own stream (`seed ^ 0x5E3A11` in the site command), so
  the deal's extra draws move nothing else on the site. Every seed's row
  changes.
