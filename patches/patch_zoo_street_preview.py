r"""Can we make cars? Yes -- and a preview that measures what they collide with.

    python patches/patch_zoo_street_preview.py --check
    python patches/patch_zoo_street_preview.py
    python patches/patch_zoo_street_preview.py --selftest
    python patches/patch_zoo_street_preview.py --revert

Run from the FACTORY ROOT.

## What this is for

`simple_car` has been a Zoo species the whole time, along with `hvac_unit`,
`water_tank`, `vending_machine`, `sign_box`, `streetlight` and `prop`. Nothing
placed them, and nothing looked at them. This adds the looking.

`tools/preview_street_solids.ps1` is the sibling of `preview_dressing.ps1`:
build, render, measure. It asks one extra question, because these species are
the opposite of surface dressing -- dressing is collisionless by definition,
and a stand-in solid exists BECAUSE of the volume it occupies. So it reads the
collision back out of every built GLB with
`level_factory/packages/validation/glb_collision.py`, which needs neither
Blender nor Godot, and prints it beside the shape metrics.

Zoo ships collision as a `-colonly` sibling mesh built from BOXES
(`bpylayer/collision.py`), and `recipes/simple_car.py` returns two of them --
body and cabin. So a car already brings a clean two-box gameplay volume rather
than a triangle hull. That is worth seeing measured rather than assumed.

## The one real change to a shipped tool

`tools/preview_specimen.py` gains `--species`. `build.build_specimen` has
accepted `species=` since 0.38.0 -- `core.intent.parse` calls it "the door a
program uses" -- and this tool was still knocking with a prompt. Two species in
the library could never be reached by prompt at all, and a prompt that resolves
today does so because no better keyword match exists yet. A preview naming
seven species by prompt is seven coincidences.

`--prompt` alone behaves exactly as before; the prompt still styles the build.

## What this does NOT do

It places nothing. A car still has nowhere to go: Lot's cover boxes are a fixed
3.0 x 2.0 x 3.0 square and `simple_car` is 3.6-5.2 m deep, so it does not fit
one and would not fill one if it did. That needs road-aware placement, which is
Lot work. This is the art half, and the art half already exists.
"""
from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_streetpreview"

PREVIEW = "zoo/tools/preview_specimen.py"
SCRIPT = "zoo/tools/preview_street_solids.ps1"
VERSION_FILE = "zoo/VERSION"
CHANGELOG = "zoo/CHANGELOG.md"

OLD_VERSION, NEW_VERSION = "Zoo 0.39.0", "Zoo 0.39.1"
CHANGELOG_ANCHOR = "# Changelog\n"

PREVIEW_PRE = "0d36a978b06608e86ac2ea9a13e0efcaf625f92f929db5f39f56279b69da6488"
PREVIEW_POST = "a294f72565d4b40d213a6442565f7db649e7eb4fdbb7b9519291918fce5a9723"
PREVIEW_BYTES = 10406
SCRIPT_POST = "a55db0c8fbf1ec32833004b0428d7d4c92fc2aba3f6adc1f7cf71d0d555eb447"
SCRIPT_BYTES = 4509

