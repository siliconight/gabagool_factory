"""gdcheck's traps, and the two ways it was blind until 2026-09-25.

WHY THIS FILE EXISTS. `check_all.py` reported `lux_validator.gd:373-374` and
`skymint_profile.gd:138` as load-time parse errors. Neither is: `m`, `s` and
`c` are not parameters of the functions they sit in. The disagreement settled
itself without argument -- Lux LOADS, since `lux_apply` and three
`lux_fixture_gate` jobs all succeeded on cold run 9078 -- so a file gdcheck
called unloadable had just been loaded by Godot.

Two defects behind it, one loud and one silent:

  * `static func` was invisible. The scanner tested `startswith("func ")`, so
    a static function never entered the table and every line inside one was
    attributed to the last NON-static function above it. That is where the
    false positives came from -- and, worse because nobody sees them, it meant
    a REAL shadow or a bad `:=` inside any static function was uncatchable.
  * the `:=` trap required the parameter to be followed by `.`, `(` or `[`, so
    a bare `var n := param` -- the same load error -- slipped through.

And a third, in the FIX rather than the code: the widened pattern was applied
through a bash heredoc, which wrote `\\b` as 0x08, an actual backspace. The
regex then matched nothing and the trap silently stopped firing. `grep` showed
the line as if it were fine; `inspect.getsource` showed `\\x08`. CLAUDE.md
already records this exact shape happening twice before.

    python -m pytest tools/test_gdcheck.py -q
"""

import inspect
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gdcheck  # noqa: E402


def _lint(tmp_path, body: str):
    p = tmp_path / "t.gd"
    p.write_text(body, encoding="utf-8")
    return gdcheck.lint(str(p))


def _msgs(findings):
    return " | ".join(m for _, m in findings)


# --------------------------------------------------------------------------- #
# The regression: a static function is a function
# --------------------------------------------------------------------------- #

def test_a_shadow_inside_a_static_func_is_caught(tmp_path):
    """The silent half. Before the fix this file reported CLEAN, and the
    shadow is a parse error -- the script would not have loaded at all."""
    f = _lint(tmp_path, "extends Node\n\n"
                        "static func helper(climb: float) -> float:\n"
                        "\tvar climb := climb * 2.0\n"
                        "\treturn climb\n")
    assert len(f) == 1, _msgs(f)
    assert f[0][0] == 4 and "shadows a parameter" in f[0][1]


def test_an_untyped_inference_inside_a_static_func_is_caught(tmp_path):
    f = _lint(tmp_path, "extends Node\n\n"
                        "static func infer(value) -> int:\n"
                        "\tvar n := value\n"
                        "\treturn n\n")
    assert len(f) == 1, _msgs(f)
    assert "infers from `value`" in f[0][1]


def test_a_local_in_a_static_func_is_not_blamed_on_the_function_above(tmp_path):
    """THE FALSE POSITIVE, reduced to its bones. `m` is a parameter of the
    FIRST function and a local of the second; before the fix the second
    function did not exist as far as the scanner was concerned, so the local
    was measured against the wrong signature. This is `lux_validator.gd`."""
    f = _lint(tmp_path, "extends Node\n\n"
                        "func first(m: int) -> int:\n"
                        "\treturn m\n\n\n"
                        "static func second(scene_root: Node) -> int:\n"
                        "\tvar m: int = 1\n"
                        "\treturn m\n")
    assert f == [], _msgs(f)


@pytest.mark.parametrize("decl", ["func plain(", "static func stat("])
def test_both_spellings_reach_the_table(tmp_path, decl):
    f = _lint(tmp_path, "extends Node\n\n"
                        f"{decl}climb: float) -> float:\n"
                        "\tvar climb := 1.0\n"
                        "\treturn climb\n")
    assert len(f) == 1 and "shadows a parameter" in f[0][1], _msgs(f)


