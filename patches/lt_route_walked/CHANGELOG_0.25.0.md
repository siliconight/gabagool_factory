## [0.25.0] - a route that ended on a skip is not a route walked

### Why now

Lot 0.98.0 parks the crew's getaway van at its spawn (roadmap 206). The
walker: "you spawn, do the job, then return to the car". The route is now
spawn, objective, and back to the van, whose point is the spawn's.

`route_completion_rate` is the share of runs that recorded
`ObjectiveReached`, and that fired when `_route_index` ran off the end of the
route. The index is not progress. `_update_stuck` advances it past a point
the bot is jammed on, which roadmap 128 already said when it gave arrivals
their own counter, `_route_reached`.

On a route that ends where it starts, the result is a heist for free:
- a bot jammed in its first seconds is skipped past the objective to "back
  at the van";
- it arrives at once, because it is standing beside the van;
- the run records a finished heist for a crew that never left.

The candidate picker reads completion right after the majors.

### What changed

- **`LT_BotPlayerController.route_walked(reached, total)`** is true only
  when every point was reached. `_advance_route` asks it of the arrivals:
  `ObjectiveReached` only for a walked route, and `RouteEndedShort {reached,
  total}` for one that ended on a skip, so the run's log shows where it fell
  short. `walked_whole_route()` asks it for this bot.
- **The harness** gets each bot's route end with the bot
  (`route_completed.connect(_on_route_walked.bind(bot_controller))`). The
  walk is over either way, so nothing waits on it. With the guards down, the
  run ends as OBJECTIVE only for a bot that walked the route, and as
  ENEMIES_CLEARED otherwise -- what happened.

**This is stricter for every route, not only the van's.** A run that skipped
a point and reached the end used to count as completed and now does not.
Completion read before this release and after it are different numbers: a
skip-completion is what the old one counted and the new one refuses.

### Tests

**`runners/tests/test_a_skipped_route_is_not_walked.gd`**, 11 checks. They
cover:
- the rule itself, and the van's route jammed at the start;
- `ObjectiveReached` recorded only under `route_walked` in
  `_advance_route`, with `RouteEndedShort` said otherwise;
- the stuck skip still never touching the arrivals;
- the harness binding the bot, and OBJECTIVE only for a walked route.

On 0.24.0 the script fails before its first check: `route_walked` does not
exist. Every test in `runners/tests` exits 0 under Godot 4.7, headless.