PREVIEW_B64 = """\
IiIiSGVhZGxlc3MgYnVpbGQgKyByZW5kZXIgb2Ygb25lIFpvbyBzcGVjaW1lbiDigJQgYSBxdWlj
ayB2aXN1YWwgY2hlY2suCgpSdW4gaW5zaWRlIEJsZW5kZXIgKHNlZSB0b29scy9wcmV2aWV3X2Ry
ZXNzaW5nLnBzMSk6CgogICAgYmxlbmRlciAtLWJhY2tncm91bmQgLS1weXRob24gdG9vbHMvcHJl
dmlld19zcGVjaW1lbi5weSAtLSBcCiAgICAgICAgLS1wcm9tcHQgImNhcnBldCBmbG9vciIgLS1z
ZWVkIDE5OTkgLS1vdXQgX3ByZXZpZXcgXAogICAgICAgIC0tcmVuZGVyIF9wcmV2aWV3L2Zsb29y
X2NhcnBldC5wbmcgWy0tc2tpbnMgPGRpcj4gLS10aGVtZSBkZWxjb10KCmAtLXNwZWNpZXMgPG5h
bWU+YCBuYW1lcyB0aGUgc3BlY2llcyBPVVRSSUdIVCBhbmQgc2tpcHMga2V5d29yZCBtYXRjaGlu
ZyAtLQp0aGUgZG9vciBhIHByb2dyYW0gdXNlcywgYWxyZWFkeSBvcGVuIGluIGBidWlsZC5idWls
ZF9zcGVjaW1lbmAgYW5kIHVudGlsIG5vdwpub3Qgd2lyZWQgdG8gdGhpcyB0b29sLiBgY29yZS5p
bnRlbnQucGFyc2VgIGV4cGxhaW5zIHdoeSBpdCBtYXR0ZXJzOiB0d28Kc3BlY2llcyBpbiB0aGUg
bGlicmFyeSBjb3VsZCBub3QgYmUgcmVhY2hlZCB0aHJvdWdoIGEgcHJvbXB0IGF0IGFsbCwgYW5k
IGEKcHJvbXB0IHRoYXQgcmVzb2x2ZXMgdG9kYXkgZG9lcyBzbyBiZWNhdXNlIG5vIGJldHRlciBr
ZXl3b3JkIG1hdGNoIGV4aXN0cyB5ZXQsCndoaWNoIGlzIGEgY29pbmNpZGVuY2UgcmF0aGVyIHRo
YW4gYSBjb250cmFjdC4gQSBwcmV2aWV3IHNjcmlwdCBuYW1pbmcgc2V2ZW4Kc3BlY2llcyBieSBw
cm9tcHQgaXMgc2V2ZW4gY29pbmNpZGVuY2VzLiBUaGUgcHJvbXB0IGlzIHN0aWxsIHBhcnNlZCBm
b3IKbWF0ZXJpYWwsIGNvbG91ciwgd2Vhciwgc2l6ZSBhbmQgZXJhLCBzbyBzdHlsaW5nIHN1cnZp
dmVzLgoKQnVpbGRzIHRoZSBzcGVjaW1lbiB3aXRoIHRoZSBub3JtYWwgWm9vIHBpcGVsaW5lLCB0
aGVuIGZyYW1lcyBpdCBhbmQgcmVuZGVycyBhClBORyB3aXRoIEN5Y2xlcyBDUFUgKHJlbGlhYmxl
IGhlYWRsZXNzKS4gV2l0aCAtLXNraW5zIGl0IHNob3dzIHRoZSBQaXhlbGNvYXQKdGV4dHVyZTsg
d2l0aG91dCwgdGhlIGZsYXQgc3R5bGUgY29sb3VyICsgYmFrZWQgd2Vhci4gUHJpbnRzIHRoZSBi
dWlsZCBzdGF0dXMgc28KdGhlIGNvbnNvbGUgYWxvbmUgY29uZmlybXMgdGhlIHNwZWNpZXMgcmVz
b2x2ZWQgZXZlbiBpZiByZW5kZXJpbmcgaXMgc2tpcHBlZC4KCldIWSBUSEVSRSBJUyBBIEdST1VO
RCBQTEFORSBBTkQgQSBSRUQgUE9TVCBJTiBFVkVSWSBGUkFNRS4gIFRoZSBmaXJzdCB2ZXJzaW9u
CmZyYW1lZCBlYWNoIHNwZWNpbWVuIHdpdGggYGRpc3QgPSBzaXplICogMi40YCwgc28gZXZlcnkg
b2JqZWN0IGZpbGxlZCB0aGUgZnJhbWUKd2hhdGV2ZXIgaXRzIHJlYWwgc2l6ZTogYSA1IGNtIHBl
YmJsZSBhbmQgYSAzMCBjbSBzY3JhcCByZW5kZXJlZCBpZGVudGljYWxseSwKYW5kIHRoZXJlIHdh
cyBubyBmbG9vciwgc28gbm90aGluZyBzaG93ZWQgd2hldGhlciBhIHRoaW5nIHNhdCBvbiBhIHN1
cmZhY2UsCmhvdmVyZWQgb3ZlciBpdCBvciBzYW5rIHRocm91Z2ggaXQuICBGb3VyIHN1cmZhY2Ut
ZHJlc3Npbmcgc3BlY2llcyB3ZXJlCnJldmlld2VkIGZyb20gaW1hZ2VzIGxpa2UgdGhhdCBhbmQg
dGhlIHJldmlldyBjb3VsZCBub3QgaGF2ZSBjYXVnaHQgYSBzY2FsZQplcnJvciBpZiBvbmUgaGFk
IGJlZW4gdGhlcmUuICBBdXRvLWZyYW1pbmcgaXMga2VwdCwgYmVjYXVzZSBhIDQgbSBmbG9vciBt
b2R1bGUKYW5kIGEgNSBjbSBzdG9uZSBjYW5ub3Qgc2hhcmUgYSBjYW1lcmEgZGlzdGFuY2UgLS0g
YnV0IHRoZSBmcmFtZSBub3cgYWx3YXlzCmNvbnRhaW5zOgoKICAqIGEgZ3JvdW5kIHBsYW5lIGF0
IHogPSAwLCBzbyBjb250YWN0IGlzIHZpc2libGU7CiAgKiBhIHJlZCBwb3N0IGV4YWN0bHkgMC4x
MTcgbSB0YWxsLiAgVGhhdCBpcyBgdW5hc3Npc3RlZF9zdGVwX21heGAgZnJvbQogICAgYGxvdC9z
aXRlX3N0ZXBzLnB5YCAtLSB0aGUgbnVtYmVyIGV2ZXJ5IGRyZXNzaW5nIGhlaWdodCBpbiB0aGlz
IHJlcG8gaXMKICAgIGFyZ3VlZCBhZ2FpbnN0IC0tIHNvIHRoZSBvbmx5IHJ1bGVyIGluIHNob3Qg
aXMgdGhlIG9uZSB0aGF0IG1hdHRlcnMuCgotLXZpZXcgcGF0Y2ggcmVuZGVycyBtYW55IGluc3Rh
bmNlcyBzY2F0dGVyZWQgb24gdGhlIGdyb3VuZCBhdCBzdGFuZGluZyBleWUKaGVpZ2h0LCB3aGlj
aCBpcyB0aGUgdW5pdCBhIHNjYXR0ZXIgc3BlY2llcyBpcyBhY3R1YWxseSBqdWRnZWQgaW46IGEg
c2luZ2xlCnNwZWNpbWVuIGlzIG5ldmVyIHdoYXQgdGhlIHBsYXllciBzZWVzLgoiIiIKZnJvbSBf
X2Z1dHVyZV9fIGltcG9ydCBhbm5vdGF0aW9ucwoKaW1wb3J0IG1hdGgKaW1wb3J0IG9zCmltcG9y
dCByYW5kb20KaW1wb3J0IHN5cwoKIyBsb3Qvc2l0ZV9zdGVwcy5weTogUiAqICgxIC0gY29zKGZs
b29yX21heF9hbmdsZSkpIGZvciBhIDAuNCBtIGNhcHN1bGUgYXQgNDUuClVOQVNTSVNURURfU1RF
UF9NQVhfTSA9IDAuMTE3CgoKZGVmIF9hcmcoZmxhZywgZGVmYXVsdD1Ob25lKToKICAgIGFyZ3Yg
PSBzeXMuYXJndgogICAgYXJndiA9IGFyZ3ZbYXJndi5pbmRleCgiLS0iKSArIDE6XSBpZiAiLS0i
IGluIGFyZ3YgZWxzZSBhcmd2WzE6XQogICAgcmV0dXJuIGFyZ3ZbYXJndi5pbmRleChmbGFnKSAr
IDFdIGlmIGZsYWcgaW4gYXJndiBlbHNlIGRlZmF1bHQKCgpkZWYgX2ZsYWcoZmxhZyk6CiAgICBh
cmd2ID0gc3lzLmFyZ3YKICAgIGFyZ3YgPSBhcmd2W2FyZ3YuaW5kZXgoIi0tIikgKyAxOl0gaWYg
Ii0tIiBpbiBhcmd2IGVsc2UgYXJndlsxOl0KICAgIHJldHVybiBmbGFnIGluIGFyZ3YKCgpkZWYg
X2dyb3VuZChicHksIHNpemU9OC4wKToKICAgIG1lID0gYnB5LmRhdGEubWVzaGVzLm5ldygiUHJl
dkdyb3VuZCIpCiAgICBtZS5mcm9tX3B5ZGF0YShbKC1zaXplLCAtc2l6ZSwgMC4wKSwgKHNpemUs
IC1zaXplLCAwLjApLAogICAgICAgICAgICAgICAgICAgIChzaXplLCBzaXplLCAwLjApLCAoLXNp
emUsIHNpemUsIDAuMCldLCBbXSwgWygwLCAxLCAyLCAzKV0pCiAgICBvYiA9IGJweS5kYXRhLm9i
amVjdHMubmV3KCJQcmV2R3JvdW5kIiwgbWUpCiAgICBicHkuY29udGV4dC5zY2VuZS5jb2xsZWN0
aW9uLm9iamVjdHMubGluayhvYikKICAgIG0gPSBicHkuZGF0YS5tYXRlcmlhbHMubmV3KCJNX1By
ZXZHcm91bmQiKQogICAgbS51c2Vfbm9kZXMgPSBUcnVlCiAgICBiID0gbS5ub2RlX3RyZWUubm9k
ZXMuZ2V0KCJQcmluY2lwbGVkIEJTREYiKQogICAgaWYgYjoKICAgICAgICAjIE1pZCBncmV5IG9u
IHB1cnBvc2U6IGEgZGFyayBmbG9vciBmbGF0dGVycyBkcmVzc2luZyBieSBnaXZpbmcgaXQKICAg
ICAgICAjIGNvbnRyYXN0IGl0IHdpbGwgbm90IGhhdmUgb24gYSByZWFsIGNvbmNyZXRlIHN1cmZh
Y2UuCiAgICAgICAgYi5pbnB1dHNbIkJhc2UgQ29sb3IiXS5kZWZhdWx0X3ZhbHVlID0gKDAuNDIs
IDAuNDIsIDAuNDMsIDEuMCkKICAgICAgICBiLmlucHV0c1siUm91Z2huZXNzIl0uZGVmYXVsdF92
YWx1ZSA9IDAuOTUKICAgIG9iLmRhdGEubWF0ZXJpYWxzLmFwcGVuZChtKQogICAgcmV0dXJuIG9i
CgoKZGVmIF9zY2FsZV9wb3N0KGJweSwgYXQsIGhlaWdodD1VTkFTU0lTVEVEX1NURVBfTUFYX00p
OgogICAgbWUgPSBicHkuZGF0YS5tZXNoZXMubmV3KCJQcmV2U2NhbGVQb3N0IikKICAgIHIgPSBt
YXgoMC4wMDgsIGhlaWdodCAqIDAuMDkpCiAgICB2ID0gWygtciwgLXIsIDAuMCksIChyLCAtciwg
MC4wKSwgKHIsIHIsIDAuMCksICgtciwgciwgMC4wKSwKICAgICAgICAgKC1yLCAtciwgaGVpZ2h0
KSwgKHIsIC1yLCBoZWlnaHQpLCAociwgciwgaGVpZ2h0KSwgKC1yLCByLCBoZWlnaHQpXQogICAg
ZiA9IFsoMCwgMywgMiwgMSksICg0LCA1LCA2LCA3KSwgKDAsIDEsIDUsIDQpLAogICAgICAgICAo
MSwgMiwgNiwgNSksICgyLCAzLCA3LCA2KSwgKDMsIDAsIDQsIDcpXQogICAgbWUuZnJvbV9weWRh
dGEodiwgW10sIGYpCiAgICBvYiA9IGJweS5kYXRhLm9iamVjdHMubmV3KCJQcmV2U2NhbGVQb3N0
IiwgbWUpCiAgICBvYi5sb2NhdGlvbiA9IGF0CiAgICBicHkuY29udGV4dC5zY2VuZS5jb2xsZWN0
aW9uLm9iamVjdHMubGluayhvYikKICAgIG0gPSBicHkuZGF0YS5tYXRlcmlhbHMubmV3KCJNX1By
ZXZTY2FsZVBvc3QiKQogICAgbS51c2Vfbm9kZXMgPSBUcnVlCiAgICBiID0gbS5ub2RlX3RyZWUu
bm9kZXMuZ2V0KCJQcmluY2lwbGVkIEJTREYiKQogICAgaWYgYjoKICAgICAgICBiLmlucHV0c1si
QmFzZSBDb2xvciJdLmRlZmF1bHRfdmFsdWUgPSAoMC44NSwgMC4yMiwgMC4xNSwgMS4wKQogICAg
b2IuZGF0YS5tYXRlcmlhbHMuYXBwZW5kKG0pCiAgICByZXR1cm4gb2IKCgpkZWYgX2xpZ2h0X2Fu
ZF93b3JsZChicHksIG1hdGhfKToKICAgIHNkID0gYnB5LmRhdGEubGlnaHRzLm5ldygiUHJldlN1
biIsICJTVU4iKQogICAgc2QuZW5lcmd5ID0gMy41CiAgICB0cnk6CiAgICAgICAgc2QuYW5nbGUg
PSAwLjEwCiAgICBleGNlcHQgRXhjZXB0aW9uOgogICAgICAgIHBhc3MKICAgIHN1biA9IGJweS5k
YXRhLm9iamVjdHMubmV3KCJQcmV2U3VuIiwgc2QpCiAgICBicHkuY29udGV4dC5zY2VuZS5jb2xs
ZWN0aW9uLm9iamVjdHMubGluayhzdW4pCiAgICBzdW4ucm90YXRpb25fZXVsZXIgPSAobWF0aF8u
cmFkaWFucyg1NSksIG1hdGhfLnJhZGlhbnMoMTIpLAogICAgICAgICAgICAgICAgICAgICAgICAg
IG1hdGhfLnJhZGlhbnMoMzUpKQogICAgc2MgPSBicHkuY29udGV4dC5zY2VuZQogICAgaWYgc2Mu
d29ybGQgaXMgTm9uZToKICAgICAgICBzYy53b3JsZCA9IGJweS5kYXRhLndvcmxkcy5uZXcoIlBy
ZXZXb3JsZCIpCiAgICBzYy53b3JsZC51c2Vfbm9kZXMgPSBUcnVlCiAgICBiZyA9IHNjLndvcmxk
Lm5vZGVfdHJlZS5ub2Rlcy5nZXQoIkJhY2tncm91bmQiKQogICAgaWYgYmc6CiAgICAgICAgYmcu
aW5wdXRzWzBdLmRlZmF1bHRfdmFsdWUgPSAoMC4wOSwgMC4xMCwgMC4xMiwgMS4wKQogICAgICAg
IGJnLmlucHV0c1sxXS5kZWZhdWx0X3ZhbHVlID0gMC41NQoKCmRlZiBfYm91bmRzKGJweSwgbWF0
aHV0aWxzLCBtZXNoZXMpOgogICAgbG8gPSBbMWU5XSAqIDMKICAgIGhpID0gWy0xZTldICogMwog
ICAgZm9yIG8gaW4gbWVzaGVzOgogICAgICAgIGZvciBjb3JuZXIgaW4gby5ib3VuZF9ib3g6CiAg
ICAgICAgICAgIHdjID0gby5tYXRyaXhfd29ybGQgQCBtYXRodXRpbHMuVmVjdG9yKGNvcm5lcls6
XSkKICAgICAgICAgICAgZm9yIGkgaW4gcmFuZ2UoMyk6CiAgICAgICAgICAgICAgICBsb1tpXSA9
IG1pbihsb1tpXSwgd2NbaV0pCiAgICAgICAgICAgICAgICBoaVtpXSA9IG1heChoaVtpXSwgd2Nb
aV0pCiAgICByZXR1cm4gbG8sIGhpCgoKZGVmIG1haW4oKToKICAgIHByb21wdCA9IF9hcmcoIi0t
cHJvbXB0IiwgImNhcnBldCBmbG9vciIpCiAgICBzZWVkID0gaW50KF9hcmcoIi0tc2VlZCIsICIx
OTk5IikpCiAgICBvdXQgPSBvcy5wYXRoLmFic3BhdGgoX2FyZygiLS1vdXQiLCAiX3ByZXZpZXci
KSkKICAgIHJlbmRlciA9IG9zLnBhdGguYWJzcGF0aChfYXJnKCItLXJlbmRlciIsICJwcmV2aWV3
LnBuZyIpKQogICAgc2tpbnMgPSBfYXJnKCItLXNraW5zIikKICAgIHRoZW1lID0gX2FyZygiLS10
aGVtZSIsICJkZWxjbyIpCiAgICB2aWV3ID0gX2FyZygiLS12aWV3IiwgImF1dG8iKSAgICAgICAg
ICAgICMgYXV0byB8IHBhdGNoCiAgICBwYXRjaF9uID0gaW50KF9hcmcoIi0tcGF0Y2giLCAiNDUi
KSkKICAgIHBhdGNoX2V4dGVudCA9IGZsb2F0KF9hcmcoIi0tcGF0Y2gtZXh0ZW50IiwgIjEuMTUi
KSkKICAgIG5vX2dyb3VuZCA9IF9mbGFnKCItLW5vLWdyb3VuZCIpCiAgICBzcGVjaWVzID0gX2Fy
ZygiLS1zcGVjaWVzIiwgTm9uZSkKCiAgICByZXBvID0gb3MucGF0aC5kaXJuYW1lKG9zLnBhdGgu
ZGlybmFtZShvcy5wYXRoLmFic3BhdGgoX19maWxlX18pKSkKICAgIGlmIHJlcG8gbm90IGluIHN5
cy5wYXRoOgogICAgICAgIHN5cy5wYXRoLmluc2VydCgwLCByZXBvKQoKICAgIGZyb20gem9vX2tl
ZXBlci5icHlsYXllciBpbXBvcnQgYnVpbGQKICAgIGlmIHNraW5zOgogICAgICAgIGZyb20gem9v
X2tlZXBlci5icHlsYXllciBpbXBvcnQgbWF0ZXJpYWxzCiAgICAgICAgbWF0ZXJpYWxzLnNldF9z
a2luX2xpYnJhcnkob3MucGF0aC5hYnNwYXRoKHNraW5zKSwgdGhlbWUpCiAgICAgICAgcHJpbnQo
ZiJbcHJldmlld10gc2tpbnM6IHtza2luc30gKHRoZW1lPXt0aGVtZX0pIikKCiAgICByZXMgPSBi
dWlsZC5idWlsZF9zcGVjaW1lbigKICAgICAgICBwcm9tcHQsIG91dCwgc2VlZD1zZWVkLCBzcGVj
aWVzPXNwZWNpZXMsCiAgICAgICAgb3B0aW9ucz17ImNvbGxpc2lvbiI6IE5vbmUsICJsb2RzIjog
RmFsc2UsCiAgICAgICAgICAgICAgICAgInNhdmVfYmxlbmQiOiBGYWxzZSwgImNsZWFyX3NjZW5l
IjogVHJ1ZX0pCiAgICBhc2tlZCA9IGYic3BlY2llcz17c3BlY2llcyFyfSIgaWYgc3BlY2llcyBl
bHNlIGYicHJvbXB0PXtwcm9tcHQhcn0iCiAgICBwcmludChmIltwcmV2aWV3XSB7YXNrZWR9IC0+
IHNwZWNpbWVuPXtyZXNbJ3NwZWNpbWVuX2lkJ119ICIKICAgICAgICAgIGYic3RhdHVzPXtyZXNb
J3JlcG9ydCddWydzdGF0dXMnXS51cHBlcigpfSIpCgogICAgaW1wb3J0IGJweQogICAgaW1wb3J0
IG1hdGh1dGlscwogICAgc2NlbmUgPSBicHkuY29udGV4dC5zY2VuZQoKICAgIG1lc2hlcyA9IFtv
IGZvciBvIGluIHNjZW5lLm9iamVjdHMgaWYgby50eXBlID09ICJNRVNIIl0KICAgIGlmIG5vdCBt
ZXNoZXM6ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICMgZmFsbCBiYWNrIHRvIHRo
ZSBleHBvcnRlZCBnbGIKICAgICAgICBnbGIgPSBOb25lCiAgICAgICAgZm9yIHYgaW4gcmVzLmdl
dCgiZmlsZXMiLCB7fSkudmFsdWVzKCk6CiAgICAgICAgICAgIGlmIHN0cih2KS5sb3dlcigpLmVu
ZHN3aXRoKCIuZ2xiIik6CiAgICAgICAgICAgICAgICBnbGIgPSB2IGlmIG9zLnBhdGguaXNhYnMo
dikgZWxzZSBvcy5wYXRoLmpvaW4ocmVzWyJvdXRfZGlyIl0sIHYpCiAgICAgICAgaWYgZ2xiIGFu
ZCBvcy5wYXRoLmlzZmlsZShnbGIpOgogICAgICAgICAgICBicHkub3BzLmltcG9ydF9zY2VuZS5n
bHRmKGZpbGVwYXRoPWdsYikKICAgICAgICAgICAgbWVzaGVzID0gW28gZm9yIG8gaW4gc2NlbmUu
b2JqZWN0cyBpZiBvLnR5cGUgPT0gIk1FU0giXQogICAgcHJpbnQoZiJbcHJldmlld10gbWVzaCBv
YmplY3RzIGluIHNjZW5lOiB7bGVuKG1lc2hlcyl9IikKICAgIGlmIG5vdCBtZXNoZXM6CiAgICAg
ICAgcHJpbnQoIltwcmV2aWV3XSBub3RoaW5nIHRvIHJlbmRlciAoYnVpbGQgbWF5IGhhdmUgZmFp
bGVkKSDigJQgc2VlIHN0YXR1cyBhYm92ZSIpCiAgICAgICAgcmV0dXJuCgogICAgbG8sIGhpID0g
X2JvdW5kcyhicHksIG1hdGh1dGlscywgbWVzaGVzKQogICAgc2l6ZSA9IG1heCgxZS0zLCBtYXgo
aGlbaV0gLSBsb1tpXSBmb3IgaSBpbiByYW5nZSgzKSkpCgogICAgIyAtLS0tIG9wdGlvbmFsIHBh
dGNoIHZpZXc6IG1hbnkgaW5zdGFuY2VzLCBzdGFuZGluZyBleWUgaGVpZ2h0IC0tLS0tLS0tLQog
ICAgaWYgdmlldyA9PSAicGF0Y2giOgogICAgICAgIHJuZyA9IHJhbmRvbS5SYW5kb20oc2VlZCBe
IDB4NUVFRCkKICAgICAgICBjZW50cmVzID0gWyhybmcudW5pZm9ybSgtcGF0Y2hfZXh0ZW50LCBw
YXRjaF9leHRlbnQpLAogICAgICAgICAgICAgICAgICAgIHJuZy51bmlmb3JtKC1wYXRjaF9leHRl
bnQsIHBhdGNoX2V4dGVudCkpCiAgICAgICAgICAgICAgICAgICBmb3IgXyBpbiByYW5nZShtYXgo
MSwgcGF0Y2hfbiAvLyA3KSldCiAgICAgICAgc3JjID0gbGlzdChtZXNoZXMpCiAgICAgICAgZm9y
IGkgaW4gcmFuZ2UocGF0Y2hfbik6CiAgICAgICAgICAgIGlmIHJuZy5yYW5kb20oKSA8IDAuMTg6
ICAgICAgICAgICAgICAgICAjIHN0cmF5IHRhaWwKICAgICAgICAgICAgICAgIHggPSBybmcudW5p
Zm9ybSgtcGF0Y2hfZXh0ZW50LCBwYXRjaF9leHRlbnQpCiAgICAgICAgICAgICAgICB5ID0gcm5n
LnVuaWZvcm0oLXBhdGNoX2V4dGVudCwgcGF0Y2hfZXh0ZW50KQogICAgICAgICAgICBlbHNlOiAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIyBjbHVzdGVyZWQgYm9keQogICAgICAg
ICAgICAgICAgY3gsIGN5ID0gY2VudHJlc1tybmcucmFuZHJhbmdlKGxlbihjZW50cmVzKSldCiAg
ICAgICAgICAgICAgICB4ID0gbWF4KC1wYXRjaF9leHRlbnQsIG1pbihwYXRjaF9leHRlbnQsIGN4
ICsgcm5nLmdhdXNzKDAsIDAuMjIpKSkKICAgICAgICAgICAgICAgIHkgPSBtYXgoLXBhdGNoX2V4
dGVudCwgbWluKHBhdGNoX2V4dGVudCwgY3kgKyBybmcuZ2F1c3MoMCwgMC4yMikpKQogICAgICAg
ICAgICBzID0gMC42NSArIChybmcucmFuZG9tKCkgKiogMikgKiAwLjkgICAgIyBsb2dub3JtYWwt
aXNoIHNpemUgc3ByZWFkCiAgICAgICAgICAgIGZvciBvIGluIHNyYzoKICAgICAgICAgICAgICAg
IGR1cCA9IG8uY29weSgpICAgICAgICAgICAgICAgICAgICAgICMgbGlua2VkIGR1cGxpY2F0ZTog
c2hhcmVzIG1lc2gKICAgICAgICAgICAgICAgIGR1cC5sb2NhdGlvbiA9ICh4LCB5LCAwLjApCiAg
ICAgICAgICAgICAgICBkdXAucm90YXRpb25fZXVsZXIgPSAoMC4wLCAwLjAsIHJuZy51bmlmb3Jt
KDAuMCwgNi4yODMxODUzKSkKICAgICAgICAgICAgICAgIGR1cC5zY2FsZSA9IChzLCBzLCBzKQog
ICAgICAgICAgICAgICAgc2NlbmUuY29sbGVjdGlvbi5vYmplY3RzLmxpbmsoZHVwKQogICAgICAg
IGZvciBvIGluIHNyYzoKICAgICAgICAgICAgby5sb2NhdGlvbiA9IChwYXRjaF9leHRlbnQgKiAz
LjAsIDAuMCwgMC4wKSAgICMgbW92ZSB0aGUgb3JpZ2luYWwgb3V0CiAgICAgICAgdGFyZ2V0ID0g
bWF0aHV0aWxzLlZlY3RvcigoMC4wLCAwLjAsIHNpemUgKiAwLjUpKQogICAgICAgIGRpc3QgPSBw
YXRjaF9leHRlbnQgKiAyLjMKICAgICAgICBleWUgPSAxLjU1CiAgICAgICAgcmVzX3h5ID0gKDEx
MDAsIDYyMCkKICAgIGVsc2U6CiAgICAgICAgY2VudHJlID0gbWF0aHV0aWxzLlZlY3RvcihbKGxv
W2ldICsgaGlbaV0pIC8gMiBmb3IgaSBpbiByYW5nZSgzKV0pCiAgICAgICAgdGFyZ2V0ID0gbWF0
aHV0aWxzLlZlY3RvcigoY2VudHJlLngsIGNlbnRyZS55LCBtYXgobG9bMl0sIDAuMCkKICAgICAg
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICArIHNpemUgKiAwLjQpKQogICAgICAgIGRpc3Qg
PSBzaXplICogMi40CiAgICAgICAgZXllID0gbWF4KHNpemUgKiAwLjc1LCBtaW4oMS42LCBzaXpl
ICogMi4wKSkKICAgICAgICByZXNfeHkgPSAoOTYwLCA2NDApCgogICAgaWYgbm90IG5vX2dyb3Vu
ZDoKICAgICAgICBfZ3JvdW5kKGJweSwgc2l6ZT1tYXgoNC4wLCBzaXplICogNi4wKSkKICAgICAg
ICBfc2NhbGVfcG9zdChicHksICh0YXJnZXQueCArIG1heChzaXplICogMC45LCAwLjA2KSwKICAg
ICAgICAgICAgICAgICAgICAgICAgICB0YXJnZXQueSAtIG1heChzaXplICogMC41LCAwLjA0KSwg
MC4wKSkKCiAgICBjYW1fZGF0YSA9IGJweS5kYXRhLmNhbWVyYXMubmV3KCJQcmV2Q2FtIikKICAg
IGNhbV9kYXRhLmxlbnMgPSA0MC4wCiAgICBjYW0gPSBicHkuZGF0YS5vYmplY3RzLm5ldygiUHJl
dkNhbSIsIGNhbV9kYXRhKQogICAgc2NlbmUuY29sbGVjdGlvbi5vYmplY3RzLmxpbmsoY2FtKQog
ICAgc2NlbmUuY2FtZXJhID0gY2FtCiAgICBjYW0ubG9jYXRpb24gPSBtYXRodXRpbHMuVmVjdG9y
KChkaXN0ICogMC43MiwgLWRpc3QgKiAwLjcyLCBleWUpKQogICAgY2FtLnJvdGF0aW9uX2V1bGVy
ID0gKHRhcmdldCAtIGNhbS5sb2NhdGlvbikudG9fdHJhY2tfcXVhdCgiLVoiLCAiWSIpLnRvX2V1
bGVyKCkKCiAgICBfbGlnaHRfYW5kX3dvcmxkKGJweSwgbWF0aCkKCiAgICBzY2VuZS5yZW5kZXIu
ZW5naW5lID0gIkNZQ0xFUyIKICAgIHRyeToKICAgICAgICBzY2VuZS5jeWNsZXMuZGV2aWNlID0g
IkNQVSIKICAgICAgICBzY2VuZS5jeWNsZXMuc2FtcGxlcyA9IDQwCiAgICAgICAgc2NlbmUuY3lj
bGVzLnVzZV9kZW5vaXNpbmcgPSBUcnVlCiAgICBleGNlcHQgRXhjZXB0aW9uOgogICAgICAgIHBh
c3MKICAgIHNjZW5lLnJlbmRlci5yZXNvbHV0aW9uX3gsIHNjZW5lLnJlbmRlci5yZXNvbHV0aW9u
X3kgPSByZXNfeHkKICAgIHNjZW5lLnJlbmRlci5maWxlcGF0aCA9IHJlbmRlcgogICAgYnB5Lm9w
cy5yZW5kZXIucmVuZGVyKHdyaXRlX3N0aWxsPVRydWUpCiAgICBwcmludChmIltwcmV2aWV3XSBy
ZW5kZXJlZCAtPiB7cmVuZGVyfSAgIgogICAgICAgICAgZiIodmlldz17dmlld30sIGdyb3VuZD17
J25vJyBpZiBub19ncm91bmQgZWxzZSAneWVzJ30sICIKICAgICAgICAgIGYicnVsZXI9e1VOQVNT
SVNURURfU1RFUF9NQVhfTX0gbSkiKQoKCm1haW4oKQo=
"""

