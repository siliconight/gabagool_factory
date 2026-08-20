#!/usr/bin/env python3
"""patch_dressing_shape.py -- second shape pass on the Layer 3 dressing kit,
plus the instrument that made it possible to know it was needed.

WHAT THIS CHANGES AND WHY, IN THE ORDER THE EVIDENCE ARRIVED.

The first four surface-dressing species were reviewed from four renders. The
renders showed slabs with flat tops, a pebble and a rubble fragment that could
not be told apart, and grass that read as paper slivers -- but a render cannot
say WHY, and every explanation offered for it was a guess. So the first thing
built was a ruler.

  tools/shape_metrics.py    NEW. Measures a GLB's shape, not just its size,
                            with no Blender and no dependencies. It also reads
                            POSITION accessor min/max, which is the height
                            measurement `glb_nodes.py` could never make -- that
                            tool reads NODE translations, and a Zoo dressing
                            GLB has one node at the origin, so it reported
                            "0 with an explicit translation" and measured
                            nothing.

Pointed at the shipped kit, it gave the diagnosis in four lines:

  species        tris/budget  regions  contact  b/a    plan_fill
  pebble           334/260      12      0.000   0.97     0.68
  rubble_frag      176/320       7      0.001   0.80     0.59
  weed_tuft         60/300       6      0.785   0.70     0.64
  litter_scrap      24/200       4      0.929   0.67     0.62

  * `regions` is normal_regions_80: how many distinct facing directions cover
    80% of the surface. Seven means the rubble fragment was still a box. That
    is not a tuning failure, it is arithmetic: `jitter_verts` moves VERTICES,
    and a cube has six faces however far its eight corners travel.
    IRREGULARITY IS BOUNDED ABOVE BY FACE COUNT. The fix has to add faces.
  * `contact` is base_contact_ratio: 0.000 and 0.001 mean the pebble and the
    rubble never touched the ground they were dressing.
  * pebble was 28% over its own triangle budget -- which is the unexplained
    `status=WARN` on all four specimen builds.

So, four geometry operations that add faces rather than move them, and one
that draws proportion instead of leaving it to chance:

  geometry.subdivide       give a primitive interior vertices to displace
  geometry.displace_lobes  broad bulges along the normal (moves the
                           SILHOUETTE) plus a fine grain (roughens the
                           surface). Per-vertex jitter only ever did the
                           second, which is why it never helped.
  geometry.fracture        slice with half-space planes and cap the cuts.
                           Broken rock IS an intersection of half-spaces.
                           `steep` biases the planes vertical, because a
                           randomly oriented cut usually shaves the top or
                           bottom where a standing eye cannot see it: measured
                           over four seeds, four random cuts left plan_hull_fill
                           at 0.856, and the same four biased vertical took it
                           to 0.667 at one fewer triangle.
  geometry.flatten_base    shave the underside so the solid has a footprint
  geometry.add_blade       a blade with stations along its length, so it can
                           CURVE. A cone cannot; that is why the first tuft
                           read as five straight slivers.
  geometry.zingg_radii     draw the three extents as a proportion. Zingg
                           (1935) classifies gravel on b/a and c/b at 2/3, and
                           real populations sit mostly in blade and disc.
                           Drawing width, depth and height independently emits
                           equant lumps far more often than nature does, and an
                           equant lump is the most procedural silhouette there
                           is.

Measured after, same tool, same seed:

  species        tris/budget  regions  contact  b/a    plan_fill  closed
  pebble           192/260      15      0.076   0.60     0.74      yes
  rubble_frag       64/320       7      0.858   0.56     0.69      yes
  weed_tuft        154/300       3      0.706   0.72     0.54      yes
  litter_scrap      96/200       2      0.597   0.91     0.76      yes

The pebble's bevel is dropped to 0 in every style. Measured on that species,
the bevel cost 238 of 430 triangles and changed normal_regions_80 by ZERO: it
was spending 55% of the budget on edges that carry no silhouette at two metres,
and those triangles buy shape as facets instead. rubble_frag's bevel goes to 0
for the same reason -- 268 triangles down to 88, same 7 regions.

Also here, because the review that missed all of the above was conducted from
images that could not have shown it:

  zoo/tools/preview_specimen.py   every frame now contains a ground plane and
                                  a red post exactly 0.117 m tall
                                  (`unassisted_step_max`, lot/site_steps.py).
                                  The old preview used `dist = size * 2.4`, so
                                  a 5 cm pebble and a 30 cm scrap rendered the
                                  same size and nothing showed whether anything
                                  touched the floor. Adds `--view patch`, which
                                  renders many instances at standing eye height
                                  -- the unit a scatter species is actually
                                  judged in.
  zoo/tools/preview_dressing.ps1  renders both views and prints the metrics.

WHAT THIS DOES NOT DO. It sets no thresholds and adds no gate. The ruler
reports; the genome decides. Nothing here touches collision, height caps,
transparency or the traversed-space rule -- every species stays collisionless
by construction and inside its declared height band.

CONVENTIONS. Every touched file is checked to EXIST and to match its recorded
pre-hash BEFORE anything is written; a single mismatch aborts the whole run
with nothing changed. Replaced files get a `.pre_shapepass` sidecar.

    python patch_dressing_shape.py --check      # verify, change nothing
    python patch_dressing_shape.py --selftest   # falsification tests
    python patch_dressing_shape.py              # apply
    python patch_dressing_shape.py --revert     # restore from sidecars
"""
from __future__ import annotations

import base64
import hashlib
import os
import sys

SIDECAR = ".pre_shapepass"
ANCHOR = "# --- UVs + wear ---"
IMPORT_OLD = "import bmesh\nimport bpy"
IMPORT_NEW = "import math\n\nimport bmesh\nimport bpy"
GEOMETRY_REL = "zoo/zoo_keeper/bpylayer/geometry.py"

