"""
Derive a wine grape yield CSV from an ISTAT bulk export.

Computes yield = HP_Q_EXT / ART * 0.1 (= t/ha) for each season,
optionally restricting to specific NUTS2 codes.

Usage:
    python derive_yield_csv.py --istat <path>             # all 21 regions
    python derive_yield_csv.py --istat <path> --region ITG1 --out sicilia.csv

The output CSV is the format expected by CropSight's `data_loader.py`:
    year (season-key like "2014-2015"), yield (t/ha)
If --region is omitted, the CSV also includes a `polygon` column with
the lowercase region name.

Requirements:
    Python stdlib only — no pandas needed.
"""
import argparse
import csv
import sys


# Map ISTAT region codes (NUTS-2016, used in ISTAT data) to slugs
ISTAT_TO_SLUG = {
    "ITC1": "piemonte",
    "ITC2": "valle_daosta",
    "ITC3": "liguria",
    "ITC4": "lombardia",
    "ITD1": "bolzano",        # NUTS-2016
    "ITD2": "trento",         # NUTS-2016
    "ITD3": "veneto",         # NUTS-2016
    "ITD4": "friuli",         # NUTS-2016
    "ITD5": "emilia_romagna", # NUTS-2016
    "ITE1": "toscana",        # NUTS-2016
    "ITE2": "umbria",         # NUTS-2016
    "ITE3": "marche",         # NUTS-2016
    "ITE4": "lazio",          # NUTS-2016
    "ITF1": "abruzzo",
    "ITF2": "molise",
    "ITF3": "campania",
    "ITF4": "puglia",
    "ITF5": "basilicata",
    "ITF6": "calabria",
    "ITG1": "sicilia",
    "ITG2": "sardegna",
}


def main():
    parser = argparse.ArgumentParser(
        description="Derive wine grape yield CSV from ISTAT bulk export"
    )
    parser.add_argument("--istat", required=True,
                        help="Path to the ISTAT bulk CSV (DCSP_COLTIVAZIONI)")
    parser.add_argument("--region", help="ISTAT region code (e.g. ITG1). "
                                         "If omitted, outputs all regions with a polygon column.")
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--crop", default="WINEES",
                        help="Crop code (default: WINEES = wine grapes)")
    args = parser.parse_args()

    # Pull all (region, year, indicator) → value triples for the chosen crop
    raw = {}
    with open(args.istat, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("TYPE_OF_CROP") != args.crop:
                continue
            ra = row.get("REF_AREA")
            if ra not in ISTAT_TO_SLUG:
                continue
            if args.region and ra != args.region:
                continue
            try:
                yr = int(row["TIME_PERIOD"])
                obs = float(row["Observation"])
            except (ValueError, TypeError, KeyError):
                continue
            raw[(ra, yr, row["DATA_TYPE"])] = obs

    # Compute yield per (region, year) where both HP_Q_EXT and ART exist
    yields = []
    seen_pairs = set()
    for (ra, yr, dt), val in raw.items():
        if (ra, yr) in seen_pairs:
            continue
        if dt != "HP_Q_EXT":
            continue
        ar = raw.get((ra, yr, "ART"))
        if ar is None or ar <= 0:
            continue
        yld = val / ar * 0.1   # quintals/ha -> t/ha
        season = f"{yr - 1}-{yr}"
        yields.append((ISTAT_TO_SLUG[ra], season, round(yld, 4)))
        seen_pairs.add((ra, yr))

    yields.sort()

    # Write CSV
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if args.region:
            w.writerow(['year', 'yield'])
            for _, season, yld in yields:
                w.writerow([season, yld])
        else:
            w.writerow(['polygon', 'year', 'yield'])
            for poly, season, yld in yields:
                w.writerow([poly, season, yld])

    print(f"Wrote {len(yields)} rows to {args.out}", file=sys.stderr)
    if not args.region:
        unique_regions = sorted({y[0] for y in yields})
        print(f"Regions included: {unique_regions}", file=sys.stderr)


if __name__ == "__main__":
    main()
