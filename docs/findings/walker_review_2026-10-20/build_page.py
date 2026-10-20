"""Build the walker's review page for 2026-10-20 (from 2026-10-19's generator): each question with its frames, and a control for the answer that saves to the
page's own store (the published Artifact's `db`, collection `verdicts`, one document per question). A generator: it
writes index.html beside the img/ and plans/ folders `collect_frames.py` and `open_floor_plans.py` filled, and
prints what it wrote.

    python build_page.py <page dir>
"""
import html
import json
import sys
from pathlib import Path

page = Path(sys.argv[1]).resolve()

def f(key, what, inspect=False):
    return {"src": "img/%s.jpg" % key, "cap": what + (INSPECT if inspect else ""), "inspect": inspect}


INSPECT = " Inspection light: this shows form, not the level's lighting."
RR = "restaurant_row_001"

SECTIONS = [
    {"id": "s148", "item": "148", "title": "The office computers are on", "walk": "screens", "frames": [
        f("desk_before", "A desk on the top floor, before (cold run 9349, %s, evening)" % RR),
        f("desk_after", "The same desk now: the word processor (cold run 9350)"),
        f("cubicles_before", "A cubicle row, before (9349)"),
        f("cubicles_after", "The same row now (9350)"),
    ], "note": "Every desk and cubicle monitor shows one of six invented 1997 screens: a word processor (JAWN.DOC), a "
               "spreadsheet (WOODERCALC), a desktop (HOAGIE SHELL), a terminal, an amber bulletin board (SCRAPPLE BBS) "
               "and a starfield. They go dark with the lights in a power cut. Priced: no frame cost this machine can "
               "see; 18 small meshes and 0.2 MiB on this level.", "qs": [
        {"id": "q148_screens", "prompt": "Do the computer screens read as on, and as 1997?",
         "options": ["Looks right", "Needs work"]},
    ]},
    {"id": "s210", "item": "210", "title": "The street phones face the sidewalk", "walk": "phones", "frames": [
        f("phone0_before", "The phone on the main street, before: its back to the street (cold run 9350)"),
        f("phone0_after", "The same phone now, facing the street (cold run 9351)"),
        f("phone2_before", "The side street's phone, before: the same tags as every booth (9350)"),
        f("phone2_after", "The same phone now, wearing its own marks (9351)"),
    ], "note": "Every piece at a bus stop -- the mailbox, the news racks, the phone -- now faces the road from either "
               "side of it. Each booth wears one of four sets of tags and stickers, picked by where it stands.", "qs": [
        {"id": "q210_face", "prompt": "Do the phones face the right way now?", "options": ["Looks right", "Needs work"]},
        {"id": "q210_marks", "prompt": "Do the booths' tags and stickers differ enough?",
         "options": ["Looks right", "Needs work"]},
    ]},
    {"id": "s170", "item": "170", "title": "The roof hatch's hole matches its lid", "walk": "hatch", "frames": [
        f("hatch_before", "bank_branch_a04's roof hatch from above, before (cold run 9348)", inspect=True),
        f("hatch_after", "The same hatch now (cold run 9352)", inspect=True),
        f("hatch_side_before", "From the hinge side, before (9348)", inspect=True),
        f("hatch_side_after", "From the hinge side, now (9352)", inspect=True),
    ], "note": "Your note: \"the hole of the ladder opening doesn't match the lid\". The ladder cut its own hole that "
               "ran 0.35 m past the hatch, at every roof hatch in the library. The hatch now stands over the ladder's "
               "hole, so the hole, the frame and the lid are one rectangle.", "qs": [
        {"id": "q170_match", "prompt": "Does the hole match the lid now?", "options": ["Looks right", "Needs work"]},
    ]},
    {"id": "s217", "item": "217", "title": "Morning and high noon", "walk": "days", "frames": [
        f("spawn_morning", "The spawn at morning (cold run 9353, %s)" % RR),
        f("spawn_noon", "The same view at high noon (cold run 9354)"),
        f("extraction_morning", "The extraction at morning (9353)"),
        f("extraction_noon", "The extraction at high noon (9354)"),
    ], "note": "Your note: \"Build both\". The morning has the sun 28 degrees up in the east-southeast, golden, with a "
               "little haze. Noon has it 70 degrees up in the south, white, with a deep clear sky. A brief now asks for "
               "them by saying morning or noon. Priced: a day draws about a third less than the same level's evening, "
               "because the street lamps and their shadows are off.", "qs": [
        {"id": "q217_morning", "prompt": "Does the morning read as a morning?", "options": ["Looks right", "Needs work"]},
        {"id": "q217_noon", "prompt": "Does the noon read as high noon?", "options": ["Looks right", "Needs work"]},
    ]},
    {"id": "s79", "item": "79", "title": "Upper windows over the ground floor's", "frames": [
        f("fronts", "bank_branch_a04 and casino_a03, before (left, cold run 9282) and now (right, cold run 9348)"),
    ], "note": "The upper storeys' windows moved onto the openings below them, mirrored pairs together, in 32 "
               "buildings. A face that can't have both keeps its symmetry.", "qs": [
        {"id": "q79_stack", "prompt": "Do the stacked fronts read better?",
         "options": ["Better", "About the same", "Worse"]},
        {"id": "q79_tradeoff", "prompt": "Where a face can't be both stacked and symmetric, which wins?",
         "options": ["Symmetry", "Stacking"], "default": "Symmetry"},
    ]},
    {"id": "s267", "item": "267", "title": "A box that could be a barrier", "frames": [], "note":
        "Roof AC units now build as HVAC units and club bars as counters, where both were plain boxes. arena_a02 "
        "stands four 3.0 x 0.8 x 1.2 m barriers that build as boxes. Zoo's nearest model is the concrete jersey "
        "barrier; an arena's barriers are usually steel crowd rails.", "qs": [
        {"id": "q267_barrier", "prompt": "What should arena_a02's barriers be?",
         "options": ["Jersey barriers", "Crowd rails (a new model)", "Leave them boxes"]},
    ]},
]