PAYLOAD = {
  'zoo/zoo_keeper/recipes/pebble.py': {
    "kind": 'replace',
    "pre_sha": 'de580d7ae0c942947e03f38fb0f419a18ed5681c9258ec8f66fe9477402ecdb1',
    "pre_bytes": 3241,
    "post_sha": '663802be431a57556a08cb32a4bb6f1b7435e37a974985f36253330def6162bc',
    "post_bytes": 4758,
    "b64": (
    "IiIicGViYmxlIHJlY2lwZTogYSBmZXcgc21hbGwgc3RvbmVzIHNpdHRpbmcgb24gYSBzdXJmYWNlIOKAlCBMYXllciAzIG1p"
    "Y3JvIHJlbGllZi4KCldIWSBUSElTIEVYSVNUUy4gYGRvY3MvU1VSRkFDRV9EUkVTU0lORy5tZGAgZGVmaW5lcyBMYXllciAz"
    "IGFzIGNvbGxpc2lvbmxlc3MKZGV0YWlsIHNjYXR0ZXJlZCBvdmVyIGFuIGFzc2VtYmxlZCBzaXRlLCBhbmQgWm9vIHNoaXBw"
    "ZWQgZmlmdHkgc3BlY2llcyB3aXRoCm5vbmUgb2YgdGhlbSBpbiB0aGF0IGxheWVyOiBubyBncmFzcywgcGViYmxlcywgcnVi"
    "YmxlLCBsaXR0ZXIsIGxlYXZlcyBvciByb290cy4KTm90aGluZyBjb3VsZCBiZSBwbGFjZWQgYmVjYXVzZSBub3RoaW5nIGV4"
    "aXN0ZWQgdG8gcGxhY2UuIFRoaXMgaXMgdGhlIGZpcnN0IG9mCmZvdXIuCgpIRUlHSFQgSVMgVEhFIENPTlRSQUNULCBOT1Qg"
    "QSBTVFlMRSBDSE9JQ0UuIFRoZSBnZW5vbWUgY2FwcyBoZWlnaHQgYXQgMC4xMCBtLAp1bmRlciB0aGUgMC4xMTcgbSBgdW5h"
    "c3Npc3RlZF9zdGVwX21heGAgZGVyaXZlZCBpbiBgbG90L3NpdGVfc3RlcHMucHlgIGZvciB0aGlzCnN0YWNrJ3MgMC40IG0g"
    "Y2Fwc3VsZS4gQmVsb3cgdGhhdCBhIGJvZHkgc3RlcHMgb3ZlciB0aGUgb2JqZWN0IGFueXdheSwgc28KcGFzc2luZyB0aHJv"
    "dWdoIGl0IGlzIG5vdCBhIHZpc2libGUgbGllOyBhYm92ZSBpdCB0aGUgZW5naW5lIGNhbGxzIHRoZSBjb250YWN0CmEgV0FM"
    "TCBhbmQgd2Fsa2luZyB0aHJvdWdoIGluc3RlYWQgaXMgdGhlICJiZWxpZXZhYmxlIGJ1dCBmYWxzZSB0cmF2ZXJzYWwKcHJv"
    "bWlzZSIgdGhlIGd1aWRlIGZvcmJpZHMuIFRoZSB3aG9sZSBmaXJzdCBraXQgaXMgZGVsaWJlcmF0ZWx5IG1pY3JvLWJhbmQs"
    "IHNvCmV2ZXJ5IHBsYWNlbWVudCBpcyB1bmNvbmRpdGlvbmFsbHkgbGVnYWwgYW5kIHRoZSB0cmF2ZXJzZWQtc3BhY2UgcnVs"
    "ZSBpcyBuZXZlcgp0aGUgdGhpbmcgdW5kZXIgdGVzdCBvbiB0aGUgZmlyc3QgcGFzcy4KCk5PIENPTExJU0lPTiwgQlkgQ09O"
    "U1RSVUNUSU9OLiBgY29sbGlzaW9uX2JveGVzYCBpcyBlbXB0eSBhbmQgdGhlIGdlbm9tZSBzYXlzCmAiY29sbGlzaW9uIjog"
    "ZmFsc2VgLiBab28gYWxyZWFkeSByYWlzZXMgWk9PX0RSRVNTSU5HX0hBU19DT0xMSVNJT04gYXMgYQpibG9ja2VyIGZvciBh"
    "IGRyZXNzaW5nIGFzc2V0IHRoYXQgZGVjbGFyZXMgY29sbGlzaW9uOyB0aGlzIHNwZWNpZXMgY2Fubm90IHRyaXAKaXQgYmVj"
    "YXVzZSBpdCBuZXZlciBidWlsZHMgb25lLgoKU0hBUEUsIFNFQ09ORCBQQVNTLiBUaGUgZmlyc3QgdmVyc2lvbiBkcmV3IHdp"
    "ZHRoLCBkZXB0aCBhbmQgaGVpZ2h0CmluZGVwZW5kZW50bHkgYW5kIGppdHRlcmVkIHRoZSB2ZXJ0aWNlcyBvZiBhIDZ4NCBl"
    "bGxpcHNvaWQuIE1lYXN1cmVkIHdpdGgKYHRvb2xzL3NoYXBlX21ldHJpY3MucHlgLCB0aGF0IGdhdmUgYi9hID0gMC45NyAo"
    "YSBiYWxsIGluIHBsYW4pLCAxMiBkaXN0aW5jdApmYWNpbmcgZGlyZWN0aW9ucywgYW5kIGBiYXNlX2NvbnRhY3RfcmF0aW9g"
    "IDAuMDAwIC0tIGl0IHdhcyBhIGx1bXB5IHNwaGVyZQpob3ZlcmluZyBvdmVyIHRoZSBmbG9vciwgYW5kIG5vIGFtb3VudCBv"
    "ZiBleHRyYSBqaXR0ZXIgY291bGQgaGF2ZSBmaXhlZCBpdCwKYmVjYXVzZSBqaXR0ZXIgbW92ZXMgdmVydGljZXMgYW5kIHRo"
    "ZSBzaWxob3VldHRlIGlzIG1hZGUgb2YgZmFjZXMuIFRocmVlCmNoYW5nZXMsIGVhY2ggYW5zd2VyaW5nIG9uZSBtZWFzdXJl"
    "bWVudDoKCiAgLSBgemluZ2dfcmFkaWlgIGRyYXdzIHRoZSB0aHJlZSBleHRlbnRzIGFzIGEgUFJPUE9SVElPTiByYXRoZXIg"
    "dGhhbgogICAgaW5kZXBlbmRlbnRseSwgc28gdGhlIHBvcHVsYXRpb24gbGFuZHMgd2hlcmUgcmVhbCBncmF2ZWwgbGFuZHMg"
    "KG1vc3RseQogICAgYmxhZGUgYW5kIGRpc2MpIGluc3RlYWQgb2YgZGVmYXVsdGluZyB0byBlcXVhbnQuCiAgLSBgZGlzcGxh"
    "Y2VfbG9iZXNgIGFkZHMgYSBmZXcgYnJvYWQgYnVsZ2VzIGFsb25nIHRoZSB2ZXJ0ZXggbm9ybWFscywgd2hpY2gKICAgIG1v"
    "dmVzIHRoZSBzaWxob3VldHRlOyBwZXItdmVydGV4IGppdHRlciBvbmx5IHJvdWdoZW5zIHRoZSBzdXJmYWNlLgogIC0gYGZs"
    "YXR0ZW5fYmFzZWAgc2hhdmVzIHRoZSB1bmRlcnNpZGUgc28gdGhlIHN0b25lIGhhcyBhIGZvb3RwcmludCwgdGhlbiBpdAog"
    "ICAgaXMgc3VuayBieSBhIGZyYWN0aW9uIG9mIHRoYXQgc28gaXQgcmVhZHMgYXMgc2l0dGluZyBJTiB0aGUgZ3JvdW5kIHJh"
    "dGhlcgogICAgdGhhbiBiYWxhbmNlZCBvbiBpdC4KClRoZSBiZXZlbCBpcyBkZWxpYmVyYXRlbHkgMCBoZXJlOiBvbiB0aGlz"
    "IHNwZWNpZXMgaXQgd2FzIHNwZW5kaW5nIHJvdWdobHkgdHdvCnRoaXJkcyBvZiB0aGUgdHJpYW5nbGUgYnVkZ2V0IG9uIGVk"
    "Z2VzIHRoYXQgY2Fycnkgbm8gc2lsaG91ZXR0ZSBhdCB0d28gbWV0cmVzLAphbmQgdGhvc2UgdHJpYW5nbGVzIGJ1eSBtb3Jl"
    "IHNoYXBlIGFzIGZhY2V0cy4KIiIiCmZyb20gX19mdXR1cmVfXyBpbXBvcnQgYW5ub3RhdGlvbnMKCmZyb20gLi5icHlsYXll"
    "ciBpbXBvcnQgZ2VvbWV0cnksIG1hdGVyaWFscwoKCmRlZiBidWlsZChwbGFuLCBzdHJlYW1zLCBjb2xsZWN0aW9uKToKICAg"
    "IHcgPSBwbGFuWyJkaW1lbnNpb25zIl1bIndpZHRoIl0KICAgIGQgPSBwbGFuWyJkaW1lbnNpb25zIl1bImRlcHRoIl0KICAg"
    "IGggPSBwbGFuWyJkaW1lbnNpb25zIl1bImhlaWdodCJdCiAgICBiZXZlbCwgd2VhciA9IHBsYW5bImJldmVsIl0sIHBsYW5b"
    "IndlYXIiXQogICAgcm5nID0gc3RyZWFtcy5zdHJlYW0oIndlYXIiKQoKICAgIGNvdW50ID0gbWF4KDEsIGludChwbGFuWyJw"
    "YXJhbXMiXS5nZXQoInN0b25lcyIsIDMpKSkKICAgIGZhY2V0c191ID0gaW50KHBsYW5bInBhcmFtcyJdLmdldCgiZmFjZXRz"
    "X3UiLCA4KSkKICAgIGZhY2V0c192ID0gaW50KHBsYW5bInBhcmFtcyJdLmdldCgiZmFjZXRzX3YiLCA1KSkKICAgICMgQSBz"
    "dG9uZSBoYWxmLWJ1cmllZCByZWFkcyBhcyBwYXJ0IG9mIHRoZSBncm91bmQgcmF0aGVyIHRoYW4gZHJvcHBlZCBvbgogICAg"
    "IyBpdCAtLSBidXQgdGhlIGZsYXQgZmFjZXQsIG5vdCB0aGUgYnVyaWFsLCBpcyB3aGF0IHNlbGxzIHRoZSBjb250YWN0LCBz"
    "bwogICAgIyB0aGlzIGlzIG5vdyBhIHNoYWxsb3cgdHVjayB1bmRlciB0aGUgZmxvb3IgcGxhbmUgcmF0aGVyIHRoYW4gYSB0"
    "aGlyZCBvZgogICAgIyB0aGUgc3RvbmUuIEl0IGFsc28ga2VlcHMgdGhlIGZvb3RwcmludCBmcm9tIGJlaW5nIGNvcGxhbmFy"
    "IHdpdGggdGhlCiAgICAjIGZsb29yIGl0IHNpdHMgb24sIHdoaWNoIGlzIHdoZXJlIHotZmlnaHRpbmcgY29tZXMgZnJvbS4K"
    "ICAgIHNpbmsgPSBmbG9hdChwbGFuWyJwYXJhbXMiXS5nZXQoInNpbmsiLCAwLjE1KSkKICAgIGxvYmVzID0gaW50KHBsYW5b"
    "InBhcmFtcyJdLmdldCgibG9iZXMiLCAzKSkKCiAgICBibSA9IGdlb21ldHJ5Lm5ld19ibSgpCiAgICBmb3IgaSBpbiByYW5n"
    "ZShjb3VudCk6CiAgICAgICAgIyBEZXRlcm1pbmlzdGljIHNwcmVhZCBhbmQgc2l6ZSBmcm9tIHRoZSBvbmUgc3RyZWFtLCBh"
    "cyBnb2xkX2JhciBhbmQKICAgICAgICAjIGNhc2hfc3RhY2sgZG8gLS0gYSBzZWNvbmQgbmFtZWQgc3RyZWFtIGlzIG5vdCBh"
    "biBhdHRlc3RlZCBBUEkgaGVyZS4KICAgICAgICBmID0gMC41NSArIHJuZy5yYW5kb20oKSAqIDAuNDUKICAgICAgICBhLCBi"
    "LCBjID0gZ2VvbWV0cnkuemluZ2dfcmFkaWkocm5nLCB3ICogZikKICAgICAgICBjID0gbWluKGMsIGgpICAgICAgICAgICAg"
    "ICAgICAgICAgICAgICAjIHRoZSBnZW5vbWUncyBoZWlnaHQgY2FwIHdpbnMKICAgICAgICB2ZXJ0cyA9IGdlb21ldHJ5LmFk"
    "ZF9lbGxpcHNvaWQoYm0sICgwLjAsIDAuMCwgMC4wKSwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "KGEgLyAyLjAsIGIgLyAyLjAsIGMgLyAyLjApLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB1X3Nl"
    "Zz1mYWNldHNfdSwgdl9zZWc9ZmFjZXRzX3YpCiAgICAgICAgZ2VvbWV0cnkuZGlzcGxhY2VfbG9iZXMoYm0sIHZlcnRzLCBy"
    "bmcsIG1pbihhLCBiLCBjKSAqIDAuMzAsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgbG9iZXM9bG9iZXMsIHNo"
    "YXJwbmVzcz0xLjUsIGdyYWluPTAuMjUpCiAgICAgICAgYmFzZV96ID0gZ2VvbWV0cnkuZmxhdHRlbl9iYXNlKHZlcnRzLCB0"
    "b2xfZnJhYz0wLjE2KQogICAgICAgIG94ID0gKHJuZy5yYW5kb20oKSAqIDIuMCAtIDEuMCkgKiB3ICogMC41CiAgICAgICAg"
    "b3kgPSAocm5nLnJhbmRvbSgpICogMi4wIC0gMS4wKSAqIGQgKiAwLjUKICAgICAgICBnZW9tZXRyeS5wbGFjZSh2ZXJ0cywg"
    "KG94LCBveSwgLWJhc2VfeiAtIGMgKiBzaW5rKSwKICAgICAgICAgICAgICAgICAgICAgICByb3Rfej1ybmcucmFuZG9tKCkg"
    "KiA2LjI4MzE4NTMpCgogICAgc3RvbmVzID0gZ2VvbWV0cnkuYm1fdG9fb2JqZWN0KGJtLCAiRHJlc3NfUGViYmxlIiwgY29s"
    "bGVjdGlvbiwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBiZXZlbD1iZXZlbCwgdGV4ZWw9Ni4wLCBybmc9"
    "cm5nLCB3ZWFyPXdlYXIpCiAgICBtYXRlcmlhbHMuYXNzaWduKFtzdG9uZXNdLCBtYXRlcmlhbHMubWFrZV9tYXRlcmlhbCgK"
    "ICAgICAgICBmIk1fUGViYmxlX3twbGFuWydtYXRlcmlhbCddfSIsIHBsYW5bImNvbG9yIl0sIHBsYW5bIm1hdGVyaWFsIl0p"
    "KQoKICAgIHJldHVybiB7Im9iamVjdHMiOiBbc3RvbmVzXSwgImNvbGxpc2lvbl9ib3hlcyI6IFtdLCAiYXR0YWNobWVudHMi"
    "OiB7fX0K"
    ),
  },
  'zoo/zoo_keeper/recipes/rubble_frag.py': {
    "kind": 'replace',
    "pre_sha": '033181c7c32f443e077ee570014a3cdf01acdaf578c60c35c715024263d6a8a8',
    "pre_bytes": 2113,
    "post_sha": 'a2749f32d62d99ed894484ebd9c9abfefb3581616af906ca690df5aa95a1c87a',
    "post_bytes": 4091,
    "b64": (
    "IiIicnViYmxlX2ZyYWcgcmVjaXBlOiBhbmd1bGFyIGJyb2tlbiBmcmFnbWVudHMg4oCUIExheWVyIDMgbG93IGRlYnJpcy4K"
    "ClRoZSBjb3VudGVycGFydCB0byBgcGViYmxlYC4gQSBwZWJibGUgaXMgcm91bmRlZCBhbmQgcmVhZHMgYXMgbmF0dXJhbDsg"
    "cnViYmxlCmlzIEFOR1VMQVIgYW5kIHJlYWRzIGFzIGRhbWFnZSwgd2hpY2ggaXMgd2hhdCBtYWtlcyBpdCB1c2FibGUgYXMg"
    "YW4KZW52aXJvbm1lbnRhbCBjYXVzZSBtYXJrZXI6IHRoZSBndWlkZSdzIHJ1bGUgMyBpcyAicGxhY2UgcnViYmxlIG5lYXIg"
    "ZGFtYWdlIiwKYW5kIGEgZnJhZ21lbnQgdGhhdCBsb29rcyB3YXRlci13b3JuIHNheXMgdGhlIHdyb25nIHRoaW5nLgoKSGVp"
    "Z2h0IGNhcHBlZCBhdCAwLjEwIG0gaW4gdGhlIGdlbm9tZSwgdW5kZXIgYHVuYXNzaXN0ZWRfc3RlcF9tYXhgIDAuMTE3IG0K"
    "KGBsb3Qvc2l0ZV9zdGVwcy5weWApLiBDb2xsaXNpb25sZXNzIGJ5IGNvbnN0cnVjdGlvbjsgc2VlIHBlYmJsZS5weSBmb3Ig"
    "d2h5CnRoYXQgbnVtYmVyIGFuZCBub3QgYW5vdGhlci4KClNIQVBFLCBTRUNPTkQgUEFTUyAtLSBBTkQgVEhFIFJFQVNPTiBU"
    "SEUgRklSU1QgT05FIENPVUxEIE5PVCBXT1JLLiBUaGUgZmlyc3QKdmVyc2lvbiBidWlsdCAiaml0dGVyZWQgYm94ZXMgcmF0"
    "aGVyIHRoYW4gaml0dGVyZWQgZWxsaXBzb2lkcyAuLi4gdGhlIGZsYXQKZmFjZXMgYW5kIHNoYXJwIGRpaGVkcmFscyBzdXJ2"
    "aXZlIHRoZSBsb3ctcG9seSBidWRnZXQgYW5kIHJlYWQgYXMgZnJhY3R1cmUiLgpUaGUgcHJlbWlzZSB3YXMgcmlnaHQgYW5k"
    "IHRoZSBtZXRob2QgY291bGQgbm90IGRlbGl2ZXIgaXQ6IGppdHRlcmluZyB0aGUgZWlnaHQKY29ybmVycyBvZiBhIGN1YmUg"
    "cHJvZHVjZXMgYSBwYXJhbGxlbGVwaXBlZC4gSXQgbW92ZXMgdmVydGljZXMsIGFuZCB0aGUgc2l4CmZhY2VzIHN0YXkgc2l4"
    "IHBsYW5lcy4gYHRvb2xzL3NoYXBlX21ldHJpY3MucHlgIG1lYXN1cmVkIHRoZSByZXN1bHQgYXQKYG5vcm1hbF9yZWdpb25z"
    "XzgwID0gN2AgLS0gc2V2ZW4gZmFjaW5nIGRpcmVjdGlvbnMgYWNjb3VudGVkIGZvciA4MCUgb2YgdGhlCnN1cmZhY2UsIHdo"
    "aWNoIGlzIGEgYm94IGhvd2V2ZXIgZmFyIHRoZSBjb3JuZXJzIHRyYXZlbGxlZCAtLSB3aXRoCmBiYXNlX2NvbnRhY3RfcmF0"
    "aW9gIDAuMDAxLCBzbyBpdCBhbHNvIGRpZCBub3QgdG91Y2ggdGhlIGdyb3VuZC4KClJlYWwgYnJva2VuIHJvY2sgSVMgYW4g"
    "aW50ZXJzZWN0aW9uIG9mIGhhbGYtc3BhY2VzLCBzbyB0aGlzIGJ1aWxkcyBpdCB0aGF0IHdheToKYGdlb21ldHJ5LmZyYWN0"
    "dXJlYCBzbGljZXMgdGhlIHNvbGlkIHdpdGggcmFuZG9tIHBsYW5lcyBhbmQgY2FwcyBlYWNoIGN1dC4gRXZlcnkKY3V0IGFk"
    "ZHMgb25lIGZsYXQgZmFjZXQgb2YgYSBzaXplIHRoZSBjdXQgY2hvb3NlcywgbWVldGluZyBpdHMgbmVpZ2hib3VycyBhdCBh"
    "CnNoYXJwIGRpaGVkcmFsLCBhbmQgdGhlIGNvc3QgaXMgYSBmZXcgdHJpYW5nbGVzIHBlciBjdXQgLS0gc28gdGhlIGFuZ3Vs"
    "YXJpdHkKdGhlIGRvY3N0cmluZyBhbHdheXMgY2xhaW1lZCBpcyBub3cgdGhlIGFjdHVhbCBjb25zdHJ1Y3Rpb24gcmF0aGVy"
    "IHRoYW4gYSBob3BlZAotZm9yIHNpZGUgZWZmZWN0IG9mIG5vaXNlLgoiIiIKZnJvbSBfX2Z1dHVyZV9fIGltcG9ydCBhbm5v"
    "dGF0aW9ucwoKZnJvbSAuLmJweWxheWVyIGltcG9ydCBnZW9tZXRyeSwgbWF0ZXJpYWxzCgoKZGVmIGJ1aWxkKHBsYW4sIHN0"
    "cmVhbXMsIGNvbGxlY3Rpb24pOgogICAgdyA9IHBsYW5bImRpbWVuc2lvbnMiXVsid2lkdGgiXQogICAgZCA9IHBsYW5bImRp"
    "bWVuc2lvbnMiXVsiZGVwdGgiXQogICAgaCA9IHBsYW5bImRpbWVuc2lvbnMiXVsiaGVpZ2h0Il0KICAgIGJldmVsLCB3ZWFy"
    "ID0gcGxhblsiYmV2ZWwiXSwgcGxhblsid2VhciJdCiAgICBybmcgPSBzdHJlYW1zLnN0cmVhbSgid2VhciIpCgogICAgY291"
    "bnQgPSBtYXgoMSwgaW50KHBsYW5bInBhcmFtcyJdLmdldCgiY2h1bmtzIiwgNCkpKQogICAgIyBDdXRzLCBub3Qgaml0dGVy"
    "LiBUaHJlZSB0byBmaXZlIHJlYWRzIGFzIGZyYWN0dXJlOyBiZWxvdyB0aHJlZSB0aGUgYm94CiAgICAjIHN1cnZpdmVzLCBh"
    "Ym92ZSBmaXZlIHRoZSBmcmFnbWVudCB0ZW5kcyB0b3dhcmQgYSByb3VuZGVkIHBvbHloZWRyb24gYW5kCiAgICAjIHN0b3Bz"
    "IHNheWluZyAiZGFtYWdlIi4KICAgIGN1dHMgPSBtYXgoMSwgaW50KHBsYW5bInBhcmFtcyJdLmdldCgiY3V0cyIsIDQpKSkK"
    "ICAgICMgS2VwdCBhcyBhIHNtYWxsIHdlYXRoZXJpbmcgcGFzcyBvbiB0b3Agb2YgdGhlIGN1dHM6IGNoaXBwZWQgY29ybmVy"
    "cywgbm90CiAgICAjIGVyb3Npb24uIFRoaXMgaXMgd2hhdCBgcm91Z2hgIG5vdyBtZWFucy4KICAgIHJvdWdoID0gZmxvYXQo"
    "cGxhblsicGFyYW1zIl0uZ2V0KCJyb3VnaCIsIDAuMzApKQoKICAgIGJtID0gZ2VvbWV0cnkubmV3X2JtKCkKICAgIGZvciBp"
    "IGluIHJhbmdlKGNvdW50KToKICAgICAgICBmID0gMC4zNSArIHJuZy5yYW5kb20oKSAqIDAuNjUKICAgICAgICBhLCBiLCBj"
    "ID0gZ2VvbWV0cnkuemluZ2dfcmFkaWkocm5nLCB3ICogZikKICAgICAgICBjID0gbWluKGMsIGgpICAgICAgICAgICAgICAg"
    "ICAgICAgICAgICAjIHRoZSBnZW5vbWUncyBoZWlnaHQgY2FwIHdpbnMKICAgICAgICB2ZXJ0cyA9IGdlb21ldHJ5LmFkZF9i"
    "b3goYm0sICgwLjAsIDAuMCwgMC4wKSwgKGEsIGIsIGMpKQogICAgICAgICMgYHN0ZWVwYCBtYXR0ZXJzIG1vcmUgdGhhbiBg"
    "Y3V0c2A6IG1lYXN1cmVkIG92ZXIgZm91ciBzZWVkcywgZm91cgogICAgICAgICMgcmFuZG9tbHkgb3JpZW50ZWQgY3V0cyBs"
    "ZWZ0IHRoZSBwbGFuLXZpZXcgb3V0bGluZSA4NiUgYXMgYm94eSBhcyB0aGUKICAgICAgICAjIGJveCAocGxhbl9odWxsX2Zp"
    "bGwgMC44NTYpLCBiZWNhdXNlIG1vc3QgcmFuZG9tIHBsYW5lcyBzaGF2ZSB0aGUgdG9wCiAgICAgICAgIyBvciB0aGUgYm90"
    "dG9tIHdoZXJlIGEgc3RhbmRpbmcgZXllIGNhbm5vdCBzZWUgdGhlbS4gQmlhc2luZyB0aGUgc2FtZQogICAgICAgICMgZm91"
    "ciBjdXRzIHRvd2FyZCB2ZXJ0aWNhbCB0YWtlcyBwbGFuX2h1bGxfZmlsbCB0byAwLjY2NyBhbmQgZG91YmxlcwogICAgICAg"
    "ICMgcGxhbl9yYWRpYWxfY3YsIGF0IG9uZSBmZXdlciB0cmlhbmdsZS4KICAgICAgICB2ZXJ0cyA9IGdlb21ldHJ5LmZyYWN0"
    "dXJlKGJtLCB2ZXJ0cywgcm5nLCBjdXRzPWN1dHMsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBuZWFyPTAu"
    "MTAsIGZhcj0wLjUwLCBzdGVlcD0wLjg1LAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgcmFkaXVzPW1heChh"
    "LCBiLCBjKSAqIDAuNSkKICAgICAgICBnZW9tZXRyeS5kaXNwbGFjZV9sb2JlcyhibSwgdmVydHMsIHJuZywgbWluKGEsIGIs"
    "IGMpICogcm91Z2ggKiAwLjE4LAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIGxvYmVzPTIsIHNoYXJwbmVzcz0y"
    "LjIsIGdyYWluPTAuNikKICAgICAgICBiYXNlX3ogPSBnZW9tZXRyeS5mbGF0dGVuX2Jhc2UodmVydHMsIHRvbF9mcmFjPTAu"
    "MTIpCiAgICAgICAgb3ggPSAocm5nLnJhbmRvbSgpICogMi4wIC0gMS4wKSAqIHcgKiAwLjU1CiAgICAgICAgb3kgPSAocm5n"
    "LnJhbmRvbSgpICogMi4wIC0gMS4wKSAqIGQgKiAwLjU1CiAgICAgICAgZ2VvbWV0cnkucGxhY2UodmVydHMsIChveCwgb3ks"
    "IC1iYXNlX3opLAogICAgICAgICAgICAgICAgICAgICAgIHJvdF96PXJuZy5yYW5kb20oKSAqIDYuMjgzMTg1MykKCiAgICBm"
    "cmFncyA9IGdlb21ldHJ5LmJtX3RvX29iamVjdChibSwgIkRyZXNzX1J1YmJsZUZyYWciLCBjb2xsZWN0aW9uLAogICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICAgYmV2ZWw9YmV2ZWwsIHRleGVsPTYuMCwgcm5nPXJuZywgd2Vhcj13ZWFyKQog"
    "ICAgbWF0ZXJpYWxzLmFzc2lnbihbZnJhZ3NdLCBtYXRlcmlhbHMubWFrZV9tYXRlcmlhbCgKICAgICAgICBmIk1fUnViYmxl"
    "X3twbGFuWydtYXRlcmlhbCddfSIsIHBsYW5bImNvbG9yIl0sIHBsYW5bIm1hdGVyaWFsIl0pKQoKICAgIHJldHVybiB7Im9i"
    "amVjdHMiOiBbZnJhZ3NdLCAiY29sbGlzaW9uX2JveGVzIjogW10sICJhdHRhY2htZW50cyI6IHt9fQo="
    ),
  },
  'zoo/zoo_keeper/recipes/weed_tuft.py': {
    "kind": 'replace',
    "pre_sha": 'bec5baa1874abfce32f3c01b64fe6f4bc31ca818ef859b1460a735df7d103057',
    "pre_bytes": 3052,
    "post_sha": '5ab107311b247aa26a5443ab719375507f6c440377b3955d2f0991f2c1e6673c',
    "post_bytes": 5131,
    "b64": (
    "IiIid2VlZF90dWZ0IHJlY2lwZTogYSBzbWFsbCBjbHVtcCBvZiBibGFkZXMg4oCUIExheWVyIDMgZ3JvdW5kIGNvdmVyLgoK"
    "VGhlIGd1aWRlJ3MgcnVsZSAzIGFnYWluOiBncm93dGggYmVsb25ncyBhdCBjcmFja3MsIG1vaXN0dXJlLCBzaGFkZSBhbmQg"
    "ZWRnZXMuCkEgdHVmdCBpcyB0aGUgbWFya2VyIGZvciB0aGF0IGNhdXNlLCB3aGljaCBpcyB3aHkgaXQgaXMgYSBDTFVNUCBy"
    "YXRoZXIgdGhhbiBhCnNpbmdsZSBibGFkZSAtLSBvbmUgYmxhZGUgcmVhZHMgYXMgYW4gYXJ0aWZhY3QsIGEgY2x1bXAgcmVh"
    "ZHMgYXMgc29tZXRoaW5nIHRoYXQKZ3JldyB0aGVyZS4KCkhlaWdodCBjYXBwZWQgYXQgMC4xMCBtIGluIHRoZSBnZW5vbWUs"
    "IHVuZGVyIGB1bmFzc2lzdGVkX3N0ZXBfbWF4YCAwLjExNyBtCihgbG90L3NpdGVfc3RlcHMucHlgKSwgc28gdGhlIHdob2xl"
    "IGZpcnN0IGtpdCBpcyB1bmNvbmRpdGlvbmFsbHkgbGVnYWwgaW4KdHJhdmVyc2VkIHNwYWNlLiBSZWFsIGdyYXNzIGlzIG9m"
    "dGVuIHRhbGxlcjsgdGhhdCBpcyBhIGxhdGVyIGJhbmQgYW5kIGEgbGF0ZXIKZGVjaXNpb24sIG5vdCBhIHJlYXNvbiB0byBt"
    "YWtlIHRoZSBmaXJzdCBraXQgdW50ZXN0YWJsZS4KClNUSUxMIFNPTElELCBOT1QgQ0FSRFMuIEJsYWRlcyBhcmUgY2xvc2Vk"
    "IHByaXNtcyByYXRoZXIgdGhhbiBjcm9zc2VkIHF1YWRzLiBBCmNyb3NzZWQgcXVhZCBpcyBhIHNpbmdsZS1zaWRlZCBwbGFu"
    "ZSwgYW5kIHRoaXMgcGlwZWxpbmUgaGFzIGFscmVhZHkgc3BlbnQgYQpzZXNzaW9uIGNoYXNpbmcgYSB3aGl0ZSBRdWFkTWVz"
    "aCB0aGF0IHR1cm5lZCBvdXQgdG8gYmUgYSBMdXggc2lnbiBmYWNlIC0tIGEKbGF5ZXIgbWVhbnQgdG8gYmUgaW5zdGFuY2Vk"
    "IGluIHRoZSB0aG91c2FuZHMgc2hvdWxkIG5vdCBhbHNvIGJlIHRoZSBsYXllciB0aGF0CnJlaW50cm9kdWNlcyAid2hhdCBp"
    "cyB0aGF0IHN1cmZhY2UgSSBjYW4gb25seSBzZWUgZnJvbSBvbmUgc2lkZSIuIEFuCmFscGhhLWN1dG91dCBjYXJkIHNwZWNp"
    "ZXMgaXMgdGhlIHJpZ2h0IGFuc3dlciBmb3IgREVOU0UgZm9saWFnZSBhbmQgaXMgYQpzZXBhcmF0ZSBzcGVjaWVzLCBwZXIg"
    "ImNvdmVyYWdlIGZpcnN0LCBhbHBoYSBjdXRvdXRzIHNlY29uZCwgYW5kIHRydWUKdHJhbnNwYXJlbmN5IG9ubHkgd2hlbiB0"
    "aGUgbWF0ZXJpYWwgcGh5c2ljYWxseSBjYWxscyBmb3IgaXQiLgoKU0hBUEUsIFNFQ09ORCBQQVNTLiBUaGUgZmlyc3QgdmVy"
    "c2lvbiB1c2VkIGBhZGRfY3lsaW5kZXJgIHdpdGggdGhyZWUgc2VnbWVudHMKYW5kIGEgbmVhci16ZXJvIHRvcCByYWRpdXMs"
    "IHRoZW4gbGVhbmVkIGVhY2ggc3Bpa2UgYnkgZGlzcGxhY2luZyBpdHMgdXBwZXIKdmVydHMuIEEgY29uZSBoYXMgbm8gc3Rh"
    "dGlvbnMgYWxvbmcgaXRzIGxlbmd0aCwgc28gYSBsZWFuIGlzIGFsbCBpdCBjYW4gZG86IHRoZQpyZW5kZXIgd2FzIGZpdmUg"
    "c3RyYWlnaHQgdGFwZXJlZCBzbGl2ZXJzIGZhbm5lZCBvdXQgZXZlbmx5IGZyb20gYSBiYXNlIGFzIHdpZGUKYXMgdGhlIHR1"
    "ZnQsIHdoaWNoIHJlYWRzIGFzIHBhcGVyLCBub3QgZ3Jhc3MuIEZvdXIgY2hhbmdlczoKCiAgLSBgZ2VvbWV0cnkuYWRkX2Js"
    "YWRlYCBidWlsZHMgZWFjaCBibGFkZSB3aXRoIHN0YXRpb25zIGFsb25nIGl0cyBsZW5ndGgsIHNvCiAgICBpdCBjYW4gQ1VS"
    "VkUuIFJlYWwgYmxhZGVzIGxlYXZlIHRoZSBncm91bmQgdmVydGljYWwgYW5kIGJlbmQgb3Zlci4KICAtIEEgc2hhcmVkIHdp"
    "bmQgZGlyZWN0aW9uIHdpdGggcGVyLWJsYWRlIHNjYXR0ZXIsIHNvIHRoZSBjbHVtcCBhZ3JlZXMgd2l0aAogICAgaXRzZWxm"
    "IGluc3RlYWQgb2Ygc3BsYXlpbmcgZXZlbmx5IGluIGV2ZXJ5IGRpcmVjdGlvbiAtLSBhbiBldmVuIGZhbiBpcyB0aGUKICAg"
    "IGd1aWRlJ3MgcnVsZSAyIHN0YXRlZCBhdCB0aGUgc2NhbGUgb2Ygb25lIGFzc2V0LgogIC0gQmxhZGUgbGVuZ3RocyBkcmF3"
    "biB3aXRoIGEgcG93ZXIgbGF3LCBzbyBhIGZldyBzdGFuZCB0YWxsIGFuZCBtb3N0IGFyZQogICAgc2hvcnQuIEEgdW5pZm9y"
    "bSBkcmF3IGdpdmVzIGZpdmUgYmxhZGVzIG9mIG5lYXJseSBlcXVhbCBoZWlnaHQsIHdoaWNoIGlzCiAgICB0aGUgc2luZ2xl"
    "IGxvdWRlc3QgcHJvY2VkdXJhbCB0ZWxsIGluIHRoZSBmaXJzdCByZW5kZXIuCiAgLSBCbGFkZXMgZW1lcmdlIGZyb20gYSBU"
    "SUdIVCBiYXNlIChhIHRlbnRoIG9mIHRoZSB0dWZ0IHdpZHRoLCBub3QgaGFsZiksIHNvCiAgICB0aGUgY2x1bXAgcmVhZHMg"
    "YXMgb25lIHBsYW50IHJhdGhlciB0aGFuIGZpdmUgdW5yZWxhdGVkIHNwaWtlcy4KCk1BVEVSSUFMIEtJTkQgSVMgREVMSUJF"
    "UkFURUxZIFVOU0tJTk5FRC4gYHZlZ2V0YXRpb25gIGhhcyBubyBza2luIHBhY2ssIHNvCmBtYWtlX21hdGVyaWFsYCBmYWxs"
    "cyBiYWNrIHRvIGEgZmxhdCBtYXRlcmlhbCBjYXJyeWluZyB0aGUgZ2Vub21lIGNvbG91ci4gVGhhdAppcyBpbnRlbnRpb25h"
    "bDogaW5oZXJpdGluZyBgY29uY3JldGVgIG9yIGB3b29kYCB3b3VsZCBwYWludCBhIHdlZWQgd2l0aCBhCmJ1aWxkaW5nJ3Mg"
    "c3VyZmFjZSB0cmVhdG1lbnQuIElmIGEgdmVnZXRhdGlvbiBwYWNrIGlzIGFkZGVkIGxhdGVyIHRoaXMgcGlja3MgaXQKdXAg"
    "d2l0aCBubyBjaGFuZ2UgaGVyZS4KIiIiCmZyb20gX19mdXR1cmVfXyBpbXBvcnQgYW5ub3RhdGlvbnMKCmltcG9ydCBtYXRo"
    "Cgpmcm9tIC4uYnB5bGF5ZXIgaW1wb3J0IGdlb21ldHJ5LCBtYXRlcmlhbHMKCgpkZWYgYnVpbGQocGxhbiwgc3RyZWFtcywg"
    "Y29sbGVjdGlvbik6CiAgICB3ID0gcGxhblsiZGltZW5zaW9ucyJdWyJ3aWR0aCJdCiAgICBkID0gcGxhblsiZGltZW5zaW9u"
    "cyJdWyJkZXB0aCJdCiAgICBoID0gcGxhblsiZGltZW5zaW9ucyJdWyJoZWlnaHQiXQogICAgYmV2ZWwsIHdlYXIgPSBwbGFu"
    "WyJiZXZlbCJdLCBwbGFuWyJ3ZWFyIl0KICAgIHJuZyA9IHN0cmVhbXMuc3RyZWFtKCJ3ZWFyIikKCiAgICBibGFkZXMgPSBt"
    "YXgoMiwgaW50KHBsYW5bInBhcmFtcyJdLmdldCgiYmxhZGVzIiwgNykpKQogICAgdGhpY2sgPSBmbG9hdChwbGFuWyJwYXJh"
    "bXMiXS5nZXQoImJsYWRlX3RoaWNrbmVzcyIsIDAuMDA2KSkKICAgICMgQmxhZGUgd2lkdGggYXQgdGhlIGJhc2UuIEEgYmxh"
    "ZGUgaXMgYSByaWJib24sIG5vdCBhIG5lZWRsZTogdGhlIGZpcnN0CiAgICAjIGtpdCdzIGJsYWRlcyB3ZXJlIGFzIHRoaW4g"
    "YXMgdGhleSB3ZXJlIGRlZXAsIHdoaWNoIGlzIHdoeSB0aGV5IHJlYWQgYXMKICAgICMgc2xpdmVycyByYXRoZXIgdGhhbiBs"
    "ZWF2ZXMuCiAgICBid2lkdGggPSBmbG9hdChwbGFuWyJwYXJhbXMiXS5nZXQoImJsYWRlX3dpZHRoIiwgdGhpY2sgKiAyLjIp"
    "KQogICAgc3RhdGlvbnMgPSBtYXgoMiwgaW50KHBsYW5bInBhcmFtcyJdLmdldCgic3RhdGlvbnMiLCA0KSkpCiAgICAjIEhv"
    "dyB0aWdodGx5IHRoZSBibGFkZXMgc2hhcmUgb25lIHJvb3QsIGFzIGEgZnJhY3Rpb24gb2YgdHVmdCB3aWR0aC4KICAgIHJv"
    "b3QgPSBmbG9hdChwbGFuWyJwYXJhbXMiXS5nZXQoInJvb3Rfc3ByZWFkIiwgMC4xMikpCiAgICAjIEhvdyBoYXJkIHRoZSBj"
    "bHVtcCBsZWFucywgYXMgYSBmcmFjdGlvbiBvZiBibGFkZSBoZWlnaHQsIGFuZCBob3cgZmFyCiAgICAjIGluZGl2aWR1YWwg"
    "YmxhZGVzIHN0cmF5IGZyb20gdGhhdCBkaXJlY3Rpb24gaW4gcmFkaWFucy4KICAgIGxlYW4gPSBmbG9hdChwbGFuWyJwYXJh"
    "bXMiXS5nZXQoImxlYW4iLCAwLjM0KSkKICAgIHNjYXR0ZXIgPSBmbG9hdChwbGFuWyJwYXJhbXMiXS5nZXQoImxlYW5fc2Nh"
    "dHRlciIsIDAuODUpKQoKICAgIHdpbmQgPSBybmcucmFuZG9tKCkgKiA2LjI4MzE4NTMKCiAgICBibSA9IGdlb21ldHJ5Lm5l"
    "d19ibSgpCiAgICBmb3IgaSBpbiByYW5nZShibGFkZXMpOgogICAgICAgICMgUG93ZXIgbGF3OiBtb3N0IGJsYWRlcyBzaG9y"
    "dCwgYSBmZXcgdGFsbC4gQSB1bmlmb3JtIGRyYXcgb3ZlcgogICAgICAgICMgMC41NS4uMS4wIC0tIHdoYXQgdGhlIGZpcnN0"
    "IHZlcnNpb24gZGlkIC0tIHByb2R1Y2VzIGZpdmUgYmxhZGVzIG9mCiAgICAgICAgIyBuZWFybHkgdGhlIHNhbWUgaGVpZ2h0"
    "LCBhbmQgZXF1YWwgaGVpZ2h0cyByZWFkIGFzIG1hbnVmYWN0dXJlZC4KICAgICAgICB1ID0gcm5nLnJhbmRvbSgpICoqIDEu"
    "OQogICAgICAgIGJoID0gaCAqICgwLjMyICsgMC42OCAqIHUpCiAgICAgICAgYW5nID0gd2luZCArIChybmcucmFuZG9tKCkg"
    "KiAyLjAgLSAxLjApICogc2NhdHRlcgogICAgICAgIGFtdCA9IGJoICogbGVhbiAqICgwLjUgKyBybmcucmFuZG9tKCkpCiAg"
    "ICAgICAgYmVuZCA9IChtYXRoLmNvcyhhbmcpICogYW10LCBtYXRoLnNpbihhbmcpICogYW10KQogICAgICAgIHJyID0gcm9v"
    "dCAqIChybmcucmFuZG9tKCkgKiogMC41KQogICAgICAgIHJhID0gcm5nLnJhbmRvbSgpICogNi4yODMxODUzCiAgICAgICAg"
    "YmFzZSA9IChtYXRoLmNvcyhyYSkgKiB3ICogcnIsIG1hdGguc2luKHJhKSAqIGQgKiByciwgMC4wKQogICAgICAgIHRhcGVy"
    "X2kgPSAxLjIgKyBybmcucmFuZG9tKCkgKiAwLjkKICAgICAgICBnZW9tZXRyeS5hZGRfYmxhZGUoYm0sIGJhc2UsIGJoLAog"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICBid2lkdGggKiAoMC43ICsgcm5nLnJhbmRvbSgpICogMC42KSwKICAgICAgICAg"
    "ICAgICAgICAgICAgICAgICAgdGhpY2sgKiAoMC43ICsgcm5nLnJhbmRvbSgpICogMC42KSwKICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICAgYmVuZD1iZW5kLCBzdGF0aW9ucz1zdGF0aW9ucywgdGFwZXI9dGFwZXJfaSwKICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICAgY3VybD1ybmcucmFuZG9tKCkgKiAwLjYpCgogICAgdHVmdCA9IGdlb21ldHJ5LmJtX3RvX29iamVjdChibSwg"
    "IkRyZXNzX1dlZWRUdWZ0IiwgY29sbGVjdGlvbiwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgYmV2ZWw9YmV2"
    "ZWwsIHRleGVsPTguMCwgcm5nPXJuZywgd2Vhcj13ZWFyKQogICAgbWF0ZXJpYWxzLmFzc2lnbihbdHVmdF0sIG1hdGVyaWFs"
    "cy5tYWtlX21hdGVyaWFsKAogICAgICAgIGYiTV9XZWVkX3twbGFuWydtYXRlcmlhbCddfSIsIHBsYW5bImNvbG9yIl0sIHBs"
    "YW5bIm1hdGVyaWFsIl0pKQoKICAgIHJldHVybiB7Im9iamVjdHMiOiBbdHVmdF0sICJjb2xsaXNpb25fYm94ZXMiOiBbXSwg"
    "ImF0dGFjaG1lbnRzIjoge319Cg=="
    ),
  },
  'zoo/zoo_keeper/recipes/litter_scrap.py': {
    "kind": 'replace',
    "pre_sha": '3dcb6e4b4cf5e26bc0d8db40b8ab16cdd8a1ae63844e5e920254835ff4d30278',
    "pre_bytes": 2023,
    "post_sha": '380e39cf985a73c3b6a9f1cdfde37c3a581f9ca425a0d0a8402ab40709201fa9',
    "post_bytes": 3223,
    "b64": (
    "IiIibGl0dGVyX3NjcmFwIHJlY2lwZTogZmxhdCBjcnVtcGxlZCBzY3JhcHMg4oCUIExheWVyIDMgbGl0dGVyLgoKVGhlIGd1"
    "aWRlIHBsYWNlcyB0cmFzaCAiYWdhaW5zdCB3YWxscyBvciB0cmFmZmljIGJvdW5kYXJpZXMiLCBzbyB0aGlzIHNwZWNpZXMK"
    "ZXhpc3RzIHRvIGJlIGEgc2VhbSBhbmQgZWRnZSBtYXJrZXIgcmF0aGVyIHRoYW4gYSBmaWVsZCBzY2F0dGVyLiBJdCBpcyB0"
    "aGUKZmxhdHRlc3QgdGhpbmcgaW4gdGhlIGtpdDogdGhlIGdlbm9tZSBjYXBzIGhlaWdodCBhdCAwLjAzIG0sIHdoaWNoIGlz"
    "IGluc2lkZQpgRkxVU0hfTSA9IDAuMDJgLWFkamFjZW50IHRlcnJpdG9yeSBpbiBgbG90L3NpdGVfc3RlcHMucHlgIGFuZCBu"
    "b3doZXJlIG5lYXIgdGhlCjAuMTE3IG0gYHVuYXNzaXN0ZWRfc3RlcF9tYXhgLCBzbyBpdCBjYW5ub3QgZXZlbiBiZSBhcmd1"
    "ZWQgYWJvdXQuCgpBIHNjcmFwIGlzIGEgdGhpbiBwbGF0ZSB3aXRoIGl0cyBUT1Agc3VyZmFjZSBkaXNwbGFjZWQgb25seSAt"
    "LSBhIGNydW1wbGUsIG5vdCBhCmx1bXAuIERpc3BsYWNpbmcgYm90aCBmYWNlcyB3b3VsZCB0aGlja2VuIGl0IGludG8gYSBw"
    "ZWJibGUgd2l0aCB0aGUgd3JvbmcKbWF0ZXJpYWwuCgpTSEFQRSwgU0VDT05EIFBBU1MuIFRoaXMgd2FzIHRoZSBiZXN0IG9m"
    "IHRoZSBmaXJzdCBraXQsIGFuZCB0aGUgcmVhc29uIGlzIHdvcnRoCnJlY29yZGluZyBiZWNhdXNlIGl0IGlzIHRoZSB3aG9s"
    "ZSBkaWFnbm9zaXMgaW4gb25lIHNwZWNpZXM6IGNydW1wbGluZyB0aGUgdG9wCnZlcnRzIG9mIGEgYm94IHdhcyB0aGUgT05M"
    "WSBvcGVyYXRpb24gaW4gdGhlIGZpcnN0IGZvdXIgcmVjaXBlcyB0aGF0IHByb2R1Y2VkCm5vbi1jb3BsYW5hciBmYWNlcywg"
    "c28gaXQgd2FzIHRoZSBvbmx5IG9uZSB3aG9zZSBzaWxob3VldHRlIGFjdHVhbGx5IG1vdmVkLgpJdCB3YXMgc3RpbGwgd29y"
    "a2luZyB3aXRoIGZvdXIgY29ybmVycywgdGhvdWdoIC0tIG9uZSBxdWFkLCBmb3VyIHZlcnRpY2VzLCBhbmQKdGhlcmVmb3Jl"
    "IGV4YWN0bHkgb25lIGZvbGQuIFN1YmRpdmlkaW5nIHRoZSBwbGF0ZSBmaXJzdCBnaXZlcyB0aGUgY3J1bXBsZQppbnRlcmlv"
    "ciB2ZXJ0aWNlcyB0byB3b3JrIHdpdGgsIHNvIGEgc2NyYXAgY2FuIGZvbGQgbW9yZSB0aGFuIG9uY2U7IG1lYXN1cmVkLAp0"
    "aGF0IGlzIHRoZSBkaWZmZXJlbmNlIGJldHdlZW4gNCBmYWNpbmcgZGlyZWN0aW9ucyBhbmQgZW5vdWdoIHRvIHJlYWQgYXMg"
    "cGFwZXIuClRoZSBjb3N0IGlzIHNtYWxsIGJlY2F1c2UgdGhlIHBsYXRlIGlzIHF1YWRzIGFuZCBpdCBzdGFydHMgYXQgMjQg"
    "dHJpYW5nbGVzCmFnYWluc3QgYSAyMDAgYnVkZ2V0LgoiIiIKZnJvbSBfX2Z1dHVyZV9fIGltcG9ydCBhbm5vdGF0aW9ucwoK"
    "ZnJvbSAuLmJweWxheWVyIGltcG9ydCBnZW9tZXRyeSwgbWF0ZXJpYWxzCgoKZGVmIGJ1aWxkKHBsYW4sIHN0cmVhbXMsIGNv"
    "bGxlY3Rpb24pOgogICAgdyA9IHBsYW5bImRpbWVuc2lvbnMiXVsid2lkdGgiXQogICAgZCA9IHBsYW5bImRpbWVuc2lvbnMi"
    "XVsiZGVwdGgiXQogICAgaCA9IHBsYW5bImRpbWVuc2lvbnMiXVsiaGVpZ2h0Il0KICAgIGJldmVsLCB3ZWFyID0gcGxhblsi"
    "YmV2ZWwiXSwgcGxhblsid2VhciJdCiAgICBybmcgPSBzdHJlYW1zLnN0cmVhbSgid2VhciIpCgogICAgY291bnQgPSBtYXgo"
    "MSwgaW50KHBsYW5bInBhcmFtcyJdLmdldCgic2NyYXBzIiwgMikpKQogICAgY3J1bXBsZSA9IGZsb2F0KHBsYW5bInBhcmFt"
    "cyJdLmdldCgiY3J1bXBsZSIsIDAuNTUpKQogICAgIyBPbmUgY3V0IHR1cm5zIHRoZSBwbGF0ZSdzIDQgY29ybmVycyBpbnRv"
    "IDkgdmVydGljZXMsIHNvIHRoZSBjcnVtcGxlIGhhcwogICAgIyBzb21ld2hlcmUgdG8gZm9sZC4gVHdvIGlzIGFmZm9yZGFi"
    "bGUgaGVyZSBhbmQgcmVhZHMgYXMgdGlnaHRlciBjcmVhc2luZy4KICAgIGN1dHMgPSBtYXgoMCwgaW50KHBsYW5bInBhcmFt"
    "cyJdLmdldCgiY3V0cyIsIDEpKSkKCiAgICBibSA9IGdlb21ldHJ5Lm5ld19ibSgpCiAgICBmb3IgaSBpbiByYW5nZShjb3Vu"
    "dCk6CiAgICAgICAgZiA9IDAuNSArIHJuZy5yYW5kb20oKSAqIDAuNQogICAgICAgIHN4LCBzeSA9IHcgKiBmLCBkICogZgog"
    "ICAgICAgIHZlcnRzID0gZ2VvbWV0cnkuYWRkX2JveChibSwgKDAuMCwgMC4wLCAwLjApLCAoc3gsIHN5LCBoKSkKICAgICAg"
    "ICB2ZXJ0cyA9IGdlb21ldHJ5LnN1YmRpdmlkZShibSwgdmVydHMsIGN1dHMpCiAgICAgICAgdG9wID0gW3YgZm9yIHYgaW4g"
    "dmVydHMgaWYgdi5pc192YWxpZCBhbmQgdi5jby56ID4gMC4wXQogICAgICAgIGZvciB2IGluIHRvcDoKICAgICAgICAgICAg"
    "di5jby56ICs9IHJuZy5yYW5kb20oKSAqIGggKiBjcnVtcGxlCiAgICAgICAgICAgIHYuY28ueCArPSAocm5nLnJhbmRvbSgp"
    "ICogMi4wIC0gMS4wKSAqIHN4ICogMC4xMgogICAgICAgICAgICB2LmNvLnkgKz0gKHJuZy5yYW5kb20oKSAqIDIuMCAtIDEu"
    "MCkgKiBzeSAqIDAuMTIKICAgICAgICAjIEEgc2NyYXAgbGllcyBPTiB0aGUgc3VyZmFjZTsgdGhlIGJhc2Ugd2FzIGFscmVh"
    "ZHkgZmxhdCwgdGhpcyBqdXN0CiAgICAgICAgIyBndWFyYW50ZWVzIHRoZSBzdWJkaXZpc2lvbiBkaWQgbm90IGxlYXZlIGl0"
    "IHdhdnkuCiAgICAgICAgYmFzZV96ID0gZ2VvbWV0cnkuZmxhdHRlbl9iYXNlKHZlcnRzLCB0b2xfZnJhYz0wLjA1KQogICAg"
    "ICAgIG94ID0gKHJuZy5yYW5kb20oKSAqIDIuMCAtIDEuMCkgKiB3ICogMC42CiAgICAgICAgb3kgPSAocm5nLnJhbmRvbSgp"
    "ICogMi4wIC0gMS4wKSAqIGQgKiAwLjYKICAgICAgICBnZW9tZXRyeS5wbGFjZSh2ZXJ0cywgKG94LCBveSwgLWJhc2Vfeiks"
    "CiAgICAgICAgICAgICAgICAgICAgICAgcm90X3o9cm5nLnJhbmRvbSgpICogNi4yODMxODUzKQoKICAgIHNjcmFwcyA9IGdl"
    "b21ldHJ5LmJtX3RvX29iamVjdChibSwgIkRyZXNzX0xpdHRlclNjcmFwIiwgY29sbGVjdGlvbiwKICAgICAgICAgICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICBiZXZlbD1iZXZlbCwgdGV4ZWw9MTAuMCwgcm5nPXJuZywgd2Vhcj13ZWFyKQogICAgbWF0"
    "ZXJpYWxzLmFzc2lnbihbc2NyYXBzXSwgbWF0ZXJpYWxzLm1ha2VfbWF0ZXJpYWwoCiAgICAgICAgZiJNX0xpdHRlcl97cGxh"
    "blsnbWF0ZXJpYWwnXX0iLCBwbGFuWyJjb2xvciJdLCBwbGFuWyJtYXRlcmlhbCJdKSkKCiAgICByZXR1cm4geyJvYmplY3Rz"
    "IjogW3NjcmFwc10sICJjb2xsaXNpb25fYm94ZXMiOiBbXSwgImF0dGFjaG1lbnRzIjoge319Cg=="
    ),
  },
  'zoo/zoo_keeper/genome/species/pebble.json': {
    "kind": 'replace',
    "pre_sha": '840e14e87327f1fbfdbe47a35fffda73c534fdfc8a955a67cb485c4fc4695a42',
    "pre_bytes": 1924,
    "post_sha": 'd6fdb3bfc8e59e0ab5ee5918c4af2e47ddf8094d741d54ebcd1ba5fbaea28002',
    "post_bytes": 1922,
    "b64": (
    "ewogInNwZWNpZXMiOiAicGViYmxlIiwKICJ2ZXJzaW9uIjogMSwKICJsaWNlbnNlIjogewogICJjb25zdHJ1Y3Rpb25fa25v"
    "d2xlZGdlIjogIkNDMCIsCiAgIm5vdGVzIjogIk9yaWdpbmFsIHByb2NlZHVyYWwgY29uc3RydWN0aW9uLiBMYXllciAzIG1p"
    "Y3JvIHJlbGllZjogYSBmZXcgZmFjZXRlZCBzdG9uZXMgaGFsZi1zdW5rIGludG8gYSBzdXJmYWNlLiBIZWlnaHQgbWF4IGlz"
    "IDAuMTAgbSwgdW5kZXIgdGhlIDAuMTE3IG0gdW5hc3Npc3RlZF9zdGVwX21heCBkZXJpdmVkIGluIGxvdC9zaXRlX3N0ZXBz"
    "LnB5IGZvciB0aGlzIHN0YWNrJ3MgMC40IG0gY2Fwc3VsZSAtLSBzbyBhIGJvZHkgc3RlcHMgb3ZlciBpdCBhbnl3YXkgYW5k"
    "IHBhc3NpbmcgdGhyb3VnaCBpdCBpcyBub3QgYSBmYWxzZSB0cmF2ZXJzYWwgcHJvbWlzZS4gQ29sbGlzaW9ubGVzcyBieSBj"
    "b25zdHJ1Y3Rpb24uIFNlZSBkb2NzL1NVUkZBQ0VfRFJFU1NJTkcubWQuIFRSQU5TUEFSRU5DWTogb3BhcXVlLiIKIH0sCiAi"
    "Y29sbGlzaW9uIjogZmFsc2UsCiAidHJhbnNwYXJlbmN5IjogIm9wYXF1ZSIsCiAia2V5d29yZHMiOiBbCiAgInBlYmJsZSIs"
    "CiAgInN0b25lIiwKICAic3VyZmFjZSBkcmVzc2luZyIsCiAgIm1pY3JvIHJlbGllZiIsCiAgImdyb3VuZCBjbHV0dGVyIgog"
    "XSwKICJtYXRjaF9wcmlvcml0eSI6IC0xLAogImRpbWVuc2lvbnMiOiB7CiAgIndpZHRoIjogewogICAibWluIjogMC4wNCwK"
    "ICAgIm1heCI6IDAuMywKICAgImRlZmF1bHQiOiAwLjE0CiAgfSwKICAiZGVwdGgiOiB7CiAgICJtaW4iOiAwLjA0LAogICAi"
    "bWF4IjogMC4zLAogICAiZGVmYXVsdCI6IDAuMTIKICB9LAogICJoZWlnaHQiOiB7CiAgICJtaW4iOiAwLjAxLAogICAibWF4"
    "IjogMC4xLAogICAiZGVmYXVsdCI6IDAuMDUKICB9CiB9LAogInBhcnRzIjogWwogICJEcmVzc19QZWJibGUiCiBdLAogInBh"
    "cmFtcyI6IHsKICAic3RvbmVzIjogMywKICAiZmFjZXRzX3UiOiA4LAogICJmYWNldHNfdiI6IDUsCiAgInNpbmsiOiAwLjE1"
    "LAogICJsb2JlcyI6IDMKIH0sCiAibWF0ZXJpYWxzIjogewogICJkZWZhdWx0IjogImdyYXZlbCIsCiAgIm9wdGlvbnMiOiBb"
    "CiAgICJncmF2ZWwiLAogICAiY29uY3JldGUiLAogICAiZGlydCIKICBdCiB9LAogImJ1ZGdldHMiOiB7CiAgInRyaXNfbWF4"
    "IjogMjYwCiB9LAogImF0dGFjaG1lbnRzIjogW10sCiAic3R5bGVzIjogewogICJkZWZhdWx0IjogewogICAibWF0ZXJpYWwi"
    "OiAiZ3JhdmVsIiwKICAgImNvbG9yIjogWwogICAgMC41NiwKICAgIDAuNTUsCiAgICAwLjUzCiAgIF0sCiAgICJ3ZWFyIjog"
    "MC4xNSwKICAgImJldmVsIjogMC4wCiAgfSwKICAiZGVsY28iOiB7CiAgICJtYXRlcmlhbCI6ICJncmF2ZWwiLAogICAiY29s"
    "b3IiOiBbCiAgICAwLjUsCiAgICAwLjQ5LAogICAgMC40NgogICBdLAogICAid2VhciI6IDAuMzUsCiAgICJiZXZlbCI6IDAu"
    "MCwKICAgImFtYmllbnQiOiAwLjA1CiAgfSwKICAiY2VudGVyX2NpdHkiOiB7CiAgICJtYXRlcmlhbCI6ICJncmF2ZWwiLAog"
    "ICAiY29sb3IiOiBbCiAgICAwLjU1LAogICAgMC41NSwKICAgIDAuNTYKICAgXSwKICAgIndlYXIiOiAwLjIsCiAgICJiZXZl"
    "bCI6IDAuMCwKICAgImFtYmllbnQiOiAwLjA1CiAgfSwKICAiaW5kdXN0cmlhbF9mbGF0cyI6IHsKICAgIm1hdGVyaWFsIjog"
    "ImdyYXZlbCIsCiAgICJjb2xvciI6IFsKICAgIDAuNDcsCiAgICAwLjQ1LAogICAgMC40NAogICBdLAogICAid2VhciI6IDAu"
    "NTcsCiAgICJiZXZlbCI6IDAuMCwKICAgImFtYmllbnQiOiAwLjA1CiAgfSwKICAicm9ja2F5IjogewogICAibWF0ZXJpYWwi"
    "OiAiZ3JhdmVsIiwKICAgImNvbG9yIjogWwogICAgMC41MywKICAgIDAuNTQsCiAgICAwLjU2CiAgIF0sCiAgICJ3ZWFyIjog"
    "MC4yOSwKICAgImJldmVsIjogMC4wLAogICAiYW1iaWVudCI6IDAuMDUKICB9CiB9Cn0="
    ),
  },
  'zoo/zoo_keeper/genome/species/rubble_frag.json': {
    "kind": 'replace',
    "pre_sha": 'a72f017d2fb4ff8401ee3d157040db9360ff2e59f33e4b9c2434dcbe9c8a63e4',
    "pre_bytes": 1974,
    "post_sha": '71e567c6816fd291c10a253760ba3c215a13c394645177e96e3b6b5df016e62a',
    "post_bytes": 1976,
    "b64": (
    "ewogInNwZWNpZXMiOiAicnViYmxlX2ZyYWciLAogInZlcnNpb24iOiAxLAogImxpY2Vuc2UiOiB7CiAgImNvbnN0cnVjdGlv"
    "bl9rbm93bGVkZ2UiOiAiQ0MwIiwKICAibm90ZXMiOiAiT3JpZ2luYWwgcHJvY2VkdXJhbCBjb25zdHJ1Y3Rpb24uIExheWVy"
    "IDMgbG93IGRlYnJpczogYW5ndWxhciBicm9rZW4gZnJhZ21lbnRzLCBidWlsdCBmcm9tIGppdHRlcmVkIGJveGVzIHNvIHRo"
    "ZSBmcmFjdHVyZSByZWFkcy4gUGxhY2VkIGF0IGRhbWFnZSBhcyBhbiBlbnZpcm9ubWVudGFsIGNhdXNlIG1hcmtlci4gSGVp"
    "Z2h0IG1heCBpcyAwLjEwIG0sIHVuZGVyIHRoZSAwLjExNyBtIHVuYXNzaXN0ZWRfc3RlcF9tYXggZGVyaXZlZCBpbiBsb3Qv"
    "c2l0ZV9zdGVwcy5weSBmb3IgdGhpcyBzdGFjaydzIDAuNCBtIGNhcHN1bGUgLS0gc28gYSBib2R5IHN0ZXBzIG92ZXIgaXQg"
    "YW55d2F5IGFuZCBwYXNzaW5nIHRocm91Z2ggaXQgaXMgbm90IGEgZmFsc2UgdHJhdmVyc2FsIHByb21pc2UuIENvbGxpc2lv"
    "bmxlc3MgYnkgY29uc3RydWN0aW9uLiBTZWUgZG9jcy9TVVJGQUNFX0RSRVNTSU5HLm1kLiBUUkFOU1BBUkVOQ1k6IG9wYXF1"
    "ZS4iCiB9LAogImNvbGxpc2lvbiI6IGZhbHNlLAogInRyYW5zcGFyZW5jeSI6ICJvcGFxdWUiLAogImtleXdvcmRzIjogWwog"
    "ICJydWJibGUiLAogICJkZWJyaXMiLAogICJmcmFnbWVudCIsCiAgInN1cmZhY2UgZHJlc3NpbmciLAogICJkYW1hZ2UiCiBd"
    "LAogIm1hdGNoX3ByaW9yaXR5IjogLTEsCiAiZGltZW5zaW9ucyI6IHsKICAid2lkdGgiOiB7CiAgICJtaW4iOiAwLjA1LAog"
    "ICAibWF4IjogMC4zNSwKICAgImRlZmF1bHQiOiAwLjE2CiAgfSwKICAiZGVwdGgiOiB7CiAgICJtaW4iOiAwLjA1LAogICAi"
    "bWF4IjogMC4zNSwKICAgImRlZmF1bHQiOiAwLjE0CiAgfSwKICAiaGVpZ2h0IjogewogICAibWluIjogMC4wMSwKICAgIm1h"
    "eCI6IDAuMSwKICAgImRlZmF1bHQiOiAwLjA2CiAgfQogfSwKICJwYXJ0cyI6IFsKICAiRHJlc3NfUnViYmxlRnJhZyIKIF0s"
    "CiAicGFyYW1zIjogewogICJjaHVua3MiOiA0LAogICJjdXRzIjogNCwKICAicm91Z2giOiAwLjMKIH0sCiAibWF0ZXJpYWxz"
    "IjogewogICJkZWZhdWx0IjogImdyYXZlbCIsCiAgIm9wdGlvbnMiOiBbCiAgICJncmF2ZWwiLAogICAiY29uY3JldGUiLAog"
    "ICAiYnJpY2siLAogICAiZGlydCIKICBdCiB9LAogImJ1ZGdldHMiOiB7CiAgInRyaXNfbWF4IjogMzIwCiB9LAogImF0dGFj"
    "aG1lbnRzIjogW10sCiAic3R5bGVzIjogewogICJkZWZhdWx0IjogewogICAibWF0ZXJpYWwiOiAiZ3JhdmVsIiwKICAgImNv"
    "bG9yIjogWwogICAgMC41NiwKICAgIDAuNTUsCiAgICAwLjUzCiAgIF0sCiAgICJ3ZWFyIjogMC4xNSwKICAgImJldmVsIjog"
    "MC4wCiAgfSwKICAiZGVsY28iOiB7CiAgICJtYXRlcmlhbCI6ICJncmF2ZWwiLAogICAiY29sb3IiOiBbCiAgICAwLjUsCiAg"
    "ICAwLjQ5LAogICAgMC40NgogICBdLAogICAid2VhciI6IDAuMzUsCiAgICJiZXZlbCI6IDAuMCwKICAgImFtYmllbnQiOiAw"
    "LjA1CiAgfSwKICAiY2VudGVyX2NpdHkiOiB7CiAgICJtYXRlcmlhbCI6ICJncmF2ZWwiLAogICAiY29sb3IiOiBbCiAgICAw"
    "LjU1LAogICAgMC41NSwKICAgIDAuNTYKICAgXSwKICAgIndlYXIiOiAwLjIsCiAgICJiZXZlbCI6IDAuMCwKICAgImFtYmll"
    "bnQiOiAwLjA1CiAgfSwKICAiaW5kdXN0cmlhbF9mbGF0cyI6IHsKICAgIm1hdGVyaWFsIjogImdyYXZlbCIsCiAgICJjb2xv"
    "ciI6IFsKICAgIDAuNDcsCiAgICAwLjQ1LAogICAgMC40NAogICBdLAogICAid2VhciI6IDAuNTcsCiAgICJiZXZlbCI6IDAu"
    "MCwKICAgImFtYmllbnQiOiAwLjA1CiAgfSwKICAicm9ja2F5IjogewogICAibWF0ZXJpYWwiOiAiZ3JhdmVsIiwKICAgImNv"
    "bG9yIjogWwogICAgMC41MywKICAgIDAuNTQsCiAgICAwLjU2CiAgIF0sCiAgICJ3ZWFyIjogMC4yOSwKICAgImJldmVsIjog"
    "MC4wLAogICAiYW1iaWVudCI6IDAuMDUKICB9CiB9Cn0="
    ),
  },
  'zoo/zoo_keeper/genome/species/weed_tuft.json': {
    "kind": 'replace',
    "pre_sha": '9ee479607aa6c6a7301f75e3c20b089be74eebd7183de6b633b2b528b6fe587c',
    "pre_bytes": 2380,
    "post_sha": 'd118f64656a78b23bc37807fd4d07d973cffe455378298eff3aff8824b1949ae',
    "post_bytes": 2483,
    "b64": (
    "ewogInNwZWNpZXMiOiAid2VlZF90dWZ0IiwKICJ2ZXJzaW9uIjogMSwKICJsaWNlbnNlIjogewogICJjb25zdHJ1Y3Rpb25f"
    "a25vd2xlZGdlIjogIkNDMCIsCiAgIm5vdGVzIjogIk9yaWdpbmFsIHByb2NlZHVyYWwgY29uc3RydWN0aW9uLiBMYXllciAz"
    "IGdyb3VuZCBjb3ZlcjogYSBjbHVtcCBvZiB0YXBlcmVkIGJsYWRlcyBtYXJraW5nIGNyYWNrcywgbW9pc3R1cmUsIHNoYWRl"
    "IGFuZCBlZGdlcy4gU29saWQgdGFwZXJlZCBzcGlrZXMgcmF0aGVyIHRoYW4gY3Jvc3NlZCBxdWFkcyAtLSBhIHNpbmdsZS1z"
    "aWRlZCBwbGFuZSBpcyB0aGUgY2xhc3Mgb2Ygc3VyZmFjZSB0aGlzIHBpcGVsaW5lIGFscmVhZHkgc3BlbnQgYSBzZXNzaW9u"
    "IGNoYXNpbmcuIEhlaWdodCBtYXggaXMgMC4xMCBtLCB1bmRlciB0aGUgMC4xMTcgbSB1bmFzc2lzdGVkX3N0ZXBfbWF4IGRl"
    "cml2ZWQgaW4gbG90L3NpdGVfc3RlcHMucHkgZm9yIHRoaXMgc3RhY2sncyAwLjQgbSBjYXBzdWxlIC0tIHNvIGEgYm9keSBz"
    "dGVwcyBvdmVyIGl0IGFueXdheSBhbmQgcGFzc2luZyB0aHJvdWdoIGl0IGlzIG5vdCBhIGZhbHNlIHRyYXZlcnNhbCBwcm9t"
    "aXNlLiBDb2xsaXNpb25sZXNzIGJ5IGNvbnN0cnVjdGlvbi4gU2VlIGRvY3MvU1VSRkFDRV9EUkVTU0lORy5tZC4gVFJBTlNQ"
    "QVJFTkNZOiBvcGFxdWUuIFNvbGlkIHRhcGVyZWQgYmxhZGVzLCBubyBhbHBoYSAtLSB0aGUgZmlyc3Qga2l0IGlzIG9wYXF1"
    "ZSBlbmQgdG8gZW5kIHNvIGRlbnNpdHkgYW5kIGNvdmVyYWdlIGNhbiBiZSB0dW5lZCB3aXRob3V0IG92ZXJkcmF3IG9yIHNv"
    "cnQgb3JkZXIgYXMgY29uZm91bmRzLiBBbiBhbHBoYV9jdXRvdXQgY2FyZCB2YXJpYW50IGlzIHRoZSBpbnRlbmRlZCBuZXh0"
    "IHN0ZXAgZm9yIGRlbnNlciBmb2xpYWdlLCBwZXIgJ2NvdmVyYWdlIGZpcnN0LCBhbHBoYSBjdXRvdXRzIHNlY29uZCwgdHJ1"
    "ZSB0cmFuc3BhcmVuY3kgb25seSB3aGVuIHRoZSBtYXRlcmlhbCBjYWxscyBmb3IgaXQnLiIKIH0sCiAiY29sbGlzaW9uIjog"
    "ZmFsc2UsCiAidHJhbnNwYXJlbmN5IjogIm9wYXF1ZSIsCiAia2V5d29yZHMiOiBbCiAgIndlZWQiLAogICJncmFzcyIsCiAg"
    "InR1ZnQiLAogICJncm91bmQgY292ZXIiLAogICJzdXJmYWNlIGRyZXNzaW5nIiwKICAiZ3Jvd3RoIgogXSwKICJtYXRjaF9w"
    "cmlvcml0eSI6IC0xLAogImRpbWVuc2lvbnMiOiB7CiAgIndpZHRoIjogewogICAibWluIjogMC4wNSwKICAgIm1heCI6IDAu"
    "MywKICAgImRlZmF1bHQiOiAwLjEyCiAgfSwKICAiZGVwdGgiOiB7CiAgICJtaW4iOiAwLjA1LAogICAibWF4IjogMC4zLAog"
    "ICAiZGVmYXVsdCI6IDAuMTIKICB9LAogICJoZWlnaHQiOiB7CiAgICJtaW4iOiAwLjAyLAogICAibWF4IjogMC4xLAogICAi"
    "ZGVmYXVsdCI6IDAuMDgKICB9CiB9LAogInBhcnRzIjogWwogICJEcmVzc19XZWVkVHVmdCIKIF0sCiAicGFyYW1zIjogewog"
    "ICJibGFkZXMiOiA3LAogICJibGFkZV90aGlja25lc3MiOiAwLjAwNSwKICAiYmxhZGVfd2lkdGgiOiAwLjAxMSwKICAic3Rh"
    "dGlvbnMiOiA0LAogICJyb290X3NwcmVhZCI6IDAuMTIsCiAgImxlYW4iOiAwLjM0LAogICJsZWFuX3NjYXR0ZXIiOiAwLjg1"
    "CiB9LAogIm1hdGVyaWFscyI6IHsKICAiZGVmYXVsdCI6ICJ2ZWdldGF0aW9uIiwKICAib3B0aW9ucyI6IFsKICAgInZlZ2V0"
    "YXRpb24iCiAgXQogfSwKICJidWRnZXRzIjogewogICJ0cmlzX21heCI6IDMwMAogfSwKICJhdHRhY2htZW50cyI6IFtdLAog"
    "InN0eWxlcyI6IHsKICAiZGVmYXVsdCI6IHsKICAgIm1hdGVyaWFsIjogInZlZ2V0YXRpb24iLAogICAiY29sb3IiOiBbCiAg"
    "ICAwLjMyLAogICAgMC40LAogICAgMC4yMgogICBdLAogICAid2VhciI6IDAuMiwKICAgImJldmVsIjogMC4wCiAgfSwKICAi"
    "ZGVsY28iOiB7CiAgICJtYXRlcmlhbCI6ICJ2ZWdldGF0aW9uIiwKICAgImNvbG9yIjogWwogICAgMC4zLAogICAgMC4zOCwK"
    "ICAgIDAuMgogICBdLAogICAid2VhciI6IDAuMywKICAgImJldmVsIjogMC4wLAogICAiYW1iaWVudCI6IDAuMDUKICB9LAog"
    "ICJjZW50ZXJfY2l0eSI6IHsKICAgIm1hdGVyaWFsIjogInZlZ2V0YXRpb24iLAogICAiY29sb3IiOiBbCiAgICAwLjI4LAog"
    "ICAgMC4zNCwKICAgIDAuMjEKICAgXSwKICAgIndlYXIiOiAwLjM1LAogICAiYmV2ZWwiOiAwLjAsCiAgICJhbWJpZW50Ijog"
    "MC4wNQogIH0sCiAgImluZHVzdHJpYWxfZmxhdHMiOiB7CiAgICJtYXRlcmlhbCI6ICJ2ZWdldGF0aW9uIiwKICAgImNvbG9y"
    "IjogWwogICAgMC4zMSwKICAgIDAuMzMsCiAgICAwLjE5CiAgIF0sCiAgICJ3ZWFyIjogMC41NSwKICAgImJldmVsIjogMC4w"
    "LAogICAiYW1iaWVudCI6IDAuMDUKICB9LAogICJyb2NrYXkiOiB7CiAgICJtYXRlcmlhbCI6ICJ2ZWdldGF0aW9uIiwKICAg"
    "ImNvbG9yIjogWwogICAgMC4yOSwKICAgIDAuMzcsCiAgICAwLjIzCiAgIF0sCiAgICJ3ZWFyIjogMC4zMiwKICAgImJldmVs"
    "IjogMC4wLAogICAiYW1iaWVudCI6IDAuMDUKICB9CiB9Cn0="
    ),
  },
  'zoo/zoo_keeper/genome/species/litter_scrap.json': {
    "kind": 'replace',
    "pre_sha": '8d8d60c4fb5acb1a6c0fa4eeb1f3e258364dd0536ec0a5cf72974e5d5346b1be',
    "pre_bytes": 1742,
    "post_sha": '9d9dce7335e28471c097e72377526302f3251b23647302a2a2c575d584595d3c',
    "post_bytes": 1754,
    "b64": (
    "ewogInNwZWNpZXMiOiAibGl0dGVyX3NjcmFwIiwKICJ2ZXJzaW9uIjogMSwKICJsaWNlbnNlIjogewogICJjb25zdHJ1Y3Rp"
    "b25fa25vd2xlZGdlIjogIkNDMCIsCiAgIm5vdGVzIjogIk9yaWdpbmFsIHByb2NlZHVyYWwgY29uc3RydWN0aW9uLiBMYXll"
    "ciAzIGxpdHRlcjogZmxhdCBjcnVtcGxlZCBzY3JhcHMgZm9yIHdhbGwgYmFzZXMgYW5kIHRyYWZmaWMgZWRnZXMuIEhlaWdo"
    "dCBtYXggaXMgMC4wMyBtIC0tIG5vd2hlcmUgbmVhciB0aGUgMC4xMTcgbSB1bmFzc2lzdGVkX3N0ZXBfbWF4LCBzbyBpdCBj"
    "YW5ub3QgYmUgYXJndWVkIGFib3V0LiBDb2xsaXNpb25sZXNzIGJ5IGNvbnN0cnVjdGlvbi4gU2VlIGRvY3MvU1VSRkFDRV9E"
    "UkVTU0lORy5tZC4gVFJBTlNQQVJFTkNZOiBvcGFxdWUuIgogfSwKICJjb2xsaXNpb24iOiBmYWxzZSwKICJ0cmFuc3BhcmVu"
    "Y3kiOiAib3BhcXVlIiwKICJrZXl3b3JkcyI6IFsKICAibGl0dGVyIiwKICAidHJhc2giLAogICJwYXBlciIsCiAgInNjcmFw"
    "IiwKICAic3VyZmFjZSBkcmVzc2luZyIKIF0sCiAibWF0Y2hfcHJpb3JpdHkiOiAtMSwKICJkaW1lbnNpb25zIjogewogICJ3"
    "aWR0aCI6IHsKICAgIm1pbiI6IDAuMDQsCiAgICJtYXgiOiAwLjMsCiAgICJkZWZhdWx0IjogMC4xMgogIH0sCiAgImRlcHRo"
    "IjogewogICAibWluIjogMC4wNCwKICAgIm1heCI6IDAuMywKICAgImRlZmF1bHQiOiAwLjEKICB9LAogICJoZWlnaHQiOiB7"
    "CiAgICJtaW4iOiAwLjAwNCwKICAgIm1heCI6IDAuMDMsCiAgICJkZWZhdWx0IjogMC4wMTIKICB9CiB9LAogInBhcnRzIjog"
    "WwogICJEcmVzc19MaXR0ZXJTY3JhcCIKIF0sCiAicGFyYW1zIjogewogICJzY3JhcHMiOiAyLAogICJjcnVtcGxlIjogMC41"
    "NSwKICAiY3V0cyI6IDEKIH0sCiAibWF0ZXJpYWxzIjogewogICJkZWZhdWx0IjogInBhcGVyIiwKICAib3B0aW9ucyI6IFsK"
    "ICAgInBhcGVyIiwKICAgInBsYXN0aWMiCiAgXQogfSwKICJidWRnZXRzIjogewogICJ0cmlzX21heCI6IDIwMAogfSwKICJh"
    "dHRhY2htZW50cyI6IFtdLAogInN0eWxlcyI6IHsKICAiZGVmYXVsdCI6IHsKICAgIm1hdGVyaWFsIjogInBhcGVyIiwKICAg"
    "ImNvbG9yIjogWwogICAgMC43MiwKICAgIDAuNywKICAgIDAuNjUKICAgXSwKICAgIndlYXIiOiAwLjQsCiAgICJiZXZlbCI6"
    "IDAuMAogIH0sCiAgImRlbGNvIjogewogICAibWF0ZXJpYWwiOiAicGFwZXIiLAogICAiY29sb3IiOiBbCiAgICAwLjY4LAog"
    "ICAgMC42NiwKICAgIDAuNgogICBdLAogICAid2VhciI6IDAuNTUsCiAgICJiZXZlbCI6IDAuMCwKICAgImFtYmllbnQiOiAw"
    "LjA1CiAgfSwKICAiY2VudGVyX2NpdHkiOiB7CiAgICJtYXRlcmlhbCI6ICJwYXBlciIsCiAgICJjb2xvciI6IFsKICAgIDAu"
    "NzUsCiAgICAwLjc0LAogICAgMC43MQogICBdLAogICAid2VhciI6IDAuMzUsCiAgICJiZXZlbCI6IDAuMCwKICAgImFtYmll"
    "bnQiOiAwLjA1CiAgfSwKICAiaW5kdXN0cmlhbF9mbGF0cyI6IHsKICAgIm1hdGVyaWFsIjogInBhcGVyIiwKICAgImNvbG9y"
    "IjogWwogICAgMC42MiwKICAgIDAuNiwKICAgIDAuNTUKICAgXSwKICAgIndlYXIiOiAwLjcsCiAgICJiZXZlbCI6IDAuMCwK"
    "ICAgImFtYmllbnQiOiAwLjA1CiAgfSwKICAicm9ja2F5IjogewogICAibWF0ZXJpYWwiOiAicGFwZXIiLAogICAiY29sb3Ii"
    "OiBbCiAgICAwLjcsCiAgICAwLjY5LAogICAgMC42NgogICBdLAogICAid2VhciI6IDAuNSwKICAgImJldmVsIjogMC4wLAog"
    "ICAiYW1iaWVudCI6IDAuMDUKICB9CiB9Cn0="
    ),
  },
  'zoo/tools/preview_specimen.py': {
    "kind": 'replace',
    "pre_sha": '596a43661ad63d5dfda51e8d6819d59513be5d3af4cb50b6403158d65a8a494f',
    "pre_bytes": 4229,
    "post_sha": '0d36a978b06608e86ac2ea9a13e0efcaf625f92f929db5f39f56279b69da6488',
    "post_bytes": 9699,
    "b64": (
    "IiIiSGVhZGxlc3MgYnVpbGQgKyByZW5kZXIgb2Ygb25lIFpvbyBzcGVjaW1lbiDigJQgYSBxdWljayB2aXN1YWwgY2hlY2su"
    "CgpSdW4gaW5zaWRlIEJsZW5kZXIgKHNlZSB0b29scy9wcmV2aWV3X2RyZXNzaW5nLnBzMSk6CgogICAgYmxlbmRlciAtLWJh"
    "Y2tncm91bmQgLS1weXRob24gdG9vbHMvcHJldmlld19zcGVjaW1lbi5weSAtLSBcCiAgICAgICAgLS1wcm9tcHQgImNhcnBl"
    "dCBmbG9vciIgLS1zZWVkIDE5OTkgLS1vdXQgX3ByZXZpZXcgXAogICAgICAgIC0tcmVuZGVyIF9wcmV2aWV3L2Zsb29yX2Nh"
    "cnBldC5wbmcgWy0tc2tpbnMgPGRpcj4gLS10aGVtZSBkZWxjb10KCkJ1aWxkcyB0aGUgc3BlY2ltZW4gd2l0aCB0aGUgbm9y"
    "bWFsIFpvbyBwaXBlbGluZSwgdGhlbiBmcmFtZXMgaXQgYW5kIHJlbmRlcnMgYQpQTkcgd2l0aCBDeWNsZXMgQ1BVIChyZWxp"
    "YWJsZSBoZWFkbGVzcykuIFdpdGggLS1za2lucyBpdCBzaG93cyB0aGUgUGl4ZWxjb2F0CnRleHR1cmU7IHdpdGhvdXQsIHRo"
    "ZSBmbGF0IHN0eWxlIGNvbG91ciArIGJha2VkIHdlYXIuIFByaW50cyB0aGUgYnVpbGQgc3RhdHVzIHNvCnRoZSBjb25zb2xl"
    "IGFsb25lIGNvbmZpcm1zIHRoZSBzcGVjaWVzIHJlc29sdmVkIGV2ZW4gaWYgcmVuZGVyaW5nIGlzIHNraXBwZWQuCgpXSFkg"
    "VEhFUkUgSVMgQSBHUk9VTkQgUExBTkUgQU5EIEEgUkVEIFBPU1QgSU4gRVZFUlkgRlJBTUUuICBUaGUgZmlyc3QgdmVyc2lv"
    "bgpmcmFtZWQgZWFjaCBzcGVjaW1lbiB3aXRoIGBkaXN0ID0gc2l6ZSAqIDIuNGAsIHNvIGV2ZXJ5IG9iamVjdCBmaWxsZWQg"
    "dGhlIGZyYW1lCndoYXRldmVyIGl0cyByZWFsIHNpemU6IGEgNSBjbSBwZWJibGUgYW5kIGEgMzAgY20gc2NyYXAgcmVuZGVy"
    "ZWQgaWRlbnRpY2FsbHksCmFuZCB0aGVyZSB3YXMgbm8gZmxvb3IsIHNvIG5vdGhpbmcgc2hvd2VkIHdoZXRoZXIgYSB0aGlu"
    "ZyBzYXQgb24gYSBzdXJmYWNlLApob3ZlcmVkIG92ZXIgaXQgb3Igc2FuayB0aHJvdWdoIGl0LiAgRm91ciBzdXJmYWNlLWRy"
    "ZXNzaW5nIHNwZWNpZXMgd2VyZQpyZXZpZXdlZCBmcm9tIGltYWdlcyBsaWtlIHRoYXQgYW5kIHRoZSByZXZpZXcgY291bGQg"
    "bm90IGhhdmUgY2F1Z2h0IGEgc2NhbGUKZXJyb3IgaWYgb25lIGhhZCBiZWVuIHRoZXJlLiAgQXV0by1mcmFtaW5nIGlzIGtl"
    "cHQsIGJlY2F1c2UgYSA0IG0gZmxvb3IgbW9kdWxlCmFuZCBhIDUgY20gc3RvbmUgY2Fubm90IHNoYXJlIGEgY2FtZXJhIGRp"
    "c3RhbmNlIC0tIGJ1dCB0aGUgZnJhbWUgbm93IGFsd2F5cwpjb250YWluczoKCiAgKiBhIGdyb3VuZCBwbGFuZSBhdCB6ID0g"
    "MCwgc28gY29udGFjdCBpcyB2aXNpYmxlOwogICogYSByZWQgcG9zdCBleGFjdGx5IDAuMTE3IG0gdGFsbC4gIFRoYXQgaXMg"
    "YHVuYXNzaXN0ZWRfc3RlcF9tYXhgIGZyb20KICAgIGBsb3Qvc2l0ZV9zdGVwcy5weWAgLS0gdGhlIG51bWJlciBldmVyeSBk"
    "cmVzc2luZyBoZWlnaHQgaW4gdGhpcyByZXBvIGlzCiAgICBhcmd1ZWQgYWdhaW5zdCAtLSBzbyB0aGUgb25seSBydWxlciBp"
    "biBzaG90IGlzIHRoZSBvbmUgdGhhdCBtYXR0ZXJzLgoKLS12aWV3IHBhdGNoIHJlbmRlcnMgbWFueSBpbnN0YW5jZXMgc2Nh"
    "dHRlcmVkIG9uIHRoZSBncm91bmQgYXQgc3RhbmRpbmcgZXllCmhlaWdodCwgd2hpY2ggaXMgdGhlIHVuaXQgYSBzY2F0dGVy"
    "IHNwZWNpZXMgaXMgYWN0dWFsbHkganVkZ2VkIGluOiBhIHNpbmdsZQpzcGVjaW1lbiBpcyBuZXZlciB3aGF0IHRoZSBwbGF5"
    "ZXIgc2Vlcy4KIiIiCmZyb20gX19mdXR1cmVfXyBpbXBvcnQgYW5ub3RhdGlvbnMKCmltcG9ydCBtYXRoCmltcG9ydCBvcwpp"
    "bXBvcnQgcmFuZG9tCmltcG9ydCBzeXMKCiMgbG90L3NpdGVfc3RlcHMucHk6IFIgKiAoMSAtIGNvcyhmbG9vcl9tYXhfYW5n"
    "bGUpKSBmb3IgYSAwLjQgbSBjYXBzdWxlIGF0IDQ1LgpVTkFTU0lTVEVEX1NURVBfTUFYX00gPSAwLjExNwoKCmRlZiBfYXJn"
    "KGZsYWcsIGRlZmF1bHQ9Tm9uZSk6CiAgICBhcmd2ID0gc3lzLmFyZ3YKICAgIGFyZ3YgPSBhcmd2W2FyZ3YuaW5kZXgoIi0t"
    "IikgKyAxOl0gaWYgIi0tIiBpbiBhcmd2IGVsc2UgYXJndlsxOl0KICAgIHJldHVybiBhcmd2W2FyZ3YuaW5kZXgoZmxhZykg"
    "KyAxXSBpZiBmbGFnIGluIGFyZ3YgZWxzZSBkZWZhdWx0CgoKZGVmIF9mbGFnKGZsYWcpOgogICAgYXJndiA9IHN5cy5hcmd2"
    "CiAgICBhcmd2ID0gYXJndlthcmd2LmluZGV4KCItLSIpICsgMTpdIGlmICItLSIgaW4gYXJndiBlbHNlIGFyZ3ZbMTpdCiAg"
    "ICByZXR1cm4gZmxhZyBpbiBhcmd2CgoKZGVmIF9ncm91bmQoYnB5LCBzaXplPTguMCk6CiAgICBtZSA9IGJweS5kYXRhLm1l"
    "c2hlcy5uZXcoIlByZXZHcm91bmQiKQogICAgbWUuZnJvbV9weWRhdGEoWygtc2l6ZSwgLXNpemUsIDAuMCksIChzaXplLCAt"
    "c2l6ZSwgMC4wKSwKICAgICAgICAgICAgICAgICAgICAoc2l6ZSwgc2l6ZSwgMC4wKSwgKC1zaXplLCBzaXplLCAwLjApXSwg"
    "W10sIFsoMCwgMSwgMiwgMyldKQogICAgb2IgPSBicHkuZGF0YS5vYmplY3RzLm5ldygiUHJldkdyb3VuZCIsIG1lKQogICAg"
    "YnB5LmNvbnRleHQuc2NlbmUuY29sbGVjdGlvbi5vYmplY3RzLmxpbmsob2IpCiAgICBtID0gYnB5LmRhdGEubWF0ZXJpYWxz"
    "Lm5ldygiTV9QcmV2R3JvdW5kIikKICAgIG0udXNlX25vZGVzID0gVHJ1ZQogICAgYiA9IG0ubm9kZV90cmVlLm5vZGVzLmdl"
    "dCgiUHJpbmNpcGxlZCBCU0RGIikKICAgIGlmIGI6CiAgICAgICAgIyBNaWQgZ3JleSBvbiBwdXJwb3NlOiBhIGRhcmsgZmxv"
    "b3IgZmxhdHRlcnMgZHJlc3NpbmcgYnkgZ2l2aW5nIGl0CiAgICAgICAgIyBjb250cmFzdCBpdCB3aWxsIG5vdCBoYXZlIG9u"
    "IGEgcmVhbCBjb25jcmV0ZSBzdXJmYWNlLgogICAgICAgIGIuaW5wdXRzWyJCYXNlIENvbG9yIl0uZGVmYXVsdF92YWx1ZSA9"
    "ICgwLjQyLCAwLjQyLCAwLjQzLCAxLjApCiAgICAgICAgYi5pbnB1dHNbIlJvdWdobmVzcyJdLmRlZmF1bHRfdmFsdWUgPSAw"
    "Ljk1CiAgICBvYi5kYXRhLm1hdGVyaWFscy5hcHBlbmQobSkKICAgIHJldHVybiBvYgoKCmRlZiBfc2NhbGVfcG9zdChicHks"
    "IGF0LCBoZWlnaHQ9VU5BU1NJU1RFRF9TVEVQX01BWF9NKToKICAgIG1lID0gYnB5LmRhdGEubWVzaGVzLm5ldygiUHJldlNj"
    "YWxlUG9zdCIpCiAgICByID0gbWF4KDAuMDA4LCBoZWlnaHQgKiAwLjA5KQogICAgdiA9IFsoLXIsIC1yLCAwLjApLCAociwg"
    "LXIsIDAuMCksIChyLCByLCAwLjApLCAoLXIsIHIsIDAuMCksCiAgICAgICAgICgtciwgLXIsIGhlaWdodCksIChyLCAtciwg"
    "aGVpZ2h0KSwgKHIsIHIsIGhlaWdodCksICgtciwgciwgaGVpZ2h0KV0KICAgIGYgPSBbKDAsIDMsIDIsIDEpLCAoNCwgNSwg"
    "NiwgNyksICgwLCAxLCA1LCA0KSwKICAgICAgICAgKDEsIDIsIDYsIDUpLCAoMiwgMywgNywgNiksICgzLCAwLCA0LCA3KV0K"
    "ICAgIG1lLmZyb21fcHlkYXRhKHYsIFtdLCBmKQogICAgb2IgPSBicHkuZGF0YS5vYmplY3RzLm5ldygiUHJldlNjYWxlUG9z"
    "dCIsIG1lKQogICAgb2IubG9jYXRpb24gPSBhdAogICAgYnB5LmNvbnRleHQuc2NlbmUuY29sbGVjdGlvbi5vYmplY3RzLmxp"
    "bmsob2IpCiAgICBtID0gYnB5LmRhdGEubWF0ZXJpYWxzLm5ldygiTV9QcmV2U2NhbGVQb3N0IikKICAgIG0udXNlX25vZGVz"
    "ID0gVHJ1ZQogICAgYiA9IG0ubm9kZV90cmVlLm5vZGVzLmdldCgiUHJpbmNpcGxlZCBCU0RGIikKICAgIGlmIGI6CiAgICAg"
    "ICAgYi5pbnB1dHNbIkJhc2UgQ29sb3IiXS5kZWZhdWx0X3ZhbHVlID0gKDAuODUsIDAuMjIsIDAuMTUsIDEuMCkKICAgIG9i"
    "LmRhdGEubWF0ZXJpYWxzLmFwcGVuZChtKQogICAgcmV0dXJuIG9iCgoKZGVmIF9saWdodF9hbmRfd29ybGQoYnB5LCBtYXRo"
    "Xyk6CiAgICBzZCA9IGJweS5kYXRhLmxpZ2h0cy5uZXcoIlByZXZTdW4iLCAiU1VOIikKICAgIHNkLmVuZXJneSA9IDMuNQog"
    "ICAgdHJ5OgogICAgICAgIHNkLmFuZ2xlID0gMC4xMAogICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAgICAgICBwYXNzCiAgICBz"
    "dW4gPSBicHkuZGF0YS5vYmplY3RzLm5ldygiUHJldlN1biIsIHNkKQogICAgYnB5LmNvbnRleHQuc2NlbmUuY29sbGVjdGlv"
    "bi5vYmplY3RzLmxpbmsoc3VuKQogICAgc3VuLnJvdGF0aW9uX2V1bGVyID0gKG1hdGhfLnJhZGlhbnMoNTUpLCBtYXRoXy5y"
    "YWRpYW5zKDEyKSwKICAgICAgICAgICAgICAgICAgICAgICAgICBtYXRoXy5yYWRpYW5zKDM1KSkKICAgIHNjID0gYnB5LmNv"
    "bnRleHQuc2NlbmUKICAgIGlmIHNjLndvcmxkIGlzIE5vbmU6CiAgICAgICAgc2Mud29ybGQgPSBicHkuZGF0YS53b3JsZHMu"
    "bmV3KCJQcmV2V29ybGQiKQogICAgc2Mud29ybGQudXNlX25vZGVzID0gVHJ1ZQogICAgYmcgPSBzYy53b3JsZC5ub2RlX3Ry"
    "ZWUubm9kZXMuZ2V0KCJCYWNrZ3JvdW5kIikKICAgIGlmIGJnOgogICAgICAgIGJnLmlucHV0c1swXS5kZWZhdWx0X3ZhbHVl"
    "ID0gKDAuMDksIDAuMTAsIDAuMTIsIDEuMCkKICAgICAgICBiZy5pbnB1dHNbMV0uZGVmYXVsdF92YWx1ZSA9IDAuNTUKCgpk"
    "ZWYgX2JvdW5kcyhicHksIG1hdGh1dGlscywgbWVzaGVzKToKICAgIGxvID0gWzFlOV0gKiAzCiAgICBoaSA9IFstMWU5XSAq"
    "IDMKICAgIGZvciBvIGluIG1lc2hlczoKICAgICAgICBmb3IgY29ybmVyIGluIG8uYm91bmRfYm94OgogICAgICAgICAgICB3"
    "YyA9IG8ubWF0cml4X3dvcmxkIEAgbWF0aHV0aWxzLlZlY3Rvcihjb3JuZXJbOl0pCiAgICAgICAgICAgIGZvciBpIGluIHJh"
    "bmdlKDMpOgogICAgICAgICAgICAgICAgbG9baV0gPSBtaW4obG9baV0sIHdjW2ldKQogICAgICAgICAgICAgICAgaGlbaV0g"
    "PSBtYXgoaGlbaV0sIHdjW2ldKQogICAgcmV0dXJuIGxvLCBoaQoKCmRlZiBtYWluKCk6CiAgICBwcm9tcHQgPSBfYXJnKCIt"
    "LXByb21wdCIsICJjYXJwZXQgZmxvb3IiKQogICAgc2VlZCA9IGludChfYXJnKCItLXNlZWQiLCAiMTk5OSIpKQogICAgb3V0"
    "ID0gb3MucGF0aC5hYnNwYXRoKF9hcmcoIi0tb3V0IiwgIl9wcmV2aWV3IikpCiAgICByZW5kZXIgPSBvcy5wYXRoLmFic3Bh"
    "dGgoX2FyZygiLS1yZW5kZXIiLCAicHJldmlldy5wbmciKSkKICAgIHNraW5zID0gX2FyZygiLS1za2lucyIpCiAgICB0aGVt"
    "ZSA9IF9hcmcoIi0tdGhlbWUiLCAiZGVsY28iKQogICAgdmlldyA9IF9hcmcoIi0tdmlldyIsICJhdXRvIikgICAgICAgICAg"
    "ICAjIGF1dG8gfCBwYXRjaAogICAgcGF0Y2hfbiA9IGludChfYXJnKCItLXBhdGNoIiwgIjQ1IikpCiAgICBwYXRjaF9leHRl"
    "bnQgPSBmbG9hdChfYXJnKCItLXBhdGNoLWV4dGVudCIsICIxLjE1IikpCiAgICBub19ncm91bmQgPSBfZmxhZygiLS1uby1n"
    "cm91bmQiKQoKICAgIHJlcG8gPSBvcy5wYXRoLmRpcm5hbWUob3MucGF0aC5kaXJuYW1lKG9zLnBhdGguYWJzcGF0aChfX2Zp"
    "bGVfXykpKQogICAgaWYgcmVwbyBub3QgaW4gc3lzLnBhdGg6CiAgICAgICAgc3lzLnBhdGguaW5zZXJ0KDAsIHJlcG8pCgog"
    "ICAgZnJvbSB6b29fa2VlcGVyLmJweWxheWVyIGltcG9ydCBidWlsZAogICAgaWYgc2tpbnM6CiAgICAgICAgZnJvbSB6b29f"
    "a2VlcGVyLmJweWxheWVyIGltcG9ydCBtYXRlcmlhbHMKICAgICAgICBtYXRlcmlhbHMuc2V0X3NraW5fbGlicmFyeShvcy5w"
    "YXRoLmFic3BhdGgoc2tpbnMpLCB0aGVtZSkKICAgICAgICBwcmludChmIltwcmV2aWV3XSBza2luczoge3NraW5zfSAodGhl"
    "bWU9e3RoZW1lfSkiKQoKICAgIHJlcyA9IGJ1aWxkLmJ1aWxkX3NwZWNpbWVuKAogICAgICAgIHByb21wdCwgb3V0LCBzZWVk"
    "PXNlZWQsCiAgICAgICAgb3B0aW9ucz17ImNvbGxpc2lvbiI6IE5vbmUsICJsb2RzIjogRmFsc2UsCiAgICAgICAgICAgICAg"
    "ICAgInNhdmVfYmxlbmQiOiBGYWxzZSwgImNsZWFyX3NjZW5lIjogVHJ1ZX0pCiAgICBwcmludChmIltwcmV2aWV3XSBwcm9t"
    "cHQ9J3twcm9tcHR9JyAtPiBzcGVjaW1lbj17cmVzWydzcGVjaW1lbl9pZCddfSAiCiAgICAgICAgICBmInN0YXR1cz17cmVz"
    "WydyZXBvcnQnXVsnc3RhdHVzJ10udXBwZXIoKX0iKQoKICAgIGltcG9ydCBicHkKICAgIGltcG9ydCBtYXRodXRpbHMKICAg"
    "IHNjZW5lID0gYnB5LmNvbnRleHQuc2NlbmUKCiAgICBtZXNoZXMgPSBbbyBmb3IgbyBpbiBzY2VuZS5vYmplY3RzIGlmIG8u"
    "dHlwZSA9PSAiTUVTSCJdCiAgICBpZiBub3QgbWVzaGVzOiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAjIGZh"
    "bGwgYmFjayB0byB0aGUgZXhwb3J0ZWQgZ2xiCiAgICAgICAgZ2xiID0gTm9uZQogICAgICAgIGZvciB2IGluIHJlcy5nZXQo"
    "ImZpbGVzIiwge30pLnZhbHVlcygpOgogICAgICAgICAgICBpZiBzdHIodikubG93ZXIoKS5lbmRzd2l0aCgiLmdsYiIpOgog"
    "ICAgICAgICAgICAgICAgZ2xiID0gdiBpZiBvcy5wYXRoLmlzYWJzKHYpIGVsc2Ugb3MucGF0aC5qb2luKHJlc1sib3V0X2Rp"
    "ciJdLCB2KQogICAgICAgIGlmIGdsYiBhbmQgb3MucGF0aC5pc2ZpbGUoZ2xiKToKICAgICAgICAgICAgYnB5Lm9wcy5pbXBv"
    "cnRfc2NlbmUuZ2x0ZihmaWxlcGF0aD1nbGIpCiAgICAgICAgICAgIG1lc2hlcyA9IFtvIGZvciBvIGluIHNjZW5lLm9iamVj"
    "dHMgaWYgby50eXBlID09ICJNRVNIIl0KICAgIHByaW50KGYiW3ByZXZpZXddIG1lc2ggb2JqZWN0cyBpbiBzY2VuZToge2xl"
    "bihtZXNoZXMpfSIpCiAgICBpZiBub3QgbWVzaGVzOgogICAgICAgIHByaW50KCJbcHJldmlld10gbm90aGluZyB0byByZW5k"
    "ZXIgKGJ1aWxkIG1heSBoYXZlIGZhaWxlZCkg4oCUIHNlZSBzdGF0dXMgYWJvdmUiKQogICAgICAgIHJldHVybgoKICAgIGxv"
    "LCBoaSA9IF9ib3VuZHMoYnB5LCBtYXRodXRpbHMsIG1lc2hlcykKICAgIHNpemUgPSBtYXgoMWUtMywgbWF4KGhpW2ldIC0g"
    "bG9baV0gZm9yIGkgaW4gcmFuZ2UoMykpKQoKICAgICMgLS0tLSBvcHRpb25hbCBwYXRjaCB2aWV3OiBtYW55IGluc3RhbmNl"
    "cywgc3RhbmRpbmcgZXllIGhlaWdodCAtLS0tLS0tLS0KICAgIGlmIHZpZXcgPT0gInBhdGNoIjoKICAgICAgICBybmcgPSBy"
    "YW5kb20uUmFuZG9tKHNlZWQgXiAweDVFRUQpCiAgICAgICAgY2VudHJlcyA9IFsocm5nLnVuaWZvcm0oLXBhdGNoX2V4dGVu"
    "dCwgcGF0Y2hfZXh0ZW50KSwKICAgICAgICAgICAgICAgICAgICBybmcudW5pZm9ybSgtcGF0Y2hfZXh0ZW50LCBwYXRjaF9l"
    "eHRlbnQpKQogICAgICAgICAgICAgICAgICAgZm9yIF8gaW4gcmFuZ2UobWF4KDEsIHBhdGNoX24gLy8gNykpXQogICAgICAg"
    "IHNyYyA9IGxpc3QobWVzaGVzKQogICAgICAgIGZvciBpIGluIHJhbmdlKHBhdGNoX24pOgogICAgICAgICAgICBpZiBybmcu"
    "cmFuZG9tKCkgPCAwLjE4OiAgICAgICAgICAgICAgICAgIyBzdHJheSB0YWlsCiAgICAgICAgICAgICAgICB4ID0gcm5nLnVu"
    "aWZvcm0oLXBhdGNoX2V4dGVudCwgcGF0Y2hfZXh0ZW50KQogICAgICAgICAgICAgICAgeSA9IHJuZy51bmlmb3JtKC1wYXRj"
    "aF9leHRlbnQsIHBhdGNoX2V4dGVudCkKICAgICAgICAgICAgZWxzZTogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICMgY2x1c3RlcmVkIGJvZHkKICAgICAgICAgICAgICAgIGN4LCBjeSA9IGNlbnRyZXNbcm5nLnJhbmRyYW5nZShsZW4o"
    "Y2VudHJlcykpXQogICAgICAgICAgICAgICAgeCA9IG1heCgtcGF0Y2hfZXh0ZW50LCBtaW4ocGF0Y2hfZXh0ZW50LCBjeCAr"
    "IHJuZy5nYXVzcygwLCAwLjIyKSkpCiAgICAgICAgICAgICAgICB5ID0gbWF4KC1wYXRjaF9leHRlbnQsIG1pbihwYXRjaF9l"
    "eHRlbnQsIGN5ICsgcm5nLmdhdXNzKDAsIDAuMjIpKSkKICAgICAgICAgICAgcyA9IDAuNjUgKyAocm5nLnJhbmRvbSgpICoq"
    "IDIpICogMC45ICAgICMgbG9nbm9ybWFsLWlzaCBzaXplIHNwcmVhZAogICAgICAgICAgICBmb3IgbyBpbiBzcmM6CiAgICAg"
    "ICAgICAgICAgICBkdXAgPSBvLmNvcHkoKSAgICAgICAgICAgICAgICAgICAgICAjIGxpbmtlZCBkdXBsaWNhdGU6IHNoYXJl"
    "cyBtZXNoCiAgICAgICAgICAgICAgICBkdXAubG9jYXRpb24gPSAoeCwgeSwgMC4wKQogICAgICAgICAgICAgICAgZHVwLnJv"
    "dGF0aW9uX2V1bGVyID0gKDAuMCwgMC4wLCBybmcudW5pZm9ybSgwLjAsIDYuMjgzMTg1MykpCiAgICAgICAgICAgICAgICBk"
    "dXAuc2NhbGUgPSAocywgcywgcykKICAgICAgICAgICAgICAgIHNjZW5lLmNvbGxlY3Rpb24ub2JqZWN0cy5saW5rKGR1cCkK"
    "ICAgICAgICBmb3IgbyBpbiBzcmM6CiAgICAgICAgICAgIG8ubG9jYXRpb24gPSAocGF0Y2hfZXh0ZW50ICogMy4wLCAwLjAs"
    "IDAuMCkgICAjIG1vdmUgdGhlIG9yaWdpbmFsIG91dAogICAgICAgIHRhcmdldCA9IG1hdGh1dGlscy5WZWN0b3IoKDAuMCwg"
    "MC4wLCBzaXplICogMC41KSkKICAgICAgICBkaXN0ID0gcGF0Y2hfZXh0ZW50ICogMi4zCiAgICAgICAgZXllID0gMS41NQog"
    "ICAgICAgIHJlc194eSA9ICgxMTAwLCA2MjApCiAgICBlbHNlOgogICAgICAgIGNlbnRyZSA9IG1hdGh1dGlscy5WZWN0b3Io"
    "Wyhsb1tpXSArIGhpW2ldKSAvIDIgZm9yIGkgaW4gcmFuZ2UoMyldKQogICAgICAgIHRhcmdldCA9IG1hdGh1dGlscy5WZWN0"
    "b3IoKGNlbnRyZS54LCBjZW50cmUueSwgbWF4KGxvWzJdLCAwLjApCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgKyBzaXplICogMC40KSkKICAgICAgICBkaXN0ID0gc2l6ZSAqIDIuNAogICAgICAgIGV5ZSA9IG1heChzaXplICogMC43"
    "NSwgbWluKDEuNiwgc2l6ZSAqIDIuMCkpCiAgICAgICAgcmVzX3h5ID0gKDk2MCwgNjQwKQoKICAgIGlmIG5vdCBub19ncm91"
    "bmQ6CiAgICAgICAgX2dyb3VuZChicHksIHNpemU9bWF4KDQuMCwgc2l6ZSAqIDYuMCkpCiAgICAgICAgX3NjYWxlX3Bvc3Qo"
    "YnB5LCAodGFyZ2V0LnggKyBtYXgoc2l6ZSAqIDAuOSwgMC4wNiksCiAgICAgICAgICAgICAgICAgICAgICAgICAgdGFyZ2V0"
    "LnkgLSBtYXgoc2l6ZSAqIDAuNSwgMC4wNCksIDAuMCkpCgogICAgY2FtX2RhdGEgPSBicHkuZGF0YS5jYW1lcmFzLm5ldygi"
    "UHJldkNhbSIpCiAgICBjYW1fZGF0YS5sZW5zID0gNDAuMAogICAgY2FtID0gYnB5LmRhdGEub2JqZWN0cy5uZXcoIlByZXZD"
    "YW0iLCBjYW1fZGF0YSkKICAgIHNjZW5lLmNvbGxlY3Rpb24ub2JqZWN0cy5saW5rKGNhbSkKICAgIHNjZW5lLmNhbWVyYSA9"
    "IGNhbQogICAgY2FtLmxvY2F0aW9uID0gbWF0aHV0aWxzLlZlY3RvcigoZGlzdCAqIDAuNzIsIC1kaXN0ICogMC43MiwgZXll"
    "KSkKICAgIGNhbS5yb3RhdGlvbl9ldWxlciA9ICh0YXJnZXQgLSBjYW0ubG9jYXRpb24pLnRvX3RyYWNrX3F1YXQoIi1aIiwg"
    "IlkiKS50b19ldWxlcigpCgogICAgX2xpZ2h0X2FuZF93b3JsZChicHksIG1hdGgpCgogICAgc2NlbmUucmVuZGVyLmVuZ2lu"
    "ZSA9ICJDWUNMRVMiCiAgICB0cnk6CiAgICAgICAgc2NlbmUuY3ljbGVzLmRldmljZSA9ICJDUFUiCiAgICAgICAgc2NlbmUu"
    "Y3ljbGVzLnNhbXBsZXMgPSA0MAogICAgICAgIHNjZW5lLmN5Y2xlcy51c2VfZGVub2lzaW5nID0gVHJ1ZQogICAgZXhjZXB0"
    "IEV4Y2VwdGlvbjoKICAgICAgICBwYXNzCiAgICBzY2VuZS5yZW5kZXIucmVzb2x1dGlvbl94LCBzY2VuZS5yZW5kZXIucmVz"
    "b2x1dGlvbl95ID0gcmVzX3h5CiAgICBzY2VuZS5yZW5kZXIuZmlsZXBhdGggPSByZW5kZXIKICAgIGJweS5vcHMucmVuZGVy"
    "LnJlbmRlcih3cml0ZV9zdGlsbD1UcnVlKQogICAgcHJpbnQoZiJbcHJldmlld10gcmVuZGVyZWQgLT4ge3JlbmRlcn0gICIK"
    "ICAgICAgICAgIGYiKHZpZXc9e3ZpZXd9LCBncm91bmQ9eydubycgaWYgbm9fZ3JvdW5kIGVsc2UgJ3llcyd9LCAiCiAgICAg"
    "ICAgICBmInJ1bGVyPXtVTkFTU0lTVEVEX1NURVBfTUFYX019IG0pIikKCgptYWluKCkK"
    ),
  },
  'zoo/tools/preview_dressing.ps1': {
    "kind": 'replace',
    "pre_sha": '10c63531d3c2287919c9089684bbda32b7d572881ced3d8860ecd67e77b93c52',
    "pre_bytes": 2070,
    "post_sha": 'bdc53ed15b306fed888c8f9d317e24787500476988f1f00300826a401268746c',
    "post_bytes": 2581,
    "b64": (
    "IyBQcmV2aWV3IHRoZSBmb3VyIExheWVyIDMgc3VyZmFjZS1kcmVzc2luZyBzcGVjaWVzIGhlYWRsZXNzbHkuCiMKIyBGb3Ig"
    "ZWFjaCBzcGVjaWVzOiBidWlsZCArIHJlbmRlciBhIHNjYWxlLXRydWUgc3BlY2ltZW4gc2hvdCwgYnVpbGQgKyByZW5kZXIg"
    "YQojIFBBVENIIHNob3QgKG1hbnkgaW5zdGFuY2VzIGF0IHN0YW5kaW5nIGV5ZSBoZWlnaHQsIHdoaWNoIGlzIHRoZSB1bml0"
    "IGEKIyBzY2F0dGVyIHNwZWNpZXMgaXMgYWN0dWFsbHkganVkZ2VkIGluKSwgdGhlbiBNRUFTVVJFIHRoZSBidWlsdCBHTEIg"
    "d2l0aAojIHRvb2xzL3NoYXBlX21ldHJpY3MucHkuCiMKIyBXSFkgTUVBU1VSRSBBTkQgTk9UIEpVU1QgTE9PSy4gVGhlIGZp"
    "cnN0IHBhc3Mgb2YgdGhpcyBraXQgd2FzIHJldmlld2VkIGZyb20KIyByZW5kZXJzIGFsb25lLCBhbmQgcmVuZGVycyBhbG9u"
    "ZSBjb3VsZCBub3Qgc2hvdyB0aGF0IGEgcnViYmxlIGZyYWdtZW50IG5lZWRlZAojIG9ubHkgNyBkaXN0aW5jdCBmYWNpbmcg"
    "ZGlyZWN0aW9ucyB0byBjb3ZlciA4MCUgb2YgaXRzIHN1cmZhY2UgKGl0IHdhcyBzdGlsbCBhCiMgYm94KSwgdGhhdCBub3Ro"
    "aW5nIGluIHRoZSBraXQgdG91Y2hlZCB0aGUgZ3JvdW5kIChiYXNlX2NvbnRhY3RfcmF0aW8gMC4wMDEpLAojIG9yIHRoYXQg"
    "dGhlIHBlYmJsZSB3YXMgMzM0IHRyaWFuZ2xlcyBhZ2FpbnN0IGEgMjYwIGJ1ZGdldC4gRXZlcnkgb25lIG9mIHRob3NlCiMg"
    "aXMgb25lIG51bWJlci4gU2VuZCBiYWNrIHRoZSBQTkdzIEFORCB0aGUgdGFibGUuCiMKIyBVc2FnZTogIHB3c2ggLUV4ZWN1"
    "dGlvblBvbGljeSBCeXBhc3MgLUZpbGUgcHJldmlld19kcmVzc2luZy5wczEKCiRCbGVuZGVyID0gIkM6XGJsZW5kZXJcYmxl"
    "bmRlci5leGUiCiRab28gICAgID0gIkM6XFByb2plY3RzXGdhYmFnb29sX3N0dWRpb3NcZ2FiYWdvb2xfZmFjdG9yeVx6b28i"
    "CiRGYWN0b3J5ID0gIkM6XFByb2plY3RzXGdhYmFnb29sX3N0dWRpb3NcZ2FiYWdvb2xfZmFjdG9yeSIKCmlmICgtbm90IChU"
    "ZXN0LVBhdGggJEJsZW5kZXIpKSB7CiAgJGZvdW5kID0gR2V0LUNoaWxkSXRlbSAtUGF0aCAiQzpcYmxlbmRlciIgLUZpbHRl"
    "ciAiYmxlbmRlci5leGUiIC1SZWN1cnNlIC1FcnJvckFjdGlvbiBTaWxlbnRseUNvbnRpbnVlIHwgU2VsZWN0LU9iamVjdCAt"
    "Rmlyc3QgMQogIGlmICgkZm91bmQpIHsgJEJsZW5kZXIgPSAkZm91bmQuRnVsbE5hbWUgfQogIGVsc2UgeyBXcml0ZS1FcnJv"
    "ciAiYmxlbmRlci5leGUgbm90IGZvdW5kIHVuZGVyIEM6XGJsZW5kZXIgLSBzZXQgYCRCbGVuZGVyIGF0IHRoZSB0b3AuIjsg"
    "ZXhpdCAxIH0KfQoKJE91dCAgPSBKb2luLVBhdGggJFpvbyAiX3ByZXZpZXdfZHJlc3NpbmciCiRUb29sID0gSm9pbi1QYXRo"
    "ICRab28gInRvb2xzXHByZXZpZXdfc3BlY2ltZW4ucHkiCk5ldy1JdGVtIC1JdGVtVHlwZSBEaXJlY3RvcnkgLUZvcmNlIC1Q"
    "YXRoICRPdXQgfCBPdXQtTnVsbApXcml0ZS1Ib3N0ICJCbGVuZGVyOiAkQmxlbmRlciIKV3JpdGUtSG9zdCAiT3V0OiAgICAg"
    "JE91dCIKCiRqb2JzID0gQCgKICBAeyBwcm9tcHQgPSAicGViYmxlIjsgICAgICAgICAgbmFtZSA9ICJwZWJibGUiIH0sCiAg"
    "QHsgcHJvbXB0ID0gInJ1YmJsZSBmcmFnbWVudCI7IG5hbWUgPSAicnViYmxlX2ZyYWciIH0sCiAgQHsgcHJvbXB0ID0gIndl"
    "ZWQgdHVmdCI7ICAgICAgIG5hbWUgPSAid2VlZF90dWZ0IiB9LAogIEB7IHByb21wdCA9ICJsaXR0ZXIgc2NyYXAiOyAgICBu"
    "YW1lID0gImxpdHRlcl9zY3JhcCIgfQopCgpmb3JlYWNoICgkaiBpbiAkam9icykgewogIFdyaXRlLUhvc3QgImBuPT09IEJ1"
    "aWxkaW5nOiAkKCRqLnByb21wdCkgPT09IgogICYgJEJsZW5kZXIgLS1iYWNrZ3JvdW5kIC0tcHl0aG9uICRUb29sIC0tIGAK"
    "ICAgICAgLS1wcm9tcHQgJGoucHJvbXB0IC0tc2VlZCAxOTk5IC0tb3V0ICRPdXQgYAogICAgICAtLXJlbmRlciAoSm9pbi1Q"
    "YXRoICRPdXQgKCRqLm5hbWUgKyAiX3NwZWNpbWVuLnBuZyIpKQogIFdyaXRlLUhvc3QgIi0tLSBwYXRjaCB2aWV3OiAkKCRq"
    "LnByb21wdCkgLS0tIgogICYgJEJsZW5kZXIgLS1iYWNrZ3JvdW5kIC0tcHl0aG9uICRUb29sIC0tIGAKICAgICAgLS1wcm9t"
    "cHQgJGoucHJvbXB0IC0tc2VlZCAxOTk5IC0tb3V0ICRPdXQgLS12aWV3IHBhdGNoIC0tcGF0Y2ggNDUgYAogICAgICAtLXJl"
    "bmRlciAoSm9pbi1QYXRoICRPdXQgKCRqLm5hbWUgKyAiX3BhdGNoLnBuZyIpKQp9CgpXcml0ZS1Ib3N0ICJgbj09PSBTSEFQ"
    "RSBNRVRSSUNTIEZST00gVEhFIEJVSUxUIEdMQnMgPT09IgpXcml0ZS1Ib3N0ICIoZ2xURiBzcGFjZSBpcyBZLVVQOyBzaGFw"
    "ZV9tZXRyaWNzIGRlZmF1bHRzIHRvIHVwPTEgZm9yIHRoYXQgcmVhc29uKSIKJGVudjpQWVRIT05JT0VOQ09ESU5HID0gInV0"
    "Zi04IgpweXRob24gKEpvaW4tUGF0aCAkRmFjdG9yeSAidG9vbHNcc2hhcGVfbWV0cmljcy5weSIpIC0tZGlyICRPdXQKCldy"
    "aXRlLUhvc3QgImBuUE5HczoiCkdldC1DaGlsZEl0ZW0gJE91dCAtRmlsdGVyICoucG5nIC1FcnJvckFjdGlvbiBTaWxlbnRs"
    "eUNvbnRpbnVlIHwgRm9yRWFjaC1PYmplY3QgeyBXcml0ZS1Ib3N0ICIgICQoJF8uRnVsbE5hbWUpIiB9Cg=="
    ),
  },
  'tools/shape_metrics.py': {
    "kind": 'new',
    "pre_sha": None,
    "pre_bytes": None,
    "post_sha": 'd84b3de5d3c16562fbd25d682c028e91d8e7fd623fa5dc259f6024328aef943b',
    "post_bytes": 31322,
    "b64": (
    "IyEvdXNyL2Jpbi9lbnYgcHl0aG9uMwoiIiJzaGFwZV9tZXRyaWNzLnB5IC0tIG1lYXN1cmUgdGhlIFNIQVBFIG9mIGEgYnVp"
    "bHQgYXNzZXQsIG5vdCBqdXN0IGl0cyBzaXplLgoKV0hZIFRISVMgRVhJU1RTLiAgRXZlcnl0aGluZyBlbHNlIGluIHRoaXMg"
    "cGlwZWxpbmUgaXMgbWVhc3VyZWQgYWdhaW5zdApzb21ldGhpbmc6IHRoZSBjYXBzdWxlIGFnYWluc3QgYHVuYXNzaXN0ZWRf"
    "c3RlcF9tYXhgLCB0aGUgbGlnaHRzIGFnYWluc3QgYQpjb3VudCwgdHJhdmVyc2FsIGFnYWluc3QgdGhlIGZ1bmN0aW9uYWwg"
    "bG9jay4gIFNoYXBlIGhhZCBubyB0YXJnZXQgYW5kIG5vCmluc3RydW1lbnQsIHNvIGV2ZXJ5IGp1ZGdlbWVudCBhYm91dCB3"
    "aGV0aGVyIGEgcGViYmxlIGxvb2tlZCBsaWtlIGEgcGViYmxlIHdhcwphIHBlcnNvbiBzcXVpbnRpbmcgYXQgYSByZW5kZXIu"
    "ICBUaGF0IGlzIHRoZSBvbmUgcGxhY2UgaW4gdGhlIHN0YWNrIHdoZXJlIHdlCndlcmUgc3RpbGwgYXNzZXJ0aW5nIGluc3Rl"
    "YWQgb2YgbWVhc3VyaW5nLgoKV0hBVCBJVCBNRUFTVVJFUy4gIFR3byB1bml0cywgYmVjYXVzZSB0aGV5IGZhaWwgZGlmZmVy"
    "ZW50bHkuCgogIFNQRUNJTUVOIG1ldHJpY3MgYW5zd2VyICJpcyB0aGlzIG9uZSBvYmplY3QgdGhlIHJpZ2h0IGtpbmQgb2Yg"
    "c29saWQiLgogIFRoZXkgYXJlIGNvbXB1dGVkIGZyb20gdHJpYW5nbGVzIGFsb25lIC0tIG5vIEJsZW5kZXIsIG5vIHNjZW5l"
    "LCBubwogIG1hdGVyaWFscyAtLSBzbyB0aGV5IGNhbiBydW4gb24gYSBzaGlwcGVkIEdMQiBpbiBDSS4KCiAgUEFUQ0ggbWV0"
    "cmljcyBhbnN3ZXIgImRvZXMgYSBzY2F0dGVyIG9mIHRoZW0gcmVhZCBhcyBwbGFjZWQgb3IgYXMKICBwcm9jZWR1cmFsIG5v"
    "aXNlIi4gIGBkb2NzL1NVUkZBQ0VfRFJFU1NJTkcubWRgJ3MgZGVmaW5pdGlvbiBvZiBkb25lIHNheXMKICAibm8gb2J2aW91"
    "cyB1bmlmb3JtIHNjYXR0ZXIgcGF0dGVybiBmcm9tIHByaW1hcnkgdmlld3MiOyB0aGUgQ2xhcmstRXZhbnMKICBuZWFyZXN0"
    "LW5laWdoYm91ciByYXRpbyBiZWxvdyBpcyB0aGF0IHNlbnRlbmNlIGFzIGEgbnVtYmVyLgoKV0hBVCBJVCBET0VTIE5PVCBE"
    "Ty4gIEl0IGhhcyBubyBvcGluaW9uIGFib3V0IHdoZXRoZXIgYSBudW1iZXIgaXMgZ29vZC4gIEl0CnJlcG9ydHM7IHRoZSBn"
    "ZW5vbWUgKG9yIGEgZnV0dXJlIGdhdGUpIGRlY2lkZXMuICBUaHJlc2hvbGRzIGxpdmUgd2l0aCB0aGUKc3BlY2llcyB0aGF0"
    "IGhhcyB0byBtZWV0IHRoZW0sIG5vdCBpbiB0aGUgcnVsZXIuCgpVUCBBWElTLiAgZ2xURiBvbiBkaXNrIGlzIFktVVAsIHNv"
    "IGB1cD0xYCBpcyB0aGUgZGVmYXVsdCBoZXJlLiAgQmxlbmRlci1zaWRlCmNhbGxlcnMgYnVpbGRpbmcgaW4gWi11cCBtdXN0"
    "IHBhc3MgYHVwPTJgLiAgVGhpcyBoYXMgYml0dGVuIHRoaXMgcmVwbyBiZWZvcmUKKGBnbGJfbm9kZXMucHlgLCB0aGUgZHJl"
    "c3NpbmcgaGVpZ2h0IGNoZWNrIHRoYXQgbWVhc3VyZWQgbm90aGluZyksIHNvIHRoZSBheGlzCmlzIGFuIGV4cGxpY2l0IGFy"
    "Z3VtZW50IGV2ZXJ5d2hlcmUgcmF0aGVyIHRoYW4gYSBjb252ZW50aW9uLgoKVVNBR0UKICAgIHB5dGhvbiB0b29scy9zaGFw"
    "ZV9tZXRyaWNzLnB5IDxmaWxlLmdsYj4gW21vcmUuZ2xiIC4uLl0gWy0tanNvbl0gWy0tdXAgTl0KICAgIHB5dGhvbiB0b29s"
    "cy9zaGFwZV9tZXRyaWNzLnB5IC0tZGlyIDxmb2xkZXI+ICAgICAgICAgICAgIyBldmVyeSAqLmdsYiB1bmRlciBpdAogICAg"
    "cHl0aG9uIHRvb2xzL3NoYXBlX21ldHJpY3MucHkgLS1zZWxmdGVzdAoiIiIKZnJvbSBfX2Z1dHVyZV9fIGltcG9ydCBhbm5v"
    "dGF0aW9ucwoKaW1wb3J0IGFyZ3BhcnNlCmltcG9ydCBnbG9iCmltcG9ydCBqc29uCmltcG9ydCBtYXRoCmltcG9ydCBvcwpp"
    "bXBvcnQgc3RydWN0CmltcG9ydCBzeXMKClZFUlNJT04gPSAiMC4xLjAiCgojIEZhY2VzIHdob3NlIG5vcm1hbHMgZGlmZmVy"
    "IGJ5IGxlc3MgdGhhbiB0aGlzIGFyZSB0cmVhdGVkIGFzIG9uZSBmbGF0IHJlZ2lvbi4KIyA1IGRlZ3JlZXMgaXMgdGlnaHQg"
    "ZW5vdWdoIHRoYXQgYSBiZXZlbCBkb2VzIG5vdCBtZXJnZSB3aXRoIHRoZSBmYWNlIGl0CiMgYmV2ZWxzLCBsb29zZSBlbm91"
    "Z2ggdGhhdCBmbG9hdCBub2lzZSBvbiBhIG5vbWluYWxseSBwbGFuYXIgcXVhZCBkb2VzIG5vdAojIHNwbGl0IGl0IGluIHR3"
    "by4KQ09QTEFOQVJfREVHID0gNS4wCgojIEZhY2V0cyB3aG9zZSBub3JtYWxzIGRpZmZlciBieSBsZXNzIHRoYW4gdGhpcyBh"
    "cmUgb25lICJyZWdpb24iIG9mIHRoZQojIHNpbGhvdWV0dGUgLS0gdGhlIHNjYWxlIGF0IHdoaWNoIGFuIGV5ZSByZWFkcyBh"
    "IGZhY2UgcmF0aGVyIHRoYW4gYSBmYWNldC4KUkVHSU9OX0RFRyA9IDIwLjAKCiMgIlVwLWZhY2luZyIgZm9yIHRoZSBmbGF0"
    "LXRvcCB0ZWxsLiAgMjAgZGVncmVlcywgYmVjYXVzZSBhIHJvY2sgdG9wIHRoYXQKIyBzbG9wZXMgMTUgZGVncmVlcyBzdGls"
    "bCByZWFkcyBhcyBhIGZsYXQgdG9wIGZyb20gYSBzdGFuZGluZyBleWUgaGVpZ2h0LgpVUEZBQ0VfREVHID0gMjAuMAoKIyBB"
    "bmd1bGFyIGJpbnMgZm9yIHRoZSBwbGFuLXZpZXcgcmFkaWFsIHByb2ZpbGUuClJBRElBTF9CSU5TID0gMzYKCgojIC0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiMg"
    "R0xCIHJlYWRpbmcuICBEZWxpYmVyYXRlbHkgZGVwZW5kZW5jeS1mcmVlOiBzdHJ1Y3QgKyBqc29uLiAgbnVtcHkgd291bGQg"
    "YmUKIyBmYXN0ZXIgYW5kIGlzIHByb2JhYmx5IHByZXNlbnQsIGJ1dCB0aGlzIHRvb2wgaGFzIHRvIHJ1biBpbiBDSSBhbmQg"
    "aW4KIyBCbGVuZGVyJ3MgYnVuZGxlZCBpbnRlcnByZXRlciB3aXRob3V0IGFuIGluc3RhbGwgc3RlcC4KIyAtLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQoKX0NPTVBP"
    "TkVOVCA9IHs1MTIwOiAoImIiLCAxKSwgNTEyMTogKCJCIiwgMSksIDUxMjI6ICgiaCIsIDIpLAogICAgICAgICAgICAgIDUx"
    "MjM6ICgiSCIsIDIpLCA1MTI1OiAoIkkiLCA0KSwgNTEyNjogKCJmIiwgNCl9Cl9OQ09NUCA9IHsiU0NBTEFSIjogMSwgIlZF"
    "QzIiOiAyLCAiVkVDMyI6IDMsICJWRUM0IjogNCwKICAgICAgICAgICJNQVQyIjogNCwgIk1BVDMiOiA5LCAiTUFUNCI6IDE2"
    "fQoKCmRlZiByZWFkX2dsYihwYXRoKToKICAgICIiIlJldHVybiAoZ2x0Zl9qc29uX2RpY3QsIGJpbmFyeV9jaHVua19ieXRl"
    "cykgZm9yIGEgLmdsYiBmaWxlLiIiIgogICAgd2l0aCBvcGVuKHBhdGgsICJyYiIpIGFzIGZoOgogICAgICAgIGRhdGEgPSBm"
    "aC5yZWFkKCkKICAgIGlmIGRhdGFbOjRdICE9IGIiZ2xURiI6CiAgICAgICAgcmFpc2UgVmFsdWVFcnJvcihmIntwYXRofTog"
    "bm90IGEgR0xCIChtYWdpYyBpcyB7ZGF0YVs6NF0hcn0pIikKICAgIF92ZXIsIF9sZW5ndGggPSBzdHJ1Y3QudW5wYWNrX2Zy"
    "b20oIjxJSSIsIGRhdGEsIDQpCiAgICBvZmYsIGpzLCBiaW5fY2h1bmsgPSAxMiwgTm9uZSwgYiIiCiAgICB3aGlsZSBvZmYg"
    "KyA4IDw9IGxlbihkYXRhKToKICAgICAgICBjbGVuLCBjdHlwZSA9IHN0cnVjdC51bnBhY2tfZnJvbSgiPEk0cyIsIGRhdGEs"
    "IG9mZikKICAgICAgICBwYXlsb2FkID0gZGF0YVtvZmYgKyA4OiBvZmYgKyA4ICsgY2xlbl0KICAgICAgICBpZiBjdHlwZSA9"
    "PSBiIkpTT04iOgogICAgICAgICAgICBqcyA9IGpzb24ubG9hZHMocGF5bG9hZC5kZWNvZGUoInV0Zi04IikpCiAgICAgICAg"
    "ZWxpZiBjdHlwZSA9PSBiIkJJTlx4MDAiOgogICAgICAgICAgICBiaW5fY2h1bmsgPSBwYXlsb2FkCiAgICAgICAgb2ZmICs9"
    "IDggKyBjbGVuICsgKCg0IC0gY2xlbiAlIDQpICUgNCBpZiBjbGVuICUgNCBlbHNlIDApCiAgICBpZiBqcyBpcyBOb25lOgog"
    "ICAgICAgIHJhaXNlIFZhbHVlRXJyb3IoZiJ7cGF0aH06IG5vIEpTT04gY2h1bmsiKQogICAgcmV0dXJuIGpzLCBiaW5fY2h1"
    "bmsKCgpkZWYgX2FjY2Vzc29yKGdsdGYsIGJsb2IsIGluZGV4KToKICAgICIiIkRlY29kZSBvbmUgYWNjZXNzb3IgaW50byBh"
    "IGZsYXQgbGlzdCBvZiB0dXBsZXMgKG9yIHNjYWxhcnMpLiIiIgogICAgYWNjID0gZ2x0ZlsiYWNjZXNzb3JzIl1baW5kZXhd"
    "CiAgICBuID0gYWNjWyJjb3VudCJdCiAgICBuY29tcCA9IF9OQ09NUFthY2NbInR5cGUiXV0KICAgIGZtdCwgc2l6ZSA9IF9D"
    "T01QT05FTlRbYWNjWyJjb21wb25lbnRUeXBlIl1dCiAgICBpZiAiYnVmZmVyVmlldyIgbm90IGluIGFjYzogICAgICAgICAg"
    "ICAgICAgICAgICMgc3BhcnNlLW9ubHkgLyB6ZXJvLWZpbGxlZAogICAgICAgIHJldHVybiBbKDAuMCwpICogbmNvbXAgaWYg"
    "bmNvbXAgPiAxIGVsc2UgMCBmb3IgXyBpbiByYW5nZShuKV0KICAgIGJ2ID0gZ2x0ZlsiYnVmZmVyVmlld3MiXVthY2NbImJ1"
    "ZmZlclZpZXciXV0KICAgIGJhc2UgPSBidi5nZXQoImJ5dGVPZmZzZXQiLCAwKSArIGFjYy5nZXQoImJ5dGVPZmZzZXQiLCAw"
    "KQogICAgc3RyaWRlID0gYnYuZ2V0KCJieXRlU3RyaWRlIikgb3IgKHNpemUgKiBuY29tcCkKICAgIG91dCA9IFtdCiAgICBm"
    "b3IgaSBpbiByYW5nZShuKToKICAgICAgICB2YWxzID0gc3RydWN0LnVucGFja19mcm9tKCI8IiArIGZtdCAqIG5jb21wLCBi"
    "bG9iLCBiYXNlICsgaSAqIHN0cmlkZSkKICAgICAgICBvdXQuYXBwZW5kKHZhbHMgaWYgbmNvbXAgPiAxIGVsc2UgdmFsc1sw"
    "XSkKICAgIHJldHVybiBvdXQKCgpkZWYgZ2xiX3ByaW1pdGl2ZXMoZ2x0ZiwgYmxvYik6CiAgICAiIiJZaWVsZCAocG9zaXRp"
    "b25zLCB0cmlhbmdsZXMpIHBlciBwcmltaXRpdmUsIGluIEZJTEUgc3BhY2UuCgogICAgTm9kZSB0cmFuc2Zvcm1zIGFyZSBh"
    "cHBsaWVkIHdoZW4gYSBub2RlIG5hbWVzIGEgbWF0cml4IG9yIFRSUzsgWm9vIGJ1aWxkcwogICAgZXZlcnl0aGluZyBhdCB3"
    "b3JsZCBzY2FsZSBpbiBwbGFjZSwgc28gaW4gcHJhY3RpY2UgdGhpcyBpcyBpZGVudGl0eSwgYnV0CiAgICB0aGUgdG9vbCBp"
    "cyBhbHNvIHBvaW50ZWQgYXQgbGV2ZWwgR0xCcyB3aGVyZSBpdCBpcyBub3QuCiAgICAiIiIKICAgIG5vZGVfeGZvcm0gPSB7"
    "fQogICAgZm9yIG5pLCBub2RlIGluIGVudW1lcmF0ZShnbHRmLmdldCgibm9kZXMiLCBbXSkpOgogICAgICAgIG0gPSBub2Rl"
    "LmdldCgibWF0cml4IikKICAgICAgICBpZiBtOgogICAgICAgICAgICAjIGdsVEYgbWF0cmljZXMgYXJlIGNvbHVtbi1tYWpv"
    "ci4KICAgICAgICAgICAgbm9kZV94Zm9ybVtuaV0gPSBbW21bMF0sIG1bNF0sIG1bOF0sIG1bMTJdXSwKICAgICAgICAgICAg"
    "ICAgICAgICAgICAgICAgICAgW21bMV0sIG1bNV0sIG1bOV0sIG1bMTNdXSwKICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgW21bMl0sIG1bNl0sIG1bMTBdLCBtWzE0XV1dCiAgICAgICAgZWxzZToKICAgICAgICAgICAgdCA9IG5vZGUuZ2V0KCJ0"
    "cmFuc2xhdGlvbiIsIFswLjAsIDAuMCwgMC4wXSkKICAgICAgICAgICAgcyA9IG5vZGUuZ2V0KCJzY2FsZSIsIFsxLjAsIDEu"
    "MCwgMS4wXSkKICAgICAgICAgICAgbm9kZV94Zm9ybVtuaV0gPSBbW3NbMF0sIDAuMCwgMC4wLCB0WzBdXSwKICAgICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgWzAuMCwgc1sxXSwgMC4wLCB0WzFdXSwKICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgWzAuMCwgMC4wLCBzWzJdLCB0WzJdXV0KICAgIG1lc2hfbm9kZXMgPSB7fQogICAgZm9yIG5pLCBub2RlIGluIGVudW1l"
    "cmF0ZShnbHRmLmdldCgibm9kZXMiLCBbXSkpOgogICAgICAgIGlmICJtZXNoIiBpbiBub2RlOgogICAgICAgICAgICBtZXNo"
    "X25vZGVzLnNldGRlZmF1bHQobm9kZVsibWVzaCJdLCBbXSkuYXBwZW5kKG5pKQoKICAgIGZvciBtaSwgbWVzaCBpbiBlbnVt"
    "ZXJhdGUoZ2x0Zi5nZXQoIm1lc2hlcyIsIFtdKSk6CiAgICAgICAgZm9yIHByaW0gaW4gbWVzaC5nZXQoInByaW1pdGl2ZXMi"
    "LCBbXSk6CiAgICAgICAgICAgIGlmIHByaW0uZ2V0KCJtb2RlIiwgNCkgIT0gNDogICAgICAgICAgICMgVFJJQU5HTEVTIG9u"
    "bHkKICAgICAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgICAgIHBvc19pZHggPSBwcmltLmdldCgiYXR0cmlidXRlcyIs"
    "IHt9KS5nZXQoIlBPU0lUSU9OIikKICAgICAgICAgICAgaWYgcG9zX2lkeCBpcyBOb25lOgogICAgICAgICAgICAgICAgY29u"
    "dGludWUKICAgICAgICAgICAgcG9zID0gX2FjY2Vzc29yKGdsdGYsIGJsb2IsIHBvc19pZHgpCiAgICAgICAgICAgIGlmICJp"
    "bmRpY2VzIiBpbiBwcmltOgogICAgICAgICAgICAgICAgaWR4ID0gX2FjY2Vzc29yKGdsdGYsIGJsb2IsIHByaW1bImluZGlj"
    "ZXMiXSkKICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIGlkeCA9IGxpc3QocmFuZ2UobGVuKHBvcykpKQogICAg"
    "ICAgICAgICB0cmlzID0gWyhpZHhbaV0sIGlkeFtpICsgMV0sIGlkeFtpICsgMl0pCiAgICAgICAgICAgICAgICAgICAgZm9y"
    "IGkgaW4gcmFuZ2UoMCwgbGVuKGlkeCkgLSAyLCAzKV0KICAgICAgICAgICAgZm9yIG5pIGluIG1lc2hfbm9kZXMuZ2V0KG1p"
    "LCBbTm9uZV0pOgogICAgICAgICAgICAgICAgaWYgbmkgaXMgTm9uZToKICAgICAgICAgICAgICAgICAgICB5aWVsZCBbdHVw"
    "bGUocCkgZm9yIHAgaW4gcG9zXSwgdHJpcwogICAgICAgICAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgICAgICAgICBN"
    "ID0gbm9kZV94Zm9ybVtuaV0KICAgICAgICAgICAgICAgIHlpZWxkIFt0dXBsZShNW3JdWzBdICogcFswXSArIE1bcl1bMV0g"
    "KiBwWzFdCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKyBNW3JdWzJdICogcFsyXSArIE1bcl1bM10gZm9yIHIgaW4g"
    "cmFuZ2UoMykpCiAgICAgICAgICAgICAgICAgICAgICAgZm9yIHAgaW4gcG9zXSwgdHJpcwoKCmRlZiBnbGJfYm91bmRzKGds"
    "dGYpOgogICAgIiIiQm91bmRzIHN0cmFpZ2h0IGZyb20gdGhlIFBPU0lUSU9OIGFjY2Vzc29ycycgZGVjbGFyZWQgbWluL21h"
    "eC4KCiAgICBUaGlzIGlzIHRoZSBudW1iZXIgdGhlIG9sZCBoZWlnaHQgY2hlY2sgd2FzIHJlYWNoaW5nIGZvciBhbmQgbmV2"
    "ZXIgZ290OgogICAgYGdsYl9ub2Rlcy5weWAgcmVhZHMgTk9ERSB0cmFuc2xhdGlvbnMsIGFuZCBhIFpvbyBkcmVzc2luZyBH"
    "TEIgaGFzIGV4YWN0bHkKICAgIG9uZSBub2RlIGF0IHRoZSBvcmlnaW4sIHNvIGl0IHJlcG9ydGVkICIwIHdpdGggYW4gZXhw"
    "bGljaXQgdHJhbnNsYXRpb24iIGFuZAogICAgbWVhc3VyZWQgbm90aGluZy4gIEFjY2Vzc29yIG1pbi9tYXggaXMgbWFuZGF0"
    "b3J5IG9uIFBPU0lUSU9OIGluIGdsVEYgMi4wLAogICAgc28gdGhpcyBhbHdheXMgZXhpc3RzIGFuZCBjb3N0cyBubyBkZWNv"
    "ZGluZy4KICAgICIiIgogICAgbG8gPSBbZmxvYXQoImluZiIpXSAqIDMKICAgIGhpID0gW2Zsb2F0KCItaW5mIildICogMwog"
    "ICAgc2VlbiA9IEZhbHNlCiAgICBmb3IgbWVzaCBpbiBnbHRmLmdldCgibWVzaGVzIiwgW10pOgogICAgICAgIGZvciBwcmlt"
    "IGluIG1lc2guZ2V0KCJwcmltaXRpdmVzIiwgW10pOgogICAgICAgICAgICBwaSA9IHByaW0uZ2V0KCJhdHRyaWJ1dGVzIiwg"
    "e30pLmdldCgiUE9TSVRJT04iKQogICAgICAgICAgICBpZiBwaSBpcyBOb25lOgogICAgICAgICAgICAgICAgY29udGludWUK"
    "ICAgICAgICAgICAgYWNjID0gZ2x0ZlsiYWNjZXNzb3JzIl1bcGldCiAgICAgICAgICAgIGlmICJtaW4iIG5vdCBpbiBhY2Mg"
    "b3IgIm1heCIgbm90IGluIGFjYzoKICAgICAgICAgICAgICAgIGNvbnRpbnVlCiAgICAgICAgICAgIHNlZW4gPSBUcnVlCiAg"
    "ICAgICAgICAgIGZvciBpIGluIHJhbmdlKDMpOgogICAgICAgICAgICAgICAgbG9baV0gPSBtaW4obG9baV0sIGFjY1sibWlu"
    "Il1baV0pCiAgICAgICAgICAgICAgICBoaVtpXSA9IG1heChoaVtpXSwgYWNjWyJtYXgiXVtpXSkKICAgIHJldHVybiAodHVw"
    "bGUobG8pLCB0dXBsZShoaSkpIGlmIHNlZW4gZWxzZSBOb25lCgoKIyAtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQojIFNtYWxsIGdlb21ldHJ5IGhlbHBlcnMgKG5v"
    "IG51bXB5LCBubyBzY2lweSkuCiMgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0KCmRlZiBfY3Jvc3MoYSwgYik6CiAgICByZXR1cm4gKGFbMV0gKiBiWzJdIC0gYVsy"
    "XSAqIGJbMV0sCiAgICAgICAgICAgIGFbMl0gKiBiWzBdIC0gYVswXSAqIGJbMl0sCiAgICAgICAgICAgIGFbMF0gKiBiWzFd"
    "IC0gYVsxXSAqIGJbMF0pCgoKZGVmIF9zdWIoYSwgYik6CiAgICByZXR1cm4gKGFbMF0gLSBiWzBdLCBhWzFdIC0gYlsxXSwg"
    "YVsyXSAtIGJbMl0pCgoKZGVmIGh1bGxfMmQocG9pbnRzKToKICAgICIiIkFuZHJldydzIG1vbm90b25lIGNoYWluLiAgUmV0"
    "dXJucyB0aGUgaHVsbCBpbiBDQ1cgb3JkZXIuIiIiCiAgICBwdHMgPSBzb3J0ZWQoc2V0KHBvaW50cykpCiAgICBpZiBsZW4o"
    "cHRzKSA8PSAyOgogICAgICAgIHJldHVybiBwdHMKCiAgICBkZWYgaGFsZihzZXEpOgogICAgICAgIG91dCA9IFtdCiAgICAg"
    "ICAgZm9yIHAgaW4gc2VxOgogICAgICAgICAgICB3aGlsZSBsZW4ob3V0KSA+PSAyOgogICAgICAgICAgICAgICAgKHgxLCB5"
    "MSksICh4MiwgeTIpID0gb3V0Wy0yXSwgb3V0Wy0xXQogICAgICAgICAgICAgICAgaWYgKHgyIC0geDEpICogKHBbMV0gLSB5"
    "MSkgLSAoeTIgLSB5MSkgKiAocFswXSAtIHgxKSA+IDA6CiAgICAgICAgICAgICAgICAgICAgYnJlYWsKICAgICAgICAgICAg"
    "ICAgIG91dC5wb3AoKQogICAgICAgICAgICBvdXQuYXBwZW5kKHApCiAgICAgICAgcmV0dXJuIG91dAoKICAgIHJldHVybiBo"
    "YWxmKHB0cylbOi0xXSArIGhhbGYocmV2ZXJzZWQocHRzKSlbOi0xXQoKCmRlZiBwb2x5X2FyZWEocG9seSk6CiAgICBpZiBs"
    "ZW4ocG9seSkgPCAzOgogICAgICAgIHJldHVybiAwLjAKICAgIHMgPSAwLjAKICAgIGZvciBpIGluIHJhbmdlKGxlbihwb2x5"
    "KSk6CiAgICAgICAgeDEsIHkxID0gcG9seVtpXQogICAgICAgIHgyLCB5MiA9IHBvbHlbKGkgKyAxKSAlIGxlbihwb2x5KV0K"
    "ICAgICAgICBzICs9IHgxICogeTIgLSB4MiAqIHkxCiAgICByZXR1cm4gYWJzKHMpICogMC41CgoKZGVmIF9odWxsX3JhZGlh"
    "bF9jdihodWxsLCBiaW5zPU5vbmUpOgogICAgIiIiQ29lZmZpY2llbnQgb2YgdmFyaWF0aW9uIG9mIHRoZSByYWRpdXMgb2Yg"
    "YSBjb252ZXggcG9seWdvbiwgc2FtcGxlZCBhdAogICAgZXZlbmx5IHNwYWNlZCBhbmdsZXMgZnJvbSBpdHMgaW50ZXJpb3Ig"
    "Y2VudHJvaWQuCgogICAgQW5jaG9ycywgc28gYSB0aHJlc2hvbGQgbWVhbnMgc29tZXRoaW5nOiAgY2lyY2xlIDAuMDAsIHNx"
    "dWFyZSAwLjA4NiwKICAgIDM6MSByZWN0YW5nbGUgMC40NC4gIEhpZ2hlciBtZWFucyBhIGxlc3MgcmVndWxhciBwbGFuIG91"
    "dGxpbmUuCiAgICAiIiIKICAgIGJpbnMgPSBiaW5zIG9yIFJBRElBTF9CSU5TCiAgICBpZiBsZW4oaHVsbCkgPCAzOgogICAg"
    "ICAgIHJldHVybiAwLjAKICAgIGN4ID0gc3VtKHBbMF0gZm9yIHAgaW4gaHVsbCkgLyBsZW4oaHVsbCkgICAgICAjIGluc2lk"
    "ZSwgaHVsbCBpcyBjb252ZXgKICAgIGN5ID0gc3VtKHBbMV0gZm9yIHAgaW4gaHVsbCkgLyBsZW4oaHVsbCkKICAgIHJhZGlp"
    "ID0gW10KICAgIGZvciBiIGluIHJhbmdlKGJpbnMpOgogICAgICAgIHRoID0gMiAqIG1hdGgucGkgKiBiIC8gYmlucwogICAg"
    "ICAgIGR4LCBkeSA9IG1hdGguY29zKHRoKSwgbWF0aC5zaW4odGgpCiAgICAgICAgYmVzdCA9IE5vbmUKICAgICAgICBmb3Ig"
    "aSBpbiByYW5nZShsZW4oaHVsbCkpOgogICAgICAgICAgICB4MSwgeTEgPSBodWxsW2ldCiAgICAgICAgICAgIHgyLCB5MiA9"
    "IGh1bGxbKGkgKyAxKSAlIGxlbihodWxsKV0KICAgICAgICAgICAgZXgsIGV5ID0geDIgLSB4MSwgeTIgLSB5MQogICAgICAg"
    "ICAgICBkZW4gPSBkeCAqIGV5IC0gZHkgKiBleAogICAgICAgICAgICBpZiBhYnMoZGVuKSA8IDFlLTE1OgogICAgICAgICAg"
    "ICAgICAgY29udGludWUKICAgICAgICAgICAgdCA9ICgoeDEgLSBjeCkgKiBleSAtICh5MSAtIGN5KSAqIGV4KSAvIGRlbgog"
    "ICAgICAgICAgICBzc2VnID0gKCh4MSAtIGN4KSAqIGR5IC0gKHkxIC0gY3kpICogZHgpIC8gZGVuCiAgICAgICAgICAgIGlm"
    "IHQgPj0gMCBhbmQgLTFlLTkgPD0gc3NlZyA8PSAxICsgMWUtOToKICAgICAgICAgICAgICAgIGJlc3QgPSB0IGlmIGJlc3Qg"
    "aXMgTm9uZSBlbHNlIG1pbihiZXN0LCB0KQogICAgICAgIGlmIGJlc3QgaXMgbm90IE5vbmU6CiAgICAgICAgICAgIHJhZGlp"
    "LmFwcGVuZChiZXN0KQogICAgaWYgbGVuKHJhZGlpKSA8IDM6CiAgICAgICAgcmV0dXJuIDAuMAogICAgbWVhbl9yID0gc3Vt"
    "KHJhZGlpKSAvIGxlbihyYWRpaSkKICAgIGlmIG1lYW5fciA8PSAwOgogICAgICAgIHJldHVybiAwLjAKICAgIHZhciA9IHN1"
    "bSgociAtIG1lYW5fcikgKiogMiBmb3IgciBpbiByYWRpaSkgLyBsZW4ocmFkaWkpCiAgICByZXR1cm4gbWF0aC5zcXJ0KHZh"
    "cikgLyBtZWFuX3IKCgojIC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tCiMgU1BFQ0lNRU4gbWV0cmljcwojIC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCgpkZWYgbWVzaF9tZXRyaWNzKHZlcnRzLCB0cmlz"
    "LCB1cD0xKToKICAgICIiIlNoYXBlIG1ldHJpY3MgZm9yIG9uZSB0cmlhbmdsZSBzb3VwLgoKICAgIGB2ZXJ0c2AgaXMgYSBz"
    "ZXF1ZW5jZSBvZiAoeCwgeSwgeik7IGB0cmlzYCBhIHNlcXVlbmNlIG9mIGluZGV4IHRyaXBsZXM7CiAgICBgdXBgIHRoZSBp"
    "bmRleCBvZiB0aGUgdmVydGljYWwgYXhpcyAoMSBmb3IgZ2xURiBZLXVwLCAyIGZvciBCbGVuZGVyIFotdXApLgogICAgIiIi"
    "CiAgICBpZiBub3QgdmVydHMgb3Igbm90IHRyaXM6CiAgICAgICAgcmV0dXJuIHsiZXJyb3IiOiAiZW1wdHkgbWVzaCIsICJ0"
    "cmlzIjogMCwgInZlcnRzIjogbGVuKHZlcnRzKX0KCiAgICBheCA9IFtpIGZvciBpIGluIHJhbmdlKDMpIGlmIGkgIT0gdXBd"
    "ICAgICAgICAgICMgdGhlIHR3byBncm91bmQgYXhlcwogICAgbG8gPSBbbWluKHZbaV0gZm9yIHYgaW4gdmVydHMpIGZvciBp"
    "IGluIHJhbmdlKDMpXQogICAgaGkgPSBbbWF4KHZbaV0gZm9yIHYgaW4gdmVydHMpIGZvciBpIGluIHJhbmdlKDMpXQogICAg"
    "ZXh0ID0gW2hpW2ldIC0gbG9baV0gZm9yIGkgaW4gcmFuZ2UoMyldCgogICAgIyAtLS0gcGVyLWZhY2UgYXJlYSwgbm9ybWFs"
    "LCBzaWduZWQgdm9sdW1lIC0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQogICAgdG90YWxfYXJlYSA9IDAuMAogICAg"
    "dm9sNiA9IDAuMAogICAgZmFjZXMgPSBbXSAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAjIChhcmVhLCB1"
    "bml0IG5vcm1hbCkKICAgIGxhcmdlc3QgPSAwLjAKICAgIGZvciAoaSwgaiwgaykgaW4gdHJpczoKICAgICAgICBwLCBxLCBy"
    "ID0gdmVydHNbaV0sIHZlcnRzW2pdLCB2ZXJ0c1trXQogICAgICAgIG4gPSBfY3Jvc3MoX3N1YihxLCBwKSwgX3N1YihyLCBw"
    "KSkKICAgICAgICBtYWcgPSBtYXRoLnNxcnQoblswXSAqKiAyICsgblsxXSAqKiAyICsgblsyXSAqKiAyKQogICAgICAgIGFy"
    "ZWEgPSBtYWcgKiAwLjUKICAgICAgICBpZiBtYWcgPD0gMWUtMTg6CiAgICAgICAgICAgIGNvbnRpbnVlICAgICAgICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICMgZGVnZW5lcmF0ZSBzbGl2ZXIKICAgICAgICB0b3RhbF9hcmVhICs9IGFyZWEKICAgICAg"
    "ICBsYXJnZXN0ID0gbWF4KGxhcmdlc3QsIGFyZWEpCiAgICAgICAgZmFjZXMuYXBwZW5kKChhcmVhLCAoblswXSAvIG1hZywg"
    "blsxXSAvIG1hZywgblsyXSAvIG1hZykpKQogICAgICAgIHZvbDYgKz0gKHBbMF0gKiAocVsxXSAqIHJbMl0gLSBxWzJdICog"
    "clsxXSkKICAgICAgICAgICAgICAgICAtIHBbMV0gKiAocVswXSAqIHJbMl0gLSBxWzJdICogclswXSkKICAgICAgICAgICAg"
    "ICAgICArIHBbMl0gKiAocVswXSAqIHJbMV0gLSBxWzFdICogclswXSkpCiAgICB2b2x1bWUgPSBhYnModm9sNikgLyA2LjAK"
    "CiAgICAjIENsb3NlZG5lc3MuICBUaGUgc2lnbmVkLXZvbHVtZSBzdW0gYWJvdmUgaXMgb25seSBtZWFuaW5nZnVsIG9uIGEg"
    "Y2xvc2VkCiAgICAjIHN1cmZhY2UsIGFuZCBhbiBvcGVuIG9uZSBpcyBhIHJlYWwgZGVmZWN0IGluIGEgc2hpcHBlZCBhc3Nl"
    "dCBiZXNpZGVzOgogICAgIyB5b3Ugc2VlIHRocm91Z2ggaXQgZnJvbSBvbmUgc2lkZSBhbmQgaXRzIGxpZ2h0aW5nIGlzIHdy"
    "b25nLiAgQW4gZWRnZQogICAgIyB1c2VkIGJ5IGV4YWN0bHkgb25lIHRyaWFuZ2xlIGlzIGEgaG9sZS4KICAgIGVkZ2VfdXNl"
    "ID0ge30KICAgIGZvciAoaSwgaiwgaykgaW4gdHJpczoKICAgICAgICBmb3IgdSwgdiBpbiAoKGksIGopLCAoaiwgayksIChr"
    "LCBpKSk6CiAgICAgICAgICAgIGVkZ2VfdXNlWyh1LCB2KSBpZiB1IDwgdiBlbHNlICh2LCB1KV0gPSBcCiAgICAgICAgICAg"
    "ICAgICBlZGdlX3VzZS5nZXQoKHUsIHYpIGlmIHUgPCB2IGVsc2UgKHYsIHUpLCAwKSArIDEKICAgIG9wZW5fZWRnZXMgPSBz"
    "dW0oMSBmb3IgbiBpbiBlZGdlX3VzZS52YWx1ZXMoKSBpZiBuID09IDEpCiAgICBub25tYW5pZm9sZCA9IHN1bSgxIGZvciBu"
    "IGluIGVkZ2VfdXNlLnZhbHVlcygpIGlmIG4gPiAyKQoKICAgICMgLS0tIHByb3BvcnRpb246IHNvcnRlZCBleHRlbnRzLCBa"
    "aW5nZyBjbGFzcyAtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0KICAgIGEsIGIsIGMgPSBzb3J0ZWQoZXh0LCByZXZlcnNl"
    "PVRydWUpICAgICAgICAgICAgIyBhID49IGIgPj0gYwogICAgZWxvbmcgPSAoYiAvIGEpIGlmIGEgPiAwIGVsc2UgMC4wICAg"
    "ICAgICAgICAgICAjIGIvYQogICAgZmxhdCA9IChjIC8gYikgaWYgYiA+IDAgZWxzZSAwLjAgICAgICAgICAgICAgICAjIGMv"
    "YgogICAgIyBaaW5nZyAoMTkzNSkgc3BsaXRzIGdyYXZlbCBzaGFwZSBvbiBiL2EgYW5kIGMvYiBhdCAyLzMuICBSZWFsIGdy"
    "YXZlbAogICAgIyBwb3B1bGF0aW9ucyBzaXQgbW9zdGx5IGluIGJsYWRlK2Rpc2M7IGEgcHJvY2VkdXJhbCBnZW5lcmF0b3Ig"
    "dGhhdCBvbmx5CiAgICAjIGV2ZXIgZW1pdHMgYGVxdWFudGAgaXMgZW1pdHRpbmcgYmFsbHMsIGFuZCB0aGF0IGlzIHRoZSBz"
    "aW5nbGUgbW9zdAogICAgIyAicHJvY2VkdXJhbCIgc2lsaG91ZXR0ZSB0aGVyZSBpcy4KICAgIHppbmdnID0gKCgiZXF1YW50"
    "IiBpZiBmbGF0ID4gMiAvIDMgZWxzZSAiZGlzYyIpIGlmIGVsb25nID4gMiAvIDMKICAgICAgICAgICAgIGVsc2UgKCJyb2Qi"
    "IGlmIGZsYXQgPiAyIC8gMyBlbHNlICJibGFkZSIpKQoKICAgIGJib3hfdm9sID0gZXh0WzBdICogZXh0WzFdICogZXh0WzJd"
    "CiAgICBvY2N1cGFuY3kgPSAodm9sdW1lIC8gYmJveF92b2wpIGlmIGJib3hfdm9sID4gMWUtMTggZWxzZSAwLjAKCiAgICAj"
    "IC0tLSBmbGF0bmVzcyB0ZWxscyAtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "CiAgICAjIGRvbWluYW50X2ZhY2Vfc2hhcmU6IHRoZSBiaWdnZXN0IGNvcGxhbmFyIHJlZ2lvbiBhcyBhIGZyYWN0aW9uIG9m"
    "IHN1cmZhY2UKICAgICMgYXJlYS4gIFRoaXMgaXMgdGhlIG1ldHJpYyB0aGF0IGNhdGNoZXMgInlvdSBqaXR0ZXJlZCBhIGN1"
    "YmUncyA4IGNvcm5lcnMsCiAgICAjIHNvIGFsbCBzaXggZmFjZXMgYXJlIHN0aWxsIHNpbmdsZSBwbGFuZXMiLgogICAgY29z"
    "X2NvID0gbWF0aC5jb3MobWF0aC5yYWRpYW5zKENPUExBTkFSX0RFRykpCiAgICBkb21pbmFudCA9IDAuMAogICAgcHJvYmUg"
    "PSBmYWNlcyBpZiBsZW4oZmFjZXMpIDw9IDMwMDAgZWxzZSBmYWNlc1s6Om1heCgxLCBsZW4oZmFjZXMpIC8vIDMwMDApXQog"
    "ICAgZm9yIF8sIG4wIGluIHByb2JlOgogICAgICAgIHMgPSAwLjAKICAgICAgICBmb3IgYXJlYSwgbiBpbiBmYWNlczoKICAg"
    "ICAgICAgICAgaWYgbjBbMF0gKiBuWzBdICsgbjBbMV0gKiBuWzFdICsgbjBbMl0gKiBuWzJdID49IGNvc19jbzoKICAgICAg"
    "ICAgICAgICAgIHMgKz0gYXJlYQogICAgICAgIGRvbWluYW50ID0gbWF4KGRvbWluYW50LCBzKQogICAgZG9taW5hbnRfc2hh"
    "cmUgPSBkb21pbmFudCAvIHRvdGFsX2FyZWEgaWYgdG90YWxfYXJlYSA+IDAgZWxzZSAwLjAKCiAgICAjIG5vcm1hbF9yZWdp"
    "b25zXzgwOiBob3cgbWFueSBkaXN0aW5jdCBmYWNpbmcgZGlyZWN0aW9ucyBpdCB0YWtlcyB0bwogICAgIyBhY2NvdW50IGZv"
    "ciA4MCUgb2YgdGhlIHN1cmZhY2UuICBUSElTIGlzIHRoZSBudW1iZXIgdGhhdCBjYXRjaGVzCiAgICAjICJ5b3Ugaml0dGVy"
    "ZWQgYSBjdWJlJ3MgOCBjb3JuZXJzIi4gIEppdHRlcmluZyBtb3ZlcyB2ZXJ0aWNlcyBidXQgbm90CiAgICAjIGZhY2UgY291"
    "bnQsIHNvIGEgaml0dGVyZWQgYm94IHN0aWxsIGhhcyA2IGZhY2luZyBkaXJlY3Rpb25zIGFuZCByZWFkcyBhcwogICAgIyBh"
    "IGJveCBubyBtYXR0ZXIgaG93IGZhciB0aGUgY29ybmVycyB0cmF2ZWw7IGlycmVndWxhcml0eSBpcyBib3VuZGVkCiAgICAj"
    "IGFib3ZlIGJ5IGZhY2UgY291bnQsIGFuZCB0aGlzIG1lYXN1cmVzIHRoZSBib3VuZCByYXRoZXIgdGhhbiB0aGUgaW50ZW50"
    "LgogICAgIyBBbmNob3JzOiBjdWJlIDUsIHV2LXNwaGVyZSgyNHgxMikgfjUwKy4KICAgIGNvc19yZWcgPSBtYXRoLmNvcyht"
    "YXRoLnJhZGlhbnMoUkVHSU9OX0RFRykpCiAgICByZW1haW5pbmcgPSBsaXN0KGZhY2VzKQogICAgcmVnaW9ucywgY292ZXJl"
    "ZCA9IDAsIDAuMAogICAgdGFyZ2V0ID0gdG90YWxfYXJlYSAqIDAuODAKICAgIHdoaWxlIHJlbWFpbmluZyBhbmQgY292ZXJl"
    "ZCA8IHRhcmdldDoKICAgICAgICBiZXN0X24sIGJlc3RfcyA9IE5vbmUsIC0xLjAKICAgICAgICBmb3IgXywgbjAgaW4gcmVt"
    "YWluaW5nOgogICAgICAgICAgICBhY2MgPSBzdW0oYXJlYSBmb3IgYXJlYSwgbiBpbiByZW1haW5pbmcKICAgICAgICAgICAg"
    "ICAgICAgICAgIGlmIG4wWzBdICogblswXSArIG4wWzFdICogblsxXSArIG4wWzJdICogblsyXSA+PSBjb3NfcmVnKQogICAg"
    "ICAgICAgICBpZiBhY2MgPiBiZXN0X3M6CiAgICAgICAgICAgICAgICBiZXN0X3MsIGJlc3RfbiA9IGFjYywgbjAKICAgICAg"
    "ICBjb3ZlcmVkICs9IGJlc3RfcwogICAgICAgIHJlZ2lvbnMgKz0gMQogICAgICAgIHJlbWFpbmluZyA9IFsoYXJlYSwgbikg"
    "Zm9yIGFyZWEsIG4gaW4gcmVtYWluaW5nCiAgICAgICAgICAgICAgICAgICAgIGlmIChiZXN0X25bMF0gKiBuWzBdICsgYmVz"
    "dF9uWzFdICogblsxXQogICAgICAgICAgICAgICAgICAgICAgICAgKyBiZXN0X25bMl0gKiBuWzJdKSA8IGNvc19yZWddCiAg"
    "ICAgICAgaWYgcmVnaW9ucyA+IDQwMDogICAgICAgICAgICAgICAgICAgICAgICAgICMgcnVuYXdheSBndWFyZAogICAgICAg"
    "ICAgICBicmVhawoKICAgIGNvc191cCA9IG1hdGguY29zKG1hdGgucmFkaWFucyhVUEZBQ0VfREVHKSkKICAgIHVwX2FyZWEg"
    "PSBzdW0oYXJlYSBmb3IgYXJlYSwgbiBpbiBmYWNlcyBpZiBuW3VwXSA+PSBjb3NfdXApCiAgICB1cF9zaGFyZSA9IHVwX2Fy"
    "ZWEgLyB0b3RhbF9hcmVhIGlmIHRvdGFsX2FyZWEgPiAwIGVsc2UgMC4wCiAgICBsYXJnZXN0X3NoYXJlID0gbGFyZ2VzdCAv"
    "IHRvdGFsX2FyZWEgaWYgdG90YWxfYXJlYSA+IDAgZWxzZSAwLjAKCiAgICAjIC0tLSBwbGFuLXZpZXcgc2lsaG91ZXR0ZSAt"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0KICAgICMgTWVhc3VyZWQgb24gdGhlIHBsYW4t"
    "dmlldyBjb252ZXggSFVMTCwgc2FtcGxlZCBieSByYXktY2FzdCBhdCBmaXhlZAogICAgIyBhbmdsZXMgLS0gbm90IGJ5IGJp"
    "bm5pbmcgdGhlIHJhdyBwb2ludCBjbG91ZC4gIEJpbm5pbmcgdGhlIGNsb3VkIG1ha2VzCiAgICAjIHRoZSBudW1iZXIgZGVw"
    "ZW5kIG9uIGhvdyBtYW55IHNlZ21lbnRzIHRoZSBwcmltaXRpdmUgaGFwcGVuZWQgdG8gaGF2ZQogICAgIyAoYSAyNC1jb2x1"
    "bW4gc3BoZXJlIGxlYXZlcyBhIHRoaXJkIG9mIHRoZSBiaW5zIGVtcHR5IGFuZCBpbnZlbnRzCiAgICAjIHZhcmlhdGlvbiB0"
    "aGF0IGlzIG5vdCBpbiB0aGUgc2hhcGUpLCBhbmQgYSBtZXRyaWMgd2hvc2UgdmFsdWUgbW92ZXMgd2hlbgogICAgIyB0aGUg"
    "dGVzc2VsbGF0aW9uIG1vdmVzIGlzIG5vdCBtZWFzdXJpbmcgdGhlIHNpbGhvdWV0dGUuCiAgICBwbGFuID0gWyh2W2F4WzBd"
    "XSwgdltheFsxXV0pIGZvciB2IGluIHZlcnRzXQogICAgcGggPSBodWxsXzJkKHBsYW4pCiAgICBodWxsX2FyZWEgPSBwb2x5"
    "X2FyZWEocGgpCiAgICByYWRpYWxfY3YgPSBfaHVsbF9yYWRpYWxfY3YocGgpCiAgICBmb290X2Jib3ggPSBleHRbYXhbMF1d"
    "ICogZXh0W2F4WzFdXQogICAgaHVsbF9maWxsID0gaHVsbF9hcmVhIC8gZm9vdF9iYm94IGlmIGZvb3RfYmJveCA+IDFlLTE4"
    "IGVsc2UgMC4wCgogICAgIyAtLS0gZ3JvdW5kIGNvbnRhY3QgLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLQogICAgZXBzID0gbWF4KDFlLTYsIGV4dFt1cF0gKiAwLjAyKQogICAgYmFzZV9wdHMgPSBbKHZb"
    "YXhbMF1dLCB2W2F4WzFdXSkgZm9yIHYgaW4gdmVydHMgaWYgdlt1cF0gLSBsb1t1cF0gPD0gZXBzXQogICAgYmFzZV9hcmVh"
    "ID0gcG9seV9hcmVhKGh1bGxfMmQoYmFzZV9wdHMpKSBpZiBsZW4oYmFzZV9wdHMpID49IDMgZWxzZSAwLjAKICAgIGJhc2Vf"
    "cmF0aW8gPSBiYXNlX2FyZWEgLyBodWxsX2FyZWEgaWYgaHVsbF9hcmVhID4gMWUtMTggZWxzZSAwLjAKCiAgICByZXR1cm4g"
    "ewogICAgICAgICJ0cmlzIjogbGVuKHRyaXMpLAogICAgICAgICJ2ZXJ0cyI6IGxlbih2ZXJ0cyksCiAgICAgICAgImJib3gi"
    "OiBbcm91bmQoZSwgNSkgZm9yIGUgaW4gZXh0XSwKICAgICAgICAiZXh0ZW50X3VwIjogcm91bmQoZXh0W3VwXSwgNSksCiAg"
    "ICAgICAgImJhc2VfYXQiOiByb3VuZChsb1t1cF0sIDUpLAogICAgICAgICJheGlzX2FiYyI6IFtyb3VuZChhLCA1KSwgcm91"
    "bmQoYiwgNSksIHJvdW5kKGMsIDUpXSwKICAgICAgICAiZWxvbmdhdGlvbl9iYSI6IHJvdW5kKGVsb25nLCAzKSwKICAgICAg"
    "ICAiZmxhdG5lc3NfY2IiOiByb3VuZChmbGF0LCAzKSwKICAgICAgICAiemluZ2ciOiB6aW5nZywKICAgICAgICAidm9sdW1l"
    "Ijogcm91bmQodm9sdW1lLCA4KSwKICAgICAgICAib3Blbl9lZGdlcyI6IG9wZW5fZWRnZXMsCiAgICAgICAgIm5vbm1hbmlm"
    "b2xkX2VkZ2VzIjogbm9ubWFuaWZvbGQsCiAgICAgICAgImNsb3NlZCI6IG9wZW5fZWRnZXMgPT0gMCBhbmQgbm9ubWFuaWZv"
    "bGQgPT0gMCwKICAgICAgICAic3VyZmFjZV9hcmVhIjogcm91bmQodG90YWxfYXJlYSwgNiksCiAgICAgICAgImJib3hfb2Nj"
    "dXBhbmN5Ijogcm91bmQob2NjdXBhbmN5LCAzKSwKICAgICAgICAiZG9taW5hbnRfZmFjZV9zaGFyZSI6IHJvdW5kKGRvbWlu"
    "YW50X3NoYXJlLCAzKSwKICAgICAgICAibm9ybWFsX3JlZ2lvbnNfODAiOiByZWdpb25zLAogICAgICAgICJ1cF9mYWNpbmdf"
    "c2hhcmUiOiByb3VuZCh1cF9zaGFyZSwgMyksCiAgICAgICAgImxhcmdlc3RfZmFjZV9zaGFyZSI6IHJvdW5kKGxhcmdlc3Rf"
    "c2hhcmUsIDMpLAogICAgICAgICJwbGFuX3JhZGlhbF9jdiI6IHJvdW5kKHJhZGlhbF9jdiwgMyksCiAgICAgICAgInBsYW5f"
    "aHVsbF9maWxsIjogcm91bmQoaHVsbF9maWxsLCAzKSwKICAgICAgICAiYmFzZV9jb250YWN0X3JhdGlvIjogcm91bmQoYmFz"
    "ZV9yYXRpbywgMyksCiAgICB9CgoKZGVmIGdsYl9tZXRyaWNzKHBhdGgsIHVwPTEpOgogICAgIiIiTWV0cmljcyBmb3IgYSBH"
    "TEIsIG1lcmdpbmcgZXZlcnkgdHJpYW5nbGUgcHJpbWl0aXZlIGludG8gb25lIHNvdXAuCgogICAgTWVyZ2luZyBpcyBjb3Jy"
    "ZWN0IGZvciB0aGVzZSBzcGVjaWVzOiBhIGBwZWJibGVgIHNwZWNpbWVuIGlzIHRocmVlIHN0b25lcwogICAgdGhhdCBzaGlw"
    "IGFzIG9uZSBtZXNoIGFuZCBhcmUgc2VlbiBhcyBvbmUgY2x1bXAuICBGb3IgYSBtdWx0aS1wYXJ0IGFzc2V0CiAgICB0aGUg"
    "Y2FsbGVyIHdhbnRzIHBlci1wcmltaXRpdmUgbnVtYmVycyBpbnN0ZWFkIC0tIHVzZSBgZ2xiX3ByaW1pdGl2ZXNgLgogICAg"
    "IiIiCiAgICBnbHRmLCBibG9iID0gcmVhZF9nbGIocGF0aCkKICAgIHZlcnRzLCB0cmlzID0gW10sIFtdCiAgICBmb3IgcG9z"
    "LCBpZHggaW4gZ2xiX3ByaW1pdGl2ZXMoZ2x0ZiwgYmxvYik6CiAgICAgICAgb2ZmID0gbGVuKHZlcnRzKQogICAgICAgIHZl"
    "cnRzLmV4dGVuZChwb3MpCiAgICAgICAgdHJpcy5leHRlbmQoWyhpICsgb2ZmLCBqICsgb2ZmLCBrICsgb2ZmKSBmb3IgKGks"
    "IGosIGspIGluIGlkeF0pCiAgICBtID0gbWVzaF9tZXRyaWNzKHZlcnRzLCB0cmlzLCB1cD11cCkKICAgIG1bImZpbGUiXSA9"
    "IG9zLnBhdGguYmFzZW5hbWUocGF0aCkKICAgIGIgPSBnbGJfYm91bmRzKGdsdGYpCiAgICBpZiBiOgogICAgICAgIG1bImFj"
    "Y2Vzc29yX2V4dGVudF91cCJdID0gcm91bmQoYlsxXVt1cF0gLSBiWzBdW3VwXSwgNSkKICAgIHJldHVybiBtCgoKIyAtLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQoj"
    "IFBBVENIIG1ldHJpY3MgLS0gdGhlIHVuaXQgdGhhdCBhY3R1YWxseSByZWFkcyBvbiBzY3JlZW4KIyAtLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQoKZGVmIHBhdGNo"
    "X21ldHJpY3MocG9pbnRzLCBhcmVhPU5vbmUpOgogICAgIiIiRGlzdHJpYnV0aW9uIHN0YXRpc3RpY3MgZm9yIGEgc2NhdHRl"
    "ciBvZiBwbGFjZW1lbnRzLgoKICAgIGBwb2ludHNgIGlzIGEgc2VxdWVuY2Ugb2YgKHgsIHkpIGdyb3VuZCBwb3NpdGlvbnMu"
    "ICBgYXJlYWAgaXMgdGhlIHJlZ2lvbgogICAgdGhleSB3ZXJlIHNjYXR0ZXJlZCBvdmVyOyB3aGVuIG9taXR0ZWQgdGhlIGNv"
    "bnZleCBodWxsIG9mIHRoZSBwb2ludHMgaXMKICAgIHVzZWQsIHdoaWNoIFVOREVSU1RBVEVTIGFyZWEgZm9yIGEgY2x1c3Rl"
    "cmVkIHNldCBhbmQgdGhlcmVmb3JlIGJpYXNlcyBSCiAgICB1cHdhcmQgLS0gcGFzcyB0aGUgcmVhbCByZWdpb24gYXJlYSB3"
    "aGVuIHRoZSBjYWxsZXIga25vd3MgaXQuCgogICAgQ2xhcmsgJiBFdmFucyAoMTk1NCkgUiA9IG9ic2VydmVkIG1lYW4gbmVh"
    "cmVzdC1uZWlnaGJvdXIgZGlzdGFuY2UgZGl2aWRlZAogICAgYnkgdGhlIG1lYW4gZXhwZWN0ZWQgdW5kZXIgY29tcGxldGUg"
    "c3BhdGlhbCByYW5kb21uZXNzICgwLjUgLyBzcXJ0KGRlbnNpdHkpKS4KCiAgICAgICAgUiAgPCAxICAgY2x1c3RlcmVkICAg"
    "ICAgPC0gd2hhdCByZWFsIGRlYnJpcyBkb2VzCiAgICAgICAgUiA9PSAxICAgcmFuZG9tCiAgICAgICAgUiAgPiAxICAgZGlz"
    "cGVyc2VkICAgICAgPC0gd2hhdCBhIG5haXZlIGV2ZW4gc2NhdHRlciBkb2VzOyBSID0gMi4wIGZvcgogICAgICAgICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgIGEgcGVyZmVjdCBzcXVhcmUgbGF0dGljZQoKICAgIFRoaXMgaXMgYGRvY3MvU1VSRkFD"
    "RV9EUkVTU0lORy5tZGAncyAibm8gb2J2aW91cyB1bmlmb3JtIHNjYXR0ZXIgcGF0dGVybiIKICAgIGV4cHJlc3NlZCBhcyBz"
    "b21ldGhpbmcgYSB0ZXN0IGNhbiBhc3NlcnQgb24uCiAgICAiIiIKICAgIG4gPSBsZW4ocG9pbnRzKQogICAgaWYgbiA8IDM6"
    "CiAgICAgICAgcmV0dXJuIHsibiI6IG4sICJlcnJvciI6ICJuZWVkIGF0IGxlYXN0IDMgcG9pbnRzIn0KICAgIG5uID0gW10K"
    "ICAgIGZvciBpLCAoeDEsIHkxKSBpbiBlbnVtZXJhdGUocG9pbnRzKToKICAgICAgICBiZXN0ID0gZmxvYXQoImluZiIpCiAg"
    "ICAgICAgZm9yIGosICh4MiwgeTIpIGluIGVudW1lcmF0ZShwb2ludHMpOgogICAgICAgICAgICBpZiBpID09IGo6CiAgICAg"
    "ICAgICAgICAgICBjb250aW51ZQogICAgICAgICAgICBkID0gKHgxIC0geDIpICoqIDIgKyAoeTEgLSB5MikgKiogMgogICAg"
    "ICAgICAgICBpZiBkIDwgYmVzdDoKICAgICAgICAgICAgICAgIGJlc3QgPSBkCiAgICAgICAgbm4uYXBwZW5kKG1hdGguc3Fy"
    "dChiZXN0KSkKICAgIG1lYW5fbm4gPSBzdW0obm4pIC8gbgogICAgdmFyID0gc3VtKChkIC0gbWVhbl9ubikgKiogMiBmb3Ig"
    "ZCBpbiBubikgLyBuCiAgICBjdiA9IG1hdGguc3FydCh2YXIpIC8gbWVhbl9ubiBpZiBtZWFuX25uID4gMCBlbHNlIDAuMAoK"
    "ICAgIGlmIGFyZWEgaXMgTm9uZToKICAgICAgICBhcmVhID0gcG9seV9hcmVhKGh1bGxfMmQobGlzdChwb2ludHMpKSkKICAg"
    "IGRlbnNpdHkgPSAobiAvIGFyZWEpIGlmIGFyZWEgYW5kIGFyZWEgPiAwIGVsc2UgMC4wCiAgICBleHBlY3RlZCA9IDAuNSAv"
    "IG1hdGguc3FydChkZW5zaXR5KSBpZiBkZW5zaXR5ID4gMCBlbHNlIDAuMAogICAgUiA9IChtZWFuX25uIC8gZXhwZWN0ZWQp"
    "IGlmIGV4cGVjdGVkID4gMCBlbHNlIDAuMAogICAgcmVhZGluZyA9ICgiY2x1c3RlcmVkIiBpZiBSIDwgMC44NQogICAgICAg"
    "ICAgICAgICBlbHNlICgicmFuZG9tIiBpZiBSIDwgMS4xNSBlbHNlICJkaXNwZXJzZWQiKSkKICAgIHJldHVybiB7CiAgICAg"
    "ICAgIm4iOiBuLAogICAgICAgICJtZWFuX25uIjogcm91bmQobWVhbl9ubiwgNSksCiAgICAgICAgIm5uX2N2Ijogcm91bmQo"
    "Y3YsIDMpLAogICAgICAgICJkZW5zaXR5Ijogcm91bmQoZGVuc2l0eSwgNCksCiAgICAgICAgImNsYXJrX2V2YW5zX1IiOiBy"
    "b3VuZChSLCAzKSwKICAgICAgICAicmVhZGluZyI6IHJlYWRpbmcsCiAgICB9CgoKIyAtLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQojIHNlbGZ0ZXN0CiMgLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0KCmRl"
    "ZiBfdW5pdF9jdWJlKCk6CiAgICB2ID0gWyh4LCB5LCB6KSBmb3IgeiBpbiAoMC4wLCAxLjApIGZvciB5IGluICgwLjAsIDEu"
    "MCkgZm9yIHggaW4gKDAuMCwgMS4wKV0KICAgICMgMDooMCwwLDApIDE6KDEsMCwwKSAyOigwLDEsMCkgMzooMSwxLDApIDQ6"
    "KDAsMCwxKSA1OigxLDAsMSkgNjooMCwxLDEpIDc6KDEsMSwxKQogICAgcSA9IFsoMCwgMiwgMywgMSksICg0LCA1LCA3LCA2"
    "KSwgKDAsIDEsIDUsIDQpLAogICAgICAgICAoMiwgNiwgNywgMyksICgwLCA0LCA2LCAyKSwgKDEsIDMsIDcsIDUpXQogICAg"
    "dCA9IFtdCiAgICBmb3IgYSwgYiwgYywgZCBpbiBxOgogICAgICAgIHQgKz0gWyhhLCBiLCBjKSwgKGEsIGMsIGQpXQogICAg"
    "cmV0dXJuIHYsIHQKCgpkZWYgX3NsYWIoaCk6CiAgICB2LCB0ID0gX3VuaXRfY3ViZSgpCiAgICByZXR1cm4gWyh4LCB5LCB6"
    "ICogaCkgZm9yICh4LCB5LCB6KSBpbiB2XSwgdAoKCmRlZiBfdXZfc3BoZXJlKHU9MjQsIHZzZWc9MTIsIHI9MC41KToKICAg"
    "IHZlcnRzLCB0cmlzID0gW10sIFtdCiAgICBmb3IgaSBpbiByYW5nZSh2c2VnICsgMSk6CiAgICAgICAgcGhpID0gbWF0aC5w"
    "aSAqIGkgLyB2c2VnCiAgICAgICAgZm9yIGogaW4gcmFuZ2UodSk6CiAgICAgICAgICAgIHRoID0gMiAqIG1hdGgucGkgKiBq"
    "IC8gdQogICAgICAgICAgICB2ZXJ0cy5hcHBlbmQoKHIgKiBtYXRoLnNpbihwaGkpICogbWF0aC5jb3ModGgpLAogICAgICAg"
    "ICAgICAgICAgICAgICAgICAgIHIgKiBtYXRoLnNpbihwaGkpICogbWF0aC5zaW4odGgpLAogICAgICAgICAgICAgICAgICAg"
    "ICAgICAgIHIgKiBtYXRoLmNvcyhwaGkpICsgcikpCiAgICBmb3IgaSBpbiByYW5nZSh2c2VnKToKICAgICAgICBmb3IgaiBp"
    "biByYW5nZSh1KToKICAgICAgICAgICAgYSA9IGkgKiB1ICsgagogICAgICAgICAgICBiID0gaSAqIHUgKyAoaiArIDEpICUg"
    "dQogICAgICAgICAgICBjID0gKGkgKyAxKSAqIHUgKyBqCiAgICAgICAgICAgIGQgPSAoaSArIDEpICogdSArIChqICsgMSkg"
    "JSB1CiAgICAgICAgICAgIHRyaXMgKz0gWyhhLCBjLCBkKSwgKGEsIGQsIGIpXQogICAgcmV0dXJuIHZlcnRzLCB0cmlzCgoK"
    "ZGVmIF9mYWlsKG1zZywgZ290KToKICAgIHByaW50KGYiICBGQUlMICB7bXNnfSAgKGdvdCB7Z290fSkiKQogICAgcmV0dXJu"
    "IDEKCgpkZWYgc2VsZnRlc3QoKToKICAgIGJhZCA9IDAKICAgIHByaW50KGYic2hhcGVfbWV0cmljcyB7VkVSU0lPTn0gc2Vs"
    "ZnRlc3QgKHVwPTIsIFotdXAsIGZvciB0aGVzZSBmaXh0dXJlcykiKQoKICAgIGN1YmUgPSBtZXNoX21ldHJpY3MoKl91bml0"
    "X2N1YmUoKSwgdXA9MikKICAgIHByaW50KCIgIGN1YmUgICAgICAgICAgIiwge2s6IGN1YmVba10gZm9yIGsgaW4KICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICgiYmJveF9vY2N1cGFuY3kiLCAibm9ybWFsX3JlZ2lvbnNfODAiLAogICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICJkb21pbmFudF9mYWNlX3NoYXJlIiwKICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICAicGxhbl9odWxsX2ZpbGwiLCAiemluZ2ciLCAiYmFzZV9jb250YWN0X3JhdGlvIil9KQogICAgaWYgYWJzKGN1"
    "YmVbImJib3hfb2NjdXBhbmN5Il0gLSAxLjApID4gMC4wMToKICAgICAgICBiYWQgKz0gX2ZhaWwoImN1YmUgb2NjdXBhbmN5"
    "IHNob3VsZCBiZSAxLjAiLCBjdWJlWyJiYm94X29jY3VwYW5jeSJdKQogICAgaWYgYWJzKGN1YmVbInBsYW5faHVsbF9maWxs"
    "Il0gLSAxLjApID4gMC4wMToKICAgICAgICBiYWQgKz0gX2ZhaWwoImN1YmUgcGxhbiBodWxsIGZpbGwgc2hvdWxkIGJlIDEu"
    "MCIsIGN1YmVbInBsYW5faHVsbF9maWxsIl0pCiAgICBpZiBjdWJlWyJ6aW5nZyJdICE9ICJlcXVhbnQiOgogICAgICAgIGJh"
    "ZCArPSBfZmFpbCgiY3ViZSBzaG91bGQgYmUgZXF1YW50IiwgY3ViZVsiemluZ2ciXSkKICAgIGlmIGFicyhjdWJlWyJkb21p"
    "bmFudF9mYWNlX3NoYXJlIl0gLSAxIC8gNikgPiAwLjAxOgogICAgICAgIGJhZCArPSBfZmFpbCgiY3ViZSBkb21pbmFudCBm"
    "YWNlIHNoYXJlIHNob3VsZCBiZSAxLzYiLAogICAgICAgICAgICAgICAgICAgICBjdWJlWyJkb21pbmFudF9mYWNlX3NoYXJl"
    "Il0pCiAgICBpZiBhYnMoY3ViZVsiYmFzZV9jb250YWN0X3JhdGlvIl0gLSAxLjApID4gMC4wMToKICAgICAgICBiYWQgKz0g"
    "X2ZhaWwoImN1YmUgc2l0cyBmbGF0LCBiYXNlIGNvbnRhY3Qgc2hvdWxkIGJlIDEuMCIsCiAgICAgICAgICAgICAgICAgICAg"
    "IGN1YmVbImJhc2VfY29udGFjdF9yYXRpbyJdKQogICAgaWYgbm90IGN1YmVbImNsb3NlZCJdIG9yIGN1YmVbIm9wZW5fZWRn"
    "ZXMiXToKICAgICAgICBiYWQgKz0gX2ZhaWwoImEgY3ViZSBpcyBhIGNsb3NlZCBzdXJmYWNlIiwKICAgICAgICAgICAgICAg"
    "ICAgICAgKGN1YmVbIm9wZW5fZWRnZXMiXSwgY3ViZVsibm9ubWFuaWZvbGRfZWRnZXMiXSkpCiAgICAjIEZBTFNJRklDQVRJ"
    "T046IGEgaG9sZSBtdXN0IGJlIGRldGVjdGVkLiBEcm9wIG9uZSB0cmlhbmdsZSBhbmQgdGhlCiAgICAjIGNsb3NlZG5lc3Mg"
    "dGVzdCBoYXMgdG8gZmFpbDsgaWYgaXQgc3RpbGwgcGFzc2VzIGl0IGlzIHRlc3Rpbmcgbm90aGluZy4KICAgIGN2LCBjdCA9"
    "IF91bml0X2N1YmUoKQogICAgaG9sZWQgPSBtZXNoX21ldHJpY3MoY3YsIGN0WzotMV0sIHVwPTIpCiAgICBpZiBob2xlZFsi"
    "Y2xvc2VkIl0gb3IgaG9sZWRbIm9wZW5fZWRnZXMiXSAhPSAzOgogICAgICAgIGJhZCArPSBfZmFpbCgicmVtb3ZpbmcgYSB0"
    "cmlhbmdsZSBtdXN0IG9wZW4gZXhhY3RseSAzIGVkZ2VzIiwKICAgICAgICAgICAgICAgICAgICAgKGhvbGVkWyJjbG9zZWQi"
    "XSwgaG9sZWRbIm9wZW5fZWRnZXMiXSkpCiAgICBpZiBjdWJlWyJub3JtYWxfcmVnaW9uc184MCJdICE9IDU6CiAgICAgICAg"
    "YmFkICs9IF9mYWlsKCJhIGN1YmUgbmVlZHMgNSBvZiBpdHMgNiBmYWNlcyB0byBjb3ZlciA4MCUgb2YgYXJlYSIsCiAgICAg"
    "ICAgICAgICAgICAgICAgIGN1YmVbIm5vcm1hbF9yZWdpb25zXzgwIl0pCgogICAgc3BoID0gbWVzaF9tZXRyaWNzKCpfdXZf"
    "c3BoZXJlKCksIHVwPTIpCiAgICBwcmludCgiICBzcGhlcmUgICAgICAgICIsIHtrOiBzcGhba10gZm9yIGsgaW4KICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICgiYmJveF9vY2N1cGFuY3kiLCAibm9ybWFsX3JlZ2lvbnNfODAiLAogICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICJkb21pbmFudF9mYWNlX3NoYXJlIiwKICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICAicGxhbl9odWxsX2ZpbGwiLCAicGxhbl9yYWRpYWxfY3YiLAogICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICJiYXNlX2NvbnRhY3RfcmF0aW8iKX0pCiAgICBpZiBhYnMoc3BoWyJiYm94X29jY3VwYW5jeSJdIC0gbWF0aC5waSAv"
    "IDYpID4gMC4wMzoKICAgICAgICBiYWQgKz0gX2ZhaWwoInNwaGVyZSBvY2N1cGFuY3kgc2hvdWxkIGJlIHBpLzYgPSAwLjUy"
    "NCIsCiAgICAgICAgICAgICAgICAgICAgIHNwaFsiYmJveF9vY2N1cGFuY3kiXSkKICAgIGlmIGFicyhzcGhbInBsYW5faHVs"
    "bF9maWxsIl0gLSBtYXRoLnBpIC8gNCkgPiAwLjAzOgogICAgICAgIGJhZCArPSBfZmFpbCgic3BoZXJlIHBsYW4gaHVsbCBm"
    "aWxsIHNob3VsZCBiZSBwaS80ID0gMC43ODUiLAogICAgICAgICAgICAgICAgICAgICBzcGhbInBsYW5faHVsbF9maWxsIl0p"
    "CiAgICBpZiBzcGhbInBsYW5fcmFkaWFsX2N2Il0gPiAwLjAyOgogICAgICAgIGJhZCArPSBfZmFpbCgiYSBjaXJjbGUgaGFz"
    "IG5vIHJhZGlhbCB2YXJpYXRpb24iLCBzcGhbInBsYW5fcmFkaWFsX2N2Il0pCiAgICBpZiBzcGhbIm5vcm1hbF9yZWdpb25z"
    "XzgwIl0gPCAyMDoKICAgICAgICBiYWQgKz0gX2ZhaWwoImEgc3BoZXJlIGhhcyBtYW55IGZhY2luZyBkaXJlY3Rpb25zIiwK"
    "ICAgICAgICAgICAgICAgICAgICAgc3BoWyJub3JtYWxfcmVnaW9uc184MCJdKQogICAgIyBGQUxTSUZJQ0FUSU9OOiBub3Jt"
    "YWxfcmVnaW9uc184MCBpcyB0aGUgY3JpdGVyaW9uLTMgaW5zdHJ1bWVudDsgaWYgaXQKICAgICMgY2Fubm90IHNlcGFyYXRl"
    "IGEgNi1mYWNlZCBzb2xpZCBmcm9tIGEgdGVzc2VsbGF0ZWQgb25lIGl0IGlzIG1lYXN1cmluZwogICAgIyBub3RoaW5nLgog"
    "ICAgaWYgc3BoWyJub3JtYWxfcmVnaW9uc184MCJdIDw9IGN1YmVbIm5vcm1hbF9yZWdpb25zXzgwIl0gKiAyOgogICAgICAg"
    "IGJhZCArPSBfZmFpbCgibm9ybWFsX3JlZ2lvbnNfODAgZmFpbHMgdG8gc2VwYXJhdGUgc3BoZXJlIGZyb20gY3ViZSIsCiAg"
    "ICAgICAgICAgICAgICAgICAgIChzcGhbIm5vcm1hbF9yZWdpb25zXzgwIl0sIGN1YmVbIm5vcm1hbF9yZWdpb25zXzgwIl0p"
    "KQogICAgIyBGQUxTSUZJQ0FUSU9OOiBhIGJhbGwgbXVzdCBub3QgbG9vayBsaWtlIGEgYm94IG9uIHRoZSBtZXRyaWMgdGhh"
    "dCBpcwogICAgIyBzdXBwb3NlZCB0byB0ZWxsIHRoZW0gYXBhcnQuICBJZiB0aGlzIGV2ZXIgcGFzc2VzLCBvY2N1cGFuY3kg"
    "aXMgYnJva2VuLgogICAgaWYgYWJzKHNwaFsiYmJveF9vY2N1cGFuY3kiXSAtIGN1YmVbImJib3hfb2NjdXBhbmN5Il0pIDwg"
    "MC4zOgogICAgICAgIGJhZCArPSBfZmFpbCgib2NjdXBhbmN5IGZhaWxzIHRvIHNlcGFyYXRlIHNwaGVyZSBmcm9tIGN1YmUi"
    "LAogICAgICAgICAgICAgICAgICAgICAoc3BoWyJiYm94X29jY3VwYW5jeSJdLCBjdWJlWyJiYm94X29jY3VwYW5jeSJdKSkK"
    "ICAgIGlmIHNwaFsiYmFzZV9jb250YWN0X3JhdGlvIl0gPiAwLjE1OgogICAgICAgIGJhZCArPSBfZmFpbCgiYSBzcGhlcmUg"
    "dG91Y2hlcyB0aGUgZ3JvdW5kIGF0IGEgcG9pbnQsIG5vdCBhIGZhY2UiLAogICAgICAgICAgICAgICAgICAgICBzcGhbImJh"
    "c2VfY29udGFjdF9yYXRpbyJdKQogICAgIyBGQUxTSUZJQ0FUSU9OOiBjb250YWN0IG11c3Qgc2VwYXJhdGUgInNpdHMgZmxh"
    "dCIgZnJvbSAicmVzdHMgb24gYSBwb2ludCIuCiAgICBpZiBzcGhbImJhc2VfY29udGFjdF9yYXRpbyJdID49IGN1YmVbImJh"
    "c2VfY29udGFjdF9yYXRpbyJdICogMC41OgogICAgICAgIGJhZCArPSBfZmFpbCgiYmFzZV9jb250YWN0X3JhdGlvIGZhaWxz"
    "IHRvIHNlcGFyYXRlIHNwaGVyZSBmcm9tIGN1YmUiLAogICAgICAgICAgICAgICAgICAgICAoc3BoWyJiYXNlX2NvbnRhY3Rf"
    "cmF0aW8iXSwgY3ViZVsiYmFzZV9jb250YWN0X3JhdGlvIl0pKQogICAgaWYgY3ViZVsicGxhbl9yYWRpYWxfY3YiXSA8PSBz"
    "cGhbInBsYW5fcmFkaWFsX2N2Il06CiAgICAgICAgYmFkICs9IF9mYWlsKCJhIHNxdWFyZSBwbGFuIG11c3QgYmUgbGVzcyBy"
    "b3VuZCB0aGFuIGEgY2lyY3VsYXIgb25lIiwKICAgICAgICAgICAgICAgICAgICAgKGN1YmVbInBsYW5fcmFkaWFsX2N2Il0s"
    "IHNwaFsicGxhbl9yYWRpYWxfY3YiXSkpCgogICAgc2xhYiA9IG1lc2hfbWV0cmljcygqX3NsYWIoMC4xKSwgdXA9MikKICAg"
    "IHByaW50KCIgIHNsYWIgMXgxeDAuMSAgIiwge2s6IHNsYWJba10gZm9yIGsgaW4KICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICgidXBfZmFjaW5nX3NoYXJlIiwgImRvbWluYW50X2ZhY2Vfc2hhcmUiLAogICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICAgICJ6aW5nZyIsICJmbGF0bmVzc19jYiIpfSkKICAgIGlmIGFicyhzbGFiWyJ1cF9mYWNpbmdfc2hhcmUiXSAt"
    "IDEgLyAyLjQpID4gMC4wMjoKICAgICAgICBiYWQgKz0gX2ZhaWwoInNsYWIgdXAtZmFjaW5nIHNoYXJlIHNob3VsZCBiZSAx"
    "LzIuNCA9IDAuNDE3IiwKICAgICAgICAgICAgICAgICAgICAgc2xhYlsidXBfZmFjaW5nX3NoYXJlIl0pCiAgICBpZiBzbGFi"
    "WyJ6aW5nZyJdICE9ICJkaXNjIjoKICAgICAgICBiYWQgKz0gX2ZhaWwoImEgMXgxeDAuMSBzbGFiIGlzIGEgZGlzYyBpbiBa"
    "aW5nZyB0ZXJtcyIsIHNsYWJbInppbmdnIl0pCiAgICAjIEZBTFNJRklDQVRJT046IHRoZSBmbGF0LXRvcCB0ZWxsIG11c3Qg"
    "ZmlyZSBvbiB0aGUgc2xhYiBhbmQgbm90IG9uIHRoZSBjdWJlLgogICAgaWYgc2xhYlsidXBfZmFjaW5nX3NoYXJlIl0gPD0g"
    "Y3ViZVsidXBfZmFjaW5nX3NoYXJlIl06CiAgICAgICAgYmFkICs9IF9mYWlsKCJ1cF9mYWNpbmdfc2hhcmUgZmFpbHMgdG8g"
    "c2VwYXJhdGUgc2xhYiBmcm9tIGN1YmUiLAogICAgICAgICAgICAgICAgICAgICAoc2xhYlsidXBfZmFjaW5nX3NoYXJlIl0s"
    "IGN1YmVbInVwX2ZhY2luZ19zaGFyZSJdKSkKCiAgICAjIC0tLSBwYXRjaCBzdGF0aXN0aWNzIC0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tCiAgICBsYXR0aWNlID0gWyhpICogMS4wLCBqICogMS4wKSBmb3Ig"
    "aSBpbiByYW5nZSgxMikgZm9yIGogaW4gcmFuZ2UoMTIpXQogICAgIyBBcmVhIGlzIDEyeDEyLCBub3QgMTF4MTE6IGVhY2gg"
    "b2YgdGhlIDE0NCBwb2ludHMgb3ducyBhIDF4MSBjZWxsLgogICAgIyBVc2luZyB0aGUgaHVsbCBhcmVhICgxMXgxMSkgdW5k"
    "ZXJjb3VudHMgdGhlIHJlZ2lvbiBhbmQgaW5mbGF0ZXMgUiAtLQogICAgIyB3aGljaCBpcyBleGFjdGx5IHRoZSBiaWFzIHRo"
    "ZSBkb2NzdHJpbmcgd2FybnMgYWJvdXQsIGRlbW9uc3RyYXRlZC4KICAgIGxhdCA9IHBhdGNoX21ldHJpY3MobGF0dGljZSwg"
    "YXJlYT0xMi4wICogMTIuMCkKICAgIHByaW50KCIgIGxhdHRpY2UgMTJ4MTIgIiwge2s6IGxhdFtrXSBmb3IgayBpbiAoImNs"
    "YXJrX2V2YW5zX1IiLCAibm5fY3YiLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAicmVhZGluZyIpfSkKICAgIGlmIGFicyhsYXRbImNsYXJrX2V2YW5zX1IiXSAtIDIuMCkgPiAwLjA2OgogICAgICAgIGJh"
    "ZCArPSBfZmFpbCgic3F1YXJlIGxhdHRpY2UgUiBzaG91bGQgYmUgMi4wIiwgbGF0WyJjbGFya19ldmFuc19SIl0pCiAgICBp"
    "ZiBsYXRbInJlYWRpbmciXSAhPSAiZGlzcGVyc2VkIjoKICAgICAgICBiYWQgKz0gX2ZhaWwoImEgbGF0dGljZSBtdXN0IHJl"
    "YWQgYXMgZGlzcGVyc2VkIiwgbGF0WyJyZWFkaW5nIl0pCgogICAgaW1wb3J0IHJhbmRvbSBhcyBfcgogICAgcm5kID0gX3Iu"
    "UmFuZG9tKDE5OTkpCiAgICBwb2lzc29uID0gWyhybmQudW5pZm9ybSgwLCAxMSksIHJuZC51bmlmb3JtKDAsIDExKSkgZm9y"
    "IF8gaW4gcmFuZ2UoMTQ0KV0KICAgIHBvaSA9IHBhdGNoX21ldHJpY3MocG9pc3NvbiwgYXJlYT0xMS4wICogMTEuMCkKICAg"
    "IHByaW50KCIgIHBvaXNzb24gbj0xNDQgIiwge2s6IHBvaVtrXSBmb3IgayBpbiAoImNsYXJrX2V2YW5zX1IiLCAibm5fY3Yi"
    "LAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAicmVhZGluZyIpfSkKICAgIGlm"
    "IG5vdCAwLjg1IDw9IHBvaVsiY2xhcmtfZXZhbnNfUiJdIDw9IDEuMTU6CiAgICAgICAgYmFkICs9IF9mYWlsKCJQb2lzc29u"
    "IFIgc2hvdWxkIHNpdCBuZWFyIDEuMCIsIHBvaVsiY2xhcmtfZXZhbnNfUiJdKQoKICAgIGNsdXN0ZXJlZCA9IFtdCiAgICBm"
    "b3IgXyBpbiByYW5nZSgxMik6CiAgICAgICAgY3gsIGN5ID0gcm5kLnVuaWZvcm0oMCwgMTEpLCBybmQudW5pZm9ybSgwLCAx"
    "MSkKICAgICAgICBmb3IgXyBpbiByYW5nZSgxMik6CiAgICAgICAgICAgIGNsdXN0ZXJlZC5hcHBlbmQoKGN4ICsgcm5kLmdh"
    "dXNzKDAsIDAuMTgpLCBjeSArIHJuZC5nYXVzcygwLCAwLjE4KSkpCiAgICBjbHUgPSBwYXRjaF9tZXRyaWNzKGNsdXN0ZXJl"
    "ZCwgYXJlYT0xMS4wICogMTEuMCkKICAgIHByaW50KCIgIGNsdXN0ZXJlZCAgICAgIiwge2s6IGNsdVtrXSBmb3IgayBpbiAo"
    "ImNsYXJrX2V2YW5zX1IiLCAibm5fY3YiLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAicmVhZGluZyIpfSkKICAgIGlmIGNsdVsiY2xhcmtfZXZhbnNfUiJdID49IDAuNjoKICAgICAgICBiYWQgKz0gX2Zh"
    "aWwoInRpZ2h0IGNsdXN0ZXJzIHNob3VsZCBnaXZlIFIgd2VsbCB1bmRlciAxIiwKICAgICAgICAgICAgICAgICAgICAgY2x1"
    "WyJjbGFya19ldmFuc19SIl0pCiAgICAjIEZBTFNJRklDQVRJT046IHRoZSB0aHJlZSByZWdpbWVzIG11c3QgYmUgT1JERVJF"
    "RCwgbm90IG1lcmVseSBjb21wdXRlZC4KICAgIGlmIG5vdCAoY2x1WyJjbGFya19ldmFuc19SIl0gPCBwb2lbImNsYXJrX2V2"
    "YW5zX1IiXSA8IGxhdFsiY2xhcmtfZXZhbnNfUiJdKToKICAgICAgICBiYWQgKz0gX2ZhaWwoIlIgZmFpbHMgdG8gb3JkZXIg"
    "Y2x1c3RlcmVkIDwgcmFuZG9tIDwgZGlzcGVyc2VkIiwKICAgICAgICAgICAgICAgICAgICAgKGNsdVsiY2xhcmtfZXZhbnNf"
    "UiJdLCBwb2lbImNsYXJrX2V2YW5zX1IiXSwKICAgICAgICAgICAgICAgICAgICAgIGxhdFsiY2xhcmtfZXZhbnNfUiJdKSkK"
    "ICAgIGlmIGNsdVsibm5fY3YiXSA8PSBwb2lbIm5uX2N2Il06CiAgICAgICAgYmFkICs9IF9mYWlsKCJjbHVzdGVyZWQgc3Bh"
    "Y2luZyBtdXN0IHZhcnkgbW9yZSB0aGFuIFBvaXNzb24iLAogICAgICAgICAgICAgICAgICAgICAoY2x1WyJubl9jdiJdLCBw"
    "b2lbIm5uX2N2Il0pKQoKICAgIHByaW50KCJTRUxGVEVTVCIsICJQQVNTRUQiIGlmIGJhZCA9PSAwIGVsc2UgZiJGQUlMRUQg"
    "KHtiYWR9KSIpCiAgICByZXR1cm4gMSBpZiBiYWQgZWxzZSAwCgoKIyAtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLQoKX1RBQkxFID0gWyJ0cmlzIiwgImV4dGVudF91"
    "cCIsICJ6aW5nZyIsICJlbG9uZ2F0aW9uX2JhIiwgImZsYXRuZXNzX2NiIiwKICAgICAgICAgICJiYm94X29jY3VwYW5jeSIs"
    "ICJub3JtYWxfcmVnaW9uc184MCIsICJkb21pbmFudF9mYWNlX3NoYXJlIiwKICAgICAgICAgICJ1cF9mYWNpbmdfc2hhcmUi"
    "LAogICAgICAgICAgInBsYW5fcmFkaWFsX2N2IiwgInBsYW5faHVsbF9maWxsIiwgImJhc2VfY29udGFjdF9yYXRpbyIsCiAg"
    "ICAgICAgICAib3Blbl9lZGdlcyIsICJiYXNlX2F0Il0KCgpkZWYgbWFpbihhcmd2PU5vbmUpOgogICAgYXAgPSBhcmdwYXJz"
    "ZS5Bcmd1bWVudFBhcnNlcihkZXNjcmlwdGlvbj1fX2RvY19fLnNwbGl0bGluZXMoKVswXSkKICAgIGFwLmFkZF9hcmd1bWVu"
    "dCgiZmlsZXMiLCBuYXJncz0iKiIpCiAgICBhcC5hZGRfYXJndW1lbnQoIi0tZGlyIiwgaGVscD0ibWVhc3VyZSBldmVyeSAq"
    "LmdsYiB1bmRlciB0aGlzIGZvbGRlciIpCiAgICBhcC5hZGRfYXJndW1lbnQoIi0tdXAiLCB0eXBlPWludCwgZGVmYXVsdD0x"
    "LAogICAgICAgICAgICAgICAgICAgIGhlbHA9ImluZGV4IG9mIHRoZSB1cCBheGlzICgxID0gZ2xURiBZLXVwLCBkZWZhdWx0"
    "KSIpCiAgICBhcC5hZGRfYXJndW1lbnQoIi0tanNvbiIsIGFjdGlvbj0ic3RvcmVfdHJ1ZSIpCiAgICBhcC5hZGRfYXJndW1l"
    "bnQoIi0tc2VsZnRlc3QiLCBhY3Rpb249InN0b3JlX3RydWUiKQogICAgYXAuYWRkX2FyZ3VtZW50KCItLXZlcnNpb24iLCBh"
    "Y3Rpb249InN0b3JlX3RydWUiKQogICAgYXJncyA9IGFwLnBhcnNlX2FyZ3MoYXJndikKCiAgICBpZiBhcmdzLnZlcnNpb246"
    "CiAgICAgICAgcHJpbnQoVkVSU0lPTikKICAgICAgICByZXR1cm4gMAogICAgaWYgYXJncy5zZWxmdGVzdDoKICAgICAgICBy"
    "ZXR1cm4gc2VsZnRlc3QoKQoKICAgIHBhdGhzID0gbGlzdChhcmdzLmZpbGVzKQogICAgaWYgYXJncy5kaXI6CiAgICAgICAg"
    "cGF0aHMgKz0gc29ydGVkKGdsb2IuZ2xvYihvcy5wYXRoLmpvaW4oYXJncy5kaXIsICIqKiIsICIqLmdsYiIpLAogICAgICAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICAgcmVjdXJzaXZlPVRydWUpKQogICAgaWYgbm90IHBhdGhzOgogICAgICAgIGFw"
    "LnByaW50X2hlbHAoKQogICAgICAgIHJldHVybiAyCgogICAgcm93cyA9IFtdCiAgICBmb3IgcCBpbiBwYXRoczoKICAgICAg"
    "ICB0cnk6CiAgICAgICAgICAgIHJvd3MuYXBwZW5kKGdsYl9tZXRyaWNzKHAsIHVwPWFyZ3MudXApKQogICAgICAgIGV4Y2Vw"
    "dCBFeGNlcHRpb24gYXMgZXhjOiAgICAgICAgICAgICAgICAgICAjIG5vcWE6IEJMRTAwMSAtIHJlcG9ydCwgY29udGludWUK"
    "ICAgICAgICAgICAgcm93cy5hcHBlbmQoeyJmaWxlIjogb3MucGF0aC5iYXNlbmFtZShwKSwgImVycm9yIjogc3RyKGV4Yyl9"
    "KQoKICAgIGlmIGFyZ3MuanNvbjoKICAgICAgICBwcmludChqc29uLmR1bXBzKHJvd3MsIGluZGVudD0xKSkKICAgICAgICBy"
    "ZXR1cm4gMAoKICAgIHcgPSBtYXgoW2xlbihyLmdldCgiZmlsZSIsICI/IikpIGZvciByIGluIHJvd3NdICsgWzRdKQogICAg"
    "cHJpbnQoZiJ7J2ZpbGUnOjx7d319ICAiICsgIiAgIi5qb2luKGYie2s6PjE5fSIgZm9yIGsgaW4gX1RBQkxFKSkKICAgIGZv"
    "ciByIGluIHJvd3M6CiAgICAgICAgaWYgImVycm9yIiBpbiByOgogICAgICAgICAgICBwcmludChmIntyWydmaWxlJ106PHt3"
    "fX0gIEVSUk9SOiB7clsnZXJyb3InXX0iKQogICAgICAgICAgICBjb250aW51ZQogICAgICAgIHByaW50KGYie3JbJ2ZpbGUn"
    "XTo8e3d9fSAgIiArCiAgICAgICAgICAgICAgIiAgIi5qb2luKGYie3N0cihyLmdldChrLCAnLScpKTo+MTl9IiBmb3IgayBp"
    "biBfVEFCTEUpKQogICAgcmV0dXJuIDAKCgppZiBfX25hbWVfXyA9PSAiX19tYWluX18iOgogICAgc3lzLmV4aXQobWFpbigp"
    "KQo="
    ),
  },
}

