"""FinTwitBERT sentiment analysis for financial tweets.

Uses StephanAkkerman/FinTwitBERT-sentiment from HuggingFace to
classify tweets as bullish / neutral / bearish.

Trained on 10M+ financial tweets - handles slang, emojis, cashtags
better than generic sentiment models (80.35% accuracy).

Requires: pip install transformers torch
"""

import logging
import re
from typing import Optional

from src.models.tweet import Tweet

logger = logging.getLogger(__name__)

# Lazy-loaded pipeline (model downloads on first use ~500MB)
_pipeline = None


def _get_pipeline():
    """Lazy-load the FinTwitBERT sentiment pipeline."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    try:
        from transformers import pipeline
    except ImportError:
        raise ImportError(
            "transformers not installed. Run: pip install transformers torch"
        )

    logger.info("Loading FinTwitBERT-sentiment model (first run downloads ~500MB)...")
    _pipeline = pipeline(
        "sentiment-analysis",
        model="StephanAkkerman/FinTwitBERT-sentiment",
    )
    logger.info("FinTwitBERT-sentiment model loaded.")
    return _pipeline


def _preprocess_tweet(text: str) -> str:
    """Clean tweet text for FinTwitBERT.

    FinTwitBERT was trained with @USER and [URL] masks.
    """
    # Replace @mentions with @USER
    text = re.sub(r"@\w+", "@USER", text)
    # Replace URLs with [URL]
    text = re.sub(r"https?://\S+", "[URL]", text)
    # Truncate to model max length (128 tokens ~ 512 chars)
    return text[:512]


def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of a single text.

    Returns:
        {"label": "Bullish"|"Neutral"|"Bearish", "score": 0.0-1.0}
    """
    pipe = _get_pipeline()
    cleaned = _preprocess_tweet(text)
    result = pipe(cleaned, truncation=True, max_length=128)[0]
    return {
        "label": result["label"].capitalize(),
        "score": round(result["score"], 4),
    }


def analyze_tweet(tweet: Tweet) -> dict:
    """Analyze sentiment of a Tweet object.

    Returns:
        {"label": "Bullish"|"Neutral"|"Bearish", "score": 0.0-1.0,
         "emoji": str}
    """
    result = analyze_sentiment(tweet.text)

    # Add emoji indicator
    emoji_map = {
        "Bullish": "🟢",
        "Bearish": "🔴",
        "Neutral": "⚪",
    }
    result["emoji"] = emoji_map.get(result["label"], "⚪")
    return result


def analyze_tweets_batch(tweets: list[Tweet]) -> list[dict]:
    """Analyze sentiment for a batch of tweets.

    Returns list of dicts, each with:
        {"tweet_id", "username", "text_preview", "label", "score", "emoji"}
    """
    if not tweets:
        return []

    pipe = _get_pipeline()
    cleaned_texts = [_preprocess_tweet(t.text) for t in tweets]
    results = pipe(cleaned_texts, truncation=True, max_length=128, batch_size=16)

    emoji_map = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "⚪"}

    output = []
    for tweet, result in zip(tweets, results):
        label = result["label"].capitalize()
        output.append({
            "tweet_id": tweet.tweet_id,
            "username": tweet.username,
            "sector": tweet.sector,
            "text_preview": tweet.short_text(80),
            "label": label,
            "score": round(result["score"], 4),
            "emoji": emoji_map.get(label, "⚪"),
        })
    return output