WALKS = {
    "screens": [("walk_9350", "%s, evening: the office, its top floor and cubicles" % RR)],
    "phones": [("walk_9351", "%s, evening: the bus stops on each street" % RR)],
    "hatch": [("walk_9352", "bank_block_001, rainy night: the bank's roof")],
    "days": [("walk_9353", "%s at morning" % RR), ("walk_9354", "%s at high noon" % RR)],
}
plans = []

n_questions = sum(len(s["qs"]) for s in SECTIONS)
DATA = {"sections": SECTIONS, "plans": plans, "total": n_questions, "walks": WALKS}

CSS = r"""
:root {
  /* Layout: a single reading column of review cards, frames in a two-up grid, a sticky answer counter. */
  --bg: #121519; --surface: #1b1f25; --raise: #232830; --line: #2f3540;
  --fg: #ece7dd; --muted: #a2a7ae; --accent: #f0a33c; --accent-ink: #1a1408;
  --keep: #7cc489; --change: #e9785f;
  --display: "Barlow Condensed", "Arial Narrow", "Roboto Condensed", sans-serif;
  --body: "Public Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
  color-scheme: dark;
}
@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) {
  --bg: #f4f2ed; --surface: #ffffff; --raise: #f0ede6; --line: #d9d4ca;
  --fg: #1b1e22; --muted: #5d636b; --accent: #b0650a; --accent-ink: #ffffff;
  --keep: #2f7d3e; --change: #b5442b; color-scheme: light } }
:root[data-theme="light"] {
  --bg: #f4f2ed; --surface: #ffffff; --raise: #f0ede6; --line: #d9d4ca;
  --fg: #1b1e22; --muted: #5d636b; --accent: #b0650a; --accent-ink: #ffffff;
  --keep: #2f7d3e; --change: #b5442b; color-scheme: light }
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 15px; line-height: 1.55; }
.wrap { max-width: 1120px; margin: 0 auto; padding-block: 24px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
header.top { display: grid; gap: 10px; padding-block: 8px 20px; border-bottom: 1px solid var(--line); }
h1 { font-family: var(--display); font-weight: 700; font-size: clamp(32px, 6vw, 52px); line-height: 1; margin: 0;
  letter-spacing: 0.01em; text-transform: uppercase; text-wrap: balance; }
.lede { color: var(--muted); max-width: 68ch; margin: 0; }
.bar { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--bg);
  display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; padding-block: 10px;
  border-bottom: 1px solid var(--line); }
.count { font-family: var(--mono); font-size: 13px; font-variant-numeric: tabular-nums; }
.count b { color: var(--accent); }
.save { font-size: 13px; color: var(--muted); }
nav.jump { display: flex; flex-wrap: wrap; gap: 6px; }
nav.jump a { font-family: var(--mono); font-size: 12px; color: var(--fg); text-decoration: none;
  border: 1px solid var(--line); border-radius: 999px; padding: 2px 9px; }
nav.jump a.done { border-color: var(--keep); color: var(--keep); }
nav.jump a:focus-visible, button:focus-visible, textarea:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
section.card { margin-top: 28px; display: grid; gap: 14px; }
.head { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
.tag { font-family: var(--mono); font-size: 12px; color: var(--accent-ink); background: var(--accent);
  padding: 1px 7px; border-radius: 3px; letter-spacing: 0.04em; }
h2 { font-family: var(--display); font-weight: 600; font-size: 28px; line-height: 1.1; margin: 0; text-wrap: balance; }
.note { color: var(--muted); margin: 0; max-width: 72ch; }
.frames { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 340px), 1fr)); gap: 12px; }
figure { margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; overflow: hidden;
  display: grid; }
figure button { all: unset; cursor: zoom-in; display: block; }
figure img { display: block; width: 100%; height: auto; background: #000; }
.planbtn { all: unset; cursor: zoom-in; display: block; }
figcaption { font-size: 12.5px; color: var(--muted); padding: 7px 10px 9px; line-height: 1.4; }
figure.inspect figcaption::before { content: "INSPECT "; font-family: var(--mono); color: var(--accent); }
.qs { display: grid; gap: 10px; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px; }
.q { display: grid; gap: 8px; }
.q + .q { border-top: 1px dashed var(--line); padding-top: 10px; }
.q p { margin: 0; font-weight: 600; max-width: 76ch; }
.opts { display: flex; flex-wrap: wrap; gap: 8px; }
.opt { font: inherit; font-size: 14px; color: var(--fg); background: var(--raise); border: 1px solid var(--line);
  border-radius: 5px; padding: 6px 12px; cursor: pointer; }
.opt[aria-pressed="true"] { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
.opt .def { font-size: 11px; font-family: var(--mono); opacity: 0.75; margin-left: 6px; }
textarea { font: inherit; font-size: 14px; color: var(--fg); background: var(--bg); border: 1px solid var(--line);
  border-radius: 5px; padding: 6px 9px; min-height: 2.4em; resize: vertical; width: 100%; box-sizing: border-box; }
.walk { background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px; display: grid; gap: 8px; }
.walk code, .path { font-family: var(--mono); font-size: 13px; overflow-wrap: anywhere; }
.plans { display: grid; gap: 16px; }
.plan { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: 14px; background: var(--surface);
  border: 1px solid var(--line); border-radius: 6px; padding: 12px; }
.plan img { width: 100%; height: auto; background: #fff; border-radius: 4px; }
.plan h3 { font-family: var(--display); font-weight: 600; font-size: 21px; margin: 0 0 6px; }
.pair { display: grid; gap: 6px; padding-block: 8px; border-top: 1px dashed var(--line); }
.pair p { margin: 0; font-size: 14px; }
.pair .m { font-family: var(--mono); font-size: 12px; color: var(--muted); }
@media (max-width: 720px) { .plan { grid-template-columns: minmax(0, 1fr); } }
dialog { border: 0; padding: 0; background: transparent; max-width: min(96vw, 1400px); }
dialog::backdrop { background: rgba(0, 0, 0, 0.82); }
dialog img { display: block; max-width: 100%; max-height: 84vh; height: auto; }
dialog p { color: #ece7dd; font-size: 13px; margin: 8px 2px 0; }
@media (prefers-reduced-motion: no-preference) { .opt { transition: background 0.12s, border-color 0.12s; } }
"""

