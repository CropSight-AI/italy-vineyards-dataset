"""
Pull CORINE Land Cover 2018 class 221 (Vineyards) polygons for any
NUTS2 region, clipped to that region's administrative boundary.

Default: pulls all 21 Italian NUTS2 regions.

Output: one GeoJSON file per region in `data/corine_221_by_region/`.

Usage:
    python pull_corine_221.py                       # all 21 Italian regions
    python pull_corine_221.py --regions ITH3 ITI1   # specific regions only

Requirements:
    pip install requests shapely

This script has no external dependencies on geopandas — uses raw shapely +
requests. Adapt the REGIONS list at the top to extend to other countries.
"""
import argparse
import json
import math
import time
from pathlib import Path

import requests
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely import make_valid


# Italian NUTS2 regions: (slug, NUTS-2024 code)
ITALY_REGIONS = [
    ("piemonte",        "ITC1"),
    ("valle_daosta",    "ITC2"),
    ("liguria",         "ITC3"),
    ("lombardia",       "ITC4"),
    ("bolzano",         "ITH1"),
    ("trento",          "ITH2"),
    ("veneto",          "ITH3"),
    ("friuli",          "ITH4"),
    ("emilia_romagna",  "ITH5"),
    ("toscana",         "ITI1"),
    ("umbria",          "ITI2"),
    ("marche",          "ITI3"),
    ("lazio",           "ITI4"),
    ("abruzzo",         "ITF1"),
    ("molise",          "ITF2"),
    ("campania",        "ITF3"),
    ("puglia",          "ITF4"),
    ("basilicata",      "ITF5"),
    ("calabria",        "ITF6"),
    ("sicilia",         "ITG1"),
    ("sardegna",        "ITG2"),
]

NUTS_URL = (
    "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/"
    "NUTS_RG_10M_2024_4326_LEVL_2.geojson"
)
CORINE_URL = (
    "https://image.discomap.eea.europa.eu/arcgis/rest/services/"
    "Corine/CLC2018_WM/MapServer/0/query"
)
HEADERS = {"User-Agent": "italy-vineyards-dataset/0.1"}


def fetch_nuts_boundaries():
    """Download NUTS2 GeoJSON and build a {code: feature} dict."""
    print("Downloading NUTS2 boundaries...")
    r = requests.get(NUTS_URL, headers=HEADERS, timeout=120)
    r.raise_for_status()
    nuts = r.json()
    return {f["properties"]["NUTS_ID"]: f for f in nuts["features"]}


def fetch_corine_in_bbox(minx, miny, maxx, maxy):
    """Page through CORINE class 221 polygons inside a bbox."""
    all_features = []
    offset = 0
    while True:
        params = {
            "where": "Code_18='221'",
            "geometry": f"{minx},{miny},{maxx},{maxy}",
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "inSR": 4326,
            "outSR": 4326,
            "outFields": "Code_18,Area_Ha",
            "returnGeometry": "true",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": 1000,
        }
        r = requests.get(CORINE_URL, params=params, headers=HEADERS, timeout=180)
        r.raise_for_status()
        j = r.json()
        feats = j.get("features", [])
        all_features.extend(feats)
        if not j.get("exceededTransferLimit"):
            break
        if not feats:
            break
        offset += len(feats)
    return all_features


def clip_to_region(features, region_geom):
    """Clip vineyard polygons to the region boundary; drop empty/invalid."""
    region_geom = make_valid(region_geom)
    kept = []
    for f in features:
        try:
            poly = shape(f["geometry"])
        except Exception:
            continue
        if not poly.is_valid:
            poly = make_valid(poly)
            if poly.is_empty:
                continue
        try:
            clipped = poly.intersection(region_geom)
        except Exception:
            try:
                clipped = poly.buffer(0).intersection(region_geom)
            except Exception:
                continue
        if not clipped.is_empty:
            kept.append(clipped)
    return kept


def approx_area_ha(geom_wgs84, mean_lat):
    """Approximate area in hectares for a WGS84 geometry."""
    km_per_deg_lon = 111.32 * math.cos(math.radians(mean_lat))
    km_per_deg_lat = 110.57
    sq_km_per_sq_deg = km_per_deg_lon * km_per_deg_lat
    if hasattr(geom_wgs84, "geoms"):
        area_deg2 = sum(g.area for g in geom_wgs84.geoms)
    else:
        area_deg2 = geom_wgs84.area
    return area_deg2 * sq_km_per_sq_deg * 100


def write_geojson(polys, out_path):
    """Write a list of polygons to a FeatureCollection on disk."""
    fc = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature",
             "properties": {"Code_18": "221"},
             "geometry": mapping(p)}
            for p in polys
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(fc), encoding="utf-8")
    return out_path.stat().st_size


def main():
    parser = argparse.ArgumentParser(
        description="Pull CORINE 221 vineyard polygons for one or more NUTS2 regions"
    )
    parser.add_argument("--regions", nargs="+",
                        help="NUTS-2024 codes (default: all Italian)")
    parser.add_argument("--out-dir", default="data/corine_221_by_region",
                        help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    selected = ITALY_REGIONS
    if args.regions:
        wanted = set(args.regions)
        selected = [(s, c) for s, c in ITALY_REGIONS if c in wanted]
        if not selected:
            raise SystemExit(f"No matching regions for {args.regions!r}")

    nuts_by_id = fetch_nuts_boundaries()
    print(f"Processing {len(selected)} region(s)...\n")

    for slug, code in selected:
        feat = nuts_by_id.get(code)
        if feat is None:
            print(f"  {slug:<18} ({code}): MISSING from NUTS file")
            continue
        region_geom = make_valid(shape(feat["geometry"]))
        minx, miny, maxx, maxy = region_geom.bounds

        features = fetch_corine_in_bbox(minx, miny, maxx, maxy)
        kept = clip_to_region(features, region_geom)
        out_file = out_dir / f"{slug}_{code}.geojson"
        size_bytes = write_geojson(kept, out_file)

        mean_lat = (miny + maxy) / 2
        area_ha = approx_area_ha(unary_union(kept) if kept else None, mean_lat) if kept else 0
        print(f"  {slug:<18} ({code}): {len(kept):>4} polygons, "
              f"{area_ha:>9,.0f} ha   -> {out_file.name} ({size_bytes:,} bytes)")
        time.sleep(0.5)  # be polite to EEA

    print(f"\nDone. Files written to {out_dir}/")


if __name__ == "__main__":
    main()