SCRIPT_B64 = """\
IyBCdWlsZCwgcmVuZGVyIGFuZCBNRUFTVVJFIHRoZSBzcGVjaWVzIHRoYXQgY291bGQgc3RhbmQg
aW4gZm9yIGEgZ2FtZXBsYXkKIyBzb2xpZCBvdXRkb29ycyAtLSBhIGNhciwgYSBkdW1wc3Rlci1z
aXplZCBib3gsIGEgdmVuZGluZyBtYWNoaW5lLCBhbiBIVkFDCiMgdW5pdCwgYSB3YXRlciB0YW5r
LCBhIHNpZ24gYm94LCBhIHN0cmVldGxpZ2h0LgojCiMgVGhlIHNpYmxpbmcgb2YgcHJldmlld19k
cmVzc2luZy5wczEsIGFuZCBpdCBhc2tzIG9uZSBleHRyYSBxdWVzdGlvbiB0aGF0IG9uZQojIGRv
ZXMgbm90IG5lZWQgdG8uIFN1cmZhY2UgZHJlc3NpbmcgaXMgY29sbGlzaW9ubGVzcyBieSBkZWZp
bml0aW9uLiBUaGVzZSBhcmUKIyB0aGUgb3Bwb3NpdGU6IHRoZXkgZXhpc3QgQkVDQVVTRSBvZiB0
aGUgdm9sdW1lIHRoZXkgb2NjdXB5LCBzbyB0aGUgc2NyaXB0CiMgcmVhZHMgdGhlIGNvbGxpc2lv
biBiYWNrIG91dCBvZiBldmVyeSBidWlsdCBHTEIgYW5kIHByaW50cyBpdCBiZXNpZGUgdGhlCiMg
c2hhcGUgbWV0cmljcy4gQSBzdGFuZC1pbiB3aG9zZSBjb2xsaWRlciBkb2VzIG5vdCBtYXRjaCBp
dHMgYXJ0IGlzIHRoZSB3aG9sZQojIGRlZmVjdCB0aGlzIGZhbWlseSBvZiB3b3JrIGlzIGFib3V0
LgojCiMgU1BFQ0lFUyBBUkUgTkFNRUQgT1VUUklHSFQsIG5vdCBwcm9tcHRlZC4gYGNvcmUuaW50
ZW50LnBhcnNlYCBzYXlzIHdoeTogYQojIHByb21wdCB0aGF0IHJlc29sdmVzIHRvZGF5IGRvZXMg
c28gYmVjYXVzZSBubyBiZXR0ZXIga2V5d29yZCBtYXRjaCBleGlzdHMKIyB5ZXQsIHdoaWNoIGlz
IGEgY29pbmNpZGVuY2UgYW5kIG5vdCBhIGNvbnRyYWN0LCBhbmQgdHdvIHNwZWNpZXMgaW4gdGhl
CiMgbGlicmFyeSBjb3VsZCBuZXZlciBiZSByZWFjaGVkIGJ5IHByb21wdCBhdCBhbGwuIFRoZSBw
cm9tcHQgc3RpbGwgcmlkZXMgYWxvbmcKIyBmb3IgbWF0ZXJpYWwsIGNvbG91ciBhbmQgd2Vhci4K
IwojIFVzYWdlOiAgcHdzaCAtRXhlY3V0aW9uUG9saWN5IEJ5cGFzcyAtRmlsZSBwcmV2aWV3X3N0
cmVldF9zb2xpZHMucHMxCgokQmxlbmRlciA9ICJDOlxibGVuZGVyXGJsZW5kZXIuZXhlIgokWm9v
ICAgICA9ICJDOlxQcm9qZWN0c1xnYWJhZ29vbF9zdHVkaW9zXGdhYmFnb29sX2ZhY3Rvcnlcem9v
IgokRmFjdG9yeSA9ICJDOlxQcm9qZWN0c1xnYWJhZ29vbF9zdHVkaW9zXGdhYmFnb29sX2ZhY3Rv
cnkiCgppZiAoLW5vdCAoVGVzdC1QYXRoICRCbGVuZGVyKSkgewogICRmb3VuZCA9IEdldC1DaGls
ZEl0ZW0gLVBhdGggIkM6XGJsZW5kZXIiIC1GaWx0ZXIgImJsZW5kZXIuZXhlIiAtUmVjdXJzZSAt
RXJyb3JBY3Rpb24gU2lsZW50bHlDb250aW51ZSB8IFNlbGVjdC1PYmplY3QgLUZpcnN0IDEKICBp
ZiAoJGZvdW5kKSB7ICRCbGVuZGVyID0gJGZvdW5kLkZ1bGxOYW1lIH0KICBlbHNlIHsgV3JpdGUt
RXJyb3IgImJsZW5kZXIuZXhlIG5vdCBmb3VuZCB1bmRlciBDOlxibGVuZGVyIC0gc2V0IGAkQmxl
bmRlciBhdCB0aGUgdG9wLiI7IGV4aXQgMSB9Cn0KCiRPdXQgID0gSm9pbi1QYXRoICRab28gIl9w
cmV2aWV3X3N0cmVldCIKJFRvb2wgPSBKb2luLVBhdGggJFpvbyAidG9vbHNccHJldmlld19zcGVj
aW1lbi5weSIKTmV3LUl0ZW0gLUl0ZW1UeXBlIERpcmVjdG9yeSAtRm9yY2UgLVBhdGggJE91dCB8
IE91dC1OdWxsCldyaXRlLUhvc3QgIkJsZW5kZXI6ICRCbGVuZGVyIgpXcml0ZS1Ib3N0ICJPdXQ6
ICAgICAkT3V0IgoKIyBzcGVjaWVzIGlzIHRoZSBjb250cmFjdDsgcHJvbXB0IG9ubHkgc3R5bGVz
IGl0Lgokam9icyA9IEAoCiAgQHsgc3BlY2llcyA9ICJzaW1wbGVfY2FyIjsgICAgICBwcm9tcHQg
PSAid2VhdGhlcmVkIHNlZGFuIjsgICAgICAgICAgICAgIG5hbWUgPSAiY2FyIiB9LAogIEB7IHNw
ZWNpZXMgPSAicHJvcCI7ICAgICAgICAgICAgcHJvbXB0ID0gInJ1c3RlZCBzdGVlbCBjb250YWlu
ZXIiOyAgICAgICBuYW1lID0gInNvbGlkIiB9LAogIEB7IHNwZWNpZXMgPSAiaHZhY191bml0Ijsg
ICAgICAgcHJvbXB0ID0gInJvb2Z0b3AgaHZhYyB1bml0IjsgICAgICAgICAgICBuYW1lID0gImh2
YWMiIH0sCiAgQHsgc3BlY2llcyA9ICJ3YXRlcl90YW5rIjsgICAgICBwcm9tcHQgPSAiZ2FsdmFu
aXNlZCB3YXRlciB0YW5rIjsgICAgICAgIG5hbWUgPSAidGFuayIgfSwKICBAeyBzcGVjaWVzID0g
InZlbmRpbmdfbWFjaGluZSI7IHByb21wdCA9ICJzdHJlZXQgdmVuZGluZyBtYWNoaW5lIjsgICAg
ICAgbmFtZSA9ICJ2ZW5kaW5nIiB9LAogIEB7IHNwZWNpZXMgPSAic2lnbl9ib3giOyAgICAgICAg
cHJvbXB0ID0gInNob3Bmcm9udCBzaWduIGJveCI7ICAgICAgICAgICBuYW1lID0gInNpZ24iIH0s
CiAgQHsgc3BlY2llcyA9ICJzdHJlZXRsaWdodCI7ICAgICBwcm9tcHQgPSAiY29uY3JldGUgc3Ry
ZWV0bGlnaHQiOyAgICAgICAgIG5hbWUgPSAic3RyZWV0bGlnaHQiIH0KKQoKZm9yZWFjaCAoJGog
aW4gJGpvYnMpIHsKICBXcml0ZS1Ib3N0ICJgbj09PSBCdWlsZGluZzogJCgkai5zcGVjaWVzKSA9
PT0iCiAgJiAkQmxlbmRlciAtLWJhY2tncm91bmQgLS1weXRob24gJFRvb2wgLS0gYAogICAgICAt
LXNwZWNpZXMgJGouc3BlY2llcyAtLXByb21wdCAkai5wcm9tcHQgLS1zZWVkIDE5OTkgLS1vdXQg
JE91dCBgCiAgICAgIC0tcmVuZGVyIChKb2luLVBhdGggJE91dCAoJGoubmFtZSArICJfc3BlY2lt
ZW4ucG5nIikpCiAgaWYgKCRMQVNURVhJVENPREUgLW5lIDApIHsgV3JpdGUtSG9zdCAiICAoYnVp
bGQgcmVwb3J0ZWQgZXhpdCAkTEFTVEVYSVRDT0RFKSIgfQp9CgpXcml0ZS1Ib3N0ICJgbj09PSBT
SEFQRSBNRVRSSUNTIEZST00gVEhFIEJVSUxUIEdMQnMgPT09IgpXcml0ZS1Ib3N0ICIoZ2xURiBz
cGFjZSBpcyBZLVVQOyBzaGFwZV9tZXRyaWNzIGRlZmF1bHRzIHRvIHVwPTEgZm9yIHRoYXQgcmVh
c29uKSIKJGVudjpQWVRIT05JT0VOQ09ESU5HID0gInV0Zi04IgpweXRob24gKEpvaW4tUGF0aCAk
RmFjdG9yeSAidG9vbHNcc2hhcGVfbWV0cmljcy5weSIpIC0tZGlyICRPdXQKCiMgLS0tIHdoYXQg
Y29sbGlzaW9uIGRvZXMgZWFjaCBvbmUgYWN0dWFsbHkgYnJpbmc/IC0tLS0tLS0tLS0tLS0tLS0t
LS0tLS0tLS0tCiMgUmVhZCB3aXRoIGxldmVsX2ZhY3RvcnkncyBnbGJfY29sbGlzaW9uLCB3aGlj
aCB3YWxrcyB0aGUgY29udGFpbmVyIGFuZCB0aGUKIyBub2RlIHRyZWUgYW5kIG5lZWRzIG5laXRo
ZXIgQmxlbmRlciBub3IgR29kb3QuIEEgYC1jb2xvbmx5YCBzaWJsaW5nIG1lc2ggaXMKIyBob3cg
Wm9vIHNoaXBzIGNvbGxpc2lvbiAoYnB5bGF5ZXIvY29sbGlzaW9uLnB5KSwgc28gdGhpcyBpcyBy
ZWFkaW5nIFpvbydzIG93bgojIG91dHB1dCB0aHJvdWdoIGFuIGluZGVwZW5kZW50IGltcGxlbWVu
dGF0aW9uIHJhdGhlciB0aGFuIHRydXN0aW5nIHRoZSBidWlsZC4KJFByb2JlID0gSm9pbi1QYXRo
ICRPdXQgIl9jb2xsaXNpb25fcHJvYmUucHkiCkAnCmltcG9ydCBnbG9iLCBvcywgc3lzCnN5cy5w
YXRoLmluc2VydCgwLCBzeXMuYXJndlsxXSkKZnJvbSBwYWNrYWdlcy52YWxpZGF0aW9uLmdsYl9j
b2xsaXNpb24gaW1wb3J0IGNvbGxpc2lvbl9zb2xpZHMKCnByaW50KGYieydmaWxlJzo8MzR9IHsn
cmVhZCc6PjV9IHsnc29saWRzJzo+N30gICBjb2xsaWRlciBleHRlbnRzIChtKSIpCnByaW50KCIt
IiAqIDkyKQpmb3IgcCBpbiBzb3J0ZWQoZ2xvYi5nbG9iKG9zLnBhdGguam9pbihzeXMuYXJndlsy
XSwgIioqIiwgIiouZ2xiIiksIHJlY3Vyc2l2ZT1UcnVlKSk6CiAgICByID0gY29sbGlzaW9uX3Nv
bGlkcyhwKQogICAgbmFtZSA9IG9zLnBhdGguYmFzZW5hbWUocCkKICAgIGlmIG5vdCByLnJlYWQ6
CiAgICAgICAgcHJpbnQoZiJ7bmFtZTo8MzR9IHsnTk8nOj41fSB7Jy0nOj43fSAgIHtyLmRldGFp
bH0iKQogICAgICAgIGNvbnRpbnVlCiAgICBpZiBub3Qgci5zb2xpZHM6CiAgICAgICAgcHJpbnQo
ZiJ7bmFtZTo8MzR9IHsneWVzJzo+NX0gezA6Pjd9ICAgbm9uZSAtLSB0aGlzIGFzc2V0IGJyaW5n
cyBubyBjb2xsaXNpb24iKQogICAgICAgIGNvbnRpbnVlCiAgICBwYXJ0cyA9ICIgICIuam9pbihm
IntzLnNpemVbMF06LjJmfXh7cy5zaXplWzFdOi4yZn14e3Muc2l6ZVsyXTouMmZ9IgogICAgICAg
ICAgICAgICAgICAgICAgZm9yIHMgaW4gci5zb2xpZHMpCiAgICBwcmludChmIntuYW1lOjwzNH0g
eyd5ZXMnOj41fSB7bGVuKHIuc29saWRzKTo+N30gICB7cGFydHN9IikKJ0AgfCBTZXQtQ29udGVu
dCAtRW5jb2RpbmcgdXRmOCAkUHJvYmUKCldyaXRlLUhvc3QgImBuPT09IENPTExJU0lPTiBFQUNI
IEdMQiBCUklOR1MgKHJlYWQgYmFjaywgbm90IGFzc3VtZWQpID09PSIKcHl0aG9uICRQcm9iZSAo
Sm9pbi1QYXRoICRGYWN0b3J5ICJsZXZlbF9mYWN0b3J5IikgJE91dAoKV3JpdGUtSG9zdCAiYG5Q
TkdzOiIKR2V0LUNoaWxkSXRlbSAkT3V0IC1GaWx0ZXIgKi5wbmcgLUVycm9yQWN0aW9uIFNpbGVu
dGx5Q29udGludWUgfCBGb3JFYWNoLU9iamVjdCB7IFdyaXRlLUhvc3QgIiAgJCgkXy5GdWxsTmFt
ZSkiIH0K
"""

