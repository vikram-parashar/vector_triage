import os
import argparse
from tqdm import tqdm
import subprocess
import zipfile
import pandas as pd
from utils import DATA_DIR, DOWNLOAD_DIR, get_pg_cursor

CSV_FILENAME = "twcs.csv"
CSV_PATH = os.path.join(DATA_DIR, CSV_FILENAME)

ZIP_FILENAME = "customer-support-on-twitter.zip"
ZIP_PATH = os.path.join(DOWNLOAD_DIR, ZIP_FILENAME)
KAGGLE_URL = "https://www.kaggle.com/api/v1/datasets/download/thoughtvector/customer-support-on-twitter"


def ensure_data_exists():
    if os.path.exists(CSV_PATH):
        print(f"Data file found at {CSV_PATH}")
        return

    print(f"Data file not found at {CSV_PATH}. Attempting download...")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    command = ["curl", "-L", "-o", ZIP_PATH, KAGGLE_URL]

    try:
        print(f"Downloading {KAGGLE_URL}...")
        subprocess.run(command, check=True)

        print("Extracting...")
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extract(CSV_FILENAME, DATA_DIR)

        print("Done")

    except Exception as e:
        raise e


def ingest_tweets():
    pandas_chunksize = 10_000

    total_rows = sum(1 for _ in open(CSV_PATH)) - 1
    total_chunks = (total_rows + pandas_chunksize - 1) // pandas_chunksize

    try:
        chunk_iterator = pd.read_csv(CSV_PATH, chunksize=pandas_chunksize)
        for _, chunk in tqdm(
            enumerate(chunk_iterator), total=total_chunks, desc="Processing chunks"
        ):
            records = []

            for _, row in enumerate(chunk.itertuples(index=False)):
                records.append(
                    (
                        int(row.tweet_id) if not pd.isna(row.tweet_id) else None,
                        row.author_id,
                        row.inbound,
                        row.created_at,
                        row.text,
                        int(row.in_response_to_tweet_id)
                        if not pd.isna(row.in_response_to_tweet_id)
                        else None,
                    )
                )

            with get_pg_cursor() as cursor:
                insert_query = """
                    INSERT INTO tweets (
                        tweet_id, author_id, inbound, created_at, text ,parent_tweet_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tweet_id) DO NOTHING;
                """
                cursor.executemany(insert_query, records)

    except Exception as e:
        print("Error during ingestion")
        raise e

    print("Ingestion success")


def ingest_edges():
    pandas_chunksize = 10_000

    total_rows = sum(1 for _ in open(CSV_PATH)) - 1
    total_chunks = (total_rows + pandas_chunksize - 1) // pandas_chunksize
    try:
        chunk_iterator = pd.read_csv(CSV_PATH, chunksize=pandas_chunksize)
        for _, chunk in tqdm(
            enumerate(chunk_iterator), total=total_chunks, desc="Processing chunks"
        ):
            edges = []

            for _, row in enumerate(chunk.itertuples(index=False)):
                children = (
                    list(map(int, str(row.response_tweet_id).split(",")))
                    if not pd.isna(row.response_tweet_id)
                    else []
                )
                for v in children:
                    edges.append((row.tweet_id, v))

            with get_pg_cursor() as cursor:
                insert_query = """
                    INSERT INTO tweet_edges (
                        parent_tweet_id, child_tweet_id 
                    )
                    VALUES (%s, %s)
                    ON CONFLICT (parent_tweet_id,child_tweet_id) DO NOTHING;
                """
                cursor.executemany(insert_query, edges)

        print("updating tweet_edges.child_exists...")
        with get_pg_cursor() as cursor:
            set_child_exist_query = """
                UPDATE tweet_edges e
                SET child_exists = TRUE
                FROM tweets t
                WHERE e.child_tweet_id = t.tweet_id;
            """
            cursor.execute(set_child_exist_query)

    except Exception as e:
        print("Error during ingestion")
        raise e

    print("Ingestion success")


def test():
    df = pd.read_csv(CSV_PATH)
    vals = pd.to_numeric(df["in_response_to_tweet_id"], errors="coerce")
    print(df["in_response_to_tweet_id"].dtype)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tweets", action="store_true")
    parser.add_argument("--edges", action="store_true")
    parser.add_argument("--test", action="store_true")

    args = parser.parse_args()

    ensure_data_exists()

    if args.test:
        test()
    elif args.tweets:
        ingest_tweets()
    elif args.edges:
        ingest_edges()
    else:
        parser.print_help()
