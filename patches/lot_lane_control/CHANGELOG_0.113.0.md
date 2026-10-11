## 0.113.0 - a lane stops at a street, and the audit counts it

**Roadmap 199 and 230 step 3, beside Level Factory 0.177.0's `block`
grammar**, whose service lane behind the row ends on two side streets.

- **`site_streets.approaches`:** a road without a sidewalk is a service
  lane or an alley, and its junction with a street is stop-controlled,
  never signalised -- a signal is for a street meeting an arterial. The
  rule as it stood would have hung a signal at an alley's mouth, because
  it signalised every yielding road meeting an arterial. A side street
  ending on an arterial keeps its signal.
- **`S_TARGETS`** (`site_targets`): the roads carrying `kind:
  service_lane` and the buildings they `serve`, said as the connector the
  guide asks for with an owner and users; a site with none is told that
  deliveries and refuse share the front street. The loop such a lane
  closes was already counted (0.112.0).

**Tests:** 2 in `tests/test_site_streets_lane.py`, 1 in
`tests/test_site_targets.py`. **Suite:** RESULT_SUITE.
