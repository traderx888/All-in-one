"""Polymarket API client for fetching oil-related prediction markets."""

import logging
import requests

logger = logging.getLogger(__name__)

GAMMA_API_URL = "https://gamma-api.polymarket.com"


def fetch_oil_markets(keywords: list[str]) -> list[dict]:
    """Fetch all open markets from Polymarket that match oil-related keywords."""
    all_markets = []
    next_cursor = ""

    while True:
        params = {"closed": "false", "limit": "100", "active": "true"}
        if next_cursor:
            params["next_cursor"] = next_cursor

        try:
            resp = requests.get(f"{GAMMA_API_URL}/markets", params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.error("Failed to fetch markets: %s", e)
            break

        if not data:
            break

        for market in data:
            question = (market.get("question") or "").lower()
            description = (market.get("description") or "").lower()
            tags_raw = market.get("tags") or []
            tags = " ".join(t.lower() for t in tags_raw) if isinstance(tags_raw, list) else str(tags_raw).lower()
            searchable = f"{question} {description} {tags}"

            if any(kw.lower() in searchable for kw in keywords):
                all_markets.append(_normalize_market(market))

        next_cursor = data[-1].get("id", "") if len(data) == 100 else ""
        if not next_cursor:
            break

    logger.info("Found %d oil-related markets", len(all_markets))
    return all_markets


def _normalize_market(market: dict) -> dict:
    """Extract useful fields from a raw market response."""
    outcomes = market.get("outcomes") or []
    outcome_prices = market.get("outcomePrices") or []

    prices = {}
    if isinstance(outcomes, str):
        import json as _json
        try:
            outcomes = _json.loads(outcomes)
            outcome_prices = _json.loads(outcome_prices) if isinstance(outcome_prices, str) else outcome_prices
        except Exception:
            outcomes = []
            outcome_prices = []

    for i, outcome in enumerate(outcomes):
        price = float(outcome_prices[i]) if i < len(outcome_prices) else None
        if price is not None:
            prices[outcome] = round(price * 100, 1)  # Convert to percentage

    return {
        "id": market.get("id"),
        "condition_id": market.get("conditionId") or market.get("condition_id"),
        "question": market.get("question"),
        "description": market.get("description", "")[:200],
        "url": f"https://polymarket.com/event/{market.get('slug', '')}",
        "volume": market.get("volume"),
        "liquidity": market.get("liquidity"),
        "end_date": market.get("endDate"),
        "prices": prices,  # e.g. {"Yes": 65.2, "No": 34.8}
    }
