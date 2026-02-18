"""Console/terminal notifier using rich formatting."""

import logging
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.notifiers.base import BaseNotifier
from src.models.tweet import Tweet

logger = logging.getLogger(__name__)

# Sector color mapping
SECTOR_COLORS = {
    "semiconductor": "bright_blue",
    "gold": "yellow",
    "silver": "white",
    "crypto": "bright_magenta",
    "macro": "bright_green",
    "energy": "bright_red",
    "bonds": "cyan",
}


class ConsoleNotifier(BaseNotifier):
    """Print tweet notifications to the terminal with rich formatting."""

    def __init__(self, include_sector_tag: bool = True, include_link: bool = True):
        self.console = Console()
        self.include_sector_tag = include_sector_tag
        self.include_link = include_link

    async def send(self, tweet: Tweet, sentiment: dict = None) -> bool:
        sector = tweet.sector or "general"
        color = SECTOR_COLORS.get(sector, "bright_white")

        title = Text()
        if self.include_sector_tag:
            title.append(f"[{sector.upper()}] ", style=f"bold {color}")
        title.append(f"@{tweet.username}", style="bold cyan")
        title.append(f"  {tweet.created_at.strftime('%Y-%m-%d %H:%M')}", style="dim")

        # Append sentiment badge to title
        if sentiment and sentiment.get("label"):
            emoji = sentiment.get("emoji", "")
            label = sentiment["label"]
            score = sentiment.get("score", 0)
            sentiment_style = {
                "Bullish": "bold green",
                "Bearish": "bold red",
                "Neutral": "dim",
            }.get(label, "dim")
            title.append(f"  {emoji} {label} ({score:.0%})", style=sentiment_style)

        body = Text(tweet.text)
        if self.include_link:
            body.append(f"\n{tweet.tweet_link}", style="dim underline")

        panel = Panel(body, title=title, border_style=color, expand=False)
        self.console.print(panel)
        return True

    async def close(self):
        pass