JS = r"""
const DATA = __DATA__;
const state = {};
let db = null, saving = false;
const $ = (s, el = document) => el.querySelector(s);

function el(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v; else if (k === "text") e.textContent = v; else e.setAttribute(k, v);
  }
  for (const k of kids) if (k) e.append(k);
  return e;
}

function frameEl(fr) {
  const fig = el("figure", {class: fr.inspect ? "inspect" : ""});
  const btn = el("button", {type: "button", "aria-label": "Enlarge: " + fr.cap});
  btn.append(el("img", {src: fr.src, alt: fr.cap, loading: "lazy", width: "1280", height: "720"}));
  btn.addEventListener("click", () => openBig(fr.src, fr.cap));
  fig.append(btn, el("figcaption", {text: fr.cap}));
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
  const ta = el("textarea", {id: "note-" + q.id, rows: "1",
    placeholder: q.options.length ? "Note (optional)" : "Your answer"});
  let t = null;
  ta.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => saveNote(q.id, ta.value), 900); });
  box.append(ta);
  return box;
}

function render() {
  const root = $("#sections");
  const jump = $("#jump");
  for (const s of DATA.sections) {
    const sec = el("section", {class: "card", id: s.id});
    const head = el("div", {class: "head"}, el("span", {class: "tag", text: "#" + s.item}), el("h2", {text: s.title}));
    sec.append(head);
    if (s.note) sec.append(el("p", {class: "note", text: s.note}));
    if (s.walk && DATA.walks[s.walk]) {
      const w = el("div", {class: "walk"});
      w.append(el("p", {text: "A walk copy is ready. Open it in Godot 4.7 and press F5."}));
      for (const [dir, what] of DATA.walks[s.walk]) {
        w.append(el("div", {}, el("div", {class: "path", text: "C:\\Projects\\gabagool_studios\\gabagool_factory\\_scratch\\review\\" + dir}), el("div", {class: "note", text: what})));
      }
      sec.append(w);
    }
    if (s.frames.length) {
      const g = el("div", {class: "frames"});
      for (const fr of s.frames) g.append(frameEl(fr));
      sec.append(g);
    }
    const qs = el("div", {class: "qs"});
    for (const q of s.qs) qs.append(questionEl(q));
    sec.append(qs);
    root.append(sec);
    const a = el("a", {href: "#" + s.id, "data-sec": s.id, text: s.item});
    jump.append(a);
  }
  if (!DATA.plans.length) return;
  // roadmap 255: the open floors
  const sec = el("section", {class: "card", id: "s255"});
  sec.append(el("div", {class: "head"}, el("span", {class: "tag", text: "#255"}),
    el("h2", {text: "Open floors nobody named"})));
  sec.append(el("p", {class: "note", text: "Each red line is where two rooms meet with no wall for at least 1.2 m, so a body walks straight from one to the other. Say whether each was meant, or should be walled."}));
  const list = el("div", {class: "plans"});
  for (const p of DATA.plans) {
    const card = el("div", {class: "plan"});
    const img = el("img", {src: "plans/" + p.file, alt: p.spec + " storey " + p.story + " plan", loading: "lazy"});
    const b = el("button", {type: "button", class: "planbtn", "aria-label": "Enlarge plan"});
    b.append(img);
    b.addEventListener("click", () => openBig("plans/" + p.file, p.spec + ", storey " + p.story));
    const side = el("div");
    side.append(el("h3", {text: p.spec + ", storey " + p.story}));
    for (const pr of p.pairs) {
      const qid = "open~" + p.spec + "~" + pr.a + "+" + pr.b;
      const row = el("div", {class: "pair", "data-q": qid});
      row.append(el("p", {text: pr.a.replace(/_/g, " ") + "  and  " + pr.b.replace(/_/g, " ")}),
        el("span", {class: "m", text: pr.uncovered_m + " m open"}));
      const opts = el("div", {class: "opts"});
      for (const o of ["Meant to be open", "Wall it"]) {
        const ob = el("button", {type: "button", class: "opt", "aria-pressed": "false", "data-v": o, text: o});
        ob.addEventListener("click", () => choose(qid, o));
        opts.append(ob);
      }
      row.append(opts);
      side.append(row);
    }
    card.append(b, side);
    list.append(card);
  }
  sec.append(list);
  root.append(sec);
  jump.append(el("a", {href: "#s255", "data-sec": "s255", text: "255"}));
}

function paint() {
  let done = 0;
  for (const node of document.querySelectorAll("[data-q]")) {
    const qid = node.getAttribute("data-q");
    const v = state[qid] || {};
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
    const all = qs.length && qs.every(n => { const v = state[n.dataset.q]; return v && (v.choice || (v.note && !n.querySelector(".opt"))); });
    a.classList.toggle("done", !!all);
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

head = ('<title>October 20 Look Review</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&'
        'family=IBM+Plex+Mono&family=Public+Sans:wght@400;600&display=swap">\n<style>' + CSS + "</style>\n")
body = ('<div class="wrap">\n<header class="top">\n<h1>October 20 Look Review</h1>\n'
        '<p class="lede">What changed today, each beside frames of it: before on the left, after on the right, from levels the factory built today except where a caption '
        'names an earlier run. Frames marked INSPECT are lit with a work light to show shape; the rest show the '
        'level as a player sees it. Tap a frame to enlarge it, pick an answer, and add a note where you want one.</p>\n'
        '</header>\n<div class="bar"><span class="count" id="count"></span><span class="save" id="save">Loading saved '
        'answers.</span><nav class="jump" id="jump" aria-label="Jump to a question"></nav></div>\n'
        '<main id="sections"></main>\n</div>\n<dialog id="big" aria-label="Enlarged frame"><img alt=""><p></p></dialog>\n'
        '<script>' + JS.replace("__DATA__", json.dumps(DATA)) + "</script>\n")
(page / "index.html").write_text(head + body, encoding="utf-8")
print("wrote index.html: %d sections, %d questions, %d frames referenced"
      % (len(SECTIONS), n_questions, sum(len(s["frames"]) for s in SECTIONS)))
missing = [fr["src"] for s in SECTIONS for fr in s["frames"] if not (page / fr["src"]).is_file()]
if missing:
    raise SystemExit("MISSING files: " + ", ".join(missing))
