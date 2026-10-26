# liftsys-gyms

Gyms and fitness studios worldwide, cut into small map tiles for the lift.sys app.

- Source: [Overture Maps Foundation](https://overturemaps.org) Places, release in `meta.json`.
  Licence: [CDLA-Permissive-2.0](https://cdla.dev/permissive-2-0/). Credit "Overture Maps Foundation" wherever the data is shown.
- Tiles: `tiles/<floor(lat*4)>/<floor(lon*4)>.json`, 0.25° squares. Each is a list of
  `[id, name, lat, lon, studio(0/1), website?, phone?, address?]`. No file = no gyms there.

## Update

```
python scripts/extract.py <overture release, e.g. 2026-10-21.0> gyms.parquet   # needs duckdb
python scripts/build.py gyms.parquet . <release>
```

Releases are listed at https://docs.overturemaps.org/release/latest/.