CHANGELOG_SECTION = """\
## [0.39.1] - a preview can name its species, and street solids get a preview

### Added
- **`tools/preview_street_solids.ps1`** -- the sibling of
  `preview_dressing.ps1`, for the species that could stand in for a gameplay
  solid outdoors: `simple_car`, `prop`, `hvac_unit`, `water_tank`,
  `vending_machine`, `sign_box`, `streetlight`. Builds, renders and measures
  each one.

  **It asks one question the dressing preview does not need to.** Surface
  dressing is collisionless by definition; these exist BECAUSE of the volume
  they occupy. So the script reads the collision back out of every built GLB
  and prints it beside the shape metrics, using
  `level_factory/packages/validation/glb_collision.py` -- which walks the
  container and the node tree and needs neither Blender nor Godot. Zoo ships
  collision as a `-colonly` sibling mesh (`bpylayer/collision.py`), so this is
  Zoo's own output read back through an independent implementation rather than
  trusted from the build log.

### Changed
- **`tools/preview_specimen.py` accepts `--species`.** `build.build_specimen`
  has taken a `species=` argument since 0.38.0 -- "the door a program uses" --
  and this tool was still knocking with a prompt. `core.intent.parse` is blunt
  about the cost: two species in the library could not be reached through a
  prompt at all, and a prompt that resolves today does so because no better
  keyword match exists yet, which is a coincidence rather than a contract. A
  preview script naming seven species by prompt is seven coincidences waiting
  on the next species to be added.

  The prompt still rides along for material, colour, wear, size and era, so
  styling is unchanged. `--prompt` alone behaves exactly as before.

- The build line now prints which way it was asked --
  `species='simple_car'` or `prompt='weathered sedan'` -- so the console says
  whether keyword matching was involved.

### Notes
- A car already ships with collision: `recipes/simple_car.py` returns two
  `collision_boxes` (body and cabin), not a triangle hull and not a crude
  bounding box. That is the "art mesh does not introduce unnecessarily complex
  collision" rule already satisfied, one asset at a time.
- Nothing here places anything. These are assets and a way to look at them.

"""


