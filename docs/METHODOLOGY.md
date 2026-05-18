# Methodology

This document explains *how* the dataset was built and *why* certain design
choices were made. If you just want to use the data, the `README.md` and
the GeoJSON files are enough — but if you want to extend the dataset to
other countries or modify the derived polygons, read this first.

## Step 1: Source the raw vineyard polygons

CORINE Land Cover 2018 is the European Environment Agency's authoritative
pan-EU land cover dataset. It classifies every patch of EU land into one
of 44 categories. Class **221 ("Vineyards")** is what we want — it's
defined as "Areas planted with vines."

We use the EEA's public ArcGIS REST endpoint:

```
https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/0/query
```

This requires **no authentication** and supports queries like
`where=Code_18='221'` combined with a geographic envelope filter (we use
each NUTS2 region's bounding box). Results are paged at 1000 features per
request; CORINE has at most a few hundred class-221 polygons per Italian
region, so most queries return everything in one page.

We then **clip** the result to the actual NUTS2 boundary (CORINE bbox
queries are inclusive of any polygon that *intersects* the bbox, so we'd
otherwise pick up neighboring-region vineyards near borders).

See `scripts/pull_corine_221.py` for the working implementation.

## Step 2: Acknowledge CORINE's limitations

CORINE has a **25-hectare minimum mapping unit (MMU)**. Any vineyard
patch smaller than 25 ha gets generalized into the surrounding land
cover class (usually "Complex cultivation patterns" or "Non-irrigated
arable land"). This has two consequences:

- **Coverage is biased toward large commercial production zones.**
  Sulcis in Sardegna, Salento in Puglia, Marsala in Sicilia: well-mapped.
  Boutique-DOC regions with many small vineyards: under-mapped.

- **Some regions are dramatically under-mapped.** Two specific cases we
  observed:

  | Region | CORINE area | ISTAT area | CORINE / ISTAT |
  |---|---|---|---|
  | Emilia-Romagna | 4,282 ha | ~57,000 ha | **7.5%** |
  | Campania | 1,263 ha | ~25,000 ha | **~5%** |

  Our hypothesis: these regions have small fragmented family-run vineyards
  scattered through mixed agricultural land. CORINE classifies them as
  "Complex cultivation patterns" (class 242) or "Non-irrigated arable land"
  (class 211) instead of "Vineyards." For these regions, consider using
  OpenStreetMap `landuse=vineyard` data or commercial parcel registries.

  By contrast, Sardegna's 8,887 ha vs ISTAT's 26,600 ha (~33% coverage)
  is the more typical CORINE behavior.

## Step 3: Build derived "vineyard zone" polygons

The raw CORINE data is a fragmented `MultiPolygon` per region — hundreds
of small disconnected patches. For many downstream uses (weather sampling
inside a region, mapping a "wine country" footprint, planning logistics)
we want **one or a small number of contiguous polygons** that:

1. **Cover most of the actual vineyards** (high *coverage* of CORINE 221
   area).
2. **Don't include too much non-vineyard land** (high *density* = vineyard
   area inside polygon ÷ polygon total area).

These two goals trade off against each other. To make the trade-off
concrete, we use a **buffered union** approach:

```
1. Buffer each CORINE 221 polygon by R km (using UTM projection for
   accurate metric distances).
2. Union all buffered polygons.
3. Identify connected components in the result.
4. Keep the top N components by area.
```

The buffer R controls aggressiveness of merging:

- **Small R (0.5–1 km):** Adjacent vineyards merge into clusters; distant
  clusters stay separate. High density, lower coverage.
- **Large R (5+ km):** Almost everything merges into one mega-polygon.
  High coverage, low density (most of the polygon is non-vineyard land).

The right R depends on regional geography. We did a **buffer sweep**
analysis (sampling buffers from 0.5 to 5 km) and picked the smallest R
that yielded a defensible coverage/density combination:

| Region | Buffer | Top-N | Coverage | Density |
|---|---|---|---|---|
| Sardegna | 10 km | 1 | n/a (one polygon by design) | ~25% |
| Sicilia | 1 km | 3 | 88.6% | 39.6% |
| Puglia | 1.5 km | 5 | 90.2% | 31.2% |

Note for Puglia: an initial top-3 build gave 77.2% / 32.1%. The top-N
sweep showed that components 4 and 5 (each ~300–400 km², still dense
vineyard clusters) add +13 pp of coverage with almost no density cost
(31.2 vs 32.1) — so we ship the top-5 version. This is unlike the
buffer-size lever, where higher coverage always costs density: adding
*new clusters* at the same buffer keeps density stable because each
new cluster IS dense vineyard. See `examples/example_puglia_subpolygons.png`.

Why different parameters per region:
- **Sardegna** has clustered vineyards in one main southern wine belt; one
  polygon at 10 km buffer captures it cleanly.
- **Sicilia** has 3 distinct wine sub-regions (Western/Central/SE) — small
  buffer keeps them apart, top-3 captures the three.
- **Puglia** has more dispersed clusters; needs a slightly larger buffer
  (1.5 km) and accepts somewhat lower coverage (77%) to keep the polygon
  structure tight.

See `scripts/build_vineyard_zone.py` for the working implementation.

## Step 4: Validate downstream usage

The dataset was originally built and validated for CropSight's wine grape
yield prediction work. The validation flow was:

1. Use the derived polygon (e.g. `sicilia_1_western_1km.geojson`) as the
   sampling boundary for weather data via Open-Meteo's archive API.
2. Place a regular grid inside the polygon (`scripts/build_vineyard_zone.py`
   uses 6×6 = 36 candidate points, keeping those inside the polygon).
3. For each retained grid point, fetch 19 seasons of daily weather (9
   variables: temp max/min, rain, snow, wind gusts, radiation, cloud
   cover, soil moisture, sunshine).
4. Aggregate weekly statistics across grid points → one feature vector
   per (polygon, year, week).
5. Train a yield prediction model on ISTAT-derived yields.

The resulting MAPE on Sicilia 2006–2025 was **7.23% ± 0.31%** at best
epoch across 8 seeds. Full details in CropSight's internal
`SICILIA_PRECISION.md`.

## When to use which polygon

| If you want… | Use |
|---|---|
| Where vineyards actually are, raw | `data/corine_221_by_region/<region>_<NUTS>.geojson` |
| One contiguous polygon for a region's main wine area | `data/derived_vineyard_zones/<region>/...` |
| Country/region admin boundaries | `data/nuts2_boundaries/italy_nuts2_2024.geojson` |
| To verify CORINE is missing your vineyard plot | Cross-check with OSM `landuse=vineyard` via Overpass |
| To match yield statistics (ISTAT) | Use the *NUTS-coded filename* of the corresponding region |

## Reproducibility

Every file in this dataset can be regenerated by running:

```
pip install -r scripts/requirements.txt
python scripts/pull_corine_221.py        # pulls all 21 Italian regions
python scripts/build_vineyard_zone.py    # rebuilds derived zones
```

The scripts are deterministic given fixed input parameters (buffer
distance, top-N count). The CORINE endpoint is versioned to 2018v2020_20u1
and is stable.

## Extending to other EU countries

The CORINE service covers all 44 EEA-member countries. To pull e.g.
France or Spain, modify `pull_corine_221.py` to use the appropriate
NUTS codes (FR, ES, etc.) and reproject to the appropriate UTM zone in
`build_vineyard_zone.py`. We've kept the structure parameterized for
this purpose.