def test_a_multi_line_signature_still_resolves(tmp_path):
    """`lux_validator.gd`'s real shape: a static signature wrapped over two
    lines. The continuation join has to happen before the parameters are read
    or the tail of the list is lost."""
    f = _lint(tmp_path, "extends Node\n\n"
                        "static func wide(a: int, b: int,\n"
                        "\t\tclimb: float) -> float:\n"
                        "\tvar climb := 1.0\n"
                        "\treturn climb\n")
    assert len(f) == 1 and "shadows a parameter" in f[0][1], _msgs(f)


# --------------------------------------------------------------------------- #
# The `:=` trap's width
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("rhs", ["value", "value.summary", "value[0]",
                                 "value + 1"])
def test_inference_from_an_untyped_parameter_is_caught_however_it_is_used(
        tmp_path, rhs):
    """A bare `var n := param` was missed until the pattern lost its required
    `.`/`(`/`[` suffix. All four spellings are the same load error."""
    f = _lint(tmp_path, "extends Node\n\n"
                        "func take(value) -> int:\n"
                        f"\tvar n := {rhs}\n"
                        "\treturn 0\n")
    assert any("infers from `value`" in m for _, m in f), _msgs(f)


def test_a_typed_parameter_is_never_flagged(tmp_path):
    """The gate that makes widening safe: the finding requires membership in
    the UNTYPED parameter set, so a typed one cannot reach it."""
    f = _lint(tmp_path, "extends Node\n\n"
                        "func take(value: Dictionary) -> int:\n"
                        "\tvar n := value.size()\n"
                        "\treturn n\n")
    assert f == [], _msgs(f)


def test_a_call_that_is_not_a_parameter_is_never_flagged(tmp_path):
    f = _lint(tmp_path, "extends Node\n\n"
                        "func take(value) -> int:\n"
                        "\tvar n := helper(value)\n"
                        "\treturn n\n")
    assert not any("infers from `helper`" in m for _, m in f), _msgs(f)


# --------------------------------------------------------------------------- #
# The pattern itself, because a regex that matches nothing looks identical to
# one that finds nothing
# --------------------------------------------------------------------------- #

def test_no_control_character_hides_in_the_source():
    """A bash heredoc once wrote `\\b` into this file as 0x08, a literal
    backspace, and the trap silently stopped matching. `grep` printed the line
    as though it were fine. Tabs and newlines are legal; nothing else is."""
    raw = (HERE / "gdcheck.py").read_bytes()
    bad = sorted({b for b in raw if b < 9 or 11 <= b < 32})
    assert not bad, f"control bytes in gdcheck.py: {bad}"


def test_the_inference_pattern_is_the_intended_one():
    line = [l for l in inspect.getsource(gdcheck.lint).splitlines()
            if "m = re.match" in l]
    assert len(line) == 1
    assert r"(\w+)\b" in line[0], line[0]


def test_the_func_pattern_accepts_static_and_rejects_a_lookalike():
    assert gdcheck._FUNC.match("func a(")
    assert gdcheck._FUNC.match("\tstatic func a(")
    assert gdcheck._FUNC.match("    static   func   a(")
    assert not gdcheck._FUNC.match('\tvar s = "func a("')
    assert not gdcheck._FUNC.match("\t# func a(")
    assert not gdcheck._FUNC.match("\tfuncy(")


# --------------------------------------------------------------------------- #
# The shipped library
# --------------------------------------------------------------------------- #

def test_the_two_files_that_were_wrongly_flagged_are_clean():
    """Both are Lux's, both are load-bearing, and both were reported as
    unloadable by a checker while Godot was loading them."""
    root = HERE.parent
    for rel in ("lux/addons/lux/runtime/lux_validator.gd",
                "lux/addons/skymint/skymint_profile.gd"):
        p = root / rel
        if not p.is_file():
            pytest.skip(f"{rel} not present")
        assert gdcheck.lint(str(p)) == [], rel
