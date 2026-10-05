## [1.65.0] - colour variation in the painted windows

The walker sent window photographs (a night facade of lit rowhouse and
tenement windows, three street rows by day) and said "color variation is
key". 1.64.0 painted every lit window one warm tungsten. The night
photographs show at least four room lights -- tungsten yellow, the deep
orange of a curtained room, a pale cool fluorescent, a pink lampshade -- and
as many coverings: blinds, a roller shade pulled past half with the light
below it, curtains. The day rows add the green roller shade, closed blinds
and a box fan in the lower sash.

`core/window_panes.py` now paints sixteen states on a 4x4 atlas, 192x320:

| | states |
|---|---|
| lit | `lit`, `lit_amber`, `lit_cool`, `lit_pink` |
| lit, covered | `lit_blind`, `lit_blind_cool`, `lit_curtain`, `lit_shade`, `lit_bars` |
| dark | `dark`, `dark_blind`, `dark_shade`, `dark_curtain`, `dark_bars`, `dark_fan` |
| vacant | `boarded` |

Still one image pair, one `M_Window_pane_Face` material, glow only where room
light shows: the variety is UVs and costs no submission.

The window air conditioner every photograph shows stands out of the window,
so it is geometry, and it is not painted here.

`tests/test_window_panes.py`: the atlas has sixteen states and at least four
room lights. The earlier tests hold unchanged.
