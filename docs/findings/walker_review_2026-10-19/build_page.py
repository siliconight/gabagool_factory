"""Build the walker's review page: each question with its frames, and a control for the answer that saves to the
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
plans = json.loads((page / "plans_index.json").read_text(encoding="utf-8"))

LV = {
    "r": "restaurant_row_001, evening, cold run 9335",
    "u": "urban_row_001, evening, cold run 9336",
    "h": "county_hospital_001, rainy night, cold run 9334",
    "n": "gas_block_001, clear night, cold run 9337",
}
INSPECT = " Inspection light: this shows form, not the level's lighting."


def f(key, what, inspect=False, src=None):
    lv = LV.get(key[0]) if key[1] == "_" else None
    cap = what + (" (" + lv + ")" if lv and not src else "") + (" (" + src + ")" if src else "")
    return {"src": "img/%s.jpg" % key, "cap": cap + (INSPECT if inspect else ""), "inspect": inspect}


SECTIONS = [
    {"id": "s170", "item": "170", "title": "Roof hatches", "frames": [
        f("x_hatch_climber", "The hatch from the ladder", src="cold run 9316, when it shipped"),
        f("x_hatch_above", "The open lid from above", src="cold run 9316"),
        f("x_hatch_hinge", "The hinge side", src="cold run 9316"),
    ], "note": "None of today's levels has a roof hatch, so these are the frames from when it shipped.", "qs": [
        {"id": "q170_look", "prompt": "Does the hatch and its lid read right?", "options": ["Looks right", "Needs work"]},
        {"id": "q170_open", "prompt": "Should the lid stand open by default, so the ladder stays a way on and off the roof?",
         "options": ["Open by default", "Closed by default"], "default": "Open by default"},
    ]},
    {"id": "s179", "item": "179", "title": "Street drains", "frames": [
        f("r_drain_inspect", "A kerb inlet grate in the gutter", inspect=True),
        f("r_drain_level", "The same spot in the level's own light"),
        f("r_drain_road_inspect", "The road from above: covers and crosswalk paint", inspect=True),
    ], "qs": [
        {"id": "q179", "prompt": "Do the inlets and covers read as part of the street?", "options": ["Looks right", "Needs work"]},
    ]},
    {"id": "s228", "item": "228", "title": "The edge of the playable area", "frames": [
        f("r_edge_south", "Looking out over the south edge: backdrop rowhomes and the water tower"),
        f("r_edge_corner", "The north-east corner"),
        f("r_edge_gap", "A gap between two rowhomes on the north side"),
        f("x_edge_9230", "The edge before and after the redraw", src="cold run 9230"),
    ], "qs": [
        {"id": "q228", "prompt": "Does the edge read as the end of a neighbourhood, not the end of a map?",
         "options": ["Looks right", "Needs work"]},
    ]},
    {"id": "s238", "item": "238", "title": "Interior walls after the texture-memory cut", "frames": [
        f("r_wall_drywall", "A drywall partition and an office beyond it"),
        f("r_wall_concrete", "Concrete walls, close"),
        f("x_atlas_9274", "The cut's own before and after", src="cold run 9274"),
    ], "qs": [
        {"id": "q238", "prompt": "Do walls hold up close after the cut?", "options": ["Fine", "Too soft or noisy"]},
    ]},
    {"id": "s240", "item": "240", "title": "The Philly street pieces", "frames": [
        f("u_pole_line", "The pole line, wires and a parked car"),
        f("r_cars_row", "A block with its poles, lamps and the deli's sign"),
        f("u_street_furniture_inspect", "Meters, newspaper boxes and the sidewalk", inspect=True),
        f("r_edge_gap", "Stoops with railings"),
        f("x_shadow_options", "The street lights' shadow options, measured", src="docs/findings/pole_line"),
    ], "qs": [
        {"id": "q240_look", "prompt": "Do the poles, wires, stoops and street furniture read as a Philly street?",
         "options": ["Looks right", "Needs work"]},
        {"id": "q240_shadows", "prompt": "The street lights' shadows cost about 170 draw calls a view. Capping how many "
         "lights cast shadows saves 118 draws at 8 or 241 at 4, but moving bodies then read 8 to 26 percent darker. "
         "Keep them, or cap them?", "options": ["Keep as is", "Cap at 8", "Cap at 4"]},
    ]},
    {"id": "s241", "item": "241", "title": "The mid-rise street and its shops' glow", "frames": [
        f("u_street_wall", "The street wall of mid-rise blocks"),
        f("u_skyline", "Looking up at the blocks"),
        f("u_street_long", "Down the street past the pharmacy"),
        f("u_awning_west", "The west corner shop's glow"),
        f("u_awning_east", "The east corner shop's glow"),
        f("u_fire_escape_inspect", "Fire escapes on the walk-ups", inspect=True),
        f("u_fire_escape_close_inspect", "A fire escape, close", inspect=True),
        f("u_awning_inspect", "The corner laundromat's awning", inspect=True),
        f("u_roofs_inspect", "The roofs and parapets from above", inspect=True),
        f("x_skyline_9292", "The skyline when it first shipped", src="cold run 9292"),
    ], "qs": [
        {"id": "q241_look", "prompt": "Does the mid-rise street read as a real block?", "options": ["Looks right", "Needs work"]},
        {"id": "q241_glow", "prompt": "The shops' glow at evening is:", "options": ["Right", "Too strong", "Too weak"]},
    ]},
    {"id": "s44", "item": "44", "title": "The cars", "frames": [
        f("r_payphone_face_inspect", "Parked cars across the street", inspect=True),
        f("h_payphone_face_inspect", "A row of parked cars at the hospital", inspect=True),
        f("r_cars_lot", "A parking lot"),
    ], "qs": [
        {"id": "q44", "prompt": "Do the parked cars read right?", "options": ["Looks right", "Needs work"]},
    ]},
    {"id": "s45", "item": "45", "title": "Ground scatter", "frames": [
        f("r_spawn", "Where you start"),
        f("r_extraction", "Where you leave"),
        f("r_drain_inspect", "Litter and leaves on the sidewalk", inspect=True),
    ], "qs": [
        {"id": "q45", "prompt": "Does the litter and leaf scatter look natural, or too even?",
         "options": ["Natural", "Too even"]},
    ]},
    {"id": "s148", "item": "148", "title": "Do interiors read as lived in?", "frames": [
        f("r_room_deli_aisles", "The deli's market aisles"),
        f("r_room_deli_kitchen", "The deli's kitchen"),
        f("r_room_deli_stock", "The deli's stockroom"),
        f("r_room_rx_counter", "The pharmacy's counter area"),
        f("r_room_rx_vault", "The pharmacy's vault room"),
        f("r_room_office_bullpen", "The office bullpen"),
        f("r_room_office_lobby", "The office lobby"),
    ], "qs": [
        {"id": "q148", "prompt": "Do these rooms read as places people use?", "options": ["Yes", "Too sparse"]},
    ]},
    {"id": "s210", "item": "210", "title": "Payphones", "frames": [
        f("r_payphone_back_level", "From the street on restaurant row: you see the phone's back"),
        f("r_payphone_back_inspect", "The same phone, lit to show its shape", inspect=True),
        f("r_payphone_face_inspect", "Its face points at the storefront behind it", inspect=True),
        f("h_payphone_face_level", "At the hospital the phone stands at the kerb and faces the sidewalk"),
        f("h_payphone_face_inspect", "The hospital's phone, lit to show its shape", inspect=True),
        f("n_payphone_street", "A street phone at night: the booth's light barely reads"),
    ], "qs": [
        {"id": "q210_facing", "prompt": "Should a street phone always face the sidewalk, wherever it stands?",
         "options": ["Always face the sidewalk", "Leave as placed"], "default": "Always face the sidewalk"},
        {"id": "q210_booth", "prompt": "Does the lit booth read at night?", "options": ["Looks right", "Needs more light"]},
        {"id": "q210_themes", "prompt": "Which level themes count as city, so payphones appear there? Write them in the note.",
         "options": []},
    ]},
    {"id": "s217", "item": "217", "title": "Times of day", "frames": [
        f("n_moonlit", "A clear night away from the street lamps"),
        f("n_long", "A clear night down the street"),
        f("n_forecourt", "The gas station at night"),
        f("n_canopy", "Under the canopy"),
        f("h_rain_street", "A rainy night"),
        f("h_tree_campus", "Rain over the hospital grounds"),
        f("u_street_long", "Evening"),
    ], "note": "No level in today's set runs a rainy day, a morning or a noon, so those two questions have no frames.",
     "qs": [
        {"id": "q217_moon", "prompt": "Away from the lamps, the clear-night moonlight is:",
         "options": ["Right", "Too dark", "Too bright"]},
        {"id": "q217_rain", "prompt": "Does the rainy night read right?", "options": ["Looks right", "Needs work"]},
        {"id": "q217_rainsun", "prompt": "Should a rainy day show any sun at all?", "options": ["No sun", "A weak sun"]},
        {"id": "q217_presets", "prompt": "Morning and noon presets:", "options": ["Build both", "Not needed yet"]},
    ]},
    {"id": "s253", "item": "253", "title": "Flag assets on a walk", "frames": [], "walk": True, "qs": [
        {"id": "q253", "prompt": "Walk done?", "options": ["Done", "Not yet"]},
    ]},
]

open_qs = []
for p in plans:
    for pr in p["pairs"]:
        qid = "open~%s~%s+%s" % (p["spec"], pr["a"], pr["b"])
        open_qs.append(qid)

n_questions = sum(len(s["qs"]) for s in SECTIONS) + len(open_qs)
DATA = {"sections": SECTIONS, "plans": plans, "total": n_questions}

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
    if (s.walk) {
      const w = el("div", {class: "walk"});
      w.append(el("p", {text: "Four walk copies are ready. Open one in Godot 4.7 and press F5. Aim at a piece and press G if it looks good, or P if it needs love. Each press saves the piece, where you stood and a small frame, and I gather them afterwards."}));
      for (const [path, what] of [
        ["C:\\Projects\\gabagool_studios\\gabagool_factory\\_scratch\\review\\walk_9336", "urban_row_001, evening: the mid-rise street"],
        ["C:\\Projects\\gabagool_studios\\gabagool_factory\\_scratch\\review\\walk_9335", "restaurant_row_001, evening"],
        ["C:\\Projects\\gabagool_studios\\gabagool_factory\\_scratch\\review\\walk_9337", "gas_block_001, clear night"],
        ["C:\\Projects\\gabagool_studios\\gabagool_factory\\_scratch\\review\\walk_9334", "county_hospital_001, rainy night"]]) {
        w.append(el("div", {}, el("div", {class: "path", text: path}), el("div", {class: "note", text: what})));
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

head = ('<title>Gabagool Look Review</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&'
        'family=IBM+Plex+Mono&family=Public+Sans:wght@400;600&display=swap">\n<style>' + CSS + "</style>\n")
body = ('<div class="wrap">\n<header class="top">\n<h1>Gabagool Look Review</h1>\n'
        '<p class="lede">Every frame was shot today from levels the factory built today, except where a caption '
        'names an earlier run. Frames marked INSPECT are lit with a work light to show shape; the rest show the '
        'level as a player sees it. Tap a frame to enlarge it, pick an answer, and add a note where you want one.</p>\n'
        '</header>\n<div class="bar"><span class="count" id="count"></span><span class="save" id="save">Loading saved '
        'answers.</span><nav class="jump" id="jump" aria-label="Jump to a question"></nav></div>\n'
        '<main id="sections"></main>\n</div>\n<dialog id="big" aria-label="Enlarged frame"><img alt=""><p></p></dialog>\n'
        '<script>' + JS.replace("__DATA__", json.dumps(DATA)) + "</script>\n")
(page / "index.html").write_text(head + body, encoding="utf-8")
print("wrote index.html: %d sections + open floors (%d plans), %d questions, %d frames referenced"
      % (len(SECTIONS), len(plans), n_questions, sum(len(s["frames"]) for s in SECTIONS)))
missing = [fr["src"] for s in SECTIONS for fr in s["frames"] if not (page / fr["src"]).is_file()]
missing += ["plans/" + p["file"] for p in plans if not (page / "plans" / p["file"]).is_file()]
if missing:
    raise SystemExit("MISSING files: " + ", ".join(missing))
