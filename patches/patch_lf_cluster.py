"""Level Factory 0.176.0: the buildings beside the objective drawn by a cluster template, when the brief asks.

Roadmap 230, the walker's adjacency and layout guide of 2026-10-10. Anchored edits, each file
pinned by hash and each anchor asserted once, nothing written on a miss; the file's own line
endings kept:
- `packages/core/models.py`: `MissionBrief.cluster` after `surroundings`; in the functional
  signature when set;
- `packages/pipeline/building_library.py`: `pick_lot(..., preferred=)` draws the template's
  families first; `lot_for` and `lot_for_brief` thread it from `cluster`;
- `packages/pipeline/site_variation.py`: `cluster_resolved`, the record the spec writer calls;
- `apps/cli/commands/__init__.py`: the site spec carries `cluster_resolved` beside
  `surroundings_resolved`.
New files, refused if they exist: `packages/pipeline/cluster.py`, `tests/unit/test_cluster.py`.
CHANGELOG and VERSION from `lf_cluster/CHANGELOG_0.176.0.md`; `--suite-pending` leaves
RESULT_SUITE to `--fill` from `result_suite.txt`.

    python patches/patch_lf_cluster.py --suite-pending && cd level_factory && python -m pytest -q > out.txt 2>&1; echo exit=$?
    python patches/patch_lf_cluster.py --fill
    LF_ROOT=<copy> python patches/patch_lf_cluster.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_cluster"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"0.175.1", b"0.176.0"
CHANGELOG_HEAD = "## [0.175.1] - The backdrop's by-side count counts every piece\n"
SHA = {"packages/core/models.py": "e53f5259d8c9183d",
       "packages/pipeline/building_library.py": "d130a21fba4fa0ca",
       "packages/pipeline/site_variation.py": "b2fe7fdaf2687cde",
       "apps/cli/commands/__init__.py": "21270d869dd5e299"}
NEW = {"packages/pipeline/cluster.py": "cluster.py", "tests/unit/test_cluster.py": "test_cluster.py"}

# --- models.py ---------------------------------------------------------
M_FIELD_OLD = "    surroundings: str = \"\"\n    seed_policy: str = \"derived\"\n"
M_FIELD_NEW = (
    "    surroundings: str = \"\"\n"
    "    #: WHICH BUILDINGS STAND BESIDE THE OBJECTIVE (0.176.0, roadmap 230): a cluster\n"
    "    #: template's id from the walker's adjacency guide (`cluster.TEMPLATES`), or\n"
    "    #: `auto` for the archetype's words to decide. Empty, the lot is drawn as it\n"
    "    #: always was. In the functional signature when set: it changes the lot.\n"
    "    cluster: str = \"\"\n"
    "    seed_policy: str = \"derived\"\n")
M_SIG_OLD = "        if self.lot_library:\n            sig[\"lot_library\"] = self.lot_library\n"
M_SIG_NEW = (M_SIG_OLD
             + "        # the same care for the cluster (0.176.0): named, it changes the lot\n"
             "        if self.cluster:\n"
             "            sig[\"cluster\"] = self.cluster\n")

# --- building_library.py ----------------------------------------------
B_SIG_OLD = ("def pick_lot(entries: list[dict], seed: int, count: int,\n"
             "             anchor: str = None) -> list[dict]:\n")
B_SIG_NEW = ("def pick_lot(entries: list[dict], seed: int, count: int,\n"
             "             anchor: str = None, preferred=None) -> list[dict]:\n")
B_LOOP_OLD = ("        out.append(variants[next(rng) % len(variants)])\n"
              "    while len(out) < count and pool:\n")
B_LOOP_NEW = (
    "        out.append(variants[next(rng) % len(variants)])\n"
    "    # THE TEMPLATE'S FAMILIES FIRST (0.176.0, roadmap 230): in the order the\n"
    "    # guide lists them, each drawn from the pool when the library has it, the\n"
    "    # stream spent on the variant alone -- so a brief with no template keeps\n"
    "    # 0.175.1's draw byte for byte, and a family the library lacks is skipped.\n"
    "    for fam in (preferred or ()):\n"
    "        if len(out) >= count:\n"
    "            break\n"
    "        if fam in pool:\n"
    "            pool.remove(fam)\n"
    "            variants = by_family[fam]\n"
    "            out.append(variants[next(rng) % len(variants)])\n"
    "    while len(out) < count and pool:\n")
B_LOT_SIG_OLD = ("def lot_for(library, building_count, candidate_id, *,\n"
                 "            themed: bool = False, anchor: str = None) -> tuple[list[dict], list[dict]]:\n")
B_LOT_SIG_NEW = ("def lot_for(library, building_count, candidate_id, *,\n"
                 "            themed: bool = False, anchor: str = None,\n"
                 "            preferred=None) -> tuple[list[dict], list[dict]]:\n")
B_LOT_RET_OLD = "    return pick_lot(complete, seed, count, anchor=anchor), incomplete\n"
B_LOT_RET_NEW = "    return pick_lot(complete, seed, count, anchor=anchor, preferred=preferred), incomplete\n"
B_BRIEF_OLD = (
    "    return lot_for(getattr(model, \"lot_library\", None),\n"
    "                   getattr(model, \"building_count\", 1),\n"
    "                   candidate_id, themed=themed,\n"
    "                   anchor=getattr(model, \"archetype\", \"\") or \"\")\n")
B_BRIEF_NEW = (
    "    # the cluster template's families, when the brief names one (0.176.0)\n"
    "    from packages.pipeline import cluster\n"
    "    template = cluster.template_for(getattr(model, \"cluster\", \"\"),\n"
    "                                    getattr(model, \"archetype\", \"\") or \"\")\n"
    "    return lot_for(getattr(model, \"lot_library\", None),\n"
    "                   getattr(model, \"building_count\", 1),\n"
    "                   candidate_id, themed=themed,\n"
    "                   anchor=getattr(model, \"archetype\", \"\") or \"\",\n"
    "                   preferred=cluster.preferred_families(template) if template else None)\n")

# --- site_variation.py --------------------------------------------------
V_OLD = ("    return _SURROUNDINGS_BY_SHAPE.get(shape, \"borough\")\n"
         "\n\n"
         "def _steps(shape: str, count: int) -> list:\n")
V_NEW = ("    return _SURROUNDINGS_BY_SHAPE.get(shape, \"borough\")\n"
         "\n\n"
         "def cluster_resolved(asked, archetype) -> dict:\n"
         "    \"\"\"The cluster template the lot was drawn by (0.176.0, roadmap 230), recorded\n"
         "    beside the surroundings: what was asked, what was got, whether the spelling\n"
         "    was known, and the families preferred in the guide's order.\"\"\"\n"
         "    from packages.pipeline import cluster\n"
         "    return cluster.resolved(asked, archetype)\n"
         "\n\n"
         "def _steps(shape: str, count: int) -> list:\n")

# --- commands/__init__.py -----------------------------------------------
C_OLD = ("            \"known\": site_variation.surroundings_known(model.surroundings),\n"
         "        },\n")
C_NEW = (C_OLD
         + "        # WHICH NEIGHBOURS THE BRIEF ASKED FOR (0.176.0, roadmap 230): the cluster\n"
         "        # template the lot was drawn by, or none, recorded as the surroundings are.\n"
         "        \"cluster_resolved\": site_variation.cluster_resolved(\n"
         "            getattr(model, \"cluster\", \"\"), model.archetype),\n")

EDITS = {
    "packages/core/models.py": [(M_FIELD_OLD, M_FIELD_NEW), (M_SIG_OLD, M_SIG_NEW)],
    "packages/pipeline/building_library.py": [(B_SIG_OLD, B_SIG_NEW), (B_LOOP_OLD, B_LOOP_NEW),
                                              (B_LOT_SIG_OLD, B_LOT_SIG_NEW), (B_LOT_RET_OLD, B_LOT_RET_NEW),
                                              (B_BRIEF_OLD, B_BRIEF_NEW)],
    "packages/pipeline/site_variation.py": [(V_OLD, V_NEW)],
    "apps/cli/commands/__init__.py": [(C_OLD, C_NEW)],
}


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old), old[:60])
    return text.replace(old, new)


def _fill():
    cl = LF / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Level Factory 0.176.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.176.0.md").decode("utf-8")
    assert entry.startswith("## [0.176.0] - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    writes = {}
    for rel, pairs in EDITS.items():
        raw = (LF / rel).read_bytes()
        got = hashlib.sha256(raw).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        assert "cluster" not in text.split("def ")[0] or rel != "packages/pipeline/building_library.py", (rel, "already applied")
        for old, new in pairs:
            text = _once(text, old, new, rel)
        writes[LF / rel] = text.replace("\n", eol.decode()).encode("utf-8")
    for rel in NEW:
        assert not (LF / rel).exists(), (rel, "already exists")
    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # Every pin and anchor matched: now write.
    for rel, name in NEW.items():
        (LF / rel).write_bytes(_src(name))
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.175.1 -> 0.176.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