def _decode(p): return base64.b64decode("".join(p.split()))
def _sha(b): return hashlib.sha256(b).hexdigest()


def _replace(path, payload, pre, post, *, check):
    raw = path.read_bytes(); got = _sha(raw); data = _decode(payload)
    if _sha(data) != post:
        print(f"REFUSING: {path.name} payload != recorded post_sha"); return 1
    if got == post:
        print(f"  already applied  {path.name}"); return 0
    if got != pre:
        print(f"REFUSING: {path.name} is not the file this was built against.\n"
              f"    expected {pre[:12]}  found {got[:12]} ({len(raw):,} bytes)")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,}"); return 0
    side = path.with_suffix(path.suffix + SIDECAR)
    if not side.is_file(): side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,}")
    return 0


def _create(path, payload, post, *, check):
    data = _decode(payload)
    if _sha(data) != post:
        print(f"REFUSING: {path.name} payload != post_sha"); return 1
    if path.is_file():
        if _sha(path.read_bytes()) == post:
            print(f"  already applied  {path.name}"); return 0
        print(f"REFUSING: {path} exists with different content"); return 1
    if check:
        print(f"  would create {path.name}  ({len(data):,} bytes)"); return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"  created      {path.name}  {len(data):,} bytes")
    return 0


def _bump(path, *, check):
    raw = path.read_bytes(); text = raw.decode("utf-8")
    if NEW_VERSION in text:
        print("  already applied  VERSION"); return 0
    if OLD_VERSION not in text:
        print(f"REFUSING: zoo/VERSION does not contain {OLD_VERSION!r}"); return 1
    if check:
        print(f"  would patch  VERSION  {OLD_VERSION} -> {NEW_VERSION}"); return 0
    side = path.with_suffix(path.suffix + SIDECAR)
    if not side.is_file(): side.write_bytes(raw)
    path.write_bytes(text.replace(OLD_VERSION, NEW_VERSION, 1).encode("utf-8"))
    print(f"  patched      VERSION  {OLD_VERSION} -> {NEW_VERSION}")
    return 0


