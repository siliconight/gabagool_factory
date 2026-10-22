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

## The walker's answers, 2026-10-22

Five of the six questions answered on the page between 12:11 and 12:15 UTC; `verdicts_2026-10-22/verdicts/` is the
page's store as read back that day, one document per question.

| question | answer | the walker's note |
|---|---|---|
| deli_a03's drawing | Needs work | "we need to find a way to be simple and not noisy visually. assume that in game, a player could rotate it as well to" |
| office's drawing | Needs work | |
| pharmacy_a01's drawing | Looks right | |
| a facade's drawing | No drawing, as now | |
| what players should see | Simpler | "simpler but carry all of the signals needed" |
| anything left out | (unanswered) | |

**Read**: the one-storey pharmacy reads; the two busy buildings do not -- their furniture, room labels and dashed
leaders crowd the structure. A view a player can rotate is a model, not one drawing: roadmap 295's map mesh, a floor
at a time with only what a body navigates by, is that shape. Both directions are filed under roadmap 296 and 295.

**How to rebuild the page:**

    python docs/findings/walker_review_2026-10-21_drawings/build_page.py <package dir> <deli_counter checkout> <new page dir>

then publish the page dir's `index.html` with its `drawings/` files and `capabilities: {db: {}}`.
