## [0.56.0] - chain link

The walker, 2026-10-04, choosing what stands across the through road:
"empty lot is a good start" -- a fenced vacant lot (the mockup is
`docs/findings/backdrop_mock/` at the factory root). A fence needs a
see-through wire fabric. Zoo's painted atlas is RGB with no alpha, and
Pixelcoat already writes cutout packs (road paint, foliage) that Zoo's
textured path exports as alphaMode MASK -- so per the gap protocol the
surface is Pixelcoat's to grow.

`procedural_surface.diamond_mesh(size, count, seed, wire=)`: two crossed
families of diagonal wires, `count` diamonds across the tile on each axis
(tileable for an integer count), 1 on a wire and 0.5 exactly at its edge,
so a cutout at threshold 0.5 keeps the wires and nothing else. Dispatched
as the `diamond_mesh` generator.

`profiles/materials/chain_link_galvanized.json`, kind `chain_link`: a 1 m
tile of 16 diamonds (62.5 mm, the common 2 to 2.5 inch mesh), galvanised
greys, rust at the knuckles as wear, `wire` 0.14 so about a quarter of the
tile is wire, alpha-cut, `alpha_mode: scissor`. One theme-neutral profile,
mapped by both level themes (`delco`, `delco_1997`): chain link is a
commodity.

THE WEAVE, from the walker's references (2026-10-04; four Blender pages,
three of them a video or a product page with no written method): chain link
is zig-zag strands hooked over and under each other, not two families of
straight wire. `diamond_mesh(..., weave=True)` gives that SHADING -- a round
highlight along each wire, darkened where it passes under its neighbour,
alternating along each strand -- and the profile uses it as its meso
albedo band at the cutout's own count, so it lands on the wires the cutout
keeps. The references build the wire as geometry; that is out on cost, a
180 m street of it being hundreds of thousands of triangles. At 512 px a
metre the over/under reads as a slight darkening at the crossings, no more.

`tests/test_chain_link.py`: the mesh's diamonds land on the diagonals 16 px
apart at 8 across 128 px, open in the middle, a quarter covered; the profile
synthesises an RGBA albedo with a hard alpha, 15-35 % kept and galvanised
rather than black; both level themes map the kind to it.
