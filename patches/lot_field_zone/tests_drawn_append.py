

# --- the dressing reads the site as drawn (0.95.0) ----------------------------

def test_assemble_writes_the_site_it_drew(tmp_path):
    import json
    spec_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "specs", "coldrun_kerb_probe.json")
    lot.assemble(spec_path, str(tmp_path))
    authored = json.load(open(spec_path, encoding="utf-8"))
    drawn = json.load(open(tmp_path / f"{authored['name']}.site.drawn.json", encoding="utf-8"))
    # what assemble adds: the fields and their driveways, the cover, every
    # building's footprint; none of it in the authored spec
    assert drawn["fields"] and drawn["driveways"] == [f["driveway"] for f in drawn["fields"]]
    assert not authored.get("fields")
    assert drawn["cover"] and all(b.get("_footprint") for b in drawn["buildings"])


def test_the_surfaces_cli_reads_the_drawn_site_and_says_so(tmp_path):
    import json
    spec_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "specs", "coldrun_kerb_probe.json")
    lot.assemble(spec_path, str(tmp_path))
    out = tmp_path / "surfaces.json"
    assert SS.main([spec_path, "--out", str(out), "--base-dir", str(tmp_path)]) in (0, 1)
    doc = json.load(open(out, encoding="utf-8"))
    assert any(z["surface_zone_id"].startswith("field_") for z in doc["zones"])
    assert any(s["family"] == "parking" for s in doc["tops"])
    assert any(f["code"] == SS.CODE_SPEC_AS_DRAWN for f in doc["findings"])
    # the control: the same spec with no drawn site beside it is read as before
    bare = tmp_path / "bare"
    bare.mkdir()
    out2 = tmp_path / "surfaces_bare.json"
    SS.main([spec_path, "--out", str(out2), "--base-dir", ""])
    doc2 = json.load(open(out2, encoding="utf-8"))
    assert not any(z["surface_zone_id"].startswith("field_") for z in doc2["zones"])
    assert not any(f["code"] == SS.CODE_SPEC_AS_DRAWN for f in doc2["findings"])
