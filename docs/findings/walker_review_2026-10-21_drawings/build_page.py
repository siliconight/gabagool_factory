"""Build the walker's review page for roadmap 296: the drawings a level now carries (2026-10-21).

Reads a cold run's portable-godot package -- its `buildings.json` and each standing building's `lot/<id>/drawings/` --
copies every drawing it names into the page folder, draws one facade beside them (Deli Counter's `axonometric`, to show
what a facade's drawing would be), and writes index.html: a section a building with its exploded drawing and its plans,
then the facades and scoping a level out in the game, each with an answer that saves to the page's own store (the
published Artifact's `db`, collection `verdicts`, one document per question, `{choice, note, at}`), as the look-review
pages of 2026-10-19 and 2026-10-20 do. Its style is 2026-10-20's, read from that page's generator, so the series reads
as one.

    python build_page.py <package dir> <deli_counter checkout> <new page dir>
"""
import collections
import json
import re
import shutil
import sys
from pathlib import Path

pkg, dc, page = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
assert not page.exists(), "the page dir must be new"
HERE = Path(__file__).resolve().parent
CSS = re.search(r'CSS = r"""(.*?)"""', (HERE.parent / "walker_review_2026-10-20" / "build_page.py").read_text(
    encoding="utf-8"), re.S).group(1)
CSS += r"""
.gallery { display: grid; gap: 12px; }
.gallery figure img { background: #ffffff; }
.axo img { max-height: 78vh; width: auto; max-width: 100%; margin: 0 auto; }
.plansrow { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr)); gap: 12px; }
.facts { font-family: var(--mono); font-size: 12.5px; color: var(--muted); margin: 0; }
"""
sys.path.insert(0, str(dc))
import axonometric  # noqa: E402
import spec_loader  # noqa: E402

index = json.loads((pkg / "buildings.json").read_text(encoding="utf-8"))
RUN = sys.argv[1].split("cold-")[1].split("-ws")[0] if "cold-" in sys.argv[1] else "?"


def storey_name(s):
    return "Basement" if s < 0 else ("Ground floor" if s == 0 else "Floor %d" % s)


def rooms_by_storey(spec_id):
    d = json.loads((dc / "specs" / (spec_id + ".json")).read_text(encoding="utf-8"))
    by = collections.defaultdict(list)
    for r in d.get("rooms") or []:
        by[int(r.get("story", 0))].append(str(r["id"]).replace("_", " "))
    return by


SECTIONS = []
seen = set()
(page / "drawings").mkdir(parents=True)
for e in index["buildings"]:
    if e["kind"] != "building" or not e.get("axonometric") or e["id"] in seen:
        continue
    seen.add(e["id"])
    out = page / "drawings" / e["id"]
    out.mkdir()
    shots = []
    for rel, cap in [(e["axonometric"], "The whole building, each floor lifted apart")] + [
            (p["file"], storey_name(p["storey"]) + " plan") for p in e["plans"]]:
        src = pkg / rel[len("res://"):]
        shutil.copy2(src, out / src.name)
        shots.append({"src": "drawings/%s/%s" % (e["id"], src.name), "cap": cap})
    by = rooms_by_storey(e["id"])
    facts = "; ".join("%s: %s" % (storey_name(s).lower(), ", ".join(sorted(by[s]))) for s in sorted(by))
    SECTIONS.append({
        "id": "s_" + e["id"], "item": e["id"], "title": e["id"].replace("_", " "),
        "note": "Stands as %s in the level, at %s m. %d floor(s)." % (e["node"], ", ".join("%g" % v for v in e["at"]),
                                                                     len(e["plans"])),
        "facts": facts, "shots": shots,
        "qs": [{"id": "q_" + e["id"], "prompt": "Does this drawing read as the building?",
                "options": ["Looks right", "Needs work"]}]})

empties = [e for e in index["buildings"] if e["kind"] == "empty"]
fid = empties[0]["id"] if empties else "gs_empty_rowhome_a"
(page / "drawings" / "facade_example.svg").write_text(
    axonometric.render_axonometric(spec_loader.load_spec(str(dc / "specs" / (fid + ".json")))), encoding="utf-8")
