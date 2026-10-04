# Cold run 9142 -- a car's paint rides its vertices, untouched

gas_block_001, 9141's brief and seed (9080), on Zoo 1.59.0 and otherwise
9141's stack (Level Factory 0.134.0, Lot 0.94.0, Lux 0.66.0, Deli Counter
0.172.0, Pixelcoat 0.55.0, Patina 0.22.0), exported with `--bake-lights`.
**Zero interventions** (journal 0, unattributed files 0, no retries, no
observations). The same three buildings, fields, cars and pads as 9141.

Findings 63 -> 63, identical code for code: a car's collision boxes and
dims did not move, so neither did any encounter.

    [export] light bake: 198 model(s) and 1554 primitive mesh(es) lightmapped,
             7 kept dynamic; 76 steady rig(s) baked, 17 failing left live;
             3205 users, 54.6 s in the editor          (9141: 3463 users)

The 258 lightmap users fewer are the car meshes the merge folded.

## Price (`docs/findings/cars_price/`)

9141's package against this one -- the same site, differing only in the
car modules -- on Level Factory's fixed-station harness, GL Compatibility,
and 9141's again after as the control:

    mean over 53 headings       draws    median ms   GPU ms
    9142 - 9141                 -77.8    -0.23       -0.12
      best heading (longest_sightline, yaw 112.5)
                                -330     -0.77
    control (9141 twice)         -2.1    +0.09       +0.05
                                         (max |4.78|, one hitch)

The draws are the firm number: the harness reads them deterministically,
and they fell by more than the parking fields added in 9141 (+52), because
the 29 kerb-lane cars are the same modules. The frame time fell clear of
the control's mean; the machine was noisier this hour than at 9141's
pricing (mean median 4.58 ms against 3.88), so it is the weaker of the two
readings. Stations over the provisional 2,000-draw budget: 3 in both.
