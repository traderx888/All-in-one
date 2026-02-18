"""Factory functions to build components from configuration."""

import logging

from src.scrapers.base import BaseScraper
from src.scrapers.nitter import NitterScraper
from src.scrapers.twitter_api import TwitterAPIScraper
from src.notifiers.base import BaseNotifier
from src.notifiers.console import ConsoleNotifier
from src.notifiers.telegram import TelegramNotifier
from src.notifiers.discord import DiscordNotifier
from src.notifiers.line_notify import LineNotifier

logger = logging.getLogger(__name__)


def create_scraper(settings: dict) -> BaseScraper:
    """Create the appropriate scraper based on settings."""
    scraper_cfg = settings.get("scraper", {})
    backend = scraper_cfg.get("backend", "nitter")
    timeout = scraper_cfg.get("request_timeout", 30)
    user_agent = scraper_cfg.get("user_agent", "")

    if backend == "api":
        token = scraper_cfg.get("twitter_api", {}).get("bearer_token", "")
        logger.info("Using Twitter API v2 backend")
        return TwitterAPIScraper(bearer_token=token, timeout=timeout)
    else:
        instances = scraper_cfg.get("nitter_instances", [])
        logger.info("Using Nitter RSS backend with %d instances", len(instances))
        return NitterScraper(
            instances=instances, timeout=timeout, user_agent=user_agent
        )


def create_notifiers(settings: dict) -> list[BaseNotifier]:
    """Create all enabled notification channels."""
    notifiers: list[BaseNotifier] = []
    notif_cfg = settings.get("notifications", {})
    include_sector = notif_cfg.get("include_sector_tag", True)
    include_link = notif_cfg.get("include_tweet_link", True)

    # Console (always available)
    if notif_cfg.get("console", {}).get("enabled", True):
        notifiers.append(
            ConsoleNotifier(include_sector_tag=include_sector, include_link=include_link)
        )

    # Telegram
    tg = notif_cfg.get("telegram", {})
    if tg.get("enabled"):
        notifiers.append(TelegramNotifier(tg["bot_token"], tg["chat_id"]))
        logger.info("Telegram notifications enabled")

    # Discord
    dc = notif_cfg.get("discord", {})
    if dc.get("enabled"):
        notifiers.append(DiscordNotifier(dc["webhook_url"]))
        logger.info("Discord notifications enabled")

    # LINE Notify
    ln = notif_cfg.get("line", {})
    if ln.get("enabled"):
        notifiers.append(LineNotifier(ln["access_token"]))
        logger.info("LINE Notify notifications enabled")

    return notifiers