SECTIONS.append({
    "id": "s_facades", "item": "facades", "title": "The rowhome facades",
    "note": ("The level also stands %d rowhome facades, %d different ones. A facade is a street wall with no inside, "
             "so its exploded drawing is an empty walled box, like this one (%s). Each facade's package says why it "
             "carries no drawing instead." % (len(empties), len({e["id"] for e in empties}), fid.replace("_", " "))),
    "facts": "", "shots": [{"src": "drawings/facade_example.svg", "cap": "What a facade's drawing would be"}],
    "qs": [{"id": "q_facades", "prompt": "Should a facade carry a drawing?",
            "options": ["No drawing, as now", "A front elevation", "Something else"],
            "default": "No drawing, as now"}]})
SECTIONS.append({
    "id": "s_scope", "item": "in game", "title": "Scoping out the level",
    "note": ("Your idea: players scope out the level before the job and see the buildings it is made of. Every level "
             "now ships these drawings with a list of its buildings and where each stands (buildings.json). They "
             "ship as plain files, so they cost a level nothing until a screen opens them. The game would draw "
             "that screen; the factory supplies the drawings."),
    "facts": "", "shots": [],
    "qs": [{"id": "q_scope", "prompt": "Is this the kind of drawing players should see?",
            "options": ["Yes, like this", "Simpler", "More detail"]},
           {"id": "q_scope_note", "prompt": "Anything a player should see that these leave out?", "options": []}]})

n_questions = sum(len(s["qs"]) for s in SECTIONS)
DATA = {"sections": SECTIONS, "total": n_questions}

JS = r"""
const DATA = __DATA__;
const state = {};
let db = null;
const $ = (s, el = document) => el.querySelector(s);

function el(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v; else if (k === "text") e.textContent = v; else e.setAttribute(k, v);
  }
  for (const k of kids) if (k) e.append(k);
  return e;
}

function shotEl(sh, cls) {
  const fig = el("figure", {class: cls || ""});
  const btn = el("button", {type: "button", "aria-label": "Enlarge: " + sh.cap});
  btn.append(el("img", {src: sh.src, alt: sh.cap, loading: "lazy"}));
  btn.addEventListener("click", () => openBig(sh.src, sh.cap));
  fig.append(btn, el("figcaption", {text: sh.cap}));
  return fig;
}

function questionEl(q) {
  const box = el("div", {class: "q", "data-q": q.id});
  box.append(el("p", {text: q.prompt}));
  if (q.options.length) {
    const opts = el("div", {class: "opts", role: "group", "aria-label": q.prompt});
    for (const o of q.options) {
      const b = el("button", {type: "button", class: "opt", "aria-pressed": "false", "data-v": o});
      b.textContent = o;
      if (q.default === o) b.append(el("span", {class: "def", text: "my default"}));
      b.addEventListener("click", () => choose(q.id, o));
      opts.append(b);
    }
    box.append(opts);
  }
  const ta = el("textarea", {id: "note-" + q.id, rows: "1", placeholder: q.options.length ? "Note (optional)" : "Your answer"});
  let t = null;
  ta.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => saveNote(q.id, ta.value), 900); });
  box.append(ta);
  return box;
}

function render() {
  const root = $("#sections"), jump = $("#jump");
  for (const s of DATA.sections) {
    const sec = el("section", {class: "card", id: s.id});
    sec.append(el("div", {class: "head"}, el("span", {class: "tag", text: s.item}), el("h2", {text: s.title})));
    if (s.note) sec.append(el("p", {class: "note", text: s.note}));
    if (s.facts) sec.append(el("p", {class: "facts", text: s.facts}));
    if (s.shots.length) {
      const g = el("div", {class: "gallery"});
      g.append(shotEl(s.shots[0], "axo"));
      if (s.shots.length > 1) {
        const row = el("div", {class: "plansrow"});
        for (const sh of s.shots.slice(1)) row.append(shotEl(sh));
        g.append(row);
      }
      sec.append(g);
    }
    const qs = el("div", {class: "qs"});
    for (const q of s.qs) qs.append(questionEl(q));
    sec.append(qs);
    root.append(sec);
    jump.append(el("a", {href: "#" + s.id, "data-sec": s.id, text: s.item}));
  }
}

function paint() {
  let done = 0;
  for (const node of document.querySelectorAll("[data-q]")) {
    const v = state[node.getAttribute("data-q")] || {};
    const hasOpts = !!node.querySelector(".opt[data-v]");
    if (v.choice || (!hasOpts && v.note)) done++;
    for (const b of node.querySelectorAll(".opt[data-v]")) b.setAttribute("aria-pressed", String(b.dataset.v === v.choice));
    const ta = node.querySelector("textarea");
    if (ta && document.activeElement !== ta && typeof v.note === "string") ta.value = v.note;
  }
  $("#count").innerHTML = "";
  $("#count").append(el("b", {text: String(done)}), document.createTextNode(" of " + DATA.total + " answered"));
  for (const a of document.querySelectorAll("nav.jump a")) {
    const sec = document.getElementById(a.dataset.sec);
    const qs = sec ? [...sec.querySelectorAll("[data-q]")] : [];
    a.classList.toggle("done", !!qs.length && qs.every(n => { const v = state[n.dataset.q]; return v && (v.choice || (v.note && !n.querySelector(".opt"))); }));
  }
}

const chains = {};
function write(qid) {
  const body = {choice: (state[qid] || {}).choice || "", note: (state[qid] || {}).note || "", at: new Date().toISOString()};
  paint();
  if (!db) return;
  chains[qid] = (chains[qid] || Promise.resolve()).then(() => db.doc("verdicts/" + qid).set(body)).then(
    () => { $("#save").textContent = "Saved. I read these answers back from the page."; },
    (e) => { $("#save").textContent = "Could not save that answer (" + (e && e.code || "error") + "). Reply in chat instead."; });
}
function choose(qid, v) { state[qid] = Object.assign({}, state[qid], {choice: (state[qid] || {}).choice === v ? "" : v}); write(qid); }
function saveNote(qid, text) { state[qid] = Object.assign({}, state[qid], {note: text}); write(qid); }

function openBig(src, cap) {
  const d = $("#big");
  $("#big img").src = src; $("#big img").alt = cap; $("#big p").textContent = cap;
  if (typeof d.showModal === "function") d.showModal();
}

render();
paint();
$("#big").addEventListener("click", () => $("#big").close());

(async () => {
  const c = window.claude;
  db = c && c.use ? await c.use("db") : null;
  if (!db) { $("#save").textContent = "Answers can't be saved in this view. Reply in chat, or open the page in Claude."; return; }
  $("#save").textContent = "Answers save to this page as you go.";
  db.collection("verdicts").onSnapshot((snap) => {
    for (const d of snap.docs) { const v = d.data(); if (v) state[d.id] = {choice: v.choice || "", note: v.note || ""}; }
    paint();
  }, (e) => { $("#save").textContent = "Saved answers could not be loaded (" + e.code + "). New answers may not save."; });
})();
"""

