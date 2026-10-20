---
name: elevated-shots-are-orthographic
description: "look_shots' elev_* views are orthographic and level -- they see no horizontal face and draw far objects at full size; pick before attributing a patch"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-11T11:02:49.390Z
---

look_shots' four elevated views (`elev_W/E/N/S`) are ORTHOGRAPHIC cameras looking level (eye and target at one height, an ~8 m tall frame; the shots report's `derivation` says "orthographic"). Two consequences, both learned the hard way on 2026-10-11:

- They see NO horizontal face. A roof, a container top, a slab's upper surface is edge-on.
- Distance does not shrink anything. A 1.8 m lit window 91 m away draws at 1.8 m, so a far backdrop detail can look like a near object.

**Why:** cold run 9226 read a bright patch in `elev_W` as "a container's top face" and Zoo 1.99.0 darkened container roofs for it; cold run 9240 showed the patch unchanged, and `docs/cold_runs/cold_9240/slab_ray.py` proved it was a backdrop warehouse's lit high window (backdrop_117, third window of six). 9226's reading is retracted in its NOTES and in roadmap 228.

**How to apply:** before a frame becomes evidence about an object, pick the object: map pixels through the camera recorded in the shots JSON (eye, target, ortho height), check the mapping on known props, and intersect the slots manifest (Blender Z-up; Godot (X,Y,Z) = Blender (X,-Z,Y)); `slab_ray.py` is the template. Only count boxes in front of the eye. See [[presentation-gates-were-unread]] for the sibling failure (reading the wrong artefact).
