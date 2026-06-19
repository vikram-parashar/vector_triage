from typing import List
from sentence_transformers import SentenceTransformer

from utils import get_pg_cursor


def get_embeddings(text_list: List[str]):
    model = SentenceTransformer("BAAI/bge-base-en-v1.5")

    embeddings = model.encode(text_list, batch_size=32)

    return embeddings


def _get_root_nodes():
    with get_pg_cursor() as cursor:
        query = """
        select tweet_id from tweets where parent_tweet_id is null
        """
        cursor.execute(query)
        tweet_ids = []
        for tweet in cursor.fetchall():
            tweet_ids.append(tweet[0])

        return tweet_ids


def build_graph():
    from collections import defaultdict

    G = defaultdict(list)

    with get_pg_cursor() as cursor:
        cursor.execute("""
            SELECT parent_tweet_id, child_tweet_id
            FROM tweet_edges
            WHERE child_exists = TRUE
        """)

        for u, v in cursor:
            G[u].append(v)
            G[v].append(u)

    return G


G = build_graph()
seen = set()


def get_conversation(start):
    stack = [start]
    conv_ids = []

    while stack:
        u = stack.pop()

        if u in seen:
            continue

        seen.add(u)
        conv_ids.append(u)

        stack.extend(G[u])

    return conv_ids


def make_summary_from(root_tweet_id):
    conv_ids = get_conversation(root_tweet_id)
    with get_pg_cursor() as cursor:
        cursor.execute(
            """
            SELECT tweet_id, text, inbound, created_at
            FROM tweets
            WHERE tweet_id = ANY(%s)
            ORDER BY created_at
        """,
            (conv_ids,),
        )
        tweets = cursor.fetchall()
    tweets.sort(key=lambda x: x[3])
    customer = []
    support = []
    for tweet in tweets:
        if tweet[2]:
            customer.append(f"{tweet[1]} ")
        else:
            support.append(f"{tweet[1]} ")
    issue = " ".join(customer[:3])
    resolution = " ".join(support[-2:])
    return f""" Issue: {issue} \n Resolution: {resolution} """
