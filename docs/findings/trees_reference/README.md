# The walker's reference tree, read without running it (roadmap 216)

**Question.** What is the walker's CC0 reference tree, `one tree hill_gumroad.blend`
(2026-10-09), made of: objects, triangles, materials, alpha handling and
textures? It was asked before anything in Zoo is built toward it.

**How.** `inspect_blend.py`, run inside Blender 5.1.1, headless, with the
file on the command line and `--disable-autoexec`, so no script the file
carries could run. It lists, and runs nothing:
- objects, with their modifiers, particle systems, and triangles both raw
  and evaluated through the depsgraph;
- materials, their render method and alpha handling, and the images each
  reads;
- images and text blocks. Text blocks are counted, not printed; the file
  has none.

**Output.** `inspect_blend.json`, one row an object (828 rows).

**What it says** is written up in `docs/reference/TREE_REFERENCE.md`:
- **The trunk:** one sculpted mesh of 7,030 triangles, with its Multires
  source beside it.
- **The crown:** about 800 small and 12 large bent branch cards, about 28
  and 100 triangles each.
- **The materials:** three, each a 2048 colour map with alpha and a 2048
  normal map. The cards are alpha-tested and two-sided.
- **The game tree:** about 21,000 triangles in 3 materials.

**Where the binary is.** `_archive/reference/`, untracked: it is 75 MB.
`docs/FILING.md` has the row; the note above carries its sha256.
