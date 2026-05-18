# Sources and the NUTS code drift problem

## Primary sources

### CORINE Land Cover 2018 (class 221: Vineyards)

- **Provider:** European Environment Agency (EEA) / Copernicus Land
  Monitoring Service
- **Product:** CLC2018 v.2020_20u1 (released April 2020, validated EU-27)
- **Access:** Public ArcGIS REST endpoint, no authentication required
- **Endpoint:**
  `https://image.discomap.eea.europa.eu/arcgis/rest/services/Corine/CLC2018_WM/MapServer/0`
- **Coverage:** All 44 EEA-member countries
- **Minimum mapping unit:** 25 hectares
- **Spatial resolution:** Vector polygons at 1:100,000 scale
- **Update cycle:** Every 6 years; CLC2024 is in production
- **License:** Free for use under the
  [Copernicus License](https://land.copernicus.eu/en/data-policy)
  (attribution required)

Query used for each region:

```
GET .../MapServer/0/query
  ?where=Code_18='221'
  &geometry=<region_bbox_lonlat>
  &geometryType=esriGeometryEnvelope
  &spatialRel=esriSpatialRelIntersects
  &inSR=4326&outSR=4326
  &outFields=Code_18,Area_Ha
  &returnGeometry=true
  &f=geojson
```

### NUTS 2024 statistical units

- **Provider:** Eurostat (GISCO)
- **Product:** NUTS 2024 (= NUTS 2021 vintage, no changes applied in 2024)
- **Access:** Direct download from `gisco-services.ec.europa.eu`
- **URL:**
  `https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_10M_2024_4326_LEVL_2.geojson`
- **License:** Free for use; © EuroGeographics for boundaries

## The NUTS code drift (this matters if you cross-reference with ISTAT)

When NUTS 2021 was released, **several Italian regions were re-coded** as
part of a re-balancing exercise across EU statistical units. Most
public-facing Italian data sources, including ISTAT, still use the
**pre-2021 codes** in many products.

The mapping:

| Region | Pre-2021 (used by ISTAT) | NUTS 2021/2024 (used here) | Status |
|---|---|---|---|
| Piemonte | ITC1 | ITC1 | unchanged |
| Valle d'Aosta | ITC2 | ITC2 | unchanged |
| Liguria | ITC3 | ITC3 | unchanged |
| Lombardia | ITC4 | ITC4 | unchanged |
| Bolzano | ITD1 | **ITH1** | re-coded |
| Trento | ITD2 | **ITH2** | re-coded |
| Veneto | ITD3 | **ITH3** | re-coded |
| Friuli-Venezia Giulia | ITD4 | **ITH4** | re-coded |
| Emilia-Romagna | ITD5 | **ITH5** | re-coded |
| Toscana | ITE1 | **ITI1** | re-coded |
| Umbria | ITE2 | **ITI2** | re-coded |
| Marche | ITE3 | **ITI3** | re-coded |
| Lazio | ITE4 | **ITI4** | re-coded |
| Abruzzo | ITF1 | ITF1 | unchanged |
| Molise | ITF2 | ITF2 | unchanged |
| Campania | ITF3 | ITF3 | unchanged |
| Puglia | ITF4 | ITF4 | unchanged |
| Basilicata | ITF5 | ITF5 | unchanged |
| Calabria | ITF6 | ITF6 | unchanged |
| Sicilia | ITG1 | ITG1 | unchanged |
| Sardegna | ITG2 | ITG2 | unchanged |

**Our filenames use the NUTS 2024 codes.** This was a deliberate choice:
the NUTS 2024 file is what Eurostat ships today, and the actual region
*geometries* are correct under either coding system (the borders didn't
move, only the labels). When matching against ISTAT yield data, you'll
need to look up by region name or convert codes.

## ISTAT yield data

ISTAT publishes annual wine grape statistics at the NUTS2 regional level
(but still using the pre-2021 NUTS codes in `REF_AREA`):

- Dataset code: `IT1,101_1015_DF_DCSP_COLTIVAZIONI_1,1.0`
- Crop code: `WINEES` (wine grapes)
- Relevant indicators:
  - `ART` — Total area, hectares
  - `PA_EXT` — Production area, hectares (slight subset of ART)
  - `HP_Q_EXT` — Harvested production, quintals
  - `TP_QUIN_EXT` — Total production, quintals (= harvested + un-harvested)

Yield computation:

```
yield_t_per_ha = HP_Q_EXT / ART * 0.1
```

(1 quintal = 100 kg = 0.1 tonne.)

ISTAT data is accessible via their open data portal at
[dati.istat.it](https://dati.istat.it) or the SDMX endpoint. For our work
we used the bulk CSV download.

## OpenStreetMap (comparison only, not in this dataset)

OSM has `landuse=vineyard` polygons (volunteer-mapped). Useful as a
cross-check, but coverage in Italy is incomplete (~13% of true area in
the Sardegna sample we measured). Query via Overpass API:

```
[out:json];
( way["landuse"="vineyard"](<bbox>);
  relation["landuse"="vineyard"](<bbox>); );
out geom;
```

Endpoint: `https://overpass-api.de/api/interpreter`.
