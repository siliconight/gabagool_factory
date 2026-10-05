## [0.29.1] - no gutter on an Empty's party wall

### Fixed
- **`framing.gutter_orders` skips an Empty's party walls.** On an Empty --
  a shell any of whose slots carries `glazing: "facade"` -- a top-storey
  face with no window, door or breach on any storey is a party wall. It
  gets no gutter.
  - A rowhouse roof drains front and back, and the downspouts already kept
    to faces with openings. The rule is now theirs too.
  - Between two houses of one height, the party-wall gutter was hidden.
    Beside a lower neighbour it stood exposed, lit against an unlit wall,
    and read as lines floating in the sky: roadmap 184, cold runs 9160 and
    9161.
  - A free-standing building keeps a gutter on every face, as before.
