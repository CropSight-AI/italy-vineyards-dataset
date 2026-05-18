# Italy Vineyards Dataset

> Geographic locations of Italian vineyards at the regional (NUTS2) level —
> ready-to-use GeoJSON polygons for **all 21 Italian NUTS2 regions**, plus
> a small set of derived "vineyard area" polygons used in real production
> yield-prediction work at CropSight.

## What this is

This is a curated, **CORINE Land Cover 2018 class 221** ("Vineyards")
extraction for the whole of Italy, organized as one GeoJSON file per
NUTS2 region. Files are in WGS84 (EPSG:4326), open and ready to use in
any GIS tool (QGIS, geojson.io, ArcGIS), or programmatically with
geopandas, shapely, or Leaflet/Mapbox.

Plus three "derived" sub-datasets we generated for CropSight's
yield-prediction validation work: contiguous "vineyard area" polygons
built by buffered union of the CORINE fragments. These are useful as
worked examples of how to turn the raw CORINE data into something a
modeling pipeline can sample weather inside.

## Why this exists

Open-Meteo, ERA5, and other climate APIs let you fetch weather at any
lat/lon. To do anything *agriculturally* useful with that — model yield,
detect drought stress, plan harvest logistics — you need to know **where
the vines actually are**.

The CORINE Land Cover product has the answer at EU scale (class 221 is
"Vineyards"), but:

- It's distributed as one giant pan-EU dataset, not per region.
- Italian wine regions changed NUTS codes in 2021 (Veneto: ITD3 → ITH3,
  Toscana: ITE1 → ITI1, Emilia-Romagna: ITD5 → ITH5, plus the autonomous
  provinces). Most existing data products still use the old codes.
- CORINE has a 25-hectare minimum mapping unit, so small/scattered plots
  get rolled up into surrounding land cover. Some regions (notably
  Emilia-Romagna) end up severely under-mapped — worth knowing before
  you use the data.
- Building a single contiguous "vineyard area" polygon for downstream
  sampling requires a deliberate methodology (see `docs/METHODOLOGY.md`).

This dataset solves all four problems and documents what's left.

## What's in the box

```
data/
├── corine_221_by_region/         21 GeoJSON files, one per Italian NUTS2 region
│   ├── piemonte_ITC1.geojson         NW alpine foothills, premium reds (Barolo)
│   ├── valle_daosta_ITC2.geojson     tiny alpine region (~430 ha vineyards in CORINE)
│   ├── liguria_ITC3.geojson          NW coastal, Cinque Terre area
│   ├── lombardia_ITC4.geojson        Franciacorta, Oltrepò
│   ├── bolzano_ITH1.geojson          autonomous province, Alto Adige
│   ├── trento_ITH2.geojson           autonomous province, Trentino
│   ├── veneto_ITH3.geojson           Prosecco, Amarone — largest producer
│   ├── friuli_ITH4.geojson           NE, Friuli-Venezia Giulia
│   ├── emilia_romagna_ITH5.geojson   ⚠ under-mapped in CORINE (see docs)
│   ├── toscana_ITI1.geojson          Chianti, Brunello
│   ├── umbria_ITI2.geojson           Orvieto, Sagrantino
│   ├── marche_ITI3.geojson           Verdicchio, Conero
│   ├── lazio_ITI4.geojson            Frascati, Cesanese
│   ├── abruzzo_ITF1.geojson          Montepulciano d'Abruzzo
│   ├── molise_ITF2.geojson           small southern region
│   ├── campania_ITF3.geojson         ⚠ under-mapped in CORINE
│   ├── puglia_ITF4.geojson           Primitivo, Negroamaro — heel of Italy
│   ├── basilicata_ITF5.geojson       Aglianico del Vulture
│   ├── calabria_ITF6.geojson         the toe
│   ├── sicilia_ITG1.geojson          Nero d'Avola, Etna DOC — largest area
│   └── sardegna_ITG2.geojson         Cannonau, Vermentino
│
├── nuts2_boundaries/
│   └── italy_nuts2_2024.geojson  all 21 Italian NUTS2 admin boundaries
│
└── derived_vineyard_zones/        OPTIONAL: ready-to-use contiguous polygons
    ├── sardegna/                  3 buffer-size variants (5/10/20 km)
    ├── sicilia/                   3 sub-polygons (Western/Central/SE)
    ├── puglia/                    5 sub-polygons (Daunia/Murge/Itria/Salento/Brindisi)
    └── toscana/                   3 sub-polygons (Chianti core/Brunello/Rufina)
```

Plus:

```
scripts/        How to extend or regenerate the dataset
docs/           Detailed methodology, source attribution, region stats
examples/       Example visualizations
```

## Quick start

### 1. Look at it

