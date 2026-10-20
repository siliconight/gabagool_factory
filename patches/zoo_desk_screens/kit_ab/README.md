# Zoo 1.115.0's kit A/B: one office desk and one cubicle bank, built by 1.114.1 and by the clone

`desk.slots.json` holds two slots from cold run 9349's office (`desk_rf992358c_1`, a 1.6 x 0.8 desk with office
stock, and `cubicles_w_0`, an 8 x 6 m cubicle bank whose work surfaces take office stock by default). `run_ab.sh`
builds both with Zoo 1.114.1 (arm a) and with the zoo_screens clone (arm b) through `zoo_cli.py --build-kit`, each in
a fresh Blender process, with cold run 9349's Pixelcoat skins. `glb_diff.py` reads each GLB's glTF JSON chunk and
lists every material, mesh (vertices, triangles, materials, a hash of its positions) and image that is in one arm only.

**REFUTED, KEPT: the first build moved the cubicle bank's stock.** Arm b's first diff, before the footprint fix, as
the console printed it:

    == prop_cubicle_bank_delco_02_w800_d600_h120_mdrywall.glb
      materials: 11 -> 12
        only in b: ('M_StockScreen_StockScreen_256x602_afa5671d_Face', (1, 1, 1), 'base_tex', 'emit_tex', (1.5,))
      meshes: 12 -> 13
        only in b: ('Stock_Screen', 1, 120, 60, ['M_Stock_screen_0_plastic'])
        only in b: ('Stock_Screen_led_0_Detail', 1, 120, 60, ['M_Stock_led_0_plastic'])
        only in b: ('Stock_Pencil', 1, 120, 60, ['M_Stock_pencil_0_wood'])
        only in b: ('StockScreen_Art', 1, 20, 10, ['M_StockScreen_StockScreen_256x602_afa5671d_Face'])
        only in b: ('Stock_beige_plastic_1_plastic', 1, 1128, 564, ['M_Stock_beige_plastic_1_plastic'])
        only in b: ('Stock_key_plastic_0_plastic', 1, 264, 132, ['M_Stock_key_plastic_0_plastic'])
        only in a: ('Stock_Screen', 1, 144, 72, ['M_Stock_screen_0_plastic'])
        only in a: ('Stock_Screen_led_0_Detail', 1, 144, 72, ['M_Stock_led_0_plastic'])
        only in a: ('Stock_Pencil', 1, 168, 84, ['M_Stock_pencil_0_wood'])
        only in a: ('Stock_beige_plastic_1_plastic', 1, 1272, 636, ['M_Stock_beige_plastic_1_plastic'])
        only in a: ('Stock_key_plastic_0_plastic', 1, 312, 156, ['M_Stock_key_plastic_0_plastic'])

Six screens (144 vertices, 24 a screen box) became five: the bank lost a workstation, and the stock after it drew
differently (pencils 168 -> 120). The art quad stands 2.5 mm in front of the glass and was counted in the monitor's
footprint (`_surface_stock._local_rect`), so the rect, the anchors drawn over it and the jitter all moved, and on a
tight work surface one workstation stopped fitting. The test
`test_the_screens_move_nothing_else_on_a_top` (60 cases) failed 45 on that clone; the footprint now ignores the art.

**After the fix** (`run_b.sh` rebuilt arm b alone; `glb_diff.out.txt`): every 1.114.1 mesh in both modules is in arm b
with the same vertex count, triangles, materials and position hash, and arm b adds exactly one material
(`M_StockScreen_..._Face`, emissive 1.5 over its own texture), one image (the 256 x 602 atlas, `screen_atlas_x2.png`
at twice its size) and one mesh, `StockScreen_Art`: 2 triangles on the desk, 12 on the bank's six screens.