GEOMETRY = {
  'pre_sha': '4d26e1ed42e32ed8cf1662bf93dc19b75571933f1b6d68bc6ad8fbb461da9cb8',
  'pre_bytes': 10439,
  'post_sha': 'b808f1f8ee17edb0eb019142972b4552cc5083df780a0cae20b0b1f7b8304bda',
  'post_bytes': 20883,
  "block_b64": (
    "IyAtLS0gc2hhcGUgaGVscGVycyAoTGF5ZXIgMyBzdXJmYWNlIGRyZXNzaW5nKSAtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0t"
    "LS0tLS0tCiMKIyBXSFkgVEhFU0UgRVhJU1QuICBgaml0dGVyX3ZlcnRzYCBtb3ZlcyB0aGUgdmVydGljZXMgb2YgYSBwcmlt"
    "aXRpdmUgYnV0IG5vdAojIGl0cyBGQUNFUzogaml0dGVyaW5nIHRoZSA4IGNvcm5lcnMgb2YgYSBjdWJlIHlpZWxkcyBhIHBh"
    "cmFsbGVsZXBpcGVkLCBhbmQKIyBqaXR0ZXJpbmcgYSA2eDQgZWxsaXBzb2lkIHlpZWxkcyBhIGx1bXB5IGJhbGwgd2l0aCB0"
    "aGUgc2FtZSAyNCBmYWNldHMgaXQKIyBzdGFydGVkIHdpdGguICBNZWFzdXJlZCBvbiB0aGUgZmlyc3QgZHJlc3Npbmcga2l0"
    "IHdpdGggYHRvb2xzL3NoYXBlX21ldHJpY3MucHlgLAojIGEgcnViYmxlIGZyYWdtZW50IG5lZWRlZCBvbmx5IDcgZGlzdGlu"
    "Y3QgZmFjaW5nIGRpcmVjdGlvbnMgdG8gYWNjb3VudCBmb3IgODAlCiMgb2YgaXRzIHN1cmZhY2UgYXJlYSAtLSBpdCB3YXMg"
    "c3RpbGwgYSBib3gsIGhvd2V2ZXIgZmFyIHRoZSBjb3JuZXJzIHRyYXZlbGxlZC4KIyBJcnJlZ3VsYXJpdHkgaXMgYm91bmRl"
    "ZCBhYm92ZSBieSBmYWNlIGNvdW50LCBzbyB0aGUgZml4IGhhcyB0byBhZGQgZmFjZXMKIyAoc3ViZGl2aWRlLCBmcmFjdHVy"
    "ZSkgcmF0aGVyIHRoYW4gbW92ZSB0aGUgb25lcyBhbHJlYWR5IHRoZXJlLgojCiMgRXZlcnl0aGluZyBoZXJlIHRha2VzIHRo"
    "ZSByZWNpcGUncyBvd24gYHJuZ2Agc28gYnVpbGRzIHN0YXkgZGV0ZXJtaW5pc3RpYy4KCmRlZiBzdWJkaXZpZGUoYm0sIHZl"
    "cnRzLCBjdXRzPTEpOgogICAgIiIiU3ViZGl2aWRlIGV2ZXJ5IGVkZ2Ugd2hvc2UgZW5kcyBhcmUgYm90aCBpbiBgdmVydHNg"
    "LgoKICAgIFJldHVybnMgdGhlIGVubGFyZ2VkIHZlcnRleCBzZXQsIHNvIGEgcmVjaXBlIGNhbiBrZWVwIG9wZXJhdGluZyBv"
    "biAidGhpcwogICAgY2h1bmsiIHdoaWxlIHRoZSBzaGFyZWQgYm1lc2ggaG9sZHMgc2V2ZXJhbC4KICAgICIiIgogICAgaWYg"
    "Y3V0cyA8IDE6CiAgICAgICAgcmV0dXJuIGxpc3QodmVydHMpCiAgICB2cyA9IHNldCh2ZXJ0cykKICAgIGVkZ2VzID0gW2Ug"
    "Zm9yIGUgaW4gYm0uZWRnZXMgaWYgZS52ZXJ0c1swXSBpbiB2cyBhbmQgZS52ZXJ0c1sxXSBpbiB2c10KICAgIGlmIG5vdCBl"
    "ZGdlczoKICAgICAgICByZXR1cm4gbGlzdCh2ZXJ0cykKICAgIHJldCA9IGJtZXNoLm9wcy5zdWJkaXZpZGVfZWRnZXMoYm0s"
    "IGVkZ2VzPWVkZ2VzLCBjdXRzPWN1dHMsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHVzZV9ncmlkX2Zp"
    "bGw9VHJ1ZSkKICAgICMgYHVzZV9ncmlkX2ZpbGxgIFJFQlVJTERTIHRoZSBmYWNlIGludGVyaW9ycywgd2hpY2ggaW52YWxp"
    "ZGF0ZXMgdGhlCiAgICAjIG9yaWdpbmFsIGNvcm5lciB2ZXJ0aWNlcyAtLSBtZWFzdXJlZDogYWxsIDggdmVydHMgb2YgYSBz"
    "dWJkaXZpZGVkIGN1YmUKICAgICMgY29tZSBiYWNrIGBpc192YWxpZCA9PSBGYWxzZWAuIFJldHVybmluZyB0aGVtIHByb2R1"
    "Y2VzIGEKICAgICMgIkJNZXNoIGRhdGEgb2YgdHlwZSBCTVZlcnQgaGFzIGJlZW4gcmVtb3ZlZCIgUmVmZXJlbmNlRXJyb3Ig"
    "c2V2ZXJhbAogICAgIyBvcGVyYXRpb25zIGxhdGVyLCBhIGxvbmcgd2F5IGZyb20gdGhlIGNhdXNlLiBTbyB0aGUgY2FsbGVy"
    "J3MgbGlzdCBpcwogICAgIyByZWJ1aWx0IGZyb20gdGhlIG9wJ3Mgb3duIG91dHB1dCBhbmQgZmlsdGVyZWQsIG5ldmVyIG1l"
    "cmdlZCBibGluZGx5LgogICAgb3V0ID0ge3YgZm9yIHYgaW4gdmVydHMgaWYgdi5pc192YWxpZH0KICAgIGZvciBrZXkgaW4g"
    "KCJnZW9tIiwgImdlb21fc3BsaXQiLCAiZ2VvbV9pbm5lciIpOgogICAgICAgIGZvciBnIGluIHJldC5nZXQoa2V5LCBbXSk6"
    "CiAgICAgICAgICAgIGlmIGlzaW5zdGFuY2UoZywgYm1lc2gudHlwZXMuQk1WZXJ0KSBhbmQgZy5pc192YWxpZDoKICAgICAg"
    "ICAgICAgICAgIG91dC5hZGQoZykKICAgIHJldHVybiBsaXN0KG91dCkKCgpkZWYgX3VuaXQocm5nKToKICAgICIiIlVuaWZv"
    "cm0gcmFuZG9tIGRpcmVjdGlvbiBvbiB0aGUgc3BoZXJlIChNYXJzYWdsaWEpLiIiIgogICAgd2hpbGUgVHJ1ZToKICAgICAg"
    "ICB4LCB5ID0gcm5nLnJhbmRvbSgpICogMiAtIDEsIHJuZy5yYW5kb20oKSAqIDIgLSAxCiAgICAgICAgcyA9IHggKiB4ICsg"
    "eSAqIHkKICAgICAgICBpZiBzIDwgMS4wOgogICAgICAgICAgICBmID0gMi4wICogbWF0aC5zcXJ0KDEuMCAtIHMpCiAgICAg"
    "ICAgICAgIHJldHVybiBWZWN0b3IoKHggKiBmLCB5ICogZiwgMS4wIC0gMi4wICogcykpCgoKZGVmIGRpc3BsYWNlX2xvYmVz"
    "KGJtLCB2ZXJ0cywgcm5nLCBhbW91bnQsIGxvYmVzPTMsIHNoYXJwbmVzcz0yLjAsCiAgICAgICAgICAgICAgICAgICBncmFp"
    "bj0wLjI1LCBjZW50ZXI9KDAuMCwgMC4wLCAwLjApKToKICAgICIiIlR3by1mcmVxdWVuY3kgZGlzcGxhY2VtZW50IGFsb25n"
    "IHRoZSB2ZXJ0ZXggbm9ybWFsLgoKICAgIExPVyBmcmVxdWVuY3k6IGEgZmV3IGJyb2FkIGxvYmVzLCBzbyB0aGUgc29saWQg"
    "Z2FpbnMgYXN5bW1ldHJpYyBidWxnZXMgdGhlCiAgICB3YXkgYSB3b3JuIHN0b25lIGRvZXMuICBISUdIIGZyZXF1ZW5jeTog"
    "YSBzbWFsbCBwZXItdmVydGV4IGdyYWluIG9uIHRvcC4KICAgIFVuaWZvcm0gcGVyLXZlcnRleCBub2lzZSBhbG9uZSAod2hh"
    "dCBgaml0dGVyX3ZlcnRzYCBkb2VzKSBpcwogICAgc2NhbGUtaW52YXJpYW50IGhhc2ggLS0gaXQgcm91Z2hlbnMgYSBzdXJm"
    "YWNlIHdpdGhvdXQgZXZlciBjaGFuZ2luZyB0aGUKICAgIHNpbGhvdWV0dGUsIHdoaWNoIGlzIHRoZSB0aGluZyB0aGF0IGFj"
    "dHVhbGx5IHJlYWRzIGF0IHR3byBtZXRyZXMuCgogICAgYGFtb3VudGAgaXMgdGhlIGxvdy1mcmVxdWVuY3kgYW1wbGl0dWRl"
    "IGluIG1ldHJlczsgYGdyYWluYCBpcyB0aGUKICAgIGhpZ2gtZnJlcXVlbmN5IGFtcGxpdHVkZSBhcyBhIGZyYWN0aW9uIG9m"
    "IGl0LgogICAgIiIiCiAgICBpZiBhbW91bnQgPD0gMCBvciBub3QgdmVydHM6CiAgICAgICAgcmV0dXJuIGxpc3QodmVydHMp"
    "CiAgICBibS5ub3JtYWxfdXBkYXRlKCkKICAgIGMgPSBWZWN0b3IoY2VudGVyKQogICAgZGlycyA9IFsoX3VuaXQocm5nKSwg"
    "YW1vdW50ICogKDAuNDUgKyBybmcucmFuZG9tKCkgKiAwLjkpKQogICAgICAgICAgICBmb3IgXyBpbiByYW5nZShtYXgoMSwg"
    "bG9iZXMpKV0KICAgIGZvciB2IGluIHZlcnRzOgogICAgICAgIGlmIG5vdCB2LmlzX3ZhbGlkOgogICAgICAgICAgICBjb250"
    "aW51ZQogICAgICAgIHJlbCA9IHYuY28gLSBjCiAgICAgICAgaWYgcmVsLmxlbmd0aCA+IDFlLTk6CiAgICAgICAgICAgIHUg"
    "PSByZWwubm9ybWFsaXplZCgpCiAgICAgICAgICAgIG9mZiA9IDAuMAogICAgICAgICAgICBmb3IgZCwgYW1wIGluIGRpcnM6"
    "CiAgICAgICAgICAgICAgICB3ID0gdS5kb3QoZCkKICAgICAgICAgICAgICAgIGlmIHcgPiAwLjA6CiAgICAgICAgICAgICAg"
    "ICAgICAgb2ZmICs9IGFtcCAqICh3ICoqIHNoYXJwbmVzcykKICAgICAgICAgICAgb2ZmICs9IChybmcucmFuZG9tKCkgKiAy"
    "LjAgLSAxLjApICogYW1vdW50ICogZ3JhaW4KICAgICAgICAgICAgbiA9IHYubm9ybWFsIGlmIHYubm9ybWFsLmxlbmd0aCA+"
    "IDFlLTkgZWxzZSB1CiAgICAgICAgICAgIHYuY28gKz0gbiAqIG9mZgogICAgcmV0dXJuIGxpc3QodmVydHMpCgoKZGVmIGZy"
    "YWN0dXJlKGJtLCB2ZXJ0cywgcm5nLCBjdXRzPTMsIG5lYXI9MC4zMCwgZmFyPTAuODUsCiAgICAgICAgICAgICBjZW50ZXI9"
    "KDAuMCwgMC4wLCAwLjApLCByYWRpdXM9MS4wLCBzdGVlcD0wLjApOgogICAgIiIiU2xpY2UgYSBzb2xpZCB3aXRoIHJhbmRv"
    "bSBoYWxmLXNwYWNlIHBsYW5lcywgY2FwcGluZyBlYWNoIGN1dC4KCiAgICBUaGlzIGlzIHdoYXQgbWFrZXMgYSBmcmFnbWVu"
    "dCBBTkdVTEFSIGZvciByZWFsOiBicm9rZW4gcm9jayBJUyB0aGUKICAgIGludGVyc2VjdGlvbiBvZiBoYWxmLXNwYWNlcywg"
    "c28gY3V0dGluZyB0aGUgc29saWQgcHJvZHVjZXMgZmxhdCBmYWNldHMgb2YKICAgIHVuZXF1YWwgc2l6ZSBtZWV0aW5nIGF0"
    "IHNoYXJwIGRpaGVkcmFscyAtLSB3aGljaCBpcyB0aGUgcmVhZCBgcnViYmxlX2ZyYWdgCiAgICBjbGFpbXMgaW4gaXRzIGRv"
    "Y3N0cmluZyBhbmQgZGlkIG5vdCBoYXZlLiAgRWFjaCBjdXQgYWRkcyBvbmUgZmFjZSwgc28gdGhlCiAgICB0cmlhbmdsZSBj"
    "b3N0IGlzIGEgZmV3IHRyaXMgcGVyIGN1dCBhbmQgdGhlIGNhbGxlciBjb250cm9scyBpdCBkaXJlY3RseS4KCiAgICBgbmVh"
    "cmAvYGZhcmAgYm91bmQgaG93IGZhciBvZmYgYGNlbnRlcmAgYSBjdXR0aW5nIHBsYW5lIG1heSBzaXQsIGFzIGEKICAgIGZy"
    "YWN0aW9uIG9mIGByYWRpdXNgOiBhIHBsYW5lIHRocm91Z2ggdGhlIGNlbnRyZSBoYWx2ZXMgdGhlIGZyYWdtZW50LCBzbwog"
    "ICAgdGhlIHVzZWZ1bCByYW5nZSBzaGF2ZXMgY29ybmVycyBpbnN0ZWFkLgoKICAgIGBzdGVlcGAgKDAuLjEpIGJpYXNlcyB0"
    "aGUgY3V0dGluZyBwbGFuZXMgdG93YXJkIFZFUlRJQ0FMLiAgQSBkcmVzc2luZwogICAgZnJhZ21lbnQgaXMgYSBmbGF0IHRo"
    "aW5nIGx5aW5nIG9uIHRoZSBncm91bmQsIHNvIGEgcmFuZG9tbHkgb3JpZW50ZWQgcGxhbmUKICAgIHVzdWFsbHkgc2hhdmVz"
    "IHRoZSB0b3Agb3IgdGhlIGJvdHRvbSwgd2hlcmUgbm90aGluZyBjYW4gc2VlIGl0IC0tIG1lYXN1cmVkLAogICAgZm91ciBy"
    "YW5kb20gY3V0cyBsZWZ0IHRoZSBwbGFuLXZpZXcgb3V0bGluZSA5OCUgYXMgYm94eSBhcyB0aGUgYm94IGl0CiAgICBzdGFy"
    "dGVkIGZyb20uICBUaGUgY3V0cyB0aGF0IGNoYW5nZSB3aGF0IHlvdSBzZWUgZnJvbSBzdGFuZGluZyBoZWlnaHQgYXJlCiAg"
    "ICB0aGUgb25lcyB0aGF0IGN1dCB0aGUgcGxhbiBzaWxob3VldHRlLCBhbmQgdGhvc2UgYXJlIHRoZSB2ZXJ0aWNhbCBvbmVz"
    "LgogICAgIiIiCiAgICB2ZXJ0cyA9IFt2IGZvciB2IGluIHZlcnRzIGlmIHYuaXNfdmFsaWRdCiAgICBjID0gVmVjdG9yKGNl"
    "bnRlcikKICAgIGZvciBfIGluIHJhbmdlKG1heCgwLCBjdXRzKSk6CiAgICAgICAgaWYgbGVuKHZlcnRzKSA8IDQ6CiAgICAg"
    "ICAgICAgIGJyZWFrCiAgICAgICAgbm8gPSBfdW5pdChybmcpCiAgICAgICAgaWYgc3RlZXAgPiAwLjA6CiAgICAgICAgICAg"
    "IG5vLnogKj0gbWF4KDAuMCwgMS4wIC0gc3RlZXApCiAgICAgICAgICAgIGlmIG5vLmxlbmd0aCA8IDFlLTY6CiAgICAgICAg"
    "ICAgICAgICBubyA9IFZlY3RvcigoMS4wLCAwLjAsIDAuMCkpCiAgICAgICAgICAgIG5vLm5vcm1hbGl6ZSgpCiAgICAgICAg"
    "Y28gPSBjICsgbm8gKiAocmFkaXVzICogKG5lYXIgKyBybmcucmFuZG9tKCkgKiBtYXgoMC4wLCBmYXIgLSBuZWFyKSkpCiAg"
    "ICAgICAgdnMgPSBzZXQodmVydHMpCiAgICAgICAgZ2VvbSA9IGxpc3QodnMpCiAgICAgICAgZ2VvbSArPSBbZSBmb3IgZSBp"
    "biBibS5lZGdlcyBpZiBlLnZlcnRzWzBdIGluIHZzIGFuZCBlLnZlcnRzWzFdIGluIHZzXQogICAgICAgIGdlb20gKz0gW2Yg"
    "Zm9yIGYgaW4gYm0uZmFjZXMgaWYgYWxsKHYgaW4gdnMgZm9yIHYgaW4gZi52ZXJ0cyldCiAgICAgICAgcmVzID0gYm1lc2gu"
    "b3BzLmJpc2VjdF9wbGFuZShibSwgZ2VvbT1nZW9tLCBkaXN0PTFlLTcsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICBwbGFuZV9jbz1jbywgcGxhbmVfbm89bm8sCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBj"
    "bGVhcl9vdXRlcj1UcnVlKQogICAgICAgIGN1dCA9IFtnIGZvciBnIGluIHJlcy5nZXQoImdlb21fY3V0IiwgW10pIGlmIGcu"
    "aXNfdmFsaWRdCiAgICAgICAgaWYgY3V0OgogICAgICAgICAgICBibWVzaC5vcHMuY29udGV4dHVhbF9jcmVhdGUoYm0sIGdl"
    "b209Y3V0KQogICAgICAgIHZlcnRzID0gW2cgZm9yIGcgaW4gcmVzLmdldCgiZ2VvbSIsIFtdKSBpZiBnLmlzX3ZhbGlkCiAg"
    "ICAgICAgICAgICAgICAgYW5kIGlzaW5zdGFuY2UoZywgYm1lc2gudHlwZXMuQk1WZXJ0KV0KICAgICAgICB2ZXJ0cyArPSBb"
    "ZyBmb3IgZyBpbiBjdXQgaWYgaXNpbnN0YW5jZShnLCBibWVzaC50eXBlcy5CTVZlcnQpXQogICAgICAgIHZlcnRzID0gbGlz"
    "dChzZXQodmVydHMpKQogICAgcmV0dXJuIHZlcnRzCgoKZGVmIGZsYXR0ZW5fYmFzZSh2ZXJ0cywgdG9sX2ZyYWM9MC4xNSwg"
    "cGxhbmVfej1Ob25lKToKICAgICIiIlNoYXZlIHRoZSB1bmRlcnNpZGUgZmxhdCwgZ2l2aW5nIHRoZSBzb2xpZCBhIHJlYWwg"
    "Zm9vdHByaW50LgoKICAgIEFuIG9iamVjdCB3aXRoIG5vIGNvbnRhY3QgZmFjZSByZXN0cyBvbiBhIHBvaW50IG9yIGhvdmVy"
    "cywgYW5kIGJvdGggcmVhZCBhcwogICAgcGFzdGVkIG9uIHJhdGhlciB0aGFuIGx5aW5nIHRoZXJlLiAgYHRvb2xzL3NoYXBl"
    "X21ldHJpY3MucHlgIHJlcG9ydHMgdGhpcwogICAgYXMgYGJhc2VfY29udGFjdF9yYXRpb2AsIHdoaWNoIG1lYXN1cmVkIDAu"
    "MDAwIG9uIHRoZSBmaXJzdCBwZWJibGUga2l0IGFuZAogICAgMC4wMDEgb24gdGhlIGZpcnN0IHJ1YmJsZSBraXQgLS0gbmVp"
    "dGhlciBzcGVjaWVzIHRvdWNoZWQgdGhlIGdyb3VuZCBpdCB3YXMKICAgIGRyZXNzaW5nLgoKICAgIEN1dHMgYXQgYGxvICsg"
    "dG9sX2ZyYWMgKiBoZWlnaHRgIHVubGVzcyBgcGxhbmVfemAgbmFtZXMgYW4gYWJzb2x1dGUgcGxhbmUuCiAgICBSRVRVUk5T"
    "IHRoZSByZXN1bHRpbmcgYmFzZSB6LCBzbyB0aGUgY2FsbGVyIGNhbiB0cmFuc2xhdGUgdGhlIHNvbGlkIHRvIHNpdAogICAg"
    "b24gKG9yIHNsaWdodGx5IHVuZGVyKSB0aGUgc3VyZmFjZSB3aXRob3V0IG1lYXN1cmluZyBpdCBhZ2Fpbi4KICAgICIiIgog"
    "ICAgbGl2ZSA9IFt2IGZvciB2IGluIHZlcnRzIGlmIHYuaXNfdmFsaWRdCiAgICBpZiBub3QgbGl2ZToKICAgICAgICByZXR1"
    "cm4gMC4wCiAgICBsbyA9IG1pbih2LmNvLnogZm9yIHYgaW4gbGl2ZSkKICAgIGhpID0gbWF4KHYuY28ueiBmb3IgdiBpbiBs"
    "aXZlKQogICAgY3V0ID0gKGxvICsgKGhpIC0gbG8pICogdG9sX2ZyYWMpIGlmIHBsYW5lX3ogaXMgTm9uZSBlbHNlIHBsYW5l"
    "X3oKICAgIGZvciB2IGluIGxpdmU6CiAgICAgICAgaWYgdi5jby56IDwgY3V0OgogICAgICAgICAgICB2LmNvLnogPSBjdXQK"
    "ICAgIHJldHVybiBjdXQKCgpkZWYgemluZ2dfcmFkaWkocm5nLCBiYXNlLCBlcXVhbnQ9MC4xMiwgcm9kPTAuMjIsIGRpc2M9"
    "MC4zNik6CiAgICAiIiJEcmF3IChyeCwgcnksIHJ6KSBtdWx0aXBsaWVycyB3aXRoIHRoZSBwcm9wb3J0aW9ucyByZWFsIGdy"
    "YXZlbCBoYXMuCgogICAgWmluZ2cgKDE5MzUpIGNsYXNzaWZpZXMgY2xhc3RzIGJ5IGIvYSBhbmQgYy9iIGF0IDIvMzsgbWVh"
    "c3VyZWQgcml2ZXIgYW5kCiAgICB0YWx1cyBwb3B1bGF0aW9ucyBzaXQgbW9zdGx5IGluIGJsYWRlIGFuZCBkaXNjLCBhbmQg"
    "b25seSByYXJlbHkgaW4gZXF1YW50LgogICAgQSBnZW5lcmF0b3IgdGhhdCBkcmF3cyBpdHMgdGhyZWUgZXh0ZW50cyBpbmRl"
    "cGVuZGVudGx5IGVtaXRzIGVxdWFudCBsdW1wcwogICAgZmFyIG1vcmUgb2Z0ZW4gdGhhbiBuYXR1cmUgZG9lcywgYW5kIGFu"
    "IGVxdWFudCBsdW1wIGlzIHRoZSBzaW5nbGUgbW9zdAogICAgInByb2NlZHVyYWwiIHNpbGhvdWV0dGUgYXZhaWxhYmxlLiAg"
    "VGhlIHJlbWFpbmluZyBwcm9iYWJpbGl0eSBhZnRlciB0aGUKICAgIHRocmVlIG5hbWVkIGNsYXNzZXMgaXMgYmxhZGUuCiAg"
    "ICAiIiIKICAgIHIgPSBybmcucmFuZG9tKCkKICAgIGlmIHIgPCBlcXVhbnQ6CiAgICAgICAgYmEsIGNiID0gcm5nLnVuaWZv"
    "cm0oMC43NSwgMC45NSksIHJuZy51bmlmb3JtKDAuNzIsIDAuOTIpCiAgICBlbGlmIHIgPCBlcXVhbnQgKyByb2Q6CiAgICAg"
    "ICAgYmEsIGNiID0gcm5nLnVuaWZvcm0oMC4zNSwgMC42MiksIHJuZy51bmlmb3JtKDAuNzIsIDAuOTUpCiAgICBlbGlmIHIg"
    "PCBlcXVhbnQgKyByb2QgKyBkaXNjOgogICAgICAgIGJhLCBjYiA9IHJuZy51bmlmb3JtKDAuNzIsIDAuOTUpLCBybmcudW5p"
    "Zm9ybSgwLjI4LCAwLjYwKQogICAgZWxzZToKICAgICAgICBiYSwgY2IgPSBybmcudW5pZm9ybSgwLjQwLCAwLjY0KSwgcm5n"
    "LnVuaWZvcm0oMC4zMiwgMC42MikKICAgIGEgPSBiYXNlCiAgICBiID0gYSAqIGJhCiAgICBjID0gYiAqIGNiCiAgICByZXR1"
    "cm4gYSwgYiwgYwoKCmRlZiBhZGRfYmxhZGUoYm0sIGJhc2UsIGhlaWdodCwgd2lkdGgsIHRoaWNrbmVzcywgYmVuZD0oMC4w"
    "LCAwLjApLAogICAgICAgICAgICAgIHN0YXRpb25zPTQsIHRhcGVyPTEuNiwgY3VybD0wLjApOgogICAgIiIiT25lIHRhcGVy"
    "ZWQsIENVUlZFRCBibGFkZSBvZiB2ZWdldGF0aW9uIGFzIGEgY2xvc2VkIHRyaWFuZ3VsYXIgcHJpc20uCgogICAgQnVpbHQg"
    "ZGlyZWN0bHkgcmF0aGVyIHRoYW4gZnJvbSBgYWRkX2N5bGluZGVyYCwgYmVjYXVzZSBhIGNvbmUgaGFzIG5vCiAgICBzdGF0"
    "aW9ucyBhbG9uZyBpdHMgbGVuZ3RoIGFuZCB0aGVyZWZvcmUgY2Fubm90IGJlbmQ6IHRoZSBmaXJzdCB3ZWVkX3R1ZnQKICAg"
    "IGtpdCB3YXMgZml2ZSBzdHJhaWdodCB0YXBlcmVkIHNwaWtlcywgd2hpY2ggaXMgd2h5IGl0IHJlbmRlcmVkIGFzIHBhcGVy"
    "CiAgICBzbGl2ZXJzIHJhdGhlciB0aGFuIGdyYXNzLiAgQSBibGFkZSB0aGF0IHJlYWRzIGhhcyB0aHJlZSBwcm9wZXJ0aWVz"
    "IGEKICAgIHN0cmFpZ2h0IHNwaWtlIGNhbm5vdCBoYXZlIC0tIGl0IGN1cnZlcywgaXQgaXMgd2lkZXN0IG5lYXIgdGhlIGJh"
    "c2UsIGFuZCBpdAogICAgZW5kcyBpbiBhIHBvaW50LgoKICAgIFNvbGlkLCBub3QgYSBjYXJkOiBhIGNyb3NzZWQtcXVhZCBi"
    "bGFkZSBpcyBhIHNpbmdsZS1zaWRlZCBwbGFuZSwgYW5kIHRoaXMKICAgIHJlcG8gaGFzIGFscmVhZHkgc3BlbnQgYSBzZXNz"
    "aW9uIGNoYXNpbmcgb25lIG9mIHRob3NlLiAgQSBjYXJkIHZhcmlhbnQgd2l0aAogICAgYW4gYWxwaGEgY3V0b3V0IGlzIHRo"
    "ZSByaWdodCBhbnN3ZXIgZm9yIGRlbnNlIGZvbGlhZ2UgbGF0ZXIsIHBlciAiY292ZXJhZ2UKICAgIGZpcnN0LCBhbHBoYSBj"
    "dXRvdXRzIHNlY29uZCI7IGl0IGlzIGEgZGlmZmVyZW50IHNwZWNpZXMsIG5vdCB0aGlzIG9uZS4KCiAgICBgYmVuZGAgaXMg"
    "dGhlIGhvcml6b250YWwgZGlzcGxhY2VtZW50IGF0IHRoZSB0aXAsIGFwcGxpZWQgcXVhZHJhdGljYWxseSBzbwogICAgdGhl"
    "IGJsYWRlIGxlYXZlcyB0aGUgZ3JvdW5kIHZlcnRpY2FsIGFuZCBsZWFucyBhcyBpdCByaXNlcy4gIGBjdXJsYCBhZGRzIGEK"
    "ICAgIGN1YmljIHRlcm0sIHdoaWNoIGlzIHdoYXQgbWFrZXMgYSBsb25nIGJsYWRlIGZvbGQgb3ZlciByYXRoZXIgdGhhbiBs"
    "ZWFuLgogICAgIiIiCiAgICBzdGF0aW9ucyA9IG1heCgyLCBpbnQoc3RhdGlvbnMpKQogICAgcmluZyA9IFtdCiAgICBmb3Ig"
    "aSBpbiByYW5nZShzdGF0aW9ucyk6CiAgICAgICAgdCA9IGkgLyBmbG9hdChzdGF0aW9ucykKICAgICAgICB3ID0gbWF4KDFl"
    "LTUsIHdpZHRoICogMC41ICogKDEuMCAtIHQgKiogdGFwZXIpKQogICAgICAgIHRoID0gbWF4KDFlLTUsIHRoaWNrbmVzcyAq"
    "ICgxLjAgLSB0ICogMC43NSkpCiAgICAgICAgeiA9IGhlaWdodCAqIHQKICAgICAgICBkeCA9IGJlbmRbMF0gKiB0ICogdCAr"
    "IGN1cmwgKiAodCAqKiAzKSAqIGJlbmRbMF0KICAgICAgICBkeSA9IGJlbmRbMV0gKiB0ICogdCArIGN1cmwgKiAodCAqKiAz"
    "KSAqIGJlbmRbMV0KICAgICAgICByaW5nLmFwcGVuZChbYm0udmVydHMubmV3KChiYXNlWzBdICsgZHggLSB3LCBiYXNlWzFd"
    "ICsgZHksIGJhc2VbMl0gKyB6KSksCiAgICAgICAgICAgICAgICAgICAgIGJtLnZlcnRzLm5ldygoYmFzZVswXSArIGR4ICsg"
    "dywgYmFzZVsxXSArIGR5LCBiYXNlWzJdICsgeikpLAogICAgICAgICAgICAgICAgICAgICBibS52ZXJ0cy5uZXcoKGJhc2Vb"
    "MF0gKyBkeCwgYmFzZVsxXSArIGR5ICsgdGgsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgYmFzZVsyXSAr"
    "IHopKV0pCiAgICB0aXAgPSBibS52ZXJ0cy5uZXcoKGJhc2VbMF0gKyBiZW5kWzBdICogKDEuMCArIGN1cmwpLAogICAgICAg"
    "ICAgICAgICAgICAgICAgICBiYXNlWzFdICsgYmVuZFsxXSAqICgxLjAgKyBjdXJsKSwKICAgICAgICAgICAgICAgICAgICAg"
    "ICAgYmFzZVsyXSArIGhlaWdodCkpCiAgICBmb3IgaSBpbiByYW5nZShzdGF0aW9ucyAtIDEpOgogICAgICAgIGEsIGIgPSBy"
    "aW5nW2ldLCByaW5nW2kgKyAxXQogICAgICAgIGZvciBrIGluIHJhbmdlKDMpOgogICAgICAgICAgICBrMiA9IChrICsgMSkg"
    "JSAzCiAgICAgICAgICAgIGJtLmZhY2VzLm5ldygoYVtrXSwgYVtrMl0sIGJbazJdLCBiW2tdKSkKICAgIGxhc3QgPSByaW5n"
    "Wy0xXQogICAgZm9yIGsgaW4gcmFuZ2UoMyk6CiAgICAgICAgYm0uZmFjZXMubmV3KChsYXN0W2tdLCBsYXN0WyhrICsgMSkg"
    "JSAzXSwgdGlwKSkKICAgIGJtLmZhY2VzLm5ldygocmluZ1swXVsyXSwgcmluZ1swXVsxXSwgcmluZ1swXVswXSkpCiAgICB2"
    "ZXJ0cyA9IFt2IGZvciByIGluIHJpbmcgZm9yIHYgaW4gcl0gKyBbdGlwXQogICAgcmV0dXJuIHZlcnRzCgoK"
  ),
}


