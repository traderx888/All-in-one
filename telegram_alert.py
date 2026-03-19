"""Telegram alert sender for oil price market updates."""

import logging
import requests

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"


def send_alert(bot_token: str, chat_id: str, message: str) -> bool:
    """Send a message via Telegram Bot API."""
    url = f"{TELEGRAM_API}/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error("Failed to send Telegram alert: %s", e)
        return False


def format_new_market_alert(market: dict) -> str:
    """Format an alert for a newly discovered oil market."""
    prices_str = _format_prices(market.get("prices", {}))
    volume = market.get("volume")
    volume_str = f"${float(volume):,.0f}" if volume else "N/A"

    return (
        f"🛢 <b>New Oil Market on Polymarket</b>\n\n"
        f"<b>{market['question']}</b>\n\n"
        f"📊 Prices: {prices_str}\n"
        f"💰 Volume: {volume_str}\n"
        f"🔗 <a href=\"{market['url']}\">View on Polymarket</a>"
    )


def format_price_change_alert(market: dict, old_prices: dict, new_prices: dict) -> str:
    """Format an alert for a significant price change."""
    changes = []
    for outcome, new_price in new_prices.items():
        old_price = old_prices.get(outcome)
        if old_price is not None:
            diff = new_price - old_price
            arrow = "📈" if diff > 0 else "📉"
            changes.append(f"  {outcome}: {old_price}% → {new_price}% ({arrow} {diff:+.1f}%)")

    changes_str = "\n".join(changes) if changes else "  Price updated"

    return (
        f"🛢 <b>Oil Market Price Change</b>\n\n"
        f"<b>{market['question']}</b>\n\n"
        f"📊 Changes:\n{changes_str}\n\n"
        f"🔗 <a href=\"{market['url']}\">View on Polymarket</a>"
    )


def _format_prices(prices: dict) -> str:
    if not prices:
        return "N/A"
    return " | ".join(f"{k}: {v}%" for k, v in prices.items())
