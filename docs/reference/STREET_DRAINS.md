# Manhole covers and storm inlets: where a street has them (roadmap 179)

Filed 2026-10-12 for roadmap 179, which asked that the spacing be "read at source before a number is
written down, as the hydrant figure was". The walker, 2026-10-04: "in various locations, usually on
sidewalks, we should have manhole covers, sewer drain grates (should be like fire hydrants where there
is only so many in shared area)", with five photographs (read for the format, never the marks; see the
roadmap item). Lot 0.120.0 (`lot/site_drains.py`) places them by these rules.

## Sanitary manholes

The usual citation for small sewers is the Great Lakes-Upper Mississippi "Ten States" Recommended
Standards for Wastewater Facilities; the codes that carry its wording were read, not the standard
itself:

- **At every junction, at the end of every line, and at every change of grade, size or alignment**;
  and along a run **no farther apart than 400 ft (121.9 m) on sewers of 15 in and under**, 500 ft on
  18-30 in, up to 600 ft "where adequate modern cleaning equipment" is provided
  ([Illinois 35 IAC 370.330, "Recommended Standards for Sewage Works"][il]; [Virginia
  9VAC25-790-350][va]; [Fairfax County PFM ch. 10][fairfax]).
- A city sewer runs under the street, so its manholes stand in the carriageway: at a junction, where
  the mains cross.

**Used:** a cover at every road-road junction, at the junction's centre, and on a street run longer
than 121.9 m, covers at equal intervals so none is farther apart. A road's end at the site's edge is
not the end of its sewer -- the run continues off the site -- so no cover is placed there.

## Storm inlets

- **Upstream of intersections, driveways, crosswalks and curb ramps**: "flow across cross-walks and
  curb ramps may cause a pedestrian hazard", and inlets there are designed to take all of it
  ([TxDOT Hydraulic Design Manual, ch. 10 s. 5, "Inlet Locations"][txdot]).
- Between those, inlets go where the gutter's spread reaches its limit, which needs the street's grade
  and a design storm. A site here has neither: **not placed**.
- The walker's "only so many" is the hydrant's rule (`site_furniture.CORNER_ONE_EACH`): **one inlet a
  corner**, in the gutter against the kerb on the block side of the ramp, so a crosswalk's water is
  taken before it.

## The cover in the sidewalk

The walker's photograph: a cover in the sidewalk "a step behind an inlet". No standard places these --
they are the utilities' (a valve, a meter, a trap) -- so they follow the walker's "only so many": one
behind an inlet, no two closer than the hydrant's site-wide minimum (45.7 m), and never under a piece
of furniture. The number is borrowed, not sourced.

## Sizes

- **A sanitary manhole frame and cover: a 24 in clear opening** ([Cal Poly standard 6610][calpoly];
  [Kirkland CK-S-09][kirkland]); a supplier's 24 in sewer frame and cover lists the **lid 25 5/16 in**
  and the **frame 32 3/16 in** across ([Pace Supply][pace]).
- **A curb inlet grate: 2 x 3 ft** (or 2 x 2) ([ADS Nyloplast curb inlet][ads]); the 3 ft runs along
  the kerb.
- The sidewalk cover's 18 in square is the photograph's proportion, unsourced.

[il]: https://www.ilga.gov/ftp/JCAR/AdminCode/035/035003700C03300R.html
[va]: https://law.lis.virginia.gov/admincode/title9/agency25/chapter790/section350/
[fairfax]: https://www.fairfaxcounty.gov/landdevelopment/sites/landdevelopment/files/Assets/Documents/PDF/pfm/ESRC%20Approved%20Chapter%2010.pdf
[txdot]: https://www.txdot.gov/manuals/des/hyd/chapter-10--storm-drains/section-5--storm-drain-inlets/inlet-locations.html
[calpoly]: https://afd.calpoly.edu/facilities/planning-capital-projects/construction-standard/docs/standard-details/6610-Sewer-and-Storm-Manhole.pdf
[kirkland]: https://www.kirklandwa.gov/files/sharedassets/public/v/1/development-services/pdfs/pre-approved-plans/ck-s-09.pdf
[pace]: https://www.pacesupply.com/Product/DLSA1024CPHSEWER
[ads]: https://adspipe.com/resources/documents/E58E8F78-F5CF-482F-9855D84ECA8242F4
