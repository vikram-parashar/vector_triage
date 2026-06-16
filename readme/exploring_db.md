- connect:
docker compose exec postgres psql -U postgres -d vector_triage

- checking extension for vector:
SELECT extname FROM pg_extension;

- switch db
\c vector_triage

- list tables
\dt (public tables)
\dt schema_name.*
\dt *.* (all schema
\d (all table, views, seq)

- checking tables
\d tickets
