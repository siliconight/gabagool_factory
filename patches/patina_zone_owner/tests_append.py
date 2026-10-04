

# --- 0.23.0: a zone dresses only the ground it owns ---------------------------

def _owner_case():
    """A road box inside a whole-plate open zone, as Lot emits them: the road
    first (precedence), the open ground after, each tagged with its family."""
    road = zone("road_0_s00", "play_space", "low", (-20, -4, 20, 4))
    road["tags"] = ["zone_family:road"]
    road2 = zone("road_0_s01", "play_space", "low", (19, -4, 40, 4))   # overlaps s00 at a join
    road2["tags"] = ["zone_family:road"]
    ground = zone("open_ground", "play_space", "medium", (-40, -40, 40, 40))
    ground["tags"] = ["zone_family:open"]
    return surfaces([road, road2, ground])


def _inside(p, rect):
    return rect[0] <= p[0] <= rect[2] and rect[1] <= p[1] <= rect[3]


def test_open_ground_places_nothing_on_ground_a_road_owns():
    m = plan(_owner_case(), instance_budget=4000, tri_budget=None)
    on_road = [o for o in m["orders"] if o["surface_zone_id"] == "open_ground"
               and _inside(o["pos"], (-20, -4, 40, 4))]
    assert on_road == []
    # and it still dresses the ground it does own
    assert any(o["surface_zone_id"] == "open_ground" for o in m["orders"])
    refused = [k for k in m["keep_out"]["entries"] if k["code"] == SD.CODE_NOT_OWNER]
    assert refused and all(k["surface_zone_id"] == "open_ground" for k in refused)
    assert all("road_0_s0" in k["why"] for k in refused)


def test_a_corridor_s_boxes_share_their_join():
    """A point on the overlap of two boxes of one road is road either way:
    the second box is not refused there for being second."""
    m = plan(_owner_case(), instance_budget=4000, tri_budget=None)
    assert not [k for k in m["keep_out"]["entries"] if k["code"] == SD.CODE_NOT_OWNER
                and k["surface_zone_id"].startswith("road_0")]


def test_the_rule_is_the_one_zone_for_states():
    """The control: with ownership ignored -- every zone given one family --
    open ground does land on the road, so the test above can fail."""
    surf = _owner_case()
    for z in surf["zones"]:
        z["tags"] = ["zone_family:same"]
    m = plan(surf, instance_budget=4000, tri_budget=None)
    assert [o for o in m["orders"] if o["surface_zone_id"] == "open_ground"
            and _inside(o["pos"], (-20, -4, 40, 4))]


def test_zone_family_reads_the_tag_or_falls_back_to_the_id():
    assert SD.zone_family({"surface_zone_id": "road_0_s03", "tags": ["street", "zone_family:road"]}) == "road"
    assert SD.zone_family({"surface_zone_id": "edge", "tags": []}) == "edge"
