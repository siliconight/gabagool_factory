"""Pixelcoat 0.61.0: the shop signs a band can be dealt are the names Zoo
paints over the door -- one name list, the walker's option A.

The walker, 2026-10-06, on `docs/findings/two_names_one_building/`: option A
("Agreed"). One list names a building on both its signs, and the list is the
door box's -- Zoo's `storefront_names.KINDS`, written to the Delco-slang brand
rule. Level Factory 0.148.0 deals each shell one business and hands the same
pack to its door box (Zoo 1.79.0), so the band and the door cannot disagree.

For each kind Zoo names, the family Level Factory deals for it now holds
exactly Zoo's names:

    Zoo kind   Level Factory family   names
    deli       deli                   JAWN'S HOAGIES ... YO! DELI
    pizza      pizza (new)            PIE HOLE PIZZA ... SAUCE BOSS PIZZA
    bank       bank                   FIRST DELCO SAVINGS ... YOUSE CREDIT CO-OP
    pawn       pawn                   HOCK IT HERE ... GOLD N STUFF PAWN
    market     supermarket            PIKE FOOD MARKET ... SCRAPPLE SUPERMARKET
    pharmacy   pharmacy (new)         PILLS N THRILLS, DOC'S DISCOUNT DRUGS
    card       card (new)             TOPDECK TONY'S, MINT-ISH CARDS
    video      video (new)            MACDADE MOVIES
    brewery    brewery (new)          DOWN THE SHORE BREWING, HONEST HON BREW CO

The names that held those families before keep every other family they had
(CHECK CASH NOW stays `retail`, HOAGIE HUT `restaurant`/`default` ...) and
lose only these. The families Zoo has no names for -- auto, warehouse,
industrial, retail, bar, diner, restaurant, liquor -- are unchanged: their
doors wear the band's pack too, so they agree by construction.

The colours are a palette of five, given in order, the brand's green kept
for FLAPPAHS alone. `tests/test_one_name_list.py` reads Zoo's `KINDS` as
source and holds every family above to it.

    python patch_pixelcoat_one_name_list.py
"""
import ast
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIGNS = ROOT / "pixelcoat" / "profiles" / "signs"
ZOO_SN = ROOT / "zoo" / "zoo_keeper" / "core" / "storefront_names.py"

#: Zoo kind -> Level Factory family (Level Factory 0.148.0's SIGN_FAMILIES)
FAMILY_OF = {"deli": "deli", "pizza": "pizza", "bank": "bank", "pawn": "pawn",
             "market": "supermarket", "pharmacy": "pharmacy", "card": "card",
             "video": "video", "brewery": "brewery"}
#: (panel, border, text) -- never FLAPPAHS's green
PALETTE = (("#462414", "#e2b05c", "#faecce"),     # brown
           ("#162c52", "#d6c496", "#f0ecde"),     # navy
           ("#60161a", "#e8d4aa", "#f8f0de"),     # maroon
           ("#1e1e20", "#f0c850", "#f0c850"),     # charcoal, yellow
           ("#e6dcc8", "#3c2a1e", "#2a1e16"))     # cream, dark


def _zoo_names():
    tree = ast.parse(ZOO_SN.read_text(encoding="utf-8"))
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "KINDS" for t in n.targets):
            out = {}
            for el in n.value.elts:
                kind = ast.literal_eval(el.elts[0])
                try:
                    names = ast.literal_eval(el.elts[2])
                except ValueError:
                    continue                      # `(PY.STORE,)` and the club's None
                if kind in FAMILY_OF and names:
                    out[kind] = list(names)
            return out
    raise SystemExit("no KINDS in " + str(ZOO_SN))


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower().replace("'", "")).strip("_")


def _rt(path):
    raw = path.read_bytes()
    assert b"\r\n" not in raw, path
    text = raw.decode("utf-8")
    data = json.loads(text)
    for indent in (1, 2):
        if json.dumps(data, indent=indent, ensure_ascii=False) + "\n" == text:
            return data, indent
    raise SystemExit(f"{path}: does not round-trip; edit by hand")


