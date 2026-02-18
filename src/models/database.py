"""SQLite database for persisting tweets and tracking state."""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models.tweet import Tweet

logger = logging.getLogger(__name__)


class Database:
    """SQLite storage for monitored tweets."""

    def __init__(self, db_path: str = "data/tweets.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_id    TEXT PRIMARY KEY,
                username    TEXT NOT NULL,
                text        TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                url         TEXT,
                sector      TEXT,
                is_retweet  INTEGER DEFAULT 0,
                is_reply    INTEGER DEFAULT 0,
                media_urls  TEXT DEFAULT '',
                fetched_at  TEXT NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tweets_username
            ON tweets(username)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tweets_sector
            ON tweets(sector)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tweets_created
            ON tweets(created_at DESC)
        """)
        # Track last fetch time per account
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fetch_state (
                username      TEXT PRIMARY KEY,
                last_tweet_id TEXT,
                last_fetch_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def tweet_exists(self, tweet_id: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM tweets WHERE tweet_id = ?", (tweet_id,)
        )
        return cur.fetchone() is not None

    def save_tweet(self, tweet: Tweet) -> bool:
        """Save a tweet. Returns True if it was new (inserted)."""
        if self.tweet_exists(tweet.tweet_id):
            return False
        self.conn.execute(
            """INSERT INTO tweets
               (tweet_id, username, text, created_at, url, sector,
                is_retweet, is_reply, media_urls, fetched_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                tweet.tweet_id,
                tweet.username,
                tweet.text,
                tweet.created_at.isoformat(),
                tweet.url,
                tweet.sector,
                int(tweet.is_retweet),
                int(tweet.is_reply),
                ",".join(tweet.media_urls),
                tweet.fetched_at.isoformat(),
            ),
        )
        self.conn.commit()
        logger.debug("Saved new tweet %s from @%s", tweet.tweet_id, tweet.username)
        return True

    def save_tweets(self, tweets: list[Tweet]) -> list[Tweet]:
        """Save multiple tweets. Returns list of newly inserted tweets."""
        new_tweets = []
        for tweet in tweets:
            if self.save_tweet(tweet):
                new_tweets.append(tweet)
        return new_tweets

    def update_fetch_state(self, username: str, last_tweet_id: str = ""):
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            """INSERT OR REPLACE INTO fetch_state
               (username, last_tweet_id, last_fetch_at)
               VALUES (?, ?, ?)""",
            (username, last_tweet_id, now),
        )
        self.conn.commit()

    def get_last_tweet_id(self, username: str) -> Optional[str]:
        cur = self.conn.execute(
            "SELECT last_tweet_id FROM fetch_state WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        return row["last_tweet_id"] if row else None

    def get_recent_tweets(
        self,
        username: Optional[str] = None,
        sector: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get recent tweets, optionally filtered by username or sector."""
        query = "SELECT * FROM tweets WHERE 1=1"
        params = []
        if username:
            query += " AND username = ?"
            params.append(username)
        if sector:
            query += " AND sector = ?"
            params.append(sector)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        cur = self.conn.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def get_account_stats(self) -> list[dict]:
        """Get tweet count and last fetch time per account."""
        cur = self.conn.execute("""
            SELECT
                t.username,
                COUNT(*) as tweet_count,
                MAX(t.created_at) as latest_tweet,
                f.last_fetch_at
            FROM tweets t
            LEFT JOIN fetch_state f ON t.username = f.username
            GROUP BY t.username
            ORDER BY t.username
        """)
        return [dict(row) for row in cur.fetchall()]

    def prune_old_tweets(self, max_per_account: int = 5000):
        """Remove oldest tweets beyond the limit per account."""
        usernames = self.conn.execute(
            "SELECT DISTINCT username FROM tweets"
        ).fetchall()
        for (username,) in usernames:
            self.conn.execute(
                """DELETE FROM tweets WHERE username = ? AND tweet_id NOT IN (
                    SELECT tweet_id FROM tweets WHERE username = ?
                    ORDER BY created_at DESC LIMIT ?
                )""",
                (username, username, max_per_account),
            )
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
