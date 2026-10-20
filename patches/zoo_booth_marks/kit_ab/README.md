# Kit A/B: Zoo 1.116.0 against 1.117.0's clone, four street payphones

**What it is.** The four payphone looks (`phones.slots.json`: the default 0.75 x 0.5 x 2.3 booth, variants 0 to 3,
copied from 1.116.0's `patches/zoo_payphone_marks/kit_ab/`) built by `zoo_cli.py --build-kit` in Blender, once with
the repo at 1.116.0 (arm `a`) and once with the `zoo_marks` clone (arm `b`), each arm in a fresh Blender process with
cold run 9351's skins (`run_ab.sh`). `read_ab.py` reads every module back out of its GLB: each mesh's triangles and a
hash of its positions, the materials, the images, and the paint atlases written beside them (`builds.out.txt`).

**What it found.**

- Every module's meshes are 1.116.0's: `Payphone_Art` 1,052 triangles, `PayphoneGlow_Art` 4, the collision mesh 48,
  each with the same positions to a hash in both arms. Still two materials a module.
- The lit atlas (`PayphoneGlow_289x121_a89585e5`, the header and the diffuser) is the same image in both arms, and
  shared by all four looks.
- The paint atlas is repainted in every look -- variant 0 too, which 1.116.0 kept byte for byte -- and grows from
  256 x 1182 to 256 x 1360 (the second side panel's tile starts a new shelf of the atlas). The PNGs: 126-127 KB in
  1.116.0, 145-146 KB in 1.117.0.
- The GLBs are 79,620 bytes in both arms: the images are written beside them, not inside.

The contact sheet of the panels themselves, every look painted by 1.116.0 and by 1.117.0 (each at twice its
size, as its texels are and as a camera samples them), is `../marks_1160_vs_1170.jpg`.

    sh run_ab.sh
    python read_ab.py > builds.out.txt