head = ('<title>October 21 Drawings Review</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&'
        'family=IBM+Plex+Mono&family=Public+Sans:wght@400;600&display=swap">\n<style>' + CSS + "</style>\n")
body = ('<div class="wrap">\n<header class="top">\n<h1>October 21 Drawings Review</h1>\n'
        '<p class="lede">Every building a level stands now carries its own drawings: the whole building with each floor '
        'lifted apart so you can see into it, and a plan of each floor. These are the three buildings in cold run '
        + RUN + "'s level, restaurant_row_001, taken from the package it shipped. Tap a drawing to see it larger, "
        'pick an answer, and add a note where you want one.</p>\n'
        '</header>\n<div class="bar"><span class="count" id="count"></span><span class="save" id="save">Loading saved '
        'answers.</span><nav class="jump" id="jump" aria-label="Jump to a section"></nav></div>\n'
        '<main id="sections"></main>\n</div>\n<dialog id="big" aria-label="Enlarged drawing"><img alt=""><p></p></dialog>\n'
        '<script>' + JS.replace("__DATA__", json.dumps(DATA)) + "</script>\n")
(page / "index.html").write_text(head + body, encoding="utf-8")
files = sorted(p.relative_to(page).as_posix() for p in (page / "drawings").rglob("*") if p.is_file())
missing = [sh["src"] for s in SECTIONS for sh in s["shots"] if not (page / sh["src"]).is_file()]
if missing:
    raise SystemExit("MISSING files: " + ", ".join(missing))
print("wrote index.html: %d sections, %d questions, %d drawings (%s)" % (len(SECTIONS), n_questions, len(files),
                                                                     ", ".join(files)))