def _insert(path, *, check):
    raw = path.read_bytes(); text = raw.decode("utf-8")
    nl = "\r\n" if "\r\n" in text[:4000] else "\n"
    sec = CHANGELOG_SECTION.replace("\n", nl)
    if sec in text:
        print("  already applied  CHANGELOG.md"); return 0
    anchor = CHANGELOG_ANCHOR.replace("\n", nl)
    if not text.startswith(anchor):
        print(f"REFUSING: CHANGELOG.md does not start with {CHANGELOG_ANCHOR!r}")
        return 1
    i = len(anchor)
    while text[i:i + len(nl)] == nl:
        i += len(nl)
    data = (text[:i] + sec + text[i:]).encode("utf-8")
    if check:
        print(f"  would patch  CHANGELOG.md  {len(raw):,} -> {len(data):,}"); return 0
    side = path.with_suffix(path.suffix + SIDECAR)
    if not side.is_file(): side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      CHANGELOG.md  {len(raw):,} -> {len(data):,}")
    return 0


def _selftest() -> int:
    bad = 0
    for name, data, post, n in (
            ("preview_specimen", _decode(PREVIEW_B64), PREVIEW_POST, PREVIEW_BYTES),
            ("preview_street_solids", _decode(SCRIPT_B64), SCRIPT_POST, SCRIPT_BYTES)):
        ok = _sha(data) == post and len(data) == n
        print(f"[selftest] {name} payload {len(data):,} bytes "
              f"sha {_sha(data)[:12]} {'ok' if ok else 'MISMATCH'}")
        bad |= 0 if ok else 1

    src = _decode(PREVIEW_B64).decode("utf-8")
    tree = ast.parse(src)

    # --species has to be READ and PASSED, not merely mentioned in the prose.
    reads = any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_arg"
                and n.args and isinstance(n.args[0], ast.Constant)
                and n.args[0].value == "--species" for n in ast.walk(tree))
    passes = any(isinstance(n, ast.Call)
                 and getattr(getattr(n.func, "value", None), "id", "") == "build"
                 and getattr(n.func, "attr", "") == "build_specimen"
                 and any(k.arg == "species" for k in n.keywords)
                 for n in ast.walk(tree))
    print(f"[selftest] preview_specimen reads --species: {reads}")
    print(f"[selftest] and passes species= to build_specimen: {passes}")
    if not (reads and passes):
        print("[selftest] FAIL: the flag is decoration unless it reaches the "
              "build. A docstring that says --species while the call still "
              "resolves by keyword is worse than no flag.")
        bad = 1

    ps = _decode(SCRIPT_B64).decode("utf-8")
    named = ps.count("--species $j.species")
    jobs = ps.count("species = ")
    print(f"[selftest] preview script names {jobs} species and passes "
          f"--species {named} time(s)")
    if named < 1 or jobs < 5:
        print("[selftest] FAIL: the script should name every species outright")
        bad = 1
    if "--prompt $j.prompt" not in ps:
        print("[selftest] FAIL: the prompt should still ride along for styling")
        bad = 1

    # the embedded collision probe has to be valid python, or it fails in the
    # middle of a Blender run rather than here.
    try:
        body = ps.split("@'\n", 1)[1].split("\n'@", 1)[0]
        ast.parse(body)
        print(f"[selftest] embedded collision probe parses ({len(body)} bytes)")
    except (IndexError, SyntaxError) as exc:
        print(f"[selftest] FAIL: embedded probe is not valid python: {exc}")
        bad = 1

    print("[selftest] " + ("PASS" if not bad else "FAILED"))
    return bad


