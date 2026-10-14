## [0.205.0] - The site says what its street is: an urban brief's spec carries `streetscape: "urban"`

**Factory roadmap 241.** Lot 0.123.0 plants a city block's trees on an urban street: one every 30 ft, 30 ft clear
of a corner, read at source from Philadelphia's own siting guidelines (the factory root's
`docs/reference/STREET_TREES.md`). It asks the site spec, and the spec did not say. The compose stage decides
urban (`_urban`: a library, and `models.streetscape_effective` of the brief's field and its Empties) and kept the
answer to itself.

- **`_write_site_spec` writes `spec["streetscape"] = "urban"`** where it decides urban, and nothing for a strip,
  whose spec is byte for byte what it was.
- **`tests/unit/test_streetscape_in_site_spec.py`** has 1 check, read as source. It fails on 0.204.0, which writes no `spec["streetscape"]`. The suite:
  `python -m pytest -q`: exit 0, 2,389 passed (0.204.0's 2,387, `test_streetscape_in_site_spec.py`'s 1, and the sibling-locator guard's case over the new file), 14 skipped (the real-tool smoke), 1 xfail, counted off the progress marks.
