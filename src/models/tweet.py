"""Tweet data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Tweet:
    """Represents a single tweet/post from Twitter/X."""

    tweet_id: str
    username: str
    text: str
    created_at: datetime
    url: str
    sector: str = ""
    is_retweet: bool = False
    is_reply: bool = False
    media_urls: list[str] = field(default_factory=list)
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def tweet_link(self) -> str:
        """Full URL to the tweet on X."""
        if self.url:
            return self.url
        return f"https://x.com/{self.username}/status/{self.tweet_id}"

    def short_text(self, max_len: int = 200) -> str:
        """Truncated text for notifications."""
        if len(self.text) <= max_len:
            return self.text
        return self.text[:max_len] + "..."

    def to_dict(self) -> dict:
        return {
            "tweet_id": self.tweet_id,
            "username": self.username,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
            "url": self.url,
            "sector": self.sector,
            "is_retweet": self.is_retweet,
            "is_reply": self.is_reply,
            "media_urls": ",".join(self.media_urls),
            "fetched_at": self.fetched_at.isoformat(),
        }
