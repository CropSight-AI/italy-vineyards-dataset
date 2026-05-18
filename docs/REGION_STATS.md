# Per-region statistics

CORINE Land Cover 2018, class 221 ("Vineyards"), Italy.

## Full table

| NUTS-2024 | NUTS-2016 | Region | Polygons | CORINE area (ha) | ISTAT wine grape area (ha, 2023-25 avg) | CORINE / ISTAT |
|---|---|---|---|---|---|---|
| ITG1 | ITG1 | Sicilia | 351 | 155,495 | ~118,000 | 132% * |
| ITF4 | ITF4 | Puglia | 314 | 140,782 | ~93,000 | 151% * |
| ITH3 | ITD3 | Veneto | 225 | 72,919 | ~99,000 | 74% |
| ITI1 | ITE1 | Toscana | 690 | 66,689 | ~60,000 | 111% |
| ITC1 | ITC1 | Piemonte | 112 | 61,900 | ~40,000 | 155% * |
| ITF1 | ITF1 | Abruzzo | 80 | 20,988 | ~32,000 | 66% |
| ITC4 | ITC4 | Lombardia | 37 | 15,964 | ~22,000 | 73% |
| ITH4 | ITD4 | Friuli-Venezia Giulia | 111 | 14,775 | ~26,000 | 57% |
| ITI4 | ITE4 | Lazio | 96 | 14,173 | ~17,000 | 83% |
| ITH2 | ITD2 | Trento | 49 | 9,470 | ~10,000 | 95% |
| ITG2 | ITG2 | Sardegna | 92 | 8,887 | ~27,000 | 33% |
| ITI2 | ITE2 | Umbria | 81 | 6,093 | ~12,000 | 51% |
| ITI3 | ITE3 | Marche | 124 | 5,942 | ~15,000 | 40% |
| ITH1 | ITD1 | Bolzano | 31 | 5,233 | ~5,500 | 95% |
| ITF2 | ITF2 | Molise | 15 | 4,784 | ~5,000 | 96% |
| ITF6 | ITF6 | Calabria | 31 | 4,466 | ~9,000 | 50% |
| ITH5 | ITD5 | **Emilia-Romagna** | 19 | **4,282** | **~52,000** | **8%** ⚠ |
| ITF5 | ITF5 | Basilicata | 21 | 1,384 | ~2,500 | 55% |
| ITF3 | ITF3 | **Campania** | 19 | **1,263** | **~22,000** | **6%** ⚠ |
| ITC2 | ITC2 | Valle d'Aosta | 9 | 430 | ~440 | 98% |
| ITC3 | ITC3 | Liguria | 7 | 353 | ~1,400 | 25% |
| **TOTAL** | — | — | **2,547** | **614,372** | ~669,000 | **92%** |

\* For Sicilia, Puglia and Piemonte, CORINE area exceeds ISTAT reported
area. This is because CORINE 2018 reflects 2018 land cover, while ISTAT
reports active commercial production. Some CORINE-classified vineyards
may have been abandoned, replanted to other crops, or reduced in
intensity by the time of recent ISTAT counts. The CORINE polygon is still
a useful spatial layer; just don't take its area as gospel.

## Under-mapped regions (⚠)

**Emilia-Romagna (ITH5)** and **Campania (ITF3)** show only 6–8% coverage
of ISTAT-reported wine grape area. Likely cause: these regions have many
small fragmented family-run vineyards mixed with other crops; CORINE
classifies the surrounding patches as "Complex cultivation patterns"
(class 242) instead of "Vineyards" (class 221).

For these two regions, the dataset captures the *spatial distribution of
larger commercial vineyards*, not the full picture. Recommended
mitigations:

1. Use the CORINE 221 polygons as a starting point, then expand using
   OSM `landuse=vineyard` or other data.
2. For yield-prediction work, treat the polygon as "where the biggest
   vineyards are" and accept that smaller production areas are missing.
3. If precise vineyard locations matter, source from Italian agricultural
   parcel registries (SIGC / AGEA) — these are authoritative but require
   institutional access.

## Best-mapped regions

Eight regions have CORINE coverage above 90% of ISTAT area:

- Sicilia, Puglia, Piemonte (artificially high due to outdated CORINE vs.
  contracting modern area)
- Toscana, Trento, Bolzano, Molise, Valle d'Aosta (genuinely good
  coverage)

For these regions the dataset is essentially a complete map of vineyard
locations.

## Notes on small regions

**Valle d'Aosta, Liguria** — tiny vineyard footprints (430 ha and 353 ha
respectively in CORINE). Production is artisanal and concentrated in a
few microzones (e.g., Cinque Terre in Liguria). The dataset captures
them but expect sparse polygon counts; the geographic precision is
limited for these regions.

**Basilicata, Calabria** — moderate under-mapping (50–55%). Wine
production is real but concentrated in specific zones (Vulture in
Basilicata, Cirò in Calabria). The CORINE polygons capture the main
zones; smaller scattered vineyards may be missing.
