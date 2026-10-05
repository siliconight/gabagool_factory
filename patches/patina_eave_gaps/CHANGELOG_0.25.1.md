## [0.25.1] - a gutter runs the whole eave

### Fixed
- **The gutter broke over every top-floor window.** Seen in cold run 9153's
  frames, close up: each rowhome's pale gutter stopped at every top-floor
  window bay and started again past it. `roofline_slots` returned the top
  storey's WALL slots, and a window is a slot of its own -- so the eave over
  it carried no gutter. This predates 0.25.0; it showed once the gutter was
  pale painted metal standing off the wall.

  The top storey's exterior windows, doors and breaches are now part of the
  roofline. Each opening's module is the storey's height -- Deli Counter
  0.176.0 names heights apart -- so its gutter hangs at the same line, above
  the opening's head and clear of the opening keep-out. Downspout run ends
  read the same roofline and are unchanged; a pipe that would pass an
  opening is still refused by the keep-out.

`tests/test_gutter_eave_gaps.py`:
- on Deli Counter's real `gs_empty_rowhome_f`, the front gutter runs the
  whole eave without a gap (fails on 0.25.0: a gap over each top-floor
  window);
- no gutter over a window touches its opening;
- a top-storey opening is part of the roofline and a lower one is not.