def repo_root(start=None):
    """Walk up from this script until the tree looks like gabagool_factory."""
    d = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    for _ in range(8):
        if (os.path.isdir(os.path.join(d, "zoo", "zoo_keeper"))
                and os.path.isdir(os.path.join(d, "tools"))):
            return d
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    return None


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rd(p):
    with open(p, "rb") as fh:
        return fh.read()


def wr(p, b):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as fh:
        fh.write(b)


def geometry_apply(pre_text):
    """The anchored edit, as a pure function so --selftest can falsify it."""
    if pre_text.count(ANCHOR) != 1:
        raise ValueError(f"anchor {ANCHOR!r} occurs {pre_text.count(ANCHOR)} "
                         "times, expected exactly 1")
    if pre_text.count(IMPORT_OLD) != 1:
        raise ValueError(f"import anchor occurs {pre_text.count(IMPORT_OLD)} "
                         "times, expected exactly 1")
    block = base64.b64decode(GEOMETRY["block_b64"]).decode("utf-8")
    out = pre_text.replace(IMPORT_OLD, IMPORT_NEW, 1)
    return out.replace(ANCHOR, block + ANCHOR, 1)


def plan(root):
    """Return (ok, rows). Reads only; writes nothing."""
    rows, ok = [], True
    for rel, d in PAYLOAD.items():
        p = os.path.join(root, rel.replace("/", os.sep))
        exists = os.path.isfile(p)
        if d["kind"] == "new":
            if exists and sha(rd(p)) == d["post_sha"]:
                rows.append((rel, "already-current", True))
            elif exists:
                rows.append((rel, "EXISTS AND DIFFERS - refusing", False))
                ok = False
            else:
                rows.append((rel, f"create {d['post_bytes']} B", True))
            continue
        if not exists:
            rows.append((rel, "MISSING - refusing", False))
            ok = False
            continue
        cur = sha(rd(p))
        if cur == d["post_sha"]:
            rows.append((rel, "already-current", True))
        elif cur == d["pre_sha"]:
            rows.append((rel, f"replace {d['pre_bytes']} -> {d['post_bytes']} B",
                         True))
        else:
            rows.append((rel, f"DRIFT sha {cur[:12]} != {d['pre_sha'][:12]}",
                         False))
            ok = False

    p = os.path.join(root, GEOMETRY_REL.replace("/", os.sep))
    if not os.path.isfile(p):
        rows.append((GEOMETRY_REL, "MISSING - refusing", False))
        ok = False
    else:
        cur = sha(rd(p))
        if cur == GEOMETRY["post_sha"]:
            rows.append((GEOMETRY_REL, "already-current", True))
        elif cur == GEOMETRY["pre_sha"]:
            rows.append((GEOMETRY_REL,
                         f"anchored insert {GEOMETRY['pre_bytes']} -> "
                         f"{GEOMETRY['post_bytes']} B", True))
        else:
            rows.append((GEOMETRY_REL,
                         f"DRIFT sha {cur[:12]} != {GEOMETRY['pre_sha'][:12]}",
                         False))
            ok = False
    return ok, rows