TARGETS = (PREVIEW, SCRIPT, VERSION_FILE, CHANGELOG)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--revert", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()

    root = Path.cwd()
    for rel in (PREVIEW, VERSION_FILE, CHANGELOG):
        if not (root / rel).is_file():
            print(f"cannot find {rel} -- run from the factory root")
            return 1

    if args.revert:
        bad = 0
        for rel in TARGETS:
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if side.is_file():
                p.write_bytes(side.read_bytes()); print(f"  reverted     {rel}")
            elif rel == SCRIPT and p.is_file():
                p.unlink(); print(f"  removed      {rel}  (this patch made it)")
            else:
                print(f"  no sidecar for {rel}"); bad = 1
        return bad

    def sweep(check):
        b = _replace(root / PREVIEW, PREVIEW_B64, PREVIEW_PRE, PREVIEW_POST,
                     check=check)
        b |= _create(root / SCRIPT, SCRIPT_B64, SCRIPT_POST, check=check)
        b |= _bump(root / VERSION_FILE, check=check)
        b |= _insert(root / CHANGELOG, check=check)
        return b

    if sweep(check=True):
        print("\n  Nothing was written. Fix the drift above and re-run.")
        return 1
    if args.check:
        return 0
    if sweep(check=False):
        print("\n  PARTIAL APPLICATION -- check the sidecars.")
        return 1
    print()
    print("  Run it:  pwsh -File zoo\\tools\\preview_street_solids.ps1")
    print("           (needs Blender; it builds, renders and measures)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
