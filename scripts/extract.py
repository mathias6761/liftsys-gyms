# Pull every gym / fitness studio in the world out of Overture Maps Places (free, CDLA-Permissive-2.0)
# into one local parquet file. Usage: python extract.py <release> <out.parquet>
import sys
import duckdb

release, out = sys.argv[1], sys.argv[2]
c = duckdb.connect()
c.sql("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
src = f"read_parquet('s3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*', hive_partitioning=1)"
c.sql(f"""
COPY (
  SELECT id, names.primary AS name, ST_Y(geometry) AS lat, ST_X(geometry) AS lon,
         basic_category, taxonomy.primary AS cat, confidence,
         websites[1] AS website, phones[1] AS phone,
         addresses[1].freeform AS street, addresses[1].locality AS city
  FROM {src}
  WHERE (basic_category IN ('gym', 'fitness_studio')
         OR taxonomy.primary IN ('boxing_class', 'boxing_gym', 'martial_arts_club', 'cycling_class', 'rock_climbing_gym', 'crossfit', 'gymnastics_center'))
    AND confidence >= 0.6
    AND coalesce(operating_status, 'open') <> 'permanently_closed'
    AND names.primary IS NOT NULL
) TO '{out}' (FORMAT parquet)
""")
print(c.sql(f"SELECT count(*), count(DISTINCT cat) FROM '{out}'").fetchall())