def show(rows):
    w = max(len(r[0]) for r in rows)
    for rel, msg, good in rows:
        print(f"  {'ok ' if good else 'STOP'}  {rel:<{w}}  {msg}")


def apply(root):
    ok, rows = plan(root)
    show(rows)
    if not ok:
        print("\nREFUSING: nothing written. Resolve the lines marked STOP.")
        return 1
    written = 0
    for rel, d in PAYLOAD.items():
        p = os.path.join(root, rel.replace("/", os.sep))
        post = base64.b64decode(d["b64"])
        if os.path.isfile(p):
            cur = rd(p)
            if sha(cur) == d["post_sha"]:
                continue
            side = p + SIDECAR
            if not os.path.exists(side):
                wr(side, cur)
        wr(p, post)
        assert sha(rd(p)) == d["post_sha"], rel
        written += 1

    p = os.path.join(root, GEOMETRY_REL.replace("/", os.sep))
    cur = rd(p)
    if sha(cur) != GEOMETRY["post_sha"]:
        side = p + SIDECAR
        if not os.path.exists(side):
            wr(side, cur)
        out = geometry_apply(cur.decode("utf-8")).encode("utf-8")
        if sha(out) != GEOMETRY["post_sha"]:
            raise SystemExit("geometry.py: result hash mismatch, aborting "
                             f"({sha(out)[:12]} != {GEOMETRY['post_sha'][:12]})")
        wr(p, out)
        written += 1
    print(f"\nWROTE {written} file(s). Sidecars: *{SIDECAR}")
    print("Next, in this order, and read each before running the next:")
    print("  python tools/shape_metrics.py --selftest")
    print("  pwsh -ExecutionPolicy Bypass -File zoo\\tools\\preview_dressing.ps1")
    return 0


