"""Level Factory 0.238.0 on a CLONE (<repo>): a junction's two directions take turns (the walker's walk of cold run
9386, finding 11: "traffic lights done change?"; and Lot 0.128.0, which faces every approach). Anchored; refuses on a
miss.

    python edit_lf_signal_opposition.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("assets/godot/zoo_worldskin.gd", [
    ('''## ONE CLOCK FOR EVERY SIGNAL: no instance term, where the shutters and the
## turning parts have one. Lot stands a signal only on a yielding leg's
## corner, its heads facing the through road -- both directions of it at a
## crossroads, measured on Lot's tee and cross junctions -- so every head at a
## junction serves the same traffic and must show the same lens. Two heads on
## one pole share one lens mesh a colour, and agree whatever the clock. Every
## junction in a level runs in step, as a coordinated arterial does.''',
     '''## ONE CLOCK FOR EVERY SIGNAL, AND TWO DIRECTIONS ON IT (0.238.0). Until
## Lot 0.128.0 a signal stood only on a yielding leg's corner with its heads
## facing the through road, so every head at a junction served the same
## traffic and showed the same lens. Lot now faces EVERY approach from its far
## right (the walker, walking cold run 9386: "where are the traffic lights for
## this side of the road?"), and on one clock the side street and the main
## road went green together. So a head's own FACING picks its half of the
## cycle: heads facing along world X run on the clock, heads facing along Z
## half a cycle later. The two directions of a junction face perpendicular
## axes and the two ways along one road face the same axis, so a junction
## takes turns with no table of junctions -- read off the node's own basis in
## the vertex stage (`MODEL_MATRIX[2]`, the axis both of Zoo's forms face
## along). Two heads on one pole share one lens mesh a colour and agree. Every
## junction in a level runs in step, as a coordinated arterial does.
##
## WHERE THE AXIS RULE FAILS, said rather than hidden: a junction whose roads
## both lie within a few degrees of the diagonal to the world's axes would put
## its two directions on one half. Level Factory's grammars lay roads on the
## axes; a diagonal junction is a gap to close in Lot (a junction phase on the
## slot), not here.'''),
    ('''const SIGNAL_CYCLE_S: float = 60.0
## Each colour's window, seconds into the cycle, tiling it: green 33 s, amber
## 4 s (MUTCD's yellow change interval is 3 to 6 s), red 23 s. Whole seconds,
## so the boundary two windows share is one float in both.
const SIGNAL_WINDOWS_S: Dictionary = {"Green": [0.0, 33.0], "Amber": [33.0, 37.0], "Red": [37.0, 60.0]}''',
     '''## The whole cycle, and each colour's window in it for a head on the X half,
## seconds, tiling it: green 18 s, amber 4 s (MUTCD's yellow change interval
## is 3 to 6 s), red 26 s -- of which the last 2 s are the ALL-RED clearance,
## while the other half's red has not yet ended. A Z head reads the same
## windows half a cycle on (`SIGNAL_HALF_CYCLE_S`), so its green begins as
## the X half's all-red ends. Whole seconds, so a boundary two windows share
## is one float in both.
##
## 0.165.0 ran 60 s (green 33). The walker, walking cold run 9386, of a
## junction they passed: "traffic lights done change?" -- measured, the
## package's lenses carried the 0.165.0 clock, so the lights DID change, once
## a minute, and a passer-by saw one state. 48 s keeps a real signal's order
## and amber and changes within 24 s of anyone arriving. The green is the
## taste knob: there is no physical number for how long a level's player
## watches a corner.
const SIGNAL_CYCLE_S: float = 48.0
const SIGNAL_HALF_CYCLE_S: float = SIGNAL_CYCLE_S / 2.0
const SIGNAL_WINDOWS_S: Dictionary = {"Green": [0.0, 18.0], "Amber": [18.0, 22.0], "Red": [22.0, 48.0]}'''),
    ('''uniform float cycle_s = 60.0;
uniform float lit_from_s = 0.0;
uniform float lit_to_s = 0.0;

void fragment() {
	// one clock for every signal: no instance term (the pass's notes)
	float t = mod(TIME, cycle_s);''',
     '''uniform float cycle_s = 48.0;
uniform float half_cycle_s = 24.0;
uniform float lit_from_s = 0.0;
uniform float lit_to_s = 0.0;

// which half of the cycle this head runs on: 0 facing along world X, 1 along Z
// -- the node's own basis, so a junction's two directions take turns
varying float half_;

void vertex() {
	vec3 face = MODEL_MATRIX[2].xyz;
	half_ = step(abs(face.x), abs(face.z));
}

void fragment() {
	// one clock for every signal, its two directions half a cycle apart
	float t = mod(TIME + half_ * half_cycle_s, cycle_s);'''),
    ('''	sm.set_shader_parameter("cycle_s", SIGNAL_CYCLE_S)
	var w: Array = SIGNAL_WINDOWS_S[colour]''',
     '''	sm.set_shader_parameter("cycle_s", SIGNAL_CYCLE_S)
	sm.set_shader_parameter("half_cycle_s", SIGNAL_HALF_CYCLE_S)
	var w: Array = SIGNAL_WINDOWS_S[colour]'''),
])

edit("tests/unit/test_worldskin_signal_lenses.py", [
    ('''def test_every_signal_keeps_one_clock():
    """No per-node term: every head at a junction faces the through road and
    must show the same lens; the shutters' and turning parts' hash is the
    opposite of what a signal needs."""
    sh = _shader(_src())
    assert "NODE_POSITION_WORLD" not in sh and "hash" not in sh
    assert "mod(TIME, cycle_s)" in sh''',
     '''def test_a_junction_s_two_directions_take_turns_on_one_clock():
    """0.238.0: Lot faces every approach (0.128.0), so a head's FACING picks its
    half of the cycle -- the node's own basis, never a hash or a position,
    which would split one junction's heads apart. FAILS ON 0.237.0: one clock
    and no half, so the side street and the main road went green together."""
    src = _src()
    sh = _shader(src)
    assert "NODE_POSITION_WORLD" not in sh and "hash" not in sh
    assert "MODEL_MATRIX[2]" in sh and "half_ = step(abs(face.x), abs(face.z));" in sh
    assert "mod(TIME + half_ * half_cycle_s, cycle_s)" in sh
    m = re.search(r"^const SIGNAL_HALF_CYCLE_S: float = SIGNAL_CYCLE_S / 2\\.0$", src, re.M)
    assert m, "the half cycle is not half the cycle"
    assert '"half_cycle_s", SIGNAL_HALF_CYCLE_S' in _func(src, "_signal_lens_material")


def test_the_two_halves_never_go_together_and_clear_on_all_red():
    """At every instant at most one half shows green or amber, and each change
    of right of way passes through a moment when both show red (the all-red
    clearance) -- read off the windows the shader is given."""
    src = _src()
    cycle, wins = _cycle(src), _windows(src)
    half = cycle / 2.0

    def lit(t):
        t %= cycle
        return next(c for c, (a, b) in wins.items() if a <= t < b)

    all_red = 0
    for k in range(int(cycle * 4)):
        t = k * 0.25
        x, z = lit(t), lit(t + half)
        assert not (x != "Red" and z != "Red"), (t, x, z)
        all_red += x == "Red" and z == "Red"
    assert all_red > 0, "no all-red clearance between the halves"


def test_a_passer_by_sees_a_change():
    """The walker, walking cold run 9386: "traffic lights done change?" -- the
    lights changed once a minute on 0.165.0's 60 s clock. Each half changes
    within half the cycle, and the cycle is under a minute."""
    cycle = _cycle(_src())
    assert cycle < 60.0, cycle
    assert _windows(_src())["Green"][1] <= cycle / 2.0'''),
])
print("zoo_worldskin: signal halves by facing, 48 s cycle; tests")
