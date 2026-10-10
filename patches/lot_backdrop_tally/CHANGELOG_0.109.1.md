## 0.109.1 - the backdrop's summary line counts pieces, not rowhomes

**Cold run 9226** (roadmap 228, the yards recipe) printed `LOT_BACKDROP_PLACED:
recipe yards, 0 rowhome(s) in 3 bands a side (N 41, S 37, E 21, W 21), 5
module(s), 1 water tower(s)`: the line read `summary["houses"]`, which counts
the borough's rowhomes, of a recipe that lays none, and said "3 bands a
side" of every recipe when only the borough has three. The by-side figures
were pieces all along.

**Now** the line says what was laid: `LOT_BACKDROP_PLACED: recipe yards, 120
piece(s) (backdrop_warehouse 23, cargo_container 97) by side (N 41, S 37,
E 21, W 21), 5 module(s), 1 water tower(s)`. `summary()` is unchanged.