The easiest way to inspect any file is to drag-drop it into
[geojson.io](https://geojson.io) — you'll see the polygon overlaid on
satellite imagery within seconds.

For programmatic access:

```python
import geopandas as gpd
piemonte = gpd.read_file("data/corine_221_by_region/piemonte_ITC1.geojson")
print(piemonte.head())
print(f"Total area: {piemonte.to_crs(epsg=3035).geometry.area.sum() / 1e4:.0f} hectares")
```

### 2. Use it as the spatial layer for a yield model

The full template (sample weather at grid points inside the polygon,
aggregate to weekly features per season, train a model on ISTAT yield):
see `docs/METHODOLOGY.md` and the `derived_vineyard_zones/` examples.

### 3. Extend it

To add a new region (Italian or other CORINE-covered EU country):
see `scripts/pull_corine_221.py`. To derive a new contiguous
"vineyard zone" polygon: see `scripts/build_vineyard_zone.py`.

## Per-region statistics

Polygon count and CORINE-mapped vineyard area for each region:

| NUTS code | Region | Polygons | Vineyard area (ha) | Notable |
|---|---|---|---|---|
| ITG1 | Sicilia | 351 | 155,495 | largest mapped |
| ITF4 | Puglia | 314 | 140,782 | second largest |
| ITC1 | Piemonte | 112 | 61,900 | |
| ITH3 | Veneto | 225 | 72,919 | largest producer (ISTAT) |
| ITI1 | Toscana | 690 | 66,689 | most fragmented |
| ITF1 | Abruzzo | 80 | 20,988 | |
| ITC4 | Lombardia | 37 | 15,964 | |
| ITH2 | Trento | 49 | 9,470 | autonomous province |
| ITH4 | Friuli | 111 | 14,775 | |
| ITG2 | Sardegna | 92 | 8,887 | |
| ITI4 | Lazio | 96 | 14,173 | |
| ITI2 | Umbria | 81 | 6,093 | |
| ITI3 | Marche | 124 | 5,942 | |
| ITH1 | Bolzano | 31 | 5,233 | autonomous province |
| ITF2 | Molise | 15 | 4,784 | |
| ITF6 | Calabria | 31 | 4,466 | |
| ITH5 | Emilia-Romagna | 19 | **4,282** | ⚠ severely under-mapped |
| ITF5 | Basilicata | 21 | 1,384 | |
| ITF3 | Campania | 19 | **1,263** | ⚠ severely under-mapped |
| ITC2 | Valle d'Aosta | 9 | 430 | tiny alpine |
| ITC3 | Liguria | 7 | 353 | smallest |

**Total:** 2,547 vineyard polygons across Italy, **~615,000 hectares**.

For reference, ISTAT's total Italian wine grape area is ~660,000 ha
(varies year-to-year). CORINE captures **~93% of the total**, but
distribution is uneven — see the ⚠ flagged regions below.

## Known limitations

1. **Emilia-Romagna and Campania are severely under-mapped in CORINE.**
   ISTAT reports ~57,000 ha for Emilia-Romagna's wine grapes; CORINE shows
   only 4,282 ha (~7%). For these regions, use the dataset for
   *geographic distribution* but **don't trust it for total area**.
   See `docs/METHODOLOGY.md` for our hypothesis on why.

2. **CORINE vintage is 2018.** Vineyard locations change slowly so this
   is generally fine, but newly planted or grubbed-up areas after 2018
   won't reflect reality. CORINE 2024 release is in progress.

3. **25-hectare minimum mapping unit.** Small/scattered plots and
   single-vineyard wineries are not represented. For micro-vineyard
   work (e.g., specific DOC zones, single estates), use OpenStreetMap
   `landuse=vineyard` or commercial parcel data instead.

4. **NUTS code drift.** In NUTS 2021 (used here as the "2024" vintage),
   several Italian regions were re-coded. ISTAT and many older data
   sources still use the pre-2021 codes. Cross-reference is documented
   in `docs/SOURCES.md`.

## Sources and attribution

This dataset is derived from two public sources. Both are open-access
and require attribution:

- **CORINE Land Cover 2018 v.2020_20u1** by the European Environment
  Agency (Copernicus Land Monitoring Service), distributed via the
  EEA's public ArcGIS REST endpoint at
  `image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM`.
  Class 221 = "Vineyards". License: free for use with attribution under
  the [Copernicus License](https://land.copernicus.eu/en/data-policy).

- **NUTS 2024 statistical units** by Eurostat (GISCO), downloaded from
  `gisco-services.ec.europa.eu/distribution/v2/nuts/`.
  License: free for use with attribution
  (© EuroGeographics for the administrative boundaries).

If you use this dataset, please cite:

> Italy Vineyards Dataset, derived from CORINE Land Cover 2018 (EEA,
> Copernicus) and Eurostat NUTS 2024 statistical units. <CropSight,
> 2026, https://github.com/your-org/italy-vineyards-dataset>

## License

The dataset itself is published under **CC-BY 4.0** to match the
upstream Copernicus/Eurostat license terms. See `LICENSE`.

The code in `scripts/` is published under **MIT**.

## Documentation

| File | Contents |
|---|---|
| `docs/METHODOLOGY.md` | How we built the derived "vineyard zone" polygons (buffered union, top-N components, coverage/density trade-off). |
| `docs/SOURCES.md` | Source-data details: CORINE service URLs, NUTS code drift mapping, ISTAT yield data structure. |
| `docs/REGION_STATS.md` | Full per-region table: polygon count, mapped area, vs ISTAT-reported area. |

## Examples

See `examples/` for three rendered maps showing how the raw CORINE data
and the derived polygons fit together for Sardegna, Sicilia, and Puglia.

## Contact / contributions

This dataset was curated and validated at CropSight as part of yield
prediction R&D. Issues, corrections, and extensions to other EU countries
are welcome via GitHub PR or issue.
