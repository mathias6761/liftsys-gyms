# Turn the extracted parquet into small map tiles the app downloads on demand.
# Tile = 0.25° x 0.25° (about 28 x 15 km in Europe), path tiles/<floor(lat*4)>/<floor(lon*4)>.json
# Usage: python build.py <gyms.parquet> <repo dir> <release>
import json
import math
import os
import re
import shutil
import sys
from collections import defaultdict

import duckdb

src, repo, release = sys.argv[1], sys.argv[2], sys.argv[3]
STUDIO = {'yoga_studio', 'pilates_studio', 'tai_chi_studio', 'barre_class', 'martial_arts_club', 'cycling_class', 'rock_climbing_gym', 'gymnastics_center', 'boxing_class'}

rows = duckdb.sql(f"SELECT id, name, lat, lon, cat, confidence, website, phone, street, city FROM '{src}' ORDER BY confidence DESC").fetchall()

norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
tiles = defaultdict(list)
seen = defaultdict(list)  # (cell) -> [(lat, lon, normname)] to drop duplicates of the same gym
kept = 0
for id_, name, lat, lon, cat, conf, web, phone, street, city in rows:
    if lat is None or lon is None:
        continue
    n = norm(name)
    cell = (round(lat * 500), round(lon * 500))  # ~200 m buckets
    near = [s for dx in (-1, 0, 1) for dy in (-1, 0, 1) for s in seen[(cell[0] + dx, cell[1] + dy)]]
    if any(n and (n == m or n in m or m in n) and abs(lat - a) < 0.0012 and abs(lon - b) < 0.002 for a, b, m in near):
        continue
    seen[cell].append((lat, lon, n))
    addr = ', '.join(x for x in (street, city) if x)
    rec = [id_[:16], name, round(lat, 5), round(lon, 5), 1 if cat in STUDIO else 0, web or '', phone or '', addr]
    while rec and rec[-1] == '':
        rec.pop()
    tiles[(math.floor(lat * 4), math.floor(lon * 4))].append(rec)
    kept += 1

out = os.path.join(repo, 'tiles')
shutil.rmtree(out, ignore_errors=True)
for (la, lo), recs in tiles.items():
    d = os.path.join(out, str(la))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f'{lo}.json'), 'w') as f:
        json.dump(recs, f, ensure_ascii=False, separators=(',', ':'))

with open(os.path.join(repo, 'meta.json'), 'w') as f:
    json.dump({'v': 1, 'release': release, 'gyms': kept, 'tiles': len(tiles), 'tileDeg': 0.25, 'fields': ['id', 'name', 'lat', 'lon', 'studio', 'website', 'phone', 'address'], 'attribution': 'Overture Maps Foundation (CDLA-Permissive-2.0)'}, f, indent=2)
print(f'{len(rows)} rows -> {kept} gyms in {len(tiles)} tiles')
