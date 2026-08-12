# RETRACTED — Laser Tag does not grade stale scenes

**The claim this file originally made is false.** It asserted that
`laser_tag_evaluate` stages a scene without its closure and grades whatever is
left in the staging directory, and that every grade in the project's history is
therefore suspect. None of that is true. The document is kept rather than
deleted because the way it went wrong is worth more than the way it went right.

Refuted 2026-08-09, same session, by `lf diagnostics`.

---

## What was actually happening

`laser_tag_evaluate.candidate.seed_5017` **never ran.**

```json
"status": "FAILED",  "started_at": null,  "exit_code": null,
"command": [],       "build_fingerprint": "",
"failure": { "failure_class": "input_validation_error", "transient": false }
```

No command, no start time, no fingerprint, no log. The job was **refused at
pre-flight** by `LaserTagAdapter.validate_configuration`, before Godot was
invoked — which is precisely what that code exists to do, and says so:

> *"Pre-flight the map contract (TDD 8). Without the LT_* hooks — or the root
> positions staging derives them from — the run completes zero firefights and
> reports a grade for a match it never played. Better to say so before spending
> 900 seconds."*

The blocker is real, current, and carries its own fix:

```
[BLOCKER] JOB_PREFLIGHT_REFUSED (configuration)
  1 of 3 mission destination(s) cannot be walked to from the player spawn:
  Route_2 is sealed off from the crew spawn (4 collider(s) could not be reduced
  to a box, so the walkable area may be larger than this: Player/col
  (CapsuleShape3D), site.tscn:path_1/col, site.tscn:path_2/col, and 1 more);
  the bot cannot finish the route, which Laser Tag reports as TRAVERSAL with
  0% completion
  fix: Fix the input the pre-flight named, then re-run the stage.
```

Item 7 changed the lot; the new lot for 5017 has a sealed route; the pre-flight
caught it. The system worked.

## Why the staging directory looked stale

Because it was — **and correctly so.** It held the output of the last execution
that actually happened, before item 7 changed the lot. The job has not run
since, so nothing rewrote it. The fourteen accumulated buildings are ordinary
debris from a directory that is only written when a job runs, and the
160.85-second report I read was that same older execution's, which is why its
duration was byte-identical every time I looked.

`stage_godot_project` copies the scene's siblings with `rmtree`-and-replace,
and its comments describe this exact class of defect as already fixed. It was.

## Also retracted: "findings carry no code"

`code: None` appears in **Laser Tag's raw report**. LF's `_normalize` assigns
codes on the way into the shared model, and `lf validate` shows them:
`JOB_PREFLIGHT_REFUSED`, `LT_MAP_TRAVERSAL`, `LT_NO_SURVIVABLE_OPENING`,
`LT_ROUTE_NEVER_COMPLETED`, `LT_MAP_OVEREXPOSED_ZONE`, `LT_MAP_PLAYER_STUCK`,
`LOT_COVER_PLACED`, `LT_ENGAGEMENT_NOT_CONFIGURABLE`, and more — 37 findings,
1 blocker, 5 major, 10 moderate, 21 minor. The caveat was noted when the
raw report was first read and then written up as a defect anyway.

## Also retracted

* **"A failed job cannot be re-run."** It re-evaluates every time and is
  refused every time, because its *input* is bad. Deleting the job directory
  changed nothing because there was nothing to redo.
* **"The mission is wedged with no exit."** The fix is named in the finding.
* **"`b1`–`b5` ids prove an older convention."** The current, correct
  `site.tscn` uses the same ids. Scene `ext_resource` ids and spec building ids
  are different namespaces.
* **"The stuck point is on `construction_site_a02` / item 3."** Located against
  a level that predated the current lot. Item 3's status is unknown, not clear.

---

## The lesson, which is the reason to keep this file

**Six commands of directory archaeology, and the answer was one CLI verb.**
`lf diagnostics <job>` states in nine lines that the job never started. `lf
validate <mission>` prints every finding with its code, severity and suggested
fix. Neither was used until the very end, after an hour of inferring pipeline
behaviour from file listings.

The specific error: **a stale artefact was treated as evidence of a stale
process.** A directory that is only written when a job runs will look
arbitrarily old when the job stops running, and that is not a defect — it is
the absence of one. Every subsequent observation was then fitted to a
conclusion already reached.

The repo's own rule covers it: *a probe prints what it measured and stops.*
A directory listing measures what is on disk. It does not measure what a
program did.

**Ask the tool what happened before reconstructing it from its leavings.**
