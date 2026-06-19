CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE tweets (
    tweet_id BIGINT PRIMARY KEY,
    author_id TEXT,
    inbound BOOLEAN,
    created_at TIMESTAMP,
    text TEXT,
    parent_tweet_id BIGINT
);

CREATE TABLE tweet_edges(
    parent_tweet_id BIGINT not null,
    child_tweet_id BIGINT  not null,
    child_exists boolean default true,
    PRIMARY KEY (parent_tweet_id, child_tweet_id)
)
