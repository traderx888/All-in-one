#!/usr/bin/env python3
"""
Polymarket Oil Price Alert Bot

Monitors Polymarket for oil-related prediction markets and sends
Telegram alerts when new markets appear or prices change significantly.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from polymarket_client import fetch_oil_markets
from telegram_alert import (
    format_new_market_alert,
    format_price_change_alert,
    send_alert,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("oil-alert-bot")

STATE_FILE = Path("market_state.json")


def load_state() -> dict:
    """Load previously seen markets from disk."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state: dict) -> None:
    """Persist market state to disk."""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def check_and_alert(bot_token: str, chat_id: str, keywords: list[str], threshold: float) -> None:
    """Fetch markets, compare with saved state, and send alerts."""
    markets = fetch_oil_markets(keywords)
    state = load_state()
    new_state = {}

    for market in markets:
        mid = market["id"]
        if not mid:
            continue

        new_state[mid] = market["prices"]

        if mid not in state:
            # New market discovered
            msg = format_new_market_alert(market)
            logger.info("New market: %s", market["question"])
            send_alert(bot_token, chat_id, msg)
        else:
            # Check for significant price changes
            old_prices = state[mid]
            new_prices = market["prices"]
            for outcome, new_price in new_prices.items():
                old_price = old_prices.get(outcome)
                if old_price is not None and abs(new_price - old_price) >= threshold:
                    msg = format_price_change_alert(market, old_prices, new_prices)
                    logger.info("Price change on: %s", market["question"])
                    send_alert(bot_token, chat_id, msg)
                    break  # One alert per market per cycle

    save_state(new_state)


def main() -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id or bot_token == "your_bot_token_here":
        logger.error(
            "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID. "
            "Copy .env.example to .env and fill in your credentials."
        )
        sys.exit(1)

    poll_interval = int(os.getenv("POLL_INTERVAL", "300"))
    keywords = [k.strip() for k in os.getenv("OIL_KEYWORDS", "oil,crude,brent,wti,petroleum,opec").split(",")]
    threshold = float(os.getenv("PRICE_CHANGE_THRESHOLD", "5"))

    logger.info("Starting Oil Price Alert Bot")
    logger.info("Keywords: %s", keywords)
    logger.info("Poll interval: %ds, Price change threshold: %.1f%%", poll_interval, threshold)

    # Send startup message
    send_alert(bot_token, chat_id, "🛢 <b>Oil Price Alert Bot Started</b>\n\nMonitoring Polymarket for oil-related markets.")

    while True:
        try:
            check_and_alert(bot_token, chat_id, keywords, threshold)
        except Exception:
            logger.exception("Error during check cycle")
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
