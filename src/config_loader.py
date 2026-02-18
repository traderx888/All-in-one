"""Load and validate YAML configuration files."""

import os
import logging
from pathlib import Path

import yaml

from src.models.account import Account, Sector

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent / "config"


def _env_override(yaml_val: str, env_key: str) -> str:
    """Use environment variable if set, otherwise fall back to YAML value."""
    return os.environ.get(env_key, yaml_val) or ""


def load_settings(path: str = None) -> dict:
    """Load global settings from settings.yaml."""
    settings_path = Path(path) if path else CONFIG_DIR / "settings.yaml"
    with open(settings_path) as f:
        cfg = yaml.safe_load(f)

    # Override secrets from environment variables
    notif = cfg.get("notifications", {})

    tg = notif.get("telegram", {})
    tg["bot_token"] = _env_override(tg.get("bot_token", ""), "TELEGRAM_BOT_TOKEN")
    tg["chat_id"] = _env_override(tg.get("chat_id", ""), "TELEGRAM_CHAT_ID")

    dc = notif.get("discord", {})
    dc["webhook_url"] = _env_override(dc.get("webhook_url", ""), "DISCORD_WEBHOOK_URL")

    ln = notif.get("line", {})
    ln["access_token"] = _env_override(
        ln.get("access_token", ""), "LINE_NOTIFY_TOKEN"
    )

    api_cfg = cfg.get("scraper", {}).get("twitter_api", {})
    api_cfg["bearer_token"] = _env_override(
        api_cfg.get("bearer_token", ""), "TWITTER_BEARER_TOKEN"
    )

    return cfg


def load_accounts(path: str = None) -> tuple[list[Sector], dict[str, Account]]:
    """Load accounts grouped by sector from accounts.yaml.

    Returns:
        (sectors, all_accounts) where all_accounts is a dict
        keyed by lowercase username, with merged sector tags.
    """
    accounts_path = Path(path) if path else CONFIG_DIR / "accounts.yaml"
    with open(accounts_path) as f:
        cfg = yaml.safe_load(f)

    sectors = []
    all_accounts: dict[str, Account] = {}  # username -> Account

    for sector_name, sector_data in cfg.get("sectors", {}).items():
        sector = Sector(
            name=sector_name,
            description=sector_data.get("description", ""),
        )
        for acct_data in sector_data.get("accounts", []):
            username = acct_data["username"]
            key = username.lower()

            if key in all_accounts:
                # Account appears in multiple sectors - merge
                existing = all_accounts[key]
                if sector_name not in existing.sectors:
                    existing.sectors.append(sector_name)
                # Use highest priority
                priority_rank = {"high": 3, "medium": 2, "low": 1}
                new_pri = acct_data.get("priority", "medium")
                if priority_rank.get(new_pri, 0) > priority_rank.get(
                    existing.priority, 0
                ):
                    existing.priority = new_pri
                sector.accounts.append(existing)
            else:
                account = Account(
                    username=username,
                    note=acct_data.get("note", ""),
                    priority=acct_data.get("priority", "medium"),
                    sectors=[sector_name],
                )
                all_accounts[key] = account
                sector.accounts.append(account)

        sectors.append(sector)

    logger.info(
        "Loaded %d sectors with %d unique accounts",
        len(sectors), len(all_accounts),
    )
    return sectors, all_accounts
