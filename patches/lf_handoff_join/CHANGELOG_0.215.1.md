## [0.215.1] - HANDOFF.md's layers paragraph stands on its own

**Found reading cold run 9314's package** (the factory's `docs/cold_runs/cold_9314/NOTES.md`), the first to carry
0.213.0's paragraph. `HANDOFF_LANGUAGE` ends with one newline, and 0.213.0 appended `handoff_layers_text` straight
after it, so the paragraph on the layers landed as the last line of the paragraph before it ("The production game
runtime remains authoritative ...") -- one paragraph to a Markdown reader, two sentences apart in the file.

- **`handoff_text(layers, mode)`:** HANDOFF.md whole -- `HANDOFF_LANGUAGE` with its trailing newlines taken, a
  blank line, the layers paragraph. The export writes it; nothing else moves.
- **`tests/unit/test_layers_shown.py`:** the composed text carries the blank line before "WHAT THIS PACKAGE IS
  MADE OF" and ends with one newline; the call site restated. The new test fails on 0.215.0 (no `handoff_text`).

**Suite:** exit 0, 2,451 by the progress tally (2,436 passed, 14 skipped, 1 xfail): 0.215.0's 2,435 passed and the new test; the 14 skipped are the real-tool smoke, as before
