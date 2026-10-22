# The walker's drawings review, 2026-10-21

**What it is.** One page with the drawings a level now carries (the factory's roadmap 296): each of the three
buildings cold run 9378's level stands -- deli_a03, pharmacy_a01, office -- as its exploded axonometric and its storey
plans, then the rowhome facades and scoping a level out in the game, with an answer to tap and a note for each:
https://claude.ai/artifact/BG8SRKn7xVCEz3L3JFyg3y (private to the walker). It holds six questions. Answers save to
the page's own store, collection `verdicts`, one document per question (`{choice, note, at}`), read back with the
ArtifactData tool, as 2026-10-19's and 2026-10-20's pages do (`docs/findings/walker_review_2026-10-19/`,
`docs/findings/walker_review_2026-10-20/`), whose style this one reads.

**Where the drawings came from.** Copied out of cold run 9378's package
(`workspaces/cold-9378-ws/.level_factory/exports/LF_restaurant_row_001.portable-godot/lot/<id>/drawings/`), the
files `buildings.json` names -- so the page shows what ships, not a drawing made for the page. The one exception is
the facade example, drawn for the page by Deli Counter 0.257.0's `axonometric` from the first Empty the index names,
because a facade's package carries no drawing by design.

**Checked before it was shown**: one headless screenshot at desktop width; after publishing, the store written once,
read back and the probe deleted. The page's own save, which runs in the walker's viewer, was not exercised here.

**How to rebuild the page:**

    python docs/findings/walker_review_2026-10-21_drawings/build_page.py <package dir> <deli_counter checkout> <new page dir>

then publish the page dir's `index.html` with its `drawings/` files and `capabilities: {db: {}}`.
