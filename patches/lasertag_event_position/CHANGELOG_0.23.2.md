## [0.23.2] - a named event is logged at the position it carries

`LT_MetricsCollector.record_event` logged every named event -- PlayerStuck,
EnemyStuck, RouteProgress, ObjectiveReached -- with a top-level `position`
of (0, 0, 0), while both stuck emitters (`LT_BotPlayerController.
_update_stuck`, `LT_EnemyBrain._on_stuck`) put the real one in
`metadata.position`. Every reader took the top-level field: Level Factory's
notes for cold runs 9140 and 9141 recorded seed 9181's stuck events as
carrying "no position" and left two attributions open on it. Read from the
metadata, 1,354 of that candidate's 1,378 stuck events are the crew at one
spot, Godot (55.3, 6.0, 13.1), six metres up.

The event is now logged at `metadata.position` when it carries one, and at
the origin, as before, when it does not.

`runners/tests/test_event_carries_its_position.gd`: a stuck event's
top-level position is its metadata's; an event with none still logs the
origin; the counters still count.
