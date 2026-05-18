"""
Build derived "vineyard zone" polygons by buffered union of CORINE class
221 polygons.

The approach: buffer each vineyard fragment by R kilometers (using UTM
projection for accurate metric distances), union the buffered polygons,
identify connected components, and keep the top N by area.

Usage:
    python build_vineyard_zone.py --region puglia_ITF4 --buffer 1.5 --top-n 3
    python build_vineyard_zone.py --region sardegna_ITG2 --buffer 10 --top-n 1

UTM zone is auto-detected from the centroid longitude (works for all
Italian regions). Output is in WGS84 (EPSG:4326).

Requirements:
    pip install geopandas shapely
"""
import argparse
import json
import math
from pathlib import Path

import geopandas as gpd
from shapely.ops import unary_union
from shapely.geometry import MultiPolygon, mapping
from shapely import make_valid


def utm_epsg_from_lon(lon):
    """Best UTM zone for a given longitude (Northern hemisphere)."""
    zone = int((lon + 180) / 6) + 1
    return 32600 + zone  # 32601..32660 are UTM N zones


def main():
    parser = argparse.ArgumentParser(
        description="Build vineyard zone polygons by buffered union of CORINE 221"
    )
    parser.add_argument("--region", required=True,
                        help="Region file slug (e.g. 'puglia_ITF4')")
    parser.add_argument("--input-dir", default="data/corine_221_by_region",
                        help="Where to find the CORINE region GeoJSON files")
    parser.add_argument("--buffer", type=float, default=1.5,
                        help="Buffer distance in km (default: 1.5)")
    parser.add_argument("--top-n", type=int, default=3,
                        help="How many top connected components to keep (default: 3)")
    parser.add_argument("--out-dir", default="data/derived_vineyard_zones",
                        help="Output directory")
    args = parser.parse_args()

    src = Path(args.input_dir) / f"{args.region}.geojson"
    if not src.exists():
        raise SystemExit(f"Input not found: {src}")

    vine_gdf = gpd.read_file(src)
    print(f"Loaded {len(vine_gdf)} CORINE 221 polygons from {src}")

    # Auto-select UTM zone from the dataset centroid
    centroid_lon = unary_union(list(vine_gdf.geometry)).centroid.x
    utm_epsg = utm_epsg_from_lon(centroid_lon)
    print(f"Using UTM EPSG:{utm_epsg} (longitude {centroid_lon:.2f})")

    vine_utm = vine_gdf.to_crs(epsg=utm_epsg)

    # Buffer + union
    buffered = unary_union(
        [make_valid(g).buffer(args.buffer * 1000) for g in vine_utm.geometry]
    )
    if isinstance(buffered, MultiPolygon):
        comps = sorted(buffered.geoms, key=lambda g: g.area, reverse=True)
    else:
        comps = [buffered]
    print(f"Buffer = {args.buffer} km  ->  {len(comps)} connected components")
    print(f"Top-{args.top_n} component areas (km²): "
          f"{[round(g.area / 1e6) for g in comps[:args.top_n]]}")

    total_vineyard_area = unary_union(list(vine_utm.geometry)).area

    out_dir = Path(args.out_dir) / args.region
    out_dir.mkdir(parents=True, exist_ok=True)

    print()
    print(f"{'#':<5}{'polygon area km²':<20}{'vineyard inside ha':<22}"
          f"{'coverage %':<13}{'density %':<10}")

    saved = []
    for i, comp in enumerate(comps[:args.top_n]):
        inside = unary_union(
            [g.intersection(comp) for g in vine_utm.geometry if g.intersects(comp)]
        ).area
        area_km2 = comp.area / 1e6
        inside_ha = inside / 1e4
        coverage = 100 * inside / total_vineyard_area
        density = 100 * inside / comp.area if comp.area > 0 else 0

        comp_wgs84 = (
            gpd.GeoSeries([comp], crs=f"EPSG:{utm_epsg}")
            .to_crs(epsg=4326)
            .iloc[0]
        )

        out_file = out_dir / f"{args.region}_comp{i+1}_buf{args.buffer}km.geojson"
        fc = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "rank": i + 1,
                    "source": args.region,
                    "buffer_km": args.buffer,
                    "area_km2": area_km2,
                    "inside_vineyard_ha": inside_ha,
                    "coverage_pct": coverage,
                    "density_pct": density,
                },
                "geometry": mapping(comp_wgs84),
            }],
        }
        out_file.write_text(json.dumps(fc), encoding="utf-8")
        saved.append(out_file)
        print(f"{i+1:<5}{area_km2:<20,.0f}{inside_ha:>10,.0f}            "
              f"{coverage:<13.1f}{density:<10.1f}")

    print()
    print(f"Saved {len(saved)} files to {out_dir}/")


if __name__ == "__main__":
    main()