def revert(root):
    n = 0
    for rel in list(PAYLOAD) + [GEOMETRY_REL]:
        p = os.path.join(root, rel.replace("/", os.sep))
        side = p + SIDECAR
        if os.path.exists(side):
            wr(p, rd(side))
            os.remove(side)
            print(f"  reverted {rel}")
            n += 1
        elif PAYLOAD.get(rel, {}).get("kind") == "new" and os.path.isfile(p):
            if sha(rd(p)) == PAYLOAD[rel]["post_sha"]:
                os.remove(p)
                print(f"  removed  {rel} (this patch created it)")
                n += 1
            else:
                print(f"  KEPT     {rel} (modified since; not ours to delete)")
    print(f"reverted {n} file(s)")
    return 0


def selftest():
    bad = 0

    def fail(msg):
        nonlocal bad
        print(f"  FAIL  {msg}")
        bad += 1

    print("patch_dressing_shape selftest")

    # 1. every payload decodes to its recorded hash and byte count
    for rel, d in PAYLOAD.items():
        b = base64.b64decode(d["b64"])
        if sha(b) != d["post_sha"] or len(b) != d["post_bytes"]:
            fail(f"payload {rel} does not match its recorded hash/size")
    print(f"  ok    {len(PAYLOAD)} payloads decode to their recorded hashes")

    # 2. the anchored edit reproduces the recorded post-hash from a file with
    #    the recorded pre-hash -- reconstructed here, not read from disk.
    block = base64.b64decode(GEOMETRY["block_b64"]).decode("utf-8")
    if ANCHOR in block:
        fail("the inserted block contains the anchor it is inserted before; "
             "applying twice would be undetectable")
    print("  ok    inserted block does not contain its own anchor")

    # 3. FALSIFICATION: a duplicated anchor must be REFUSED, not silently
    #    half-applied. Two selftest needles in this repo have already spanned a
    #    line break and tested nothing, so this asserts on the exception.
    doubled = f"x\n{IMPORT_OLD}\ny\n{ANCHOR}\nz\n{ANCHOR}\n"
    try:
        geometry_apply(doubled)
        fail("a doubled anchor was accepted; the occurrence check is dead")
    except ValueError:
        print("  ok    doubled anchor refused")

    # 4. FALSIFICATION: a missing anchor must be REFUSED.
    try:
        geometry_apply(f"x\n{IMPORT_OLD}\nno anchor here\n")
        fail("a missing anchor was accepted; the occurrence check is dead")
    except ValueError:
        print("  ok    missing anchor refused")

    # 5. FALSIFICATION: drift detection. One flipped byte in a pre-image must
    #    change its hash; if not, the whole refuse-on-drift rule is theatre.
    ref = base64.b64decode(next(iter(PAYLOAD.values()))["b64"])
    mutated = bytearray(ref)
    mutated[len(mutated) // 2] ^= 0x20
    if sha(bytes(mutated)) == sha(ref):
        fail("a mutated payload hashed identically")
    else:
        print("  ok    one flipped byte changes the hash")

    # 6. the applied result must be exactly the recorded post-image, so a
    #    partial insert cannot pass.
    root = repo_root()
    if root:
        p = os.path.join(root, GEOMETRY_REL.replace("/", os.sep))
        if os.path.isfile(p):
            cur = rd(p)
            if sha(cur) == GEOMETRY["pre_sha"]:
                got = geometry_apply(cur.decode("utf-8")).encode("utf-8")
                if sha(got) != GEOMETRY["post_sha"]:
                    fail("applying the anchored edit to the real pre-image "
                         "did not reproduce the recorded post-image")
                else:
                    print("  ok    anchored edit reproduces the post-image on "
                          "the real file")
            elif sha(cur) == GEOMETRY["post_sha"]:
                print("  ok    geometry.py is already at the post-image")
            else:
                print("  note  geometry.py is at neither hash; --check will "
                      "report the drift")
    else:
        print("  note  repo root not found from here; skipped the on-disk check")

    print("SELFTEST", "PASSED" if bad == 0 else f"FAILED ({bad})")
    return 1 if bad else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = None
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    root = root or repo_root()
    if not root:
        print("Could not find the gabagool_factory root from this script's "
              "location. Pass --root <path>.")
        return 2
    print(f"repo root: {root}")
    if "--revert" in argv:
        return revert(root)
    ok, rows = plan(root)
    if "--check" in argv:
        show(rows)
        print("\n--check only: nothing written."
              + ("" if ok else "  RESOLVE THE STOP LINES FIRST."))
        return 0 if ok else 1
    return apply(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
