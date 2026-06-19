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

-- there are tweets with response_tweet_id x but no tweet with tweet_id x, inserted in tweet_edges, nonetheless, for u->v, make sure u and v exist
