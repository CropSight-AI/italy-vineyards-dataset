# Changelog

## v0.1.1 — 2026-05-18

### Changed

- `data/derived_vineyard_zones/puglia/` now contains the **top-5**
  components (was top-3). Coverage rises from 77.2% to **90.2%** with
  density essentially unchanged (32.1% → 31.2%). Adds the previously
  missing Daunia/Foggia cluster (#5) and a separate eastern cluster
  around Brindisi (#4). See `docs/METHODOLOGY.md` for rationale.
- `examples/example_puglia_subpolygons.png` updated to show the top-5
  layout.

## v0.1.0 — 2026-05-18

Initial release.

### Added

- `data/corine_221_by_region/` — CORINE Land Cover 2018 class 221
  ("Vineyards") polygons for all 21 Italian NUTS2 regions, in GeoJSON
  (WGS84). 2,547 polygons, ~615,000 ha total.
- `data/nuts2_boundaries/italy_nuts2_2024.geojson` — administrative
  boundaries for all 21 Italian NUTS2 regions, NUTS-2024 vintage.
- `data/derived_vineyard_zones/` — buffered-union "vineyard area"
  polygons for Sardegna, Sicilia, and Puglia. Used in CropSight's
  yield-prediction validation work.
- `scripts/pull_corine_221.py` — regenerate the CORINE region files.
- `scripts/build_vineyard_zone.py` — derive contiguous polygons from
  CORINE 221 via buffered union.
- `scripts/derive_yield_csv.py` — derive wine grape yield series from
  ISTAT bulk export.
- `docs/METHODOLOGY.md` — how the dataset was built.
- `docs/SOURCES.md` — source attribution and NUTS code drift.
- `docs/REGION_STATS.md` — per-region polygon and area stats.
- `examples/` — three rendered example maps.
