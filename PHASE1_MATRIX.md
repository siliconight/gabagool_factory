# Phase 1 Vertical Slice — Configuration Matrix

10 pvp_heist configurations. Sibling rule (§6/§7): every same-family pair
differs in ≥2 TACTICAL and ≥2 VISUAL dimensions — planned here, checked by
the registrar. Zoo theme: delco. All doors ≥ agent-contract 1.25 m.

## BANK_BRANCH
(A01 = the Phase 0 bank_job record; Phase 1 adds A02-A04)

| id | base | tactical (entrances / objective / defender / vertical) | visual |
|---|---|---|---|
| A02 | bank_job-derived | 3 entries / vault_basement / vault_room / dual side stairs | delco_financial, maintained, brick_masonry, storefront_glass |
| A03 | bank_job-derived | 4 entries incl. garage / story1_records / records_secure / stairs + roof ladder | delco_financial_modern, renovated, curtain_glass, ribbon_glazing |
| A04 | new (hero anchor) | 4 entries / vault_basement / deep vault / 3 stairs + roof ladder | delco_civic_monumental, pristine, stone_colonnade, high_sill_slit |

## DELI
| id | base | tactical | visual |
|---|---|---|---|
| A01 | corner_deli_heist_01 | 2 entries / basement_vault / cold_storage / single stair + ladder | delco_corner_store, worn, brick_awning, neon_signage |
| A02 | night_deli-derived | 3 entries (front+loading+side) / server_room story1 / upper_hall / stair + rear ladder | delco_bodega, maintained, stucco_roll_gate, fluorescent_signage |
| A03 | deli-derived | 2 entries (front+rear) / apartment_hideout story1 / kitchen / stair + roof hatch | delco_family_market, renovated, tile_facade, painted_signage |

## WAREHOUSE
| id | base | tactical | visual |
|---|---|---|---|
| A01 | new | 3 entries (2 docks + man door) / ground cage / office | delco_industrial, worn, corrugated_steel, dock_canopies |
| A02 | new | 2 entries (dock + service) / mezzanine office story1 / floor cage / stair + roof hatch | delco_logistics_modern, maintained, insulated_panel, clerestory_band |

## PARKING_GARAGE
| id | base | tactical | visual |
|---|---|---|---|
| A01 | parking_garage | 2 entries (ramp + stair door) / attendant cash room deck0 / deck1 overlook | delco_municipal_deck, worn, board_formed_concrete, painted_wayfinding |
| A02 | garage-derived | 3 entries (2 ramps + service) / armored car deck1 / booth deck0 / stair + ladder | delco_commercial_deck, maintained, precast_panel, led_wayfinding |

## Missions
- MSN_DELI_BLOCK_01 (standard): deli A01 objective + garage A01 + warehouse A01 support.
- MSN_CENTRAL_VAULT_01 (hero): Central Bank Vault Complex — bank A04 hero anchor +
  deli A02 + warehouse A02 + garage A02 (hero rule: 2-4 buildings; bank family
  represented by the hero itself; attackers stage from the logistics hub).