def main():
    zoo = _zoo_names()
    assert set(zoo) == set(FAMILY_OF), sorted(set(FAMILY_OF) - set(zoo))
    staged = []
    for name in ("delco.json", "delco_1997.json"):
        data, indent = _rt(SIGNS / name)
        signs = data["signs"]
        families = set(FAMILY_OF.values())
        for s in signs:                           # the old names leave these families
            fams = s.get("families") or []
            if set(fams) & families:
                s["families"] = [f for f in fams if f not in families]
        slugs = {s["slug"] for s in signs}
        k = 0
        for kind, family in FAMILY_OF.items():
            for text in zoo[kind]:
                slug = _slug(text)
                assert slug not in slugs, (name, slug)
                panel, border, ink = PALETTE[k % len(PALETTE)]
                k += 1
                signs.append({"slug": slug, "text": text, "style": "panel",
                              "panel": panel, "text_color": ink, "border": border,
                              "families": [family]})
                slugs.add(slug)
        for family in families:
            got = [s["text"] for s in signs if family in (s.get("families") or [])]
            kind = next(k_ for k_, f in FAMILY_OF.items() if f == family)
            assert got == zoo[kind], (name, family, got)
        staged.append((SIGNS / name, data, indent))
    for path, data, indent in staged:
        path.write_bytes((json.dumps(data, indent=indent, ensure_ascii=False) + "\n").encode("utf-8"))
        print("patched", path.relative_to(ROOT))
    test = ROOT / "pixelcoat" / "tests" / "test_one_name_list.py"
    assert not test.exists()
    test.write_bytes(TEST.encode("utf-8"))
    print("wrote", test.relative_to(ROOT))


TEST = '''"""One name list (0.61.0): a band is dealt from the names Zoo paints over the
door, for every kind Zoo names.

The walker, 2026-10-06, option A: one list names a building on both its
signs, and it is the door box's -- Zoo's `storefront_names.KINDS`, read here
as source so the two cannot drift. Level Factory 0.148.0 deals each shell one
business and hands the same pack to its door box (Zoo 1.79.0).
"""
import ast
import json
from pathlib import Path

import pytest

SIGNS = Path(__file__).resolve().parents[1] / "profiles" / "signs"
PROFILES = [SIGNS / "delco.json", SIGNS / "delco_1997.json"]
FAMILY_OF = {"deli": "deli", "pizza": "pizza", "bank": "bank", "pawn": "pawn",
             "market": "supermarket", "pharmacy": "pharmacy", "card": "card",
             "video": "video", "brewery": "brewery"}


def _zoo_kinds():
    for parent in Path(__file__).resolve().parents:
        src = parent / "zoo" / "zoo_keeper" / "core" / "storefront_names.py"
        if src.is_file():
            tree = ast.parse(src.read_text(encoding="utf-8"))
            for n in tree.body:
                if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "KINDS"
                                                     for t in n.targets):
                    out = {}
                    for el in n.value.elts:
                        try:
                            out[ast.literal_eval(el.elts[0])] = list(ast.literal_eval(el.elts[2]))
                        except (ValueError, TypeError):
                            continue
                    return out
    return None


@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p.stem)
@pytest.mark.parametrize("kind", sorted(FAMILY_OF))
def test_a_family_zoo_names_holds_exactly_zoos_names(profile, kind):
    kinds = _zoo_kinds()
    if kinds is None:
        pytest.skip("no Zoo checkout above this repo")
    assert kind in kinds, f"Zoo no longer names {kind!r}; this map is stale"
    data = json.loads(profile.read_text(encoding="utf-8"))
    family = FAMILY_OF[kind]
    got = [s["text"] for s in data["signs"] if family in (s.get("families") or [])]
    assert got == kinds[kind], (profile.stem, family, got)


@pytest.mark.parametrize("profile", PROFILES, ids=lambda p: p.stem)
def test_the_brand_green_is_flappahs_alone(profile):
    data = json.loads(profile.read_text(encoding="utf-8"))
    green = [s["slug"] for s in data["signs"] if str(s.get("panel", "")).lower() == "#184e34"]
    assert green == ["flappahs"], green
'''


if __name__ == "__main__":
    main()
